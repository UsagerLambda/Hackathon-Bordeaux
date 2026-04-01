# Algorithmes ML — Documentation Technique

## 1. KMeans Clustering

### Objectif
Regrouper les 9 624 cellules de 250m × 250m en clusters homogènes selon leur profil de risque, sans supervision.

### Pré-traitement
```
features → StandardScaler → X_scaled (moyenne=0, écart-type=1)
```
Le StandardScaler est obligatoire pour KMeans : sans lui, les features en mètres (`dist_industrie` ~1500m) domineraient les features binaires (0/1).

### Choix de k
Deux métriques calculées pour k ∈ [2, 10] :

- **Inertie (méthode du coude)** : somme des distances au carré entre chaque point et son centroïde. Cherche le point d'inflexion où l'inertie cesse de baisser fortement.
- **Score silhouette** : mesure la cohésion interne vs séparation entre clusters. Varie de -1 à 1, plus c'est élevé mieux c'est. k optimal = argmax(silhouette).

```python
silhouette_score(X_scaled, km.labels_)
```

### Algorithme
KMeans Lloyd (scikit-learn) : `n_init=10` relances avec centroïdes aléatoires différents pour éviter les minima locaux. Convergence sur le minimum d'inertie.

### Visualisation
Réduction PCA 2D pour affichage uniquement (pas utilisée dans le clustering) :
```
X_scaled (9624 × 11) → PCA(n_components=2) → X_2d (9624 × 2)
```

---

## 2. Scoring Composite Pondéré

### Objectif
Produire un score continu 0–100 interprétable, avec deux variantes : particulier et élu.

### Pipeline

**Étape 1 — Normalisation MinMax**
```
X_norm = (X - X_min) / (X_max - X_min)  →  [0, 1]
```
Contrairement au StandardScaler (KMeans), MinMax préserve l'interprétabilité : 0 = minimum observé, 1 = maximum observé.

**Inversion des features protectrices :**
```python
dist_industrie = 1 - dist_industrie_norm   # loin = moins de risque
dist_sites_pol = 1 - dist_sites_pol_norm
green_cover    = 1 - green_cover_norm      # présence = protecteur
```

**Étape 2 — Score de base pondéré**
```
base_score = Σ (poids_i × feature_norm_i)
```
Les poids sont normalisés pour sommer à 1.

**Étape 3 — Interactions**
Certains risques se renforcent mutuellement. Bonus multiplicatif ajouté au score de base :

| Interaction | Coefficient | Logique |
|---|---|---|
| `argile × water_infiltration` | 0.10 | Sol argileux + eau = retrait-gonflement aggravé |
| `flood_score × nappe` | 0.10 | Double risque eau (surface + souterrain) |
| `zone_humide × flood_score` | 0.08 | Zone humide amplifie les crues |
| `flood_score × population` *(élu)* | 0.15 | Personnes directement exposées |
| `icu × population` *(élu)* | 0.10 | Exposition humaine à la chaleur |

```
risk_raw = base_score + Σ (coef_i × feature_A_norm × feature_B_norm)
```

**Étape 4 — Normalisation finale 0–100**
```
score = (risk_raw - min) / (max - min) × 100
```

---

## 3. SHAP — Explications par Cellule

### Objectif
Pour chaque cellule, identifier quelles features contribuent le plus au score — et dans quel sens.

### Modèle support : Ridge Regression
Le score étant déjà une somme linéaire pondérée, une régression Ridge le reproduit quasi parfaitement (R² ≈ 0.99). Avantage : `shap.LinearExplainer` est instantané (< 1s pour 9 624 cellules), contre 6+ minutes pour un Random Forest.

```python
model = Ridge()
model.fit(X_norm, score)
explainer   = shap.LinearExplainer(model, X_norm)
shap_values = explainer.shap_values(X_norm)  # shape: (9624, n_features)
```

### Interprétation des SHAP values
Pour une cellule donnée, `shap_values[i, j]` représente la contribution de la feature j au score de la cellule i, par rapport à la valeur moyenne du modèle.

```
score_cellule_i = valeur_base + Σ shap_values[i, j]
```

- **SHAP > 0** : la feature augmente le score (aggrave le risque)
- **SHAP < 0** : la feature diminue le score (facteur protecteur)

### Génération des explications
Pour chaque cellule :
1. Trier les SHAP values par ordre décroissant
2. Prendre les top 3 contributeurs positifs → phrase d'exposition
3. Prendre les top 2 contributeurs négatifs → facteurs atténuants
4. Mapper sur les conseils correspondants

```python
contribs = shap_df.iloc[idx].sort_values(ascending=False)
positifs  = contribs[contribs > 0].head(3)   # risques dominants
negatifs  = contribs[contribs < 0].head(2)   # facteurs protecteurs
```

### Deux modèles SHAP indépendants
- `shap_df` → basé sur `score_particulier` (9 features, sans population)
- `shap_df_elu` → basé sur `score_elu` (10 features, avec population)

Les conseils générés sont adaptés au profil : actions individuelles vs politiques publiques.

---

## Limites et Choix Méthodologiques

| Choix | Justification | Limite |
|---|---|---|
| KMeans plutôt que DBSCAN | Nombre de clusters contrôlable, interprétabilité | Sensible aux outliers, clusters sphériques |
| Ridge plutôt que Random Forest pour SHAP | 1000× plus rapide, adapté au score linéaire | Pas de capture des non-linéarités |
| Poids experts plutôt que data-driven | Résultats cohérents et justifiables | Subjectivité dans la hiérarchisation des risques |
| MinMax plutôt que quantile pour normalisation | Préserve les distributions réelles | Sensible aux valeurs extrêmes |
| Interactions multiplicatives | Capturent les synergies entre risques | Coefficients fixés manuellement |
