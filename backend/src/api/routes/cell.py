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
    "in_pprt", "green_cover", "zone_humide", "water_infiltration",
    "dist_industrie", "dist_sites_pol", "population",
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
    cluster_label = str(row.get("cluster_label", f"Cluster {cluster}"))

    # Calcul du centroïde pour trouver les refuges proches
    centroid = row.geometry.centroid
    nearest_refuges = get_nearest_refuges(centroid.y, centroid.x, limit=3)

    # ---------- RECHERCHE DES SITES INDUSTRIELS À PROXIMITÉ (< 250m) ----------
    # ---------- RECHERCHE DES 3 SITES INDUSTRIELS/POLLUÉS LES PLUS PROCHES ----------
    import geopandas as gpd
    from src.api.industries_loader import get_gdf_industries
    
    gdf_ind = get_gdf_industries()
    nearby_industrial_sites = []
    
    if not gdf_ind.empty:
        try:
            # Créer un Series géographique en EPSG:2154 (pour calcul en mètres)
            cell_geom_2154 = gpd.GeoSeries([centroid], crs="EPSG:4326").to_crs("EPSG:2154").iloc[0]
            
            # Calcul de distance depuis ce point pour toutes les industries
            distances = gdf_ind.distance(cell_geom_2154)
            # On prend les 3 plus proches (peu importe la distance absolue)
            closest_indices = distances.nsmallest(3).index

            for idx in closest_indices:
                match_row = gdf_ind.loc[idx]
                dist = distances.loc[idx]
                
                nom = match_row.get("nom", match_row.get("nom_etablissement", match_row.get("Name", "Inconnu")))
                if str(nom) == "nan": nom = "Inconnu"

                type_r = match_row.get("type_risque", match_row.get("pollution", "Non spécifié"))
                if str(type_r) == "nan": type_r = "Non spécifié"

                # Convertir la géométrie de l'industrie en WGS84 pour récupérer lon/lat
                geom_wgs = gpd.GeoSeries([match_row.geometry], crs="EPSG:2154").to_crs("EPSG:4326").iloc[0]

                nearby_industrial_sites.append({
                    "nom": str(nom),
                    "type_risque": str(type_r),
                    "distance_m": round(dist, 1),
                    "lat": geom_wgs.y,
                    "lon": geom_wgs.x
                })
        except Exception as e:
            print(f"Erreur lors du calcul de proximité des industries: {e}")

    # Recommandations dynamiques + conseils du collègue
    recommendations = get_recommendations(score, cluster)
    colleague_advice = str(row.get("conseils_particulier", ""))
    if colleague_advice and colleague_advice != "nan":
        recommendations.insert(0, colleague_advice)

    return {
        "cell_id": cell_id,
        "score": score,
        "cluster": {
            "id": cluster,
            "label": cluster_label
        },
        "population": int(row.get("population", 0)),
        "explication": str(row.get("explication_particulier", "")),
        "features": {col: _convert(row[col]) for col in _FEATURE_COLS if col in row},
        "recommendations": recommendations,
        "nearest_refuges": nearest_refuges,
        "nearby_industrial_sites": nearby_industrial_sites,
    }


def _convert(val):
    """Convertit les types numpy en types Python natifs pour la sérialisation JSON."""
    import numpy as np

    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val
