import math
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.data_loader import get_gdf, load_data

load_data()
gdf = get_gdf()

# remove industries.geojson to trigger the fallback!
import os
from pathlib import Path
root = Path(__file__).resolve().parents[1]
try:
    os.remove(root / "industries.geojson")
except Exception:
    pass

with TestClient(app) as client:
    # let's find a cell that has dist_industrie < 250
    gdf["dist_industrie"] = gdf["dist_industrie"].astype(float)
    matches_ind = gdf[gdf["dist_industrie"] < 250.0]
    
    if not matches_ind.empty:
        cell_id = matches_ind.iloc[0]["cell_id"]
        print(f"Testing Cell {cell_id} (has dist_industrie={matches_ind.iloc[0]['dist_industrie']}):")
        response = client.get(f"/api/cell/{cell_id}")
        data = response.json()
        print(f"nearby_industrial_sites: {data.get('nearby_industrial_sites')}")
    else:
        print("No cells with dist_industrie < 250 found in scores.geojson.")
