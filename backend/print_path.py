import sys
from pathlib import Path
import src.api.industries_loader as loader
print(loader._GEOJSON_ETAB_PATH)
print("Exists:", loader._GEOJSON_ETAB_PATH.exists())
