import geopandas as gpd
from src.api.data_loader import get_gdf, load_data

load_data()
gdf = get_gdf()
match = gdf[gdf["cell_id"] == "cell_0_55"].iloc[0]
print(f"Centroid of cell_0_55: {match.geometry.centroid}")
