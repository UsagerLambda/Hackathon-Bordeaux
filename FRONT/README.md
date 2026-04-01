# Hackathon-Bordeaux

# Projet - Resili-Score

Le projet {name} repose sur un principe simple, donner un nutri-score des risques des zones dans la Metropole de Bordeaux ainsi que des mesures qui peuvent être prises au niveau personnel et 


# Listes des données :

### Limites des communes de Bordeaux Métropole

https://datahub.bordeaux-metropole.fr/explore/dataset/fv_commu_s/map/?location=11,44.87339,-0.56271&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/FV_COMMU_S.dwg"

### PPRT

https://datahub.bordeaux-metropole.fr/explore/dataset/ri_pprt_s/map/?disjunctive.type_risque&disjunctive.etab&location=10,44.88799,-0.38246&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/RI_PPRT_S.dwg"

### Îlot de chaleur / fraicheur

https://datahub.bordeaux-metropole.fr/explore/dataset/ri_icu_ifu_s/carte-perso/?disjunctive.insee&disjunctive.dimension
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/RI_ICU_IFU_S.dwg"

### Base permanente des équipements

https://defis.data.gouv.fr/datasets/548acaf2c751df1eac4120e7
téléchargement="https://www.insee.fr/fr/statistiques/fichier/8217527/DS_BPE_CSV_FR.zip"

### Inondations par remontée de nappes

https://www.georisques.gouv.fr/donnees/bases-de-donnees/inondations-par-remontee-de-nappes
téléchargement="https://files.georisques.fr/REMNAPPES/Dept_33.zip"

### Zonages Inondation

https://www.georisques.gouv.fr/donnees/bases-de-donnees/zonages-inondation-rapportage-2020
téléchargement="https://files.georisques.fr/di_2020/tri_2020_sig_di_33.zip"

### Site et sol pollué (ou potentiellement pollué)

https://datahub.bordeaux-metropole.fr/explore/dataset/ri_basol_p/information/?disjunctive.statut_instruction&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJwaWUiLCJmdW5jIjoiQ09VTlQiLCJ5QXhpcyI6ImdpZCIsInNjaWVudGlmaWNEaXNwbGF5Ijp0cnVlLCJjb2xvciI6InJhbmdlLWN1c3RvbSIsInBvc2l0aW9uIjoiY2VudGVyIn1dLCJ4QXhpcyI6InN0YXR1dF9pbnN0cnVjdGlvbiIsIm1heHBvaW50cyI6IiIsInRpbWVzY2FsZSI6IiIsInNvcnQiOiJzZXJpZTEtMSIsInNlcmllc0JyZWFrZG93biI6IiIsInNlcmllc0JyZWFrZG93blRpbWVzY2FsZSI6IiIsImNvbmZpZyI6eyJkYXRhc2V0IjoicmlfYmFzb2xfcCIsIm9wdGlvbnMiOnsiZGlzanVuY3RpdmUuc3RhdHV0X2luc3RydWN0aW9uIjp0cnVlfX19XSwiZGlzcGxheUxlZ2VuZCI6dHJ1ZSwiYWxpZ25Nb250aCI6dHJ1ZSwidGltZXNjYWxlIjoiIn0%3D&location=11,44.82807,-0.42812&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/RI_BASOL_P.dwg"

### Installation industrielle rejetant des polluants

https://datahub.bordeaux-metropole.fr/explore/dataset/ri_etab_pol_p/map/?disjunctive.naf&location=13,44.87692,-0.55902&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/RI_ETAB_POL_P.dwg"

### Aléa retrait/gonflement des argiles

https://datahub.bordeaux-metropole.fr/explore/dataset/ri_alearga_s/map/?disjunctive.alea&location=14,44.83433,-0.53648&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/RI_ALEARGA_S.dwg"

### Mouvement de terrain

https://www.georisques.gouv.fr/donnees/bases-de-donnees/base-de-donnees-mouvements-de-terrain
téléchargement="https://www.georisques.gouv.fr/webappReport/ws/mvmt/departements/33/fichecommunes.csv?"

### Capacité d'infiltration des eaux pluviales

https://datahub.bordeaux-metropole.fr/explore/dataset/en_infiltration_s/map/?location=13,44.88519,-0.57773&basemap=jawg.streets
téléchargement="https://fr.ftp.opendatasoft.com/scnbdx/DWG/EN_INFILTRATION_S.dwg"


# Résili-Score 🏠

## Le Nutri-Score de la résilience urbaine pour Bordeaux Métropole

> **Défi** : Comment préparer les habitants de Bordeaux Métropole aux risques potentiels ?
>
> **Notre réponse** : Aujourd'hui, un habitant de Cenon doit consulter 4 sites différents pour comprendre ses risques. Résili-Score lui donne une réponse en un clic.

---

## Le Problème

Un habitant de Bordeaux Métropole est potentiellement concerné par **5 types de risques** : inondation (PPRI), retrait-gonflement des argiles (RGA), risques technologiques (PPRT), canicule et feux de forêt. Pour s'informer, il doit :

1. Consulter Géorisques pour son adresse
2. Lire le DICRIM de sa commune (PDF de 40+ pages)
3. Chercher les zones PPRI sur le géocatalogue de la métropole
4. Trouver les points de rassemblement dans le PCS communal

**Résultat** : personne ne le fait. La "culture du risque" reste un concept abstrait.

---

## Notre Solution

**Résili-Score** attribue à chaque cellule de 200m × 200m de Bordeaux Métropole un **score de résilience de A à E**, calculé à partir de données ouvertes. En un regard, l'habitant comprend :

- **Son niveau d'exposition** aux risques naturels et technologiques
- **Le profil de vulnérabilité** de sa zone (clustering K-means)
- **Les forces et faiblesses** de sa cellule (radar multi-dimensionnel)
- **Des recommandations concrètes** pour se préparer

### Pourquoi un carroyage 200m plutôt que par quartier ?

Un quartier IRIS peut faire plusieurs km² en zone périurbaine. Une cellule de 200m correspond à **quelques rues** — c'est l'échelle à laquelle les risques varient réellement. L'INSEE publie déjà un carroyage 200m avec des données de population et revenus, ce qui nous donne une grille prête à l'emploi et des features socio-démographiques gratuites.

Bordeaux Métropole (~580 km²) = **~14 500 cellules**. Parfaitement gérable pour GeoPandas.

### Le format Nutri-Score appliqué au risque

| Score | Signification | Couleur |
|-------|--------------|---------|
| **A** | Résilience forte — peu exposé, bien équipé | 🟢 Vert foncé |
| **B** | Résilience bonne — exposition modérée | 🟢 Vert clair |
| **C** | Résilience moyenne — points d'attention | 🟡 Jaune |
| **D** | Résilience fragile — actions recommandées | 🟠 Orange |
| **E** | Résilience critique — vigilance forte | 🔴 Rouge |

---

## Architecture du Score

### Deux approches complémentaires

Le projet combine **deux méthodes** qui répondent à des questions différentes :

**1. Score composite pondéré → classement A à E**
Chaque feature est normalisée (MinMaxScaler), pondérée, puis sommée. Le score brut est discrétisé en quintiles pour obtenir la lettre A→E. C'est déterministe, explicable, et donne le classement ordonné que le citoyen attend.

**2. Clustering K-means → profils de quartier**
K-means regroupe les cellules qui se ressemblent en 4-6 clusters. Un cluster n'est pas "meilleur" qu'un autre — c'est un **profil type**. Exemples possibles :

- *Centre urbain exposé inondation* — dense, bien desservi en secours, mais en plein PPRI
- *Périurbain isolé* — peu exposé aux risques naturels, mais loin des secours
- *Zone industrielle à risque* — périmètre PPRT, peu végétalisé, peu résidentiel
- *Quartier résilient* — végétalisé, hors zones à risque, bien équipé

Le profil apparaît dans le popup à côté du score, pour donner du **sens qualitatif** au-delà du simple chiffre.

### Justification des poids : méthode AHP

Les poids du score composite sont définis par **Analyse Hiérarchique des Processus** (AHP) : chaque membre de l'équipe compare les dimensions par paires ("l'inondation est-elle plus grave que le RGA ?"), et la matrice de comparaison produit des poids cohérents et justifiables devant le jury.

---

## Features par Cellule 200m

### Dimensions d'exposition (ce qui menace)

| Feature | Source | Calcul par cellule |
|---------|--------|--------------------|
| 🌊 `expo_ppri` | Zonage PPRI (Bordeaux Métropole) | % de surface en zone inondable |
| 🏚️ `expo_rga` | Exposition RGA (Géorisques / BRGM) | % de surface en exposition moyenne ou forte |
| 🏭 `expo_pprt` | Zonage PPRT (data.gouv) | % de surface en périmètre PPRT |

### Dimensions de capacité — distances aux installations (ce qui protège)

Pour chaque cellule, on calcule la **distance euclidienne au point le plus proche** de chaque catégorie d'installation. La BPE (Base Permanente des Équipements) de l'INSEE fournit les coordonnées et le type précis de chaque équipement.

| Feature | Type BPE | Code BPE | Ce qu'on mesure |
|---------|----------|----------|-----------------|
| 🚒 `dist_caserne` | Centre de secours / pompiers | D233 | Temps d'intervention potentiel |
| 🏥 `dist_hopital` | Urgences hospitalières | D107 | Accès aux soins d'urgence |
| 🏫 `dist_refuge` | Gymnases / salles polyvalentes | F102, F121 | Points de rassemblement possibles |
| 👮 `dist_police` | Police / gendarmerie | D232, D231 | Présence sécuritaire |

### Dimensions environnementales

| Feature | Source | Calcul par cellule |
|---------|--------|--------------------|
| 🌳 `taux_vegetation` | OCS GE (IGN) ou BD Topo | % de surface végétalisée (atténue chaleur + ruissellement) |
| 🏗️ `age_bati_moyen` | BD Topo (IGN) | Âge moyen pondéré des bâtiments (proxy de vulnérabilité structurelle) |

### Features bonus (carroyage INSEE, gratuites)

| Feature | Source | Intérêt |
|---------|--------|---------|
| 👥 `population` | Carroyage INSEE 200m | Pondérer l'enjeu humain |
| 💰 `niveau_vie` | Carroyage INSEE 200m | Proxy de capacité d'adaptation |

---

## Pipeline de Scoring

```
┌─────────────────────────────────────────────────────────────────┐
│                     DONNÉES BRUTES                              │
│  PPRI · RGA · PPRT · BPE · BD Topo · OCS GE · Carroyage INSEE  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   FEATURE ENGINEERING  │
              │                        │
              │  Intersection spatiale │
              │  (GeoPandas sjoin)     │
              │         +              │
              │  Calcul de distances   │
              │  (scipy cdist /        │
              │   sklearn BallTree)    │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  features_by_cell.parquet  │
              │  ~14 500 lignes × 10 cols  │
              └─────┬──────────┬───────┘
                    │          │
          ┌─────────▼──┐  ┌───▼──────────┐
          │   SCORE    │  │   K-MEANS    │
          │ COMPOSITE  │  │  CLUSTERING  │
          │            │  │              │
          │ MinMaxScale│  │ 4-6 clusters │
          │ × poids AHP│  │ → profils    │
          │ → quintiles│  │   nommés     │
          │ → A, B,    │  │              │
          │   C, D, E  │  │              │
          └─────┬──────┘  └──────┬───────┘
                │                │
                ▼                ▼
          ┌──────────────────────────┐
          │    CARTE FOLIUM          │
          │                          │
          │  Choroplèthe A→E         │
          │  + popup :               │
          │    • Score global         │
          │    • Profil cluster       │
          │    • Radar 6 dimensions   │
          │    • Recommandations      │
          │  + recherche par adresse  │
          └──────────────────────────┘
```

---

## MVP — Périmètre Semaine 1

### Ce qu'on livre ✅

- **Carte interactive Folium** : ~14 500 cellules de Bordeaux Métropole colorées A→E
- **Popup par cellule** : score global + profil K-means + radar chart + recommandations
- **Recherche par adresse** : géocodage via API BAN → zoom sur la cellule correspondante
- **Pipeline reproductible** : scripts Python documentés, de la donnée brute au score final
- **Documentation méthodologique** : justification AHP des poids, description des profils

### Ce qu'on ne fait pas (V2) ❌

- Pas de backend/API (livrable = page HTML statique générée par Folium)
- Pas de compte utilisateur
- Pas de données temps réel (Vigicrues, météo)
- Pas de simulation prospective (climat 2050)
- Pas de routage réseau (distances euclidiennes, pas itinéraires routiers)

---

## Stack Technique

| Couche | Outil | Justification |
|--------|-------|---------------|
| Données géospatiales | **GeoPandas**, Fiona, Shapely | Intersections spatiales cellule × zones de risque |
| Grille de base | **Carroyage INSEE 200m** | Grille prête à l'emploi + données population/revenus |
| Calcul de distances | **scipy.spatial.cKDTree** | Distance au point le plus proche, rapide sur 14k cells |
| Feature engineering | **pandas**, numpy | Normalisation, agrégation par cellule |
| Pondération | **AHP** (implémentation maison) | Poids justifiables par matrice de comparaison |
| Scoring | **scikit-learn** | MinMaxScaler + KMeans |
| Visualisation carte | **Folium** | Choroplèthe interactive, popups HTML |
| Géocodage | **geo.api.gouv.fr** | API BAN pour adresse → coordonnées |
| Graphiques popup | **matplotlib** ou inline SVG | Radar charts par cellule |

---

## Sources de Données

| Donnée | Source | Format | Licence |
|--------|--------|--------|---------|
| Carroyage 200m + population + revenus | INSEE | CSV + Shapefile | Licence Ouverte |
| Zonage PPRI agglomération bordelaise | Bordeaux Métropole (data.gouv) | Shapefile | Licence Ouverte |
| Exposition RGA | Géorisques (BRGM) | Shapefile / API | Licence Ouverte |
| Zonage PPRT | Bordeaux Métropole (data.gouv) | Shapefile | Licence Ouverte |
| Végétalisation / occupation du sol | OCS GE (IGN) ou Corine Land Cover | Shapefile | Licence Ouverte |
| Équipements (casernes, hôpitaux, refuges, police) | BPE INSEE | CSV géolocalisé | Licence Ouverte |
| Bâtiments (âge, hauteur) | BD Topo (IGN) | Shapefile | Licence Ouverte |

---

## Organisation de l'Équipe

### Rôles

| Rôle | Périmètre |
|------|-----------|
| 🗺️ **Data / Géo** | Collecte, intersections spatiales, features d'exposition + végétalisation |
| 🧠 **ML / Score** | Distances (cKDTree), normalisation, AHP, scoring composite, K-means |
| 🎨 **Front / Visu** | Carte Folium, popups, radar charts, recherche par adresse, polish |

### Planning

| Jour | Data / Géo | ML / Score | Front / Visu | Livrable commun |
|------|-----------|------------|-------------|-----------------|
| **J1 Lun** | Collecte datasets + vérification CRS | Télécharger BPE + filtrer types d'équipements | Setup repo + charger carroyage INSEE sur carte | `data/raw/` complet + README sources |
| **J2 Mar** | `sjoin` cellules × PPRI, RGA, PPRT | Calcul distances (cKDTree) + AHP à 3 (20 min) | Choroplèthe dummy sur vraie grille | `features_by_cell.parquet` |
| **J3 Mer** | Végétalisation + âge bâti | Score composite → A-E + K-means → profils | Brancher vrais scores → couleurs A-E | **La carte fonctionne** 🎯 |
| **J4 Jeu** | Validation terrain (3-4 quartiers connus) | Nommer les profils + recommandations par profil | Popups : radar + profil + recommandations + recherche adresse | UX complète |
| **J5 Ven** | Tests edge cases + README données | Documentation méthodologique (AHP, profils) | Polish visuel + responsive + export HTML | **Pitch prêt** 🎤 |

---

## Structure du Repo

```
resili-score/
├── README.md
├── data/
│   ├── raw/                  # Données brutes (gitignored, liens dans sources.md)
│   ├── processed/            # GeoDataFrames nettoyés
│   └── sources.md            # Documentation des sources + licences
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_scoring.ipynb
│   └── 04_clustering.ipynb
├── src/
│   ├── collect.py            # Scripts de téléchargement
│   ├── grid.py               # Chargement carroyage INSEE + clip sur métropole
│   ├── features_exposure.py  # % PPRI, RGA, PPRT par cellule
│   ├── features_distance.py  # Distances caserne, hôpital, refuge, police
│   ├── features_environment.py # Végétalisation, âge bâti
│   ├── scoring.py            # AHP + score composite + discrétisation A-E
│   ├── clustering.py         # K-means + nommage des profils
│   └── visualize.py          # Génération de la carte Folium
├── output/
│   └── resili_score_map.html # Livrable final
└── requirements.txt
```

---

## Pitch (30 secondes)

> *« Savez-vous si votre quartier est prêt pour la prochaine crue de la Garonne ? Probablement pas — et c'est normal, parce que l'information est dispersée sur 4 sites différents, noyée dans des PDFs techniques.*
>
> *Résili-Score change ça. On découpe la métropole en 14 500 cellules de 200 mètres et pour chacune, on croise 10 dimensions de données ouvertes — inondation, argiles, risques industriels, distance aux pompiers, à l'hôpital, aux refuges, végétalisation, vulnérabilité du bâti.*
>
> *Chaque cellule reçoit un score de A à E, comme un Nutri-Score, et un profil de vulnérabilité qui dit exactement pourquoi. Tapez votre adresse, comprenez vos risques, agissez. »*

---

## Risques Projet & Mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Carroyage INSEE difficile à obtenir / manipuler | Blocage J1 | Plan B : générer la grille 250m avec `shapely` (10 lignes de code) |
| Dataset introuvable ou format cassé | Feature manquante | Supprimer la dimension. 6 features propres > 10 bancales |
| Intersections spatiales trop lentes sur 14k cells | Retard J2-J3 | `simplify(tolerance=20)` sur les géométries + spatial index |
| Score non interprétable | Jury perplexe | Validation terrain : "Bacalan = D, presqu'île d'Ambès = E, Caudéran = B, ça fait sens ?" |
| K-means produit des clusters non lisibles | Profils inutiles | Fallback : pas de clustering, on garde juste le score A-E |
| Surcharge d'ambition | Rien de fini vendredi | **Règle absolue** : la carte avec scores doit tourner mercredi soir |

---

*Projet réalisé dans le cadre du défi [Prévention des risques à Bordeaux Métropole](https://defis.data.gouv.fr/defis/prevention-des-risques-a-bordeaux-metropole) — Open Data University / data.gouv.fr*
