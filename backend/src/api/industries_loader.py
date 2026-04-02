"""
industries_loader.py – Charge les sites industriels ou pollués
pour la recherche de proximité via la route /api/cell/{cell_id}.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

# Chemins pour les données industrielles
_GEOJSON_ETAB_PATH = Path("/Users/lucasscianna/Desktop/ri_etab_pol_p.geojson")
_GEOJSON_BASOL_PATH = Path("/Users/lucasscianna/Desktop/ri_basol_p.geojson")

# Fallback si jamais les fichiers sont quand même à la racine du projet
if not _GEOJSON_ETAB_PATH.exists():
    _GEOJSON_ETAB_PATH = Path(__file__).resolve().parents[3] / "ri_etab_pol_p.geojson"
if not _GEOJSON_BASOL_PATH.exists():
    _GEOJSON_BASOL_PATH = Path(__file__).resolve().parents[3] / "ri_basol_p.geojson"

gdf_industries = None

def load_industries() -> gpd.GeoDataFrame:
    """Charge les données industrielles et BASOL en mémoire et prépare l'index spatial."""
    global gdf_industries
    gdfs = []

    # 1. Chargement des établissements industriels (ETAB)
    if _GEOJSON_ETAB_PATH.exists():
        try:
            print(f"⚙️ Chargement des sites industriels depuis {_GEOJSON_ETAB_PATH.name}...")
            gdf_etab = gpd.read_file(_GEOJSON_ETAB_PATH)
            # Uniformisation des colonnes
            if "libelle" in gdf_etab.columns:
                gdf_etab["nom"] = gdf_etab["libelle"]
            gdf_etab["type_risque"] = "Établissement Industriel"
            gdfs.append(gdf_etab[["nom", "type_risque", "geometry"]])
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {_GEOJSON_ETAB_PATH.name}: {e}")

    # 2. Chargement des sites pollués (BASOL)
    if _GEOJSON_BASOL_PATH.exists():
        try:
            print(f"⚙️ Chargement des sites pollués depuis {_GEOJSON_BASOL_PATH.name}...")
            gdf_basol = gpd.read_file(_GEOJSON_BASOL_PATH)
            if "libelle" in gdf_basol.columns:
                gdf_basol["nom"] = gdf_basol["libelle"]
            gdf_basol["type_risque"] = "Site Pollué (BASOL)"
            gdfs.append(gdf_basol[["nom", "type_risque", "geometry"]])
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {_GEOJSON_BASOL_PATH.name}: {e}")

    # 3. Fusion et Indexation Spatiale
    if gdfs:
        gdf_industries = pd.concat(gdfs, ignore_index=True)
        # Reconvertir en GeoDataFrame après le concat de Pandas
        gdf_industries = gpd.GeoDataFrame(gdf_industries, crs=gdfs[0].crs)
        
        # S'assurer d'être en Lambert 93 (2154) pour calculer en mètres
        if gdf_industries.crs is None:
            gdf_industries = gdf_industries.set_crs(epsg=4326)
        if gdf_industries.crs.to_epsg() != 2154:
            gdf_industries = gdf_industries.to_crs(epsg=2154)
            
        print(f"✅ Données concaténées : {len(gdf_industries)} sites (index spatial prêt)")
    else:
        print("⚠️ Aucun fichier geojson d'industries trouvé. Données vides.")
        gdf_industries = gpd.GeoDataFrame(columns=["nom", "type_risque", "geometry"], crs="EPSG:2154")

    # Initialisation index spatial
    _ = gdf_industries.sindex
    return gdf_industries

def get_gdf_industries() -> gpd.GeoDataFrame:
    """Retourne le GeoDataFrame global condensé des industries."""
    global gdf_industries
    if gdf_industries is None:
        load_industries()
    return gdf_industries
