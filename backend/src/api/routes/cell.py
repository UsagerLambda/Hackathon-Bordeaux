"""
cell.py – Route GET /api/cell/{cell_id}
Retourne les features, le score et les recommandations d'une cellule.
"""

from fastapi import APIRouter, HTTPException

from src.api.data_loader import get_gdf
from src.api.industries_loader import get_nearest_industries
from src.api.poi_loader import get_nearest_refuges
from src.api.scoring import get_recommendations
from src.api.utils import FEATURE_COLS, convert

router = APIRouter(tags=["Cellules"])


@router.get("/cell/{cell_id}")
def get_cell(cell_id: str):
    """Retourne les données d'une cellule par son identifiant."""
    gdf = get_gdf()

    # Recherche de la cellule
    match = gdf[gdf["cell_id"] == cell_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Cellule '{cell_id}' introuvable.")

    from src.api.poi_loader import get_nearest_refuges

    row = match.iloc[0]
    score = str(row["score"])
    cluster = int(row["cluster"])
    cluster_label = str(row.get("cluster_label", f"Cluster {cluster}"))

    # Calcul du centroïde pour trouver les refuges proches
    centroid = row.geometry.centroid
    nearest_refuges = get_nearest_refuges(centroid.y, centroid.x, limit=3)
    nearby_industrial_sites = get_nearest_industries(centroid.y, centroid.x, limit=3)

    # Recommandations dynamiques + conseils du collègue
    recommendations = get_recommendations(score, cluster)
    colleague_advice = str(row.get("conseils_particulier", ""))
    if colleague_advice and colleague_advice != "nan":
        recommendations.insert(0, colleague_advice)

    return {
        "cell_id": cell_id,
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
