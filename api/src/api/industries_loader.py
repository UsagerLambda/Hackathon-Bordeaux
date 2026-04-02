"""
industries_loader.py – Charge les sites industriels ou pollués
pour la recherche de proximité via la route /api/cell/{cell_id}.
"""

import geopandas as gpd
from pathlib import Path

# Chemins possibles pour les données industrielles (à la racine du repo)
_GEOJSON_PATH = Path(__file__).resolve().parents[2] / "industries.geojson"
_DWG_ETAB_PATH = Path(__file__).resolve().parents[2] / "RI_ETAB_POL_P.dwg"
_DWG_BASOL_PATH = Path(__file__).resolve().parents[2] / "RI_BASOL_P.dwg"

gdf_industries = None

def load_industries() -> gpd.GeoDataFrame:
    """Charge les données industrielles en mémoire et prépare l'index spatial."""
    global gdf_industries
    
    path_to_load = None
    if _GEOJSON_PATH.exists():
        path_to_load = _GEOJSON_PATH
    elif _DWG_ETAB_PATH.exists():
        path_to_load = _DWG_ETAB_PATH
    elif _DWG_BASOL_PATH.exists():
        path_to_load = _DWG_BASOL_PATH
        
    if path_to_load:
        try:
            print(f"⚙️ Chargement des sites industriels depuis {path_to_load}...")
            gdf_industries = gpd.read_file(path_to_load)
            
            # Si le CRS n'est pas défini, on présume 4326 par défaut, excepté pour les DWG qui 
            # pourraient déjà être projetés. Geopandas lira le CRS s'il est dispo.
            if gdf_industries.crs is None:
                gdf_industries = gdf_industries.set_crs(epsg=4326)
                
            # On projette en EPSG:2154 (Lambert 93) pour avoir des distances en mètres
            if gdf_industries.crs.to_epsg() != 2154:
                gdf_industries = gdf_industries.to_crs(epsg=2154)
                
            # Forcer la création de l'index spatial (sindex) pour optimiser les calculs
            _ = gdf_industries.sindex
            print(f"✅ Données industrielles chargées : {len(gdf_industries)} établissements (index spatial prêt)")
            
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des industries ({path_to_load}) : {e}")
            gdf_industries = gpd.GeoDataFrame(columns=["nom", "type_risque", "geometry"], crs="EPSG:2154")
    else:
        print("⚠️ Aucun fichier de données industrielles trouvé. L'API renverra une liste vide.")
        gdf_industries = gpd.GeoDataFrame(columns=["nom", "type_risque", "geometry"], crs="EPSG:2154")

    # Création du spatial index pour l'empty DF aussi, pour éviter les erreurs
    _ = gdf_industries.sindex
    return gdf_industries

def get_gdf_industries() -> gpd.GeoDataFrame:
    """Retourne le GeoDataFrame global des industries."""
    global gdf_industries
    if gdf_industries is None:
        load_industries()
    return gdf_industries
