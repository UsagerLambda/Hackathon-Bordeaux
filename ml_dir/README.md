# Résili-Score — Pipeline ML

Le **Nutri-Score de la résilience urbaine** pour Bordeaux Métropole — un score de risque par cellule de 250m × 250m, avec explications et conseils personnalisés.

---

## Lancer le pipeline

```bash
# 1. Installer les dépendances
uv sync

# 2. Télécharger les données sources
python download_data.py

# 3. Pipeline complet
python main.py

# Ou étape par étape
python main.py features   # feature engineering
python main.py kmeans     # clustering
python main.py scoring    # scores + SHAP
```

---

## Structure

```
ml_dir/
├── main.py                    # point d'entrée
├── config.py                  # paramètres (charge .env)
├── download_data.py           # téléchargement des sources
├── .env                       # configuration locale (gitignorée)
├── .env.example               # template
└── pipeline/
    ├── features.py            # étape 1 : feature engineering → features.geojson
    ├── kmeans.py              # étape 2 : clustering KMeans → kmeans_clusters.geojson
    └── scoring.py             # étape 3 : scores + SHAP → scores.geojson
```

Outputs dans `ml_pipeline/`. `scores.geojson` est aussi copié dans `../scores/` pour le backend.

---

## Features calculées

Grille de ~9 600 cellules 250m × 250m sur Bordeaux Métropole (Lambert93) :

| Feature | Source | Type |
|---|---|---|
| `flood_score` | TRI 2020 — Géorisques | Ordinal 0–4 (4 scénarios) |
| `nappe` | Remontée de nappes — Géorisques | 0 / 1 / 2 |
| `argile` | Aléa retrait-gonflement — DataHub BM | 0 / 2 / 3 |
| `icu` | Îlot de chaleur/fraîcheur — DataHub BM | Float °C |
| `in_pprt` | Zones PPRT — DataHub BM | 0 / 1 |
| `green_cover` | Espaces verts + boisements — DataHub BM | 0 / 1 |
| `water_infiltration` | Capacité d'infiltration — DataHub BM | Note 0–20 |
| `zone_humide` | Zones humides — DataHub BM | 0 / 1 |
| `dist_industrie` | Établissements polluants — DataHub BM | Mètres |
| `dist_sites_pol` | Sites pollués BASOL — DataHub BM | Mètres |
| `population` | Carroyage 200m — INSEE 2015 | Nombre d'individus |

---

## Algorithmes

### KMeans

StandardScaler + KMeans avec k sélectionné par score silhouette sur k ∈ [2, 10] (ou fixé via `N_CLUSTERS` dans `.env`). Les labels sémantiques des clusters sont à mettre à jour dans `pipeline/kmeans.py` après chaque re-clustering.

### Scoring composite

Deux scores 0–100 calculés par MinMax + pondération expert + interactions multiplicatives :

**Score Particulier** — exposition du logement
- Poids dominants : `flood_score` (25%), `icu` (13%), `nappe` (12%)
- Interactions : argile × infiltration, flood × nappe, zone_humide × flood

**Score Élu** — exposition de la population
- Poids dominants : `flood_score` (20%), `population` (18%), `icu` (11%)
- Interactions : flood × population, icu × population, argile × infiltration, zone_humide × flood

Les poids sont configurables dans `.env`.

### SHAP

Ridge Regression + `shap.LinearExplainer` pour chaque cellule (R² ≈ 0.99, < 1s pour ~9 600 cellules). Génère une phrase d'exposition (top 3 risques) et des conseils personnalisés (particulier ou élu).

| Choix | Justification |
|---|---|
| Ridge plutôt que Random Forest | 1000× plus rapide, adapté au score linéaire |
| MinMax plutôt que quantile | Préserve les distributions réelles |
| Poids experts | Résultats justifiables devant un jury |
| KMeans plutôt que DBSCAN | Nombre de clusters contrôlable |

---

## Sources de données

Toutes sous **Licence Ouverte v2.0** (Etalab) :

| Donnée | Source |
|---|---|
| Limites communes BM | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/fv_commu_s) |
| Zonages inondation TRI 2020 | [Géorisques](https://www.georisques.gouv.fr/donnees/bases-de-donnees/zonages-inondation-rapportage-2020) |
| Remontée de nappes | [Géorisques](https://www.georisques.gouv.fr/donnees/bases-de-donnees/inondations-par-remontee-de-nappes) |
| Aléa retrait-gonflement argiles | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_alearga_s) |
| Îlot de chaleur/fraîcheur | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_icu_ifu_s) |
| Zones PPRT | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_pprt_s) |
| Établissements polluants | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_etab_pol_p) |
| Sites pollués BASOL | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_basol_p) |
| Espaces verts / continuité écologique | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ec_inv_protection_s) |
| Zones boisées | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/to_bois_s) |
| Zones humides | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ec_zone_humide_s) |
| Capacité d'infiltration | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/en_infiltration_s) |
| Population carroyage 200m | [INSEE 2015](https://datahub.bordeaux-metropole.fr/explore/dataset/population-bordeaux-metropole-donnees-carroyees-a-200-metres-millesime-2015) |

---

*Projet réalisé dans le cadre du défi [Prévention des risques à Bordeaux Métropole](https://defis.data.gouv.fr/defis/prevention-des-risques-a-bordeaux-metropole) — Open Data University / data.gouv.fr*
