import geopandas as gpd
from src.api.industries_loader import load_industries

gdf = load_industries()
print(f"Total entries: {len(gdf)}")
if len(gdf) > 0:
    print("Columns:", gdf.columns.tolist())
    print("Sample:", gdf.drop(columns=["geometry"]).head(2).to_dict("records"))
