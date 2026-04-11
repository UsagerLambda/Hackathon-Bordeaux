"""
industries_loader.py – Charge les sites industriels ou pollués
pour la recherche de proximité via la route /api/cell/{cell_id}.
"""

from typing import List, Dict
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Chemins vers les données sources téléchargées par le pipeline ML
_DATA_DIR = Path(__file__).resolve().parents[3] / "data"
_GEOJSON_ETAB_PATH = _DATA_DIR / "ri_etab_pol_p.geojson"
_GEOJSON_BASOL_PATH = _DATA_DIR / "ri_basol_p.geojson"


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

def get_nearest_industries(lat: float, lon: float, limit: int = 3) -> List[Dict]:
    """
    Retourne les N sites industriels/pollués les plus proches d'un point (lat, lon).
    Calcule en Lambert 93 (mètres) pour la précision.
    """
    gdf_ind = get_gdf_industries()
    if gdf_ind.empty:
        return []

    # 1. Créer le point en WGS84 et projeter en Lambert 93 (EPSG:2154)
    point_4326 = Point(lon, lat)
    point_2154 = gpd.GeoSeries([point_4326], crs="EPSG:4326").to_crs(epsg=2154).iloc[0]

    # 2. Exclure les géométries nulles/vides avant le calcul
    temp_gdf = gdf_ind[gdf_ind.geometry.notna() & ~gdf_ind.geometry.is_empty].copy()
    if temp_gdf.empty:
        return []

    temp_gdf["distance_m"] = temp_gdf.geometry.distance(point_2154)

    # 3. Garantir au moins 1 site de chaque type (ETAB + BASOL)
    # puis compléter avec les plus proches restants jusqu'à `limit`
    etab = temp_gdf[temp_gdf["type_risque"] == "Établissement Industriel"].sort_values("distance_m")
    basol = temp_gdf[temp_gdf["type_risque"] == "Site Pollué (BASOL)"].sort_values("distance_m")

    selected_idx = set()
    candidates = []

    # 1 nearest de chaque type en priorité
    for groupe in (etab, basol):
        if not groupe.empty:
            row = groupe.iloc[0]
            selected_idx.add(groupe.index[0])
            candidates.append(groupe.head(1))

    # Compléter avec les plus proches globaux non encore sélectionnés
    reste = temp_gdf[~temp_gdf.index.isin(selected_idx)].sort_values("distance_m")
    reste_needed = limit - len(candidates)
    if reste_needed > 0 and not reste.empty:
        candidates.append(reste.head(reste_needed))

    nearest = pd.concat(candidates).sort_values("distance_m") if candidates else temp_gdf.head(0)

    # 4. Formater pour le JSON
    results = []
    for _, row in nearest.iterrows():
        try:
            centroid_2154 = row.geometry.centroid
            centroid_4326 = gpd.GeoSeries([centroid_2154], crs="EPSG:2154").to_crs(epsg=4326).iloc[0]
            results.append({
                "nom": str(row.get("nom", "Inconnu")),
                "type_risque": str(row.get("type_risque", "Non spécifié")),
                "distance_m": round(float(row["distance_m"]), 1),
                "lat": round(float(centroid_4326.y), 6),
                "lon": round(float(centroid_4326.x), 6)
            })
        except Exception as e:
            print(f"⚠️ Site ignoré (erreur conversion): {e}")

    return results
