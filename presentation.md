# Résili-Score — Texte de présentation (~10 minutes)

| Slide | Qui | Durée |
|---|---|---|
| 1 — Titre | **Mila** | 30s |
| 2 — Participants | **Mila** + chacun se présente | 1min |
| 3 — Problématique | **Lucas** | 2min |
| 4 — Chiffres clés | **Lucas** | 1min |
| 5 — Notre solution | **Clément** | 2min |
| 6 — Sources et données | **Clément** | 1min |
| 7 — Stack technique | **Clément** (chacun présente sa partie) | 1min30 |
| 8 — Résultats + démo | **Clément** + **Lucas** + **Mila** | 1min30 |
| 9 — Et demain ? | **Lucas** | 45s |
| 10 — Conclusion | **Mila** | 30s |

---

## Slide 1 — Titre *(Mila, ~30s)*

Bonjour à tous. Je suis Mila, et avec Clément et Lucas, étudiants à Holberton School, on a construit Résili-Score en quatre jours de hackathon. On va vous expliquer pourquoi ce projet nous a semblé nécessaire, comment on l'a construit, et ce qu'on en a appris.

---

## Slide 2 — Participants *(Mila, ~1min)*

On est trois étudiants aux profils complémentaires. Clément est en dernière année de spécialisation Machine Learning — c'est lui qui a porté toute la partie données et algorithmes. Lucas et moi sommes en première année de fondamentaux — Lucas a construit le backend et l'API, et j'ai conçu l'interface et la carte interactive. On n'avait jamais travaillé ensemble sur un projet de cette ampleur. La contrainte de temps nous a obligés à être efficaces : chacun a pris son périmètre, et on a assemblé les pièces au fur et à mesure.

---

## Slide 3 — Notre problématique *(Lucas, ~2min)*

Avant de vous parler de notre solution, parlons du problème.

Les informations sur les risques naturels et industriels existent. Elles sont publiques, gratuites, accessibles en open data. Il y a des cartes d'inondation, des bases sur les argiles, des données sur les industries dangereuses, sur les îlots de chaleur. Tout ça existe.

Mais voilà le problème : ces données sont éparpillées sur des dizaines de sites différents, dans des formats techniques difficilement lisibles pour un citoyen lambda. Et surtout — chaque risque est traité séparément. Alors que dans la réalité, ils se cumulent.

Prenez un habitant de Cenon. Il peut être simultanément en zone inondable selon le PPRI, sur un sol argileux instable selon Géorisques, et à moins d'un kilomètre d'un site industriel classé. Trois risques distincts, trois bases de données distinctes. Personne ne lui dit que ces trois risques s'appliquent à son adresse, et encore moins qu'ils peuvent se renforcer mutuellement.

Ce n'est pas un risque théorique. La Garonne a encore débordé sur les quais de Bordeaux récemment. Et selon nos données, sur les 9 624 zones analysées sur Bordeaux Métropole — 100% présentent au moins un risque naturel ou industriel non nul. Tout le monde est concerné. Personne n'a d'outil simple pour s'en rendre compte.

---

## Slide 4 — Les chiffres clés *(Lucas, ~1min)*

Pour vous donner la mesure du problème : on parle de 820 000 habitants — toute la population de Bordeaux Métropole, de Bègles à Saint-Médard-en-Jalles. 28 communes. On a fusionné 11 couches de données hétérogènes — les inondations du PPRI, le retrait-gonflement des argiles, les installations classées PPRT, les îlots de chaleur urbains. Ces bases n'avaient jamais été croisées ensemble sur ce territoire. C'était le premier défi.

---

## Slide 5 — Notre solution *(Clément, ~2min)*

Notre réponse s'appelle Résili-Score. L'idée est simple : vous tapez votre adresse, et vous obtenez une lettre — de A à E, comme le Nutri-Score — qui résume le niveau de risque de votre zone. A, c'est résilient. E, c'est fragile.

Mais le score ne traite pas les risques séparément. Il modélise les interactions entre eux. Un sol argileux seul, c'est un risque maîtrisable. Combiné à une forte infiltration d'eau, le retrait-gonflement devient bien plus dangereux. Une zone inondable seule, c'est déjà sérieux. Combinée à une remontée de nappe phréatique — deux sources d'eau simultanées — le risque est aggravé. Notre algorithme intègre ces effets de cumul dans le calcul du score.

Et ce score est interprétable. Pour chaque zone, on génère automatiquement une explication en langage naturel : par exemple, "cette zone est fortement exposée à la remontée de nappe phréatique et à l'îlot de chaleur, atténuée par la présence de végétation". Et on associe à chaque profil des conseils concrets de la même manière.

---

## Slide 6 — Nos sources et nos données *(Mila, ~1min)*

On a utilisé 3 sources open data, pour un total de 11 couches de données. Géorisques pour les zonages d'inondation et les remontées de nappes. Le DataHub de Bordeaux Métropole pour les argiles, les îlots de chaleur, les zones PPRT, les sites pollués BASOL, les établissements polluants, la capacité d'infiltration des sols, les zones boisées et les zones humides. Et l'INSEE pour les données de population au carroyage 200 mètres. Tout ça est public, gratuit et disponible bien que les jeux de données Georisques & Insee soient un peu daté. Un fois récupéré, j'ai assemblé, normalisé, et croisé les données sur une grille de 9 624 cellules de 250 mètres sur 250 mètres couvrant l'ensemble de la métropole.

---

## Slide 7 — Stack technique et répartition des rôles *(Clément, ~1min30)*

Techniquement, le projet est en trois couches.

Le score, c'est un score pondéré qui agrège les 11 variables de risque en tenant compte de leurs interactions. Les poids qu'on a choisis sont basés sur notre jugement — ils sont arbitraires dans ce sens, mais entièrement documentés et transparents. Un expert en prévention des risques, ou Bordeaux Métropole elle-même, pourrait les ajuster selon ses priorités sans toucher au reste du système. Par-dessus ça, une couche d'explicabilité qui génère pour chaque zone une phrase en langage naturel — pas du jargon, une vraie phrase lisible par n'importe qui.

Lucas a exposé tout ça via une API Python avec FastAPI, qui répond en temps réel aux requêtes de la carte.

Mila a construit l'interface : une carte satellite interactive avec recherche par adresse, code couleur A à E, refuges proches, et fiche détaillée par zone.

---

## Slide 8 — Les résultats *(Clément + Lucas + Mila, ~1min30)*

**Clément — ML :**
Sur les 9 624 cellules analysées, le modèle a produit un score de A à E pour chacune, avec une explication en langage naturel générée automatiquement. Le score intègre les effets de cumul entre variables — un sol argileux combiné à une remontée de nappe, par exemple, n'est pas simplement la somme des deux risques. Le résultat est un jeu de données complet, exportable, et réutilisable par n'importe quelle collectivité.

**Lucas — Backend :**
J'ai exposé tout ça via une API FastAPI qui sert les données en temps réel. Quand le frontend fait une requête — par coordonnées ou par adresse — l'API retourne le score de la cellule correspondante, les sites industriels pollués à proximité issus de la base BASOL, et les refuges les plus proches. Tout est précalculé côté données, donc les réponses sont instantanées.

**Mila — Frontend :**
L'interface, c'est une carte satellite interactive. Le GeoJSON complet des 9 624 zones est chargé directement dans le navigateur — pas de latence, tout est visible d'un coup. Quand vous cliquez sur une cellule ou que vous tapez une adresse dans la barre de recherche, une fiche s'ouvre : le score et son explication, les sites industriels pollués dans un rayon de 250 mètres, et les refuges les plus proches. Lisible, accessible, et ça marche maintenant.

---

## Slide 9 — Et demain ? *(Lucas, ~45s)*

On n'a pas eu le temps de tout finir. Un score dédié aux élus est déjà calculé dans nos données — une vision orientée politique publique, qui pondère davantage la densité de population exposée, pour aider à prioriser les actions sur le territoire. On imagine aussi des données en temps réel — alertes Vigicrues, météo — une simulation de l'impact du changement climatique à horizon 2050, et une intégration directe dans les outils des collectivités.

---

## Slide 10 — Conclusion *(Mila, ~30s)*

En quatre jours, avec trois étudiants, des données ouvertes et des outils open source, on a construit un score de risque unifié, explicable, et accessible à n'importe quel citoyen. On espère que ça donne envie d'aller plus loin. Merci.
