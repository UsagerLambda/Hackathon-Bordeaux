"""
address.py – Route GET /api/address?q=...
Géocode une adresse via l'API BAN (geo.api.gouv.fr)
puis trouve la cellule correspondante par point-in-polygon.
"""

from fastapi import APIRouter, HTTPException, Query
import httpx
from shapely.geometry import Point

from src.api.data_loader import get_gdf
from src.api.industries_loader import get_nearest_industries
from src.api.poi_loader import get_nearest_refuges
from src.api.scoring import get_recommendations
from src.api.utils import FEATURE_COLS, convert

router = APIRouter(tags=["Adresse"])

# URL de l'API Base Adresse Nationale
_BAN_URL = "https://api-adresse.data.gouv.fr/search/"


@router.get("/address")
async def search_address(q: str = Query(..., description="Adresse à rechercher")):
    """
    Géocode une adresse et retourne la cellule Résili-Score correspondante.
    1. Appel API BAN → coordonnées lon/lat
    2. Point-in-polygon sur le GeoDataFrame
    3. Retourne features + score + recommandations
    """

    # ── 1. Géocodage via l'API BAN ──────────────────────────────────────
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(_BAN_URL, params={"q": q, "limit": 1})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Erreur lors de l'appel à l'API BAN : {exc}",
            )

    data = resp.json()
    features = data.get("features", [])
    if not features:
        raise HTTPException(
            status_code=404,
            detail=f"Adresse introuvable : '{q}'",
        )

    coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
    lon, lat = coords[0], coords[1]
    label = features[0]["properties"].get("label", q)

    # ── 2. Point-in-polygon ──────────────────────────────────────────────
    gdf = get_gdf()
    point = Point(lon, lat)

    # Recherche de la cellule contenant le point
    mask = gdf.geometry.contains(point)
    match = gdf[mask]

    if match.empty:
        # Fallback : Recherche de la cellule la plus proche (si hors grille ou sur trottoir)
        nearest_idx = gdf.geometry.distance(point).idxmin()
        row = gdf.loc[nearest_idx]
        print(f"📍 {label} : Cellule trouvée via distance (plus proche)")
    else:
        row = match.iloc[0]

    score = str(row["score"])
    cluster = int(row["cluster"])
    cluster_label = str(row.get("cluster_label", f"Cluster {cluster}"))
    cell_id = str(row["cell_id"])

    # Calcul des refuges proches de l'adresse géocodée
    nearest_refuges = get_nearest_refuges(lat, lon, limit=3)

    nearby_industrial_sites = get_nearest_industries(lat, lon, limit=3)

    # Recommandations dynamiques + conseils du collègue
    recommendations = get_recommendations(score, cluster)
    colleague_advice = str(row.get("conseils_particulier", ""))
    if colleague_advice and colleague_advice != "nan":
        recommendations.insert(0, colleague_advice)

    return {
        "cell_id": cell_id,
        "address": label,
        "coordinates": {"lat": lat, "lon": lon},
        "score": score,
        "score_num": float(row.get("score_particulier", 50)),
        "cluster": {
            "id": cluster,
            "label": cluster_label
        },
        "population": int(row.get("population", 0)),
        "explication": str(row.get("explication_particulier", "")),
        "features": {col: convert(row[col]) for col in FEATURE_COLS if col in row},
        "recommendations": recommendations,
        "nearest_refuges": nearest_refuges,
        "nearby_industrial_sites": nearby_industrial_sites,
    }


