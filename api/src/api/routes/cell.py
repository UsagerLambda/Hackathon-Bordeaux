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
    import geopandas as gpd
    from src.api.industries_loader import get_gdf_industries
    
    gdf_ind = get_gdf_industries()
    nearby_industrial_sites = []
    
    if not gdf_ind.empty:
        # Créer un GeoDataFrame à partir du centroïde, projeté en EPSG:2154 (pour calcul en mètres)
        cell_point_gdf = gpd.GeoDataFrame([{"geometry": centroid}], crs="EPSG:4326")
        cell_point_gdf = cell_point_gdf.to_crs(epsg=2154)
        
        try:
            # sjoin_nearest utilise l'index spatial automatiquement
            closest_industries = gpd.sjoin_nearest(
                cell_point_gdf, 
                gdf_ind, 
                how="inner", 
                max_distance=250.0, 
                distance_col="distance_exacte"
            )
            
            # Formater les résultats
            for _, match_row in closest_industries.iterrows():
                # On essaie plusieurs noms de colonnes probables
                nom = match_row.get("nom", match_row.get("nom_etablissement", match_row.get("Name", "Inconnu")))
                if str(nom) == "nan":
                    nom = "Inconnu"
                    
                type_r = match_row.get("type_risque", match_row.get("pollution", "Non spécifié"))
                if str(type_r) == "nan":
                    type_r = "Non spécifié"
                    
                distance = round(match_row["distance_exacte"], 1)
                
                nearby_industrial_sites.append({
                    "nom": str(nom),
                    "type_risque": str(type_r),
                    "distance_m": distance
                })
                
            # Trier la liste par distance croissante
            nearby_industrial_sites.sort(key=lambda x: x["distance_m"])
            
        except Exception as e:
            print(f"Erreur lors du calcul de proximité des industries: {e}")

    # Fallback (utilisation des données du GeoJSON pré-calculées 'dist_industrie' et 'dist_sites_pol')
    # si le fichier d'industries externe n'est pas chargé et que les données y sont présentes.
    import math
    if gdf_ind.empty:
        try:
            dist_ind = float(row.get("dist_industrie", 9999))
            if not math.isnan(dist_ind) and dist_ind < 250.0:
                nearby_industrial_sites.append({
                    "nom": "Établissement Industriel",
                    "type_risque": "Industriel (non précisé)",
                    "distance_m": round(dist_ind, 1)
                })
        except:
            pass
            
        try:
            dist_pol = float(row.get("dist_sites_pol", 9999))
            if not math.isnan(dist_pol) and dist_pol < 250.0:
                nearby_industrial_sites.append({
                    "nom": "Site Pollué",
                    "type_risque": "Pollution / Sol",
                    "distance_m": round(dist_pol, 1)
                })
        except:
            pass
            
        # Trier par distance (le fallback peut ajouter jusqu'à 2 sites)
        nearby_industrial_sites.sort(key=lambda x: x["distance_m"])

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
