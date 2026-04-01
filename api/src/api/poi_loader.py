"""
poi_loader.py – Charge et gère les Points d'Intérêt (gymnases/refuges).
Permet de trouver les N lieux de refuge les plus proches d'un point donné.
"""

import math
from typing import List, Dict

# Liste des 20 gymnases (Extraits de l'Open Data Bordeaux Métropole)
REFUGES = [
    {"name": "Gymnase Stéhélin", "address": "Bordeaux", "lat": 44.856598, "lon": -0.622511},
    {"name": "Gymnase Promis", "address": "Bordeaux", "lat": 44.838807, "lon": -0.551333},
    {"name": "Gymnase Nelson Paillou", "address": "Bordeaux", "lat": 44.822895, "lon": -0.573505},
    {"name": "Gymnase Barbey", "address": "Bordeaux", "lat": 44.827177, "lon": -0.562971},
    {"name": "Gymnase Jules Ferry", "address": "Bordeaux", "lat": 44.842556, "lon": -0.606600},
    {"name": "Gymnase Alice Milliat", "address": "Bordeaux", "lat": 44.835264, "lon": -0.572457},
    {"name": "Gymnase Johnston", "address": "Bordeaux", "lat": 44.828564, "lon": -0.599886},
    {"name": "Gymnase Tivoli", "address": "Bordeaux", "lat": 44.852833, "lon": -0.598194},
    {"name": "Gymnase Malleret", "address": "Bordeaux", "lat": 44.849130, "lon": -0.585772},
    {"name": "Gymnase Virginia", "address": "Bordeaux", "lat": 44.848739, "lon": -0.626141},
    {"name": "Gymnase Dupaty", "address": "Blanquefort", "lat": 44.907977, "lon": -0.627593},
    {"name": "Gymnase Bechon", "address": "Blanquefort", "lat": 44.916019, "lon": -0.636951},
    {"name": "Gymnase Séguinaud", "address": "Bassens", "lat": 44.890153, "lon": -0.520860},
    {"name": "Gymnase Brassens", "address": "Lormont", "lat": 44.872381, "lon": -0.517354},
    {"name": "Gymnase Marègue", "address": "Cenon", "lat": 44.851563, "lon": -0.505908},
    {"name": "Gymnase Rambaud", "address": "Bouliac", "lat": 44.813692, "lon": -0.503723},
    {"name": "Gymnase Alouette", "address": "Pessac", "lat": 44.802463, "lon": -0.668906},
    {"name": "Gymnase INJS", "address": "Gradignan", "lat": 44.785866, "lon": -0.606993},
    {"name": "Gymnase Robert Geneste", "address": "Bordeaux", "lat": 44.821800, "lon": -0.550825},
    {"name": "Gymnase Envol d'Aquitaine", "address": "Bordeaux", "lat": 44.830617, "lon": -0.565780},
]


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en mètres entre deux points (formule Haversine)."""
    R = 6371000  # Rayon de la Terre en mètres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_nearest_refuges(lat: float, lon: float, limit: int = 3) -> List[Dict]:
    """
    Retourne les N refuges les plus proches d'un point (lat, lon).
    Ajoute la distance calculée dans chaque objet.
    """
    # Calcul des distances pour tous les refuges
    with_distances = []
    for r in REFUGES:
        dist = haversine_distance(lat, lon, r["lat"], r["lon"])
        with_distances.append({**r, "distance_m": round(dist)})

    # Tri par distance croissante et limite
    nearest = sorted(with_distances, key=lambda x: x["distance_m"])
    return nearest[:limit]
