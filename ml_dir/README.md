# Résili-Score

Le **Nutri-Score de la résilience urbaine** pour Bordeaux Métropole — un score de risque par cellule de 250m × 250m, avec explications et conseils personnalisés.

---

## Ce qui a été fait

### Pipeline de données (`run.py`)

Grille de 9 624 cellules de 250m × 250m sur Bordeaux Métropole (Lambert93), avec 11 features calculées par spatial join :

| Feature | Source | Type |
|---|---|---|
| `flood_score` | TRI 2020 — Géorisques | Score ordinal 0–4 (4 scénarios mergés) |
| `nappe` | Remontée de nappes — Géorisques | 0/1/2 |
| `argile` | Aléa retrait-gonflement — DataHub BM | 0/2/3 |
| `icu` | Îlot de chaleur/fraîcheur — DataHub BM | Float °C |
| `in_pprt` | Zones PPRT — DataHub BM | 0/1 |
| `green_cover` | Espaces verts + boisements — DataHub BM | 0/1 (merge 2 couches) |
| `water_infiltration` | Capacité d'infiltration — DataHub BM | note_finale 0–20 |
| `zone_humide` | Zones humides — DataHub BM | 0/1 |
| `dist_industrie` | Établissements polluants — DataHub BM | Distance en mètres |
| `dist_sites_pol` | Sites pollués BASOL — DataHub BM | Distance en mètres |
| `population` | Carroyage 200m — INSEE 2015 | Somme individus |

### Clustering (`kmeans.ipynb`)

- StandardScaler + KMeans avec k optimal (silhouette score)
- 9 clusters avec labels sémantiques et profil population
- Export → `ml_pipeline/kmeans_clusters.geojson`

### Scoring (`scoring.ipynb`)

Deux scores 0–100 avec pondération expert + interactions entre features :

**Score Particulier** — exposition du logement aux risques naturels
- Poids dominants : `flood_score` (25%), `population` non incluse
- Interactions : argile × infiltration, flood × nappe, zone_humide × flood

**Score Élu** — exposition de la population aux risques
- Poids dominants : `flood_score` (20%) + `population` (18%)
- Interactions : flood × population, icu × population, argile × infiltration, zone_humide × flood

### Explications SHAP

Pour chaque cellule, Ridge + `shap.LinearExplainer` génère :
- `explication_particulier` — phrase décrivant les 3 principaux risques + facteurs protecteurs
- `conseils_particulier` — actions concrètes pour un particulier
- `explication_elu` — même chose à l'échelle territoriale
- `conseils_elu` — actions de politique publique (PLU, PPRT, trame verte...)

Export final → `ml_pipeline/scores.geojson`

---

## Structure du projet

```
├── config.py              # chemins, CRS, taille de cellule
├── run.py                 # pipeline features → ml_pipeline/features.geojson
├── kmeans.ipynb           # clustering KMeans → kmeans_clusters.geojson
├── scoring.ipynb          # scoring + SHAP → scores.geojson
├── data/
│   ├── fv_commu_s.geojson
│   ├── ri_alearga_s.geojson
│   ├── ri_icu_ifu_s.geojson
│   ├── ri_pprt_s.geojson
│   ├── ri_etab_pol_p.geojson
│   ├── ri_basol_p.geojson
│   ├── en_infiltration_s.geojson
│   ├── green_spaces.geojson
│   ├── to_bois_s.geojson
│   ├── ec_zone_humide_s.geojson
│   ├── population-bordeaux-metropole-donnees-carroyees-a-200-metres-millesime-2015.geojson
│   ├── ppri/FRF_TRI_BORD/     # shapefiles TRI 2020 (Géorisques)
│   └── ppri_remonte/          # Re_Nappe_fr.shp (Géorisques)
├── ml_pipeline/
│   ├── features.geojson        # output run.py
│   ├── kmeans_clusters.geojson # output kmeans.ipynb
│   └── scores.geojson          # output final scoring.ipynb
├── pyproject.toml
└── uv.lock
```

---

## Lancer le pipeline

```bash
# 1. Installer les dépendances
uv sync

# 2. Générer les features
python run.py

# 3. Clustering → kmeans.ipynb (exécuter toutes les cellules)

# 4. Scoring + SHAP → scoring.ipynb (exécuter toutes les cellules)
```

---

## Sources de données

| Donnée | Source |
|---|---|
| Limites communes BM | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/fv_commu_s) |
| PPRT | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_pprt_s) |
| Îlot de chaleur/fraîcheur | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_icu_ifu_s) |
| Remontée de nappes | [Géorisques](https://www.georisques.gouv.fr/donnees/bases-de-donnees/inondations-par-remontee-de-nappes) |
| Zonages inondation TRI 2020 | [Géorisques](https://www.georisques.gouv.fr/donnees/bases-de-donnees/zonages-inondation-rapportage-2020) |
| Sites pollués BASOL | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_basol_p) |
| Établissements polluants | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_etab_pol_p) |
| Aléa retrait-gonflement argiles | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_alearga_s) |
| Capacité d'infiltration des eaux | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/en_infiltration_s) |
| Zones boisées | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/to_bois_s) |
| Zones humides | [DataHub Bordeaux Métropole](https://datahub.bordeaux-metropole.fr/explore/dataset/ec_zone_humide_s) |
| Population carroyage 200m | [INSEE 2015](https://www.insee.fr/fr/statistiques/4176305) |

---

*Projet réalisé dans le cadre du défi [Prévention des risques à Bordeaux Métropole](https://defis.data.gouv.fr/defis/prevention-des-risques-a-bordeaux-metropole) — Open Data University / data.gouv.fr*
