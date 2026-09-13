# Journal des changements

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Ce projet n'a pas de version publiée : les entrées datent les bascules
structurantes.

## [2026-09-13] — Cohorte « jeunes » : 10 personnages (173 → 183)

Réponse au constat démographique de l'analyse (6 % de moins de 25 ans,
moyenne 46 ans) : dix jeunes rattachés à des familles déjà en place, pour
que chaque nouveau venu ait un ancrage dans le récit.

- **La Baie (7)** : Maude Pedneault (17, arbitre de hockey mineur), Zack
  Bérubé (18, commis de nuit), Thomas Bergeron (15, gardien de but), Mathis
  Truchon (20, pompiste du rang), Océane Lapointe (22, resurfaceuse de
  l'aréna), Noah Traoré (14, planchiste), Rosalie Girard (23, étudiante en
  soins infirmiers).
- **Chicoutimi (1)** : Sofia Santini (16, au restaurant familial).
- **Jonquière (2)** : Ludovic Larouche (19, ATM), Jade Boivin (12,
  patineuse artistique — première adresse sur la rue Sainte-Famille, Kénogami).
- Part des moins de 25 ans : 6,4 % → **11,5 %** ; mineurs : 3 → **8**.
- Portraits n° 174 à 183 générés par IA au ratio 3:2 (1264 × 848), deux
  gabarits WebP chacun ; planche contact reconstruite (19 rangées).
- Tests : `MINEURS` étendu, `N = 183`, nouveau garde-fou
  `test_cohorte_jeune_maintenue` (≥ 10 % de moins de 25 ans) — 39 garde-fous.
- Narration : les 10 lignes privées correspondantes sont fournies hors dépôt
  (à coller dans `data/narration.csv`).

## [2026-09-13] — Bascule « source texte » et revue qualité

Application de l'analyse du projet (`docs/analyse-projet.md`).

### Changements structurants

- **Source de vérité : `data/personnages.csv`** (16 colonnes, UTF-8, `;`).
  Le classeur `base_personnages_fictifs.xlsx` n'est plus qu'un **livrable
  généré** : il était à la fois source et cible depuis l'origine, ce qui
  rendait le diff Git illisible et toute fusion impossible.
  Migration : `scripts/init_source_csv.py` (à exécuter une seule fois).
- **Narration privée** : factions, répliques, liens et arcs vivent dans
  `data/narration.csv` (non versionné). Le classeur public ne contient plus la
  feuille *Narration* ; `base_personnages_fictifs-complet.xlsx` est régénéré en
  local et ignoré par Git. Fin de la contradiction avec le README, qui
  annonçait une narration « non exportée publiquement » alors qu'elle était
  dans le classeur commité. Un test et une étape CI vérifient qu'elle ne
  revient pas dans l'index.
- **Colonne `Branche`** (16 colonnes) : le qualificatif entre parenthèses
  (« Lavoie (JP) ») devient une colonne à part. La paire `Famille` + `Branche`
  identifie un foyer ; 57 familles et 84 foyers pour 173 personnages.
- **Factions normalisées** : 128 valeurs libres → **17 factions canoniques**
  (`data/factions.txt`), la nuance d'origine étant conservée dans
  « Faction (détail) ». Toute valeur hors vocabulaire fait échouer la
  construction.

### Carte

- **Recherche par personnage** (nom, surnom, famille, branche, rôle, adresse),
  insensible aux accents et à la casse — la recherche ne portait avant que sur
  Nominatim, donc taper « Lavoie » ne donnait rien.
- **Filtres** : secteur, type (humain/animal) et tranche d'âge, avec compteur
  « X / 173 personnages affichés ».
- **Panneau Familles hiérarchique** : clan puis foyer, cliquables.
- **Échappement HTML** de toutes les valeurs affichées (données, repères
  saisis, réponses Nominatim).
- **Portrait cliquable** : la vignette de la fiche ouvre le gabarit `-web`.
- **Une seule source HTML** : `carte-la-baie-saguenay.html` est désormais
  *dérivé* de `carte/index.html` par le script (plus de divergence possible).

### Outillage

- Suppression de `.github/workflows/relay-drive-archive.yml` (vestige
  d'infrastructure : téléchargement Drive + force-push de tag, sans rapport
  avec le projet).
- **Lint** : `ruff.toml`, `requirements-dev.txt`, crochets pre-commit, job CI
  dédié (rien de cosmétique, et aucun crochet qui toucherait aux livrables
  générés — ils n'ont pas de newline finale).
- **CI** : exécution hebdomadaire programmée + étape « la narration n'est pas
  versionnée ».
- `ecrire_xlsx()` découpé en `ecrire_personnages()` / `ecrire_lisez_moi()` /
  `ecrire_narration()` ; tous les `open()` en gestionnaire de contexte.
- Le test de date figée dérive désormais la date de `construire_base`
  (il échouait si `SOURCE_DATE_EPOCH` était défini).
- `scripts/migrer_corrections.py` (correctifs du 2026-09-12) déplacé dans
  `scripts/historique/` : il documente une migration passée et n'appartient
  plus à la chaîne de construction.

### Documentation

- README réécrit autour de la nouvelle chaîne (source texte, narration
  privée, 16 colonnes, conventions Famille/Branche, factions contrôlées).
- Nombre de garde-fous annoncé désormais vérifié par un test (le README
  annonçait 26 tests, il y en a 38).

## [2026-09-12] — Révision qualité : 13 correctifs

Dernière révision menée sur l'ancien format (classeur maître). Détail dans
`scripts/historique/migrer_corrections.py` et dans la PR #2 :
effectifs, coquilles, conventions d'adresse et de rôle, surnom hors du `Nom`,
coordonnées recalées sur le bon arrondissement, narration complétée à 100 %,
3 mineurs ajoutés, gabarit « archive » retiré, Leaflet vendorié, licences
distinguées, reproductibilité bit-à-bit assurée en CI.
