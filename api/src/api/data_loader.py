"""
data_loader.py – Charge le fichier GeoJSON kmeans_clusters.geojson
et expose le GeoDataFrame en mémoire pour toutes les routes.
"""

from pathlib import Path
from typing import Optional
import geopandas as gpd

# Chemin vers le fichier GeoJSON (à la racine du repo)
_GEOJSON_PATH = Path(__file__).resolve().parents[2] / "scores.geojson"

# GeoDataFrame global – alimenté au démarrage par load_data()
gdf: Optional[gpd.GeoDataFrame] = None


def load_data() -> gpd.GeoDataFrame:
    """
    Charge le GeoJSON en mémoire.
    Lève FileNotFoundError si le fichier est absent.
    """
    global gdf

    if not _GEOJSON_PATH.exists():
        raise FileNotFoundError(
            f"Fichier GeoJSON introuvable : {_GEOJSON_PATH}\n"
            "Place scores.geojson à la racine du repo."
        )

    gdf = gpd.read_file(_GEOJSON_PATH)

    # S'assurer que le CRS est bien WGS84 (EPSG:4326)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.set_crs(epsg=4326, allow_override=True)

    print(f"✅ GeoJSON chargé : {len(gdf)} cellules")
    return gdf


def get_gdf() -> gpd.GeoDataFrame:
    """Retourne le GeoDataFrame. Lève si non chargé."""
    if gdf is None:
        raise RuntimeError("Les données ne sont pas encore chargées. Appelle load_data() d'abord.")
    return gdf
