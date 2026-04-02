import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path

data = [
    {"nom": "Super Factory", "type_risque": "Pollution métaux", "geometry": Point(-0.880419, 44.857)},
    {"nom": "Toxic Corp", "type_risque": "Risque chimique", "geometry": Point(-0.881, 44.856162)},
    {"nom": "Far Away Inc", "type_risque": "Bruit", "geometry": Point(-0.885, 44.856162)},
]

gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
# Save as industries.geojson in the root 
root = Path(__file__).resolve().parents[1]
gdf.to_file(root / "industries.geojson", driver="GeoJSON")
print(f"Created industries.geojson at {root / 'industries.geojson'}")
