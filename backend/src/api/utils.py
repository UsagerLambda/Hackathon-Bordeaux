"""
utils.py – Utilitaires partagés entre les routes.
"""

import numpy as np

# Colonnes de features brutes exposées par les routes cell et address
FEATURE_COLS = [
    "flood_score", "nappe", "argile", "icu",
    "in_pprt", "green_cover", "zone_humide", "water_infiltration",
    "dist_industrie", "dist_sites_pol", "population",
]


def convert(val):
    """Convertit les types numpy en types Python natifs pour la sérialisation JSON."""
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, np.floating):
        return float(val)
    return val
