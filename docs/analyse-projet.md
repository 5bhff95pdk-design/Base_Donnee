# Analyse du projet — état actuel

**Mise à jour : 2026-09-13.** Cette synthèse décrit les fichiers de la branche
`arena/01a09c0e-base-donnee`, après les cinq priorités de consolidation.
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
| Relations explicites structurées | 114 |
| Personnages reliés dans cette tranche | 141 |
| Propositions de personnages centraux | 13 |

### Sources et livrables

- `data/personnages.csv` : identités, descriptions, localisation, ID permanent et
  chemin explicite du portrait. **Ce CSV, pas le classeur, est la source.**
- `data/narration.csv` : source **publique et versionnée**, jointe par ID. Ses
  noms/surnoms servent de repères de lecture ; ceux du classeur suivent la base.
- `data/factions.txt` : vocabulaire contrôlé des factions.
- `data/relations.csv` : liens relus et saisis explicitement, accompagnés du texte
  de preuve provenant de Parenté. Extraction partielle, sans inférence de liens.
- `construire_base.py` et `relations.py` : génération du classeur unique
  (**Personnages, Lisez-moi, Narration, Relations**), des exports personnages,
  de `relations_personnages.json`, des deux cartes et de la planche contact.
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
| 4 — Relations et écriture | Table sourcée, validations, feuille Excel et JSON autonome ; treize fiches proposées à part | Relations partielles et propositions non approuvées |
| 5 — Documentation | État actuel séparé des archives, guide corrigé, contrôles des chiffres et liens | L’archive conserve volontairement les anciens constats |

## 4. Vérifications et portée

| Suite | Nombre | Portée |
|---|---|---|
| Python | 60 | Données, exports, IDs, relations, portraits, conventions et documentation |
| JavaScript ciblé | 3 | Coordonnées Leaflet et révélation des catégories humain/animal avec objets simulés |
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

- Pas de clustering des marqueurs ; leur densité reste forte au zoom arrière.
- Pas de test Firefox/Safari ou d’appareil tactile réel. Les services de tuiles,
  Nominatim et la géolocalisation ne sont pas validés par les parcours simulés.
- Le chargement de repères par `JSON.parse(localStorage…)` n’est pas protégé
  contre un stockage corrompu. Les tests couvrent le cycle normal, pas ce défaut.
- Certaines erreurs de génération des cartes sont encore signalées par un
  message et un retour de fonction plutôt que par un échec explicite du processus.
- Le rythme et le déclenchement de la recherche distante restent à revoir au
  regard des politiques d’usage du fournisseur avant un déploiement public large.
- Pas d’interface d’édition multiutilisateur, d’authentification ou de serveur API.

### Données et narration

- Les coordonnées sont approximatives. Les tests d’arrondissement utilisent des
  boîtes géographiques, pas les limites administratives exactes ni une nouvelle
  vérification des rues auprès d’OpenStreetMap.
- Les IDs sont permanents par convention et validés dans l’état courant ; aucun
  registre de suppression ne garantit automatiquement leur non-réutilisation.
- Les preuves des relations sont comparées au texte source, mais le programme ne
  valide pas leur interprétation sémantique. L’extraction n’est pas exhaustive.
- Pas encore de temporalité, de statut « rumeur/perception », ni de distinction
  filiation biologique/adoptive. Une absence de lien n’est pas un fait narratif.
- Les ratios des portraits ne sont pas tous uniformes.
- Les treize personnages centraux et leurs nouveaux arcs restent à sélectionner
  et à valider ; ils ne sont pas incorporés aux données canoniques.

## 6. Licences et réutilisation

Les statuts annoncés restent **MIT pour le code**, **ODbL pour les données**,
**CC BY 4.0 pour les portraits IA**, avec les licences tierces de Leaflet et de
la police vendoriée. Voir [LICENSE-DONNEES.md](../LICENSE-DONNEES.md).

La présente revue vérifie la cohérence de la documentation, **pas la validité
juridique de tous les droits ni la conformité actuelle de chaque service de
cartographie**. Les avertissements fiction, adresses inventées et portraits IA
restent nécessaires. L’ancien choix de narration privée est abandonné : la
narration est publique dans le dépôt et le classeur.

## 7. Orientation proposée

Conserver l’architecture actuelle. Avant d’ajouter des personnages ou de changer
la pile technique, privilégier :

1. La validation éditoriale des [treize propositions](propositions-personnages-centraux.md).
2. L’enrichissement progressif des [relations sourcées](relations-personnages.md),
   avec un modèle temporel seulement lorsque les scènes en ont besoin.
3. Le traitement des erreurs de stockage et de construction signalées plus haut,
   puis l’élargissement des tests si la carte est diffusée plus largement.

Le projet dispose maintenant d’une base technique plus sûre ; la prochaine
valeur ajoutée dépend surtout des choix d’auteur et de la continuité narrative.
