from fastapi.testclient import TestClient
from src.api.main import app
from src.api.data_loader import get_gdf
import json

with TestClient(app) as client:
    print("Testing Health:")
    print(client.get("/").json())

    # Need a valid cell_id
    gdf = get_gdf()
    if not gdf.empty:
        first_cell_id = gdf["cell_id"].iloc[0]
        print(f"\nTesting Cell {first_cell_id}:")
        
        response = client.get(f"/api/cell/{first_cell_id}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps({k: data.get(k) for k in ["cell_id", "nearby_industrial_sites"]}, indent=2))
    else:
        print("GDF is empty!")
