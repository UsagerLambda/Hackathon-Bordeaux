"""
main.py — Lance le pipeline ML complet ou une étape spécifique.

Usage :
  python main.py                  # pipeline complet
  python main.py features         # étape 1 uniquement
  python main.py kmeans           # étape 2 uniquement
  python main.py scoring          # étape 3 uniquement
  python main.py features kmeans  # étapes 1 et 2
"""

import sys
import time

STEPS = {
    "features": ("Étape 1 : Feature engineering", "pipeline.features", "run_features"),
    "kmeans":   ("Étape 2 : Clustering KMeans",   "pipeline.kmeans",   "run_kmeans"),
    "scoring":  ("Étape 3 : Scoring + SHAP",      "pipeline.scoring",  "run_scoring"),
}


def run_step(name: str) -> None:
    label, module_path, fn_name = STEPS[name]
    print(f"\n── {label} {'─' * (52 - len(label))}")
    import importlib
    module = importlib.import_module(module_path)
    t0 = time.time()
    getattr(module, fn_name)()
    print(f"  ⏱  {time.time() - t0:.1f}s")


if __name__ == "__main__":
    requested = sys.argv[1:] if len(sys.argv) > 1 else list(STEPS.keys())

    unknown = [s for s in requested if s not in STEPS]
    if unknown:
        print(f"Étapes inconnues : {unknown}")
        print(f"Étapes disponibles : {list(STEPS.keys())}")
        sys.exit(1)

    t_total = time.time()
    for step in requested:
        run_step(step)

    print(f"\n✅ Pipeline terminé en {time.time() - t_total:.1f}s")
