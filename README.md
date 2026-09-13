# Base de données de personnages fictifs — La Baie (Saguenay)

Projet personnel de **fiction** : **213 personnages géolocalisés et illustrés**
dans la ville de Saguenay (arrondissements de La Baie, Chicoutimi et
Jonquière, Québec), dont **212 humains et 1 animal**. Les personnages, noms,
situations et numéros civiques sont **entièrement inventés** ; les rues et
les toponymes sont réels (OpenStreetMap).

🗺️ **Carte interactive** : ouvrir [`carte-la-baie-saguenay.html`](carte-la-baie-saguenay.html)
(ou [`carte/index.html`](carte/index.html)).
📇 **Planche contact des 213 portraits** : [`portraits/planche-contact-generale.webp`](portraits/planche-contact-generale.webp).

<a href="portraits/planche-contact-generale.webp"><img src="portraits/planche-contact-generale.webp" alt="Planche contact des portraits" width="480"></a>

> ⚠️ **Avertissement** : numéros civiques fictifs (ne pas utiliser comme
> adresses postales), coordonnées à l'échelle du quartier (± 400 m),
> **portraits générés par IA** — aucune personne réelle photographiée.

---

## Quelle documentation consulter ?

- **État actuel et limites :** [analyse du projet](docs/analyse-projet.md).
- **Géographie et provenance :** [méthode et limites](docs/geographie-provenance.md).
- **Utilisation et maintenance :** ce README.
- **Relations :** [conventions et périmètre](docs/relations-personnages.md).
- **Écriture :** [propositions à valider, non canoniques](docs/propositions-personnages-centraux.md) et
  [noyau de saison 1 proposé](docs/atelier-saison-1.md).
- **Historique :** [journal des changements](CHANGELOG.md) et
  [ancienne analyse à 173 personnages](docs/historique/analyse-173-personnages.md).

## Contenu du dépôt

| Fichier / dossier | Rôle |
|---|---|
| `data/personnages.csv` | **Source de vérité** : 213 lignes × 17 colonnes, UTF-8 `;`. Identités et descriptions à éditer ici. |
| `data/relations.csv` | 114 liens explicites entre 141 personnages, avec IDs et preuve textuelle. |
| `relations_personnages.json` | Export autonome des relations ; régénéré, ne pas éditer. |
| `relations.py` | Validation des relations, export JSON et feuille Excel. |
| `data/factions.txt` | Vocabulaire contrôlé des **17 factions** (narration). |
| `data/ids-retires.txt` | Registre versionné des IDs définitivement indisponibles après un retrait. |
| `data/narration.csv` | **Source narration** (publique, versionnée) : faction, lien au Spot, réplique, arc S1 — 9 colonnes. |
| `base_personnages_fictifs.xlsx` | Classeur public : *Personnages* (213 × 17) + *Narration* + *Relations* + *Lisez-moi*. |
| `base_personnages_fictifs.csv` | Export tableur, séparateur `;`, UTF-8 BOM (accents OK dans Excel FR). |
| `base_personnages_fictifs.json` | Export code / API, clés minuscules sans accent. |
| `base_personnages_fictifs.geojson` | Points WGS84 pour QGIS, geojson.io, uMap, Mapbox. |
| `carte/index.html` | Carte interactive Leaflet — **source HTML unique** (données réinjectées par le script). |
| `carte-la-baie-saguenay.html` | Copie de racine **dérivée** de `carte/index.html` (ne jamais l'éditer). |
| `carte/vendor/leaflet/` | **Leaflet 1.9.4 en copie locale (BSD-2)** : aucun CDN. |
| `carte/portraits/` | Vignettes 400 px servies par la carte (synchronisées par le script). |
| `atelier/index.html` | Atelier interactif de génération de scènes, non canonique et réinjecté par le script. |
| `portraits/` | Deux gabarits WebP par personnage : `-web.webp` et `-vignette.webp`, plus la planche contact. |
| `construire_base.py` | Générateur **idempotent et reproductible** de tous les livrables. |
| `scripts/init_source_csv.py` | Migration unique : ancien classeur maître → `data/*.csv`. |
| `scripts/retirer_archives_git.sh` | Purge optionnelle de l'ancien gabarit « archive » dans l'historique Git. |
| `scripts/historique/` | Scripts de migration passés, conservés pour mémoire. |
| `tests/test_base.py` | **62 garde-fous** couvrant les conventions et la documentation, lancés en CI. |
| `.github/workflows/validation.yml` | CI : lint + régénération + contrôle de reproductibilité + tests. |
| `docs/relations-personnages.md` | Conventions, périmètre partiel et liens restant à qualifier. |
| `docs/propositions-personnages-centraux.md` | Atelier narratif : 13 personnages proposés, non canonique, à valider. |
| `docs/analyse-projet.md` | État actuel, bilan des cinq priorités, vérifications et limites ouvertes. |
| `docs/geographie-provenance.md` | Méthode, attribution OSM et limites des coordonnées fictionnelles. |
| `docs/atelier-saison-1.md` | Proposition non canonique de noyau dramatique pour un premier atelier de scènes. |
| `docs/historique/` | Analyse initiale et suivis intermédiaires archivés ; ne pas utiliser comme état courant. |
| `LICENSE` / `LICENSE-DONNEES.md` | Trois statuts distincts : code MIT, données ODbL, portraits IA en CC BY 4.0. |

## Colonnes (17)

`Nom` · `Surnom` · `Type` · `Age` · `Rôle` · `Secteur` · `Adresse` ·
`Latitude` · `Longitude` · `Apparence` · `Vêtements` · `Tic / Objet` ·
`Portrait` · `Famille` · `Branche` · `Parenté` · `ID` — le dictionnaire détaillé
(dans le classeur, feuille *Lisez-moi*) est généré depuis `construire_base.py`.

Principales conventions :

- **Surnom** : une cellule vide signifie « pas de surnom » (personnage « rangé
  »), ce n'est pas un oubli. Le surnom ne s'écrit **jamais** dans le `Nom`.
- **Rôle** : métier autonome, sans référence à un autre personnage ni à une
  faction / un clan (le clan va dans `Famille` ; la faction, dans la narration).
- **Adresse** : `« Numéro, Rue »` (numéro inventé, rue réelle OSM) ; pour les
  lieux non adressables (plein air, sentier, base militaire) : `Lieu-dit : …`.
- **Vêtements** : `s.o.` = sans objet (ex. un animal), vide = inconnu.
- **Famille + Branche** : la famille est le nom du clan, **sans** qualificatif ;
  la branche précise le foyer (« JP », « ruelle », « motards »…). Deux foyers
  homonymes partagent la `Famille` et se distinguent par la `Branche`.
- **Factions** (narration) : 17 valeurs canoniques listées dans
  `data/factions.txt` ; l'ancienne nuance est gardée dans « Faction (détail) ».
- **Âge** : neuf personnages humains sont mineurs (9 à 17 ans) — la cohorte
  « jeunes » (aréna, école, cégep) a été étoffée le 2026-09-13 ; le seul
  personnage de moins de 18 ans qui ne soit pas humain reste le chat
  Pisse-Feu (7 ans en âge animal).

## Identifiants stables et renommages

Chaque personnage possède un **`ID` permanent** (`P001` à `P213` actuellement).
Il est présent dans les sources personnages/narration, les feuilles Personnages et Narration,
les exports et les données de la carte (`id` en JSON). Le GeoJSON porte également
cet identifiant dans `Feature.id`.

- Les identifiants initiaux reprennent les numéros des portraits existants,
  attribués **une seule fois**. Le générateur ne les recalcule jamais à partir
  du nom, du portrait ou de l’ordre des lignes.
- Pour ajouter un personnage, attribuer un nouvel ID jamais utilisé
  (prochain disponible dans l’état actuel : `P214`) dans `data/personnages.csv` et `data/narration.csv`.
  Ne jamais renuméroter les anciens ni réutiliser l’ID d’un personnage retiré ;
  consulter l’historique Git en cas de doute.
- Pour renommer un personnage, modifier `Nom`/`Surnom` dans
  `data/personnages.csv`, en conservant `ID` et `Portrait`, puis régénérer.
  La narration est jointe **par ID** ; ses libellés dans le classeur suivent
  automatiquement la base. Les colonnes Nom/Surnom de `data/narration.csv`
  restent des repères de lecture, à actualiser manuellement si souhaité.
- `Portrait` est désormais un chemin explicite obligatoire. Les 40 cellules
  auparavant complétées par découverte du nom ont été renseignées. Un
  renommage ne nécessite pas de renommer les images.
- Les IDs absents, invalides, dupliqués ou inscrits dans
  `data/ids-retires.txt`, les références de narration manquantes/orphelines et
  les chemins de portraits invalides bloquent la construction.
- Lorsqu’un personnage est retiré, ajouter son ID au registre avant toute
  reconstruction. Un ID retiré ne doit jamais être réutilisé.

**Évolution du schéma :** la colonne ID est ajoutée en fin de tableau
(17 colonnes Personnages, 9 colonnes Narration). Les anciennes colonnes gardent
leur position. Adapter les consommateurs qui imposaient exactement 16/8 colonnes.
Les textes en prose (`Parenté`, arcs, etc.) ne sont pas réécrits automatiquement.
Une première extraction de relations explicites est désormais disponible ci-dessous.

## Relations et atelier narratif

**114 liens explicites entre 141 personnages** sont structurés dans
`data/relations.csv` : parenté, couples, fratries, liens professionnels et
colocations. Chaque ligne contient les deux IDs, le type de relation et une
preuve issue du champ Parenté. Cette première extraction est **partielle** ;
un lien absent n’est pas une absence de relation dans l’univers.

La construction vérifie les références, types, doublons, auto-relations,
cycles parentaux et preuves périmées. Elle ajoute une feuille **Relations**
au classeur et produit **`relations_personnages.json`**. Les relations ne sont
pas injectées dans la carte ni les exports géographiques ; ses traits de famille
restent distincts de cette table. Le sens des preuves reste soumis à relecture
humaine, et non à une interprétation automatique de la prose.

Voir [les conventions et limites](docs/relations-personnages.md).

L’[atelier de personnages centraux](docs/propositions-personnages-centraux.md)
propose **13 fiches** : désir, enjeu, contradiction, opposition, décision et
progression. Les faits existants y sont sourcés séparément. **Les propositions
ne modifient pas le canon** et ne sont pas chargées par le générateur ; elles
attendent validation de l’auteur.

## Narration : publique dans le dépôt, hors des exports géo

| | Dans le dépôt ? | Où la trouve-t-on ? |
|---|---|---|
| Personnages (17 colonnes) | ✔ | `data/personnages.csv`, classeur, csv/json/geojson, carte |
| Factions, répliques, arcs | ✔ | `data/narration.csv`, feuille *Narration* du classeur |
| Vocabulaire des factions | ✔ | `data/factions.txt` (17 valeurs canoniques) |

La narration a été rendue publique le 2026-09-13 (elle était auparavant
privée et non versionnée). Elle alimente la feuille *Narration* du classeur
mais reste **volontairement hors des exports personnages** csv / json / geojson
et de la carte. Les garde-fous contrôlent notamment son absence des JSON/GeoJSON.
Un test et une étape CI vérifient aussi que
`data/narration.csv` reste bien versionné dans Git.

## Démarrage rapide

```bash
# 1. (optionnel) environnement isolé
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt        # ruff (qualité de code)

# 2. ouvrir la carte (double-clic, ou)
python3 -m http.server 8000 --bind 0.0.0.0
#   → http://localhost:8000/carte-la-baie-saguenay.html

# 3. modifier la base : éditer data/personnages.csv, puis
python3 construire_base.py
#    régénère le classeur unique (4 feuilles), les exports personnages
#    csv / json / geojson et relations_personnages.json, réinjecte les données
#    dans carte/index.html et atelier/index.html, en dérive
#    carte-la-baie-saguenay.html, synchronise les vignettes et reconstruit
#    la planche contact.

# 4. contrôler la base
python3 -m unittest discover -s tests -v   # 62 garde-fous
ruff check .                               # lint
node --test tests/carte.test.cjs            # régressions JS ciblées (Node.js 22)
```

La source se modifie dans un tableur comme n'importe quel CSV (`;` et UTF-8) ;
à défaut, un éditeur de texte suffit, et le diff Git reste lisible ligne à ligne.

### Tests navigateur (Chromium)

Les **14 tests Playwright** complètent les 62 garde-fous Python et les
6 tests JavaScript ciblés. Sept parcours sont joués sur chacune des deux
cartes : recherche sans accents et portrait, filtres combinés,
révélation des humains et de l’animal masqués, coordonnées/zoom,
création–persistance–export GeoJSON–suppression des repères, et menu
sur un écran mobile de 390 × 844 px. Chaque parcours vérifie aussi
l’absence d’exception JavaScript.

```bash
# Installation (Node.js 22 et Python 3)
npm ci
npx playwright install --with-deps chromium

# Premier terminal : serveur statique à la racine du dépôt
python3 -m http.server 8000 --bind 0.0.0.0

# Second terminal : tests et rapport
npm run test:e2e
npx playwright show-report
```

Le job CI `navigateur` démarre et arrête automatiquement le serveur.
Les traces et captures d’écran sont conservées en cas d’échec (artefact
CI disponible 7 jours). Ces fichiers et les dépendances npm sont ignorés
par Git. `E2E_BASE_URL` permet de tester un autre serveur local ;
`CHROMIUM_EXECUTABLE_PATH` permet d’utiliser un Chromium déjà installé.

Les requêtes de tuiles et de recherche distante sont **simulées** : les
tests exécutent le vrai code Leaflet, mais ne valident pas la disponibilité
d’OpenStreetMap/Nominatim. Le test mobile contrôle une petite fenêtre
Chromium, pas un appareil tactile réel. Firefox et Safari ne sont pas couverts.

### Utilisation hors ligne

Le **code** de la carte est vendorié (`carte/vendor/leaflet/`) : aucun accès à
un CDN n'est nécessaire et la carte s'ouvre sans réseau. Seuls les **fonds de
tuiles** et la recherche de lieux (Nominatim) restent des services en ligne
(voir les licences dans [`LICENSE-DONNEES.md`](LICENSE-DONNEES.md), § 4) ; pour
un usage 100 % hors ligne, brancher des tuiles locales (MBTiles / PMTiles).
La **recherche de personnages**, elle, est locale et fonctionne sans réseau.

## Reproductibilité et qualité

- `construire_base.py` n'écrit **aucune donnée volatile** : la date « Généré
  le » est figée (surcharge possible via `SOURCE_DATE_EPOCH`) et les
  métadonnées du classeur sont normalisées — un zip réécrit à date fixe
  (`figer_xlsx`). Relancer le script deux fois produit des fichiers **octet
  pour octet identiques**, ce que la CI vérifie en comparant deux
  constructions successives puis en exigeant un `git diff` vide. Seule la
  **planche contact WebP** dépend du codec `libwebp` natif : son idempotence
  est garantie sur un même runner, sans comparaison binaire
  inter-environnements (la fonte, elle, est vendoriée dans `assets/fonts/`).
- Les **62 garde-fous** vérifient notamment : effectifs et cohérence des 4
  exports, conformité de la source texte, **unicité et absence de `];`** dans
  les valeurs, adresses avec numéro ou `Lieu-dit :`, rôles sans clan,
  **Famille/Branche sans parenthèses**, coordonnées dans une boîte approximative de l’arrondissement,
  mineurs présents, **narration versionnée, complète dans le classeur et
  alignée sur la base (surnoms)**, factions dans le vocabulaire contrôlé,
  portraits et planche contact présents,
  Leaflet sans CDN, **carte de racine strictement dérivée de la canonique**,
  contrôles d’échappement HTML, IDs, relations sourcées et séparation des
  propositions narratives. Les tests contrôlent aussi les statuts de licence
  annoncés, les chiffres de l’analyse actuelle et les liens documentaires locaux.
  Ces contrôles ne remplacent ni une revue de sécurité ni une expertise juridique.
- La CI est configurée pour les push sur `main`/`arena/**`, les PR **et une fois par semaine** (détection des
  dépendances cassées), avec un job de lint `ruff` (aucune règle cosmétique,
  et aucun crochet pre-commit qui toucherait aux livrables générés).

## Provenance et licences

- **Rues et géocodage** : © contributeurs OpenStreetMap via Overpass et
  Nominatim, **ODbL**.
- **Portraits** : images **générées par IA**, personnages fictifs, **CC BY 4.0**.
- **Code** : **MIT** ; carte basée sur **Leaflet 1.9.4 (BSD-2)**.

Les statuts annoncés et points à vérifier (paternité, share-alike, étiquetage IA, conditions
des tuiles) figurent dans **[`LICENSE-DONNEES.md`](LICENSE-DONNEES.md)**.
