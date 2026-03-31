"""
address.py – Route GET /api/address?q=...
Géocode une adresse via l'API BAN (geo.api.gouv.fr)
puis trouve la cellule correspondante par point-in-polygon.
"""

from fastapi import APIRouter, HTTPException, Query
import httpx
from shapely.geometry import Point

from src.api.data_loader import get_gdf
from src.api.scoring import get_recommendations

router = APIRouter(prefix="/api", tags=["Adresse"])

# URL de l'API Base Adresse Nationale
_BAN_URL = "https://api-adresse.data.gouv.fr/search/"

# Colonnes de features brutes
_FEATURE_COLS = [
    "flood_score", "nappe", "argile", "icu",
    "in_pprt", "green_spaces", "water_infiltration",
    "dist_industrie", "dist_sites_pol",
]


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
        raise HTTPException(
            status_code=404,
            detail=f"Aucune cellule trouvée pour les coordonnées ({lat}, {lon}). "
                   "L'adresse est peut-être hors de Bordeaux Métropole.",
        )

    row = match.iloc[0]
    score = str(row["score"])
    cluster = int(row["cluster"])
    cell_id = str(row["cell_id"])

    return {
        "cell_id": cell_id,
        "address": label,
        "coordinates": {"lat": lat, "lon": lon},
        "score": score,
        "cluster": cluster,
        "features": {col: _convert(row[col]) for col in _FEATURE_COLS},
        "recommendations": get_recommendations(score, cluster),
    }


def _convert(val):
    """Convertit les types numpy en types Python natifs."""
    import numpy as np

    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val
