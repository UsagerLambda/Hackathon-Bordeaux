import geopandas as gpd

print("--- ETAB POL ---")
try:
    gdf1 = gpd.read_file("/Users/lucasscianna/Hackathon-Bordeaux/ri_etab_pol_p.geojson")
    print(gdf1.columns.tolist())
    print(gdf1.drop(columns=["geometry"]).head(2).to_dict(orient="records"))
except Exception as e:
    print(e)
    
print("--- BASOL ---")
try:
    gdf2 = gpd.read_file("/Users/lucasscianna/Hackathon-Bordeaux/ri_basol_p.geojson")
    print(gdf2.columns.tolist())
    print(gdf2.drop(columns=["geometry"]).head(2).to_dict(orient="records"))
except Exception as e:
    print(e)
