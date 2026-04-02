"""
map.py – Route GET /api/map
Retourne le GeoJSON complet avec le score A-E dans les properties.
"""

import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.api.data_loader import get_gdf

router = APIRouter(tags=["Carte"])


@router.get("/map")
def get_map():
    """
    Retourne le GeoJSON complet enrichi du score A-E.
    Utilisé par le front pour colorier la carte Maplibre/Leaflet.
    """
    gdf = get_gdf()

    # Colonnes à inclure dans le GeoJSON de sortie
    cols_to_export = [
        "cell_id", "flood_score", "nappe", "argile", "icu",
        "in_pprt", "green_cover", "zone_humide", "water_infiltration",
        "dist_industrie", "dist_sites_pol", "population",
        "cluster", "cluster_label", "score", "score_particulier", 
        "explication_particulier", "conseils_particulier",  # ← Ajoute ça
        "geometry",
    ]

    # Ne garder que les colonnes existantes
    existing_cols = [c for c in cols_to_export if c in gdf.columns]
    export_gdf = gdf[existing_cols]

    # Convertir en GeoJSON dict
    geojson = json.loads(export_gdf.to_json())

    return JSONResponse(content=geojson, media_type="application/geo+json")
