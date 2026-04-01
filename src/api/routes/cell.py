"""
cell.py – Route GET /api/cell/{cell_id}
Retourne les features, le score et les recommandations d'une cellule.
"""

from fastapi import APIRouter, HTTPException

from src.api.data_loader import get_gdf
from src.api.scoring import get_recommendations

router = APIRouter(tags=["Cellules"])

# Colonnes de features brutes à exposer
_FEATURE_COLS = [
    "flood_score", "nappe", "argile", "icu",
    "in_pprt", "green_spaces", "water_infiltration",
    "dist_industrie", "dist_sites_pol",
]


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

    # Calcul du centroïde pour trouver les refuges proches
    centroid = row.geometry.centroid
    nearest_refuges = get_nearest_refuges(centroid.y, centroid.x, limit=3)

    return {
        "cell_id": cell_id,
        "score": score,
        "cluster": cluster,
        "features": {col: _convert(row[col]) for col in _FEATURE_COLS},
        "recommendations": get_recommendations(score, cluster),
        "nearest_refuges": nearest_refuges,
    }


def _convert(val):
    """Convertit les types numpy en types Python natifs pour la sérialisation JSON."""
    import numpy as np

    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val
