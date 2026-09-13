# Analyse du projet — état actuel

**Mise à jour : 2026-09-13.** Cette synthèse décrit les fichiers de la branche
`arena/01a09c22-base-donnee`, après les cinq priorités de consolidation.
Les modifications de cette session ne constituent pas une version publiée.

L’[analyse initiale à 173 personnages et ses suivis](historique/analyse-173-personnages.md)
est conservée comme **archive historique**. Ses chiffres, conclusions et anciens
résultats de CI ne décrivent pas l’état présent. Les priorités numérotées dans
cette archive appartiennent à un autre plan d’action.

## 1. Bilan

Le projet est une base éditoriale de fiction, illustrée et géolocalisée, avec une
carte statique et des exports reproductibles. Son architecture reste adaptée à
une maintenance individuelle : sources CSV lisibles dans Git, génération Python,
classeur de consultation et carte Leaflet sans dépendance à un CDN.

La consolidation sécurise les renommages, les interactions essentielles et les
premiers liens entre personnages. **Elle ne transforme pas la base en outil
collaboratif, ni les propositions narratives en canon validé.**

Une passe de correction (2026-09-13) a traité quatre points issus d’une revue
externe : affichage entier des vignettes verticales sur la planche contact,
structuration de 41 liens de famille déjà écrits en prose, protection des
mineurs dans les moteurs de l’atelier, et mentions de non-ressemblance dans la
fiche du personnage et les licences. Les recommandations encore ouvertes
(étiquetage IA dans les fichiers d’image, élargissement aux liens d’intrigue,
décisions sur les factions `Sous-sol` / `Neutre` / `Propre` et sur la colonne
`Branche`) sont consignées dans [la revue](revue-externe-2026-09-13.md).

## 2. État des données

Les effectifs sont calculables depuis les sources ; un test contrôle ce tableau.
Les nombres de lignes excluent les en-têtes.

| Indicateur | Valeur |
|---|---|
| Personnages | 213 |
| Humains | 212 |
| Animal | 1 |
| Mineurs humains | 9 |
| La Baie | 153 |
| Chicoutimi | 41 |
| Jonquière | 19 |
| Familles | 64 |
| Foyers Famille/Branche | 101 |
| Colonnes Personnages | 17 |
| Fiches Narration | 213 |
| Colonnes Narration | 9 |
| Factions autorisées | 17 |
| Relations explicites structurées | 155 |
| Personnages reliés dans cette tranche | 176 |
| Propositions de personnages centraux | 13 |

### Sources et livrables

- `data/personnages.csv` : identités, descriptions, localisation, ID permanent et
  chemin explicite du portrait. **Ce CSV, pas le classeur, est la source.**
- `data/narration.csv` : source **publique et versionnée**, jointe par ID. Ses
  noms/surnoms servent de repères de lecture ; ceux du classeur suivent la base.
- `data/factions.txt` : vocabulaire contrôlé des factions.
- `data/ids-retires.txt` : registre versionné des IDs ne pouvant plus être réutilisés.
- `data/relations.csv` : liens relus et saisis explicitement, accompagnés du texte
  de preuve provenant de Parenté. Extraction partielle, sans inférence : les
  41 liens déclarés en prose dans Parenté mais absents de la table y ont été
  ajoutés après résolution des prénoms ambigus par Famille, Branche et secteur.
- `construire_base.py` et `relations.py` : génération du classeur unique
  (**Personnages, Lisez-moi, Narration, Relations**), des exports personnages,
  de `relations_personnages.json`, des deux cartes, de l’atelier de scènes et
  de la planche contact.
- `docs/propositions-personnages-centraux.md` : atelier **non canonique**, non lu
  par le générateur, soumis à validation de l’auteur.

### Périmètres distincts

| Contenu | Classeur | Exports personnages CSV/JSON/GeoJSON et carte | Export relations JSON |
|---|---|---|---|
| Fiches personnages avec ID | Oui | Oui | IDs et noms des extrémités seulement |
| Factions, répliques, arcs S1 | Oui, Narration | Non | Non |
| Table de relations explicites | Oui, Relations | Non | Oui, avec provenance |
| Propositions narratives | Non | Non | Non |

La carte dessine déjà des liens de **foyer**, à partir de Famille/Branche.
Ces traits ne représentent pas la nouvelle table de relations.

## 3. Les cinq priorités de cette session

| Priorité | Réalisation | Limite à retenir |
|---|---|---|
| 1 — Interactions de la carte | Correction Leaflet `lon` → `lng` ; recherche réactivant la catégorie du résultat et sa case | Pas une revue exhaustive du JavaScript |
| 2 — Tests navigateur | Sept parcours sur chacune des deux cartes, exécutés dans Chromium | Services externes simulés ; mobile = petite fenêtre, pas appareil tactile |
| 3 — Identifiants stables | P001–P213, jointure de narration par ID, portraits explicites, propagation aux exports | Ne pas réutiliser les IDs ; les mentions en prose ne se renomment pas seules |
| 4 — Relations et écriture | Table sourcée, validations, feuille Excel et JSON autonome ; treize fiches proposées à part | Relations encore partielles et propositions non approuvées |
| 5 — Documentation | État actuel séparé des archives, guide corrigé, contrôles des chiffres et liens | L’archive conserve volontairement les anciens constats |

## 4. Vérifications et portée

| Suite | Nombre | Portée |
|---|---|---|
| Python | 66 | Données, exports, IDs, relations, portraits, protection des mineurs, conventions et documentation |
| JavaScript ciblé | 10 | Coordonnées Leaflet, révélation des catégories humain/animal, robustesse des repères locaux et protection des mineurs dans l’atelier, avec objets simulés |
| Navigateur Chromium | 14 | Recherche/portrait, filtres, catégories masquées, zoom, repères et menu mobile sur les deux cartes |

Commandes et prérequis : [README — démarrage rapide](../README.md#démarrage-rapide)
et [tests navigateur](../README.md#tests-navigateur-chromium).

La vérification locale comprend les suites ci-dessus, Ruff et une reconstruction
avec comparaison des empreintes des livrables. Deux constructions successives
sur cet environnement produisent les mêmes octets. Les données sources ne sont
pas réécrites par la construction.

La CI est **configurée** pour le lint, la construction reproductible, les tests
Python/JavaScript et un job navigateur séparé. **Aucune réussite GitHub de ces
modifications n’est affirmée ici** : les résultats locaux ne prouvent pas qu’une
exécution distante a eu lieu. L’archive contient des résultats de CI anciens.

La reproductibilité binaire inter-environnements de la planche WebP n’est pas
exigée : le codec natif peut changer les octets. La CI compare néanmoins deux
constructions sur un même runner. La date du classeur est une constante de
construction (`DATE_LIVRABLE`, surcharge `SOURCE_DATE_EPOCH`), pas la date de
cette analyse ni un indicateur de fraîcheur des données.

## 5. Limites encore ouvertes

### Fonctionnement et couverture

- Pas de test Firefox/Safari ou d’appareil tactile réel. Les services de tuiles,
  Nominatim et la géolocalisation ne sont pas validés par les parcours simulés.
- Le rythme et le déclenchement de la recherche distante restent à revoir au
  regard des politiques d’usage du fournisseur avant un déploiement public large.
- Le stockage local est maintenant validé et protégé contre le JSON corrompu et
  les quotas d’écriture ; il reste propre à chaque navigateur et n’est pas une
  sauvegarde distante.
- La construction échoue maintenant explicitement si l’injection de la carte ou
  la synchronisation des vignettes ne peut pas produire les livrables attendus.
- Pas d’interface d’édition multiutilisateur, d’authentification ou de serveur API.

### Données et narration

- Les coordonnées sont approximatives. Les tests d’arrondissement utilisent des
  boîtes géographiques, pas les limites administratives exactes ni une nouvelle
  vérification des rues auprès d’OpenStreetMap.
- Les IDs sont permanents et contrôlés par `data/ids-retires.txt`. La garantie
  dépend encore de l’ajout manuel d’un ID au registre au moment d’un retrait ;
  l’historique des suppressions anciennes n’est pas reconstruit automatiquement.
- Les preuves des relations sont comparées au texte source, mais le programme ne
  valide pas leur interprétation sémantique. L’extraction n’est pas exhaustive.
- Pas encore de temporalité, de statut « rumeur/perception », ni de distinction
  filiation biologique/adoptive. Une absence de lien n’est pas un fait narratif.
- Les ratios des vignettes ne sont pas tous uniformes (12 verticales sur 213).
  La planche contact les affiche désormais entières au lieu de les recadrer :
  un recadrage « couverture » coupait le visage de cinq d’entre elles.
- Les treize personnages centraux et leurs nouveaux arcs restent à sélectionner
  et à valider ; ils ne sont pas incorporés aux données canoniques.

## 6. Licences et réutilisation

Les statuts annoncés restent **MIT pour le code**, **ODbL pour les données**,
**CC BY 4.0 pour les portraits IA**, avec les licences tierces de Leaflet et de
la police vendoriée. Voir [LICENSE-DONNEES.md](../LICENSE-DONNEES.md).

La présente revue vérifie la cohérence de la documentation, **pas la validité
juridique de tous les droits ni la conformité actuelle de chaque service de
cartographie**. Les avertissements fiction, adresses inventées et portraits IA
restent nécessaires. Une clause de non-ressemblance couvre désormais les
personnes, entreprises et organisations réelles citées comme contexte, et la
fiche de chaque personnage porte elle-même la mention « personnage de fiction —
adresse inventée ». L’ancien choix de narration privée est abandonné : la
narration est publique dans le dépôt et le classeur.

## 7. Orientation proposée

Conserver l’architecture actuelle. Avant d’ajouter des personnages ou de changer
la pile technique, privilégier :

1. La validation éditoriale des [treize propositions](propositions-personnages-centraux.md)
   et du [noyau de saison 1 proposé](atelier-saison-1.md).
2. L’enrichissement progressif des [relations sourcées](relations-personnages.md),
   avec un modèle temporel seulement lorsque les scènes en ont besoin.
3. Le traitement des erreurs de stockage et de construction signalées plus haut,
   puis l’élargissement des tests si la carte est diffusée plus largement.

Le projet dispose maintenant d’une base technique plus sûre ; la prochaine
valeur ajoutée dépend surtout des choix d’auteur et de la continuité narrative.
