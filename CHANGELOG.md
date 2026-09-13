# Journal des changements

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [2026-09-13] — Corrections issues d’une revue externe

- **Planche contact** : les 12 vignettes verticales (400 × 600) sont désormais
  affichées entières au lieu d’être recadrées au ratio 3:2 ; le recadrage
  « couverture » coupait le visage de cinq d’entre elles et annulait la seule
  fonction de la planche. Les vignettes paysage gardent le plein cadre.
- **Relations** : 41 liens de famille déjà écrits en prose dans `Parenté`
  (fratries, cousinages, oncles/tantes, grands-parents, un filleul) sont entrés
  dans `data/relations.csv` : 155 relations, 176 personnages reliés (contre 114
  et 141). Trois types documentés s’ajoutent — `oncle_de`, `grand_parent_de`,
  `parrain_de` — avec leurs inverses ; aucune relation n’est déduite du clan,
  de l’adresse ou du prénom seul.
- **Atelier** : les mineurs ne peuvent plus être la « pression » des moteurs
  « dette » et « limite » (règle de `docs/atelier-saison-1.md`, désormais
  outillée et testée) ; ils restent point de vue ou témoin, avec un repère
  visible dans la distribution et les faits de scène.
- **Mentions de fiction** : clause de non-ressemblance pour les personnes, les
  entreprises et les organisations réelles citées comme contexte
  (`LICENSE-DONNEES.md`, README) ; la fiche de chaque personnage porte
  « Personnage de fiction — adresse inventée » et les coordonnées y sont
  affichées à quatre décimales au lieu de six (précision au mètre sous une
  adresse fictive).
- **Tests** : quatre garde-fous Python (66 au total) et quatre tests JavaScript
  dédiés à l’atelier (10 au total, `tests/atelier.test.cjs`) ; la suite JS de la
  CI couvre désormais `tests/*.test.cjs`.
- Nouveau document [docs/revue-externe-2026-09-13.md](docs/revue-externe-2026-09-13.md)
  : revue externe, non canonique et hors génération, avec les recommandations
  encore ouvertes.

## [2026-09-13] — Atelier interactif de scènes

- Ajout de `atelier/index.html`, une machine à faire apparaître des tensions à
  partir des personnages, narrations et relations existants.
- L’atelier propose plusieurs moteurs de scène, un point de vue, une pression,
  un témoin, des questions de jeu et une consigne de conséquence.
- Toutes les situations générées sont explicitement non canoniques ; l’atelier
  est réinjecté par la construction mais ne modifie aucune source éditoriale.

## [2026-09-13] — Lisibilité de la carte et IDs retirés

- Ajout d’un regroupement natif des personnages au zoom arrière, sans plugin
  externe : les groupes sont cliquables et les traits de familles restent
  réservés aux niveaux de zoom détaillés.
- Ajout de `data/ids-retires.txt`, registre versionné empêchant la réutilisation
  accidentelle d’un identifiant supprimé.
- Ajout de tests ciblés pour le regroupement et le registre d’identifiants.
- Ajout de deux documents de travail non générateurs : provenance géographique
  explicitée et noyau de saison 1 proposé, sans modification du canon.

## [2026-09-13] — Robustesse de la carte et de la génération

- Le chargement des repères locaux ignore désormais proprement un JSON corrompu,
  les coordonnées invalides et les noms vides ; les erreurs de quota de
  `localStorage` sont signalées sans faire planter la carte et les modifications
  non persistées sont annulées.
- La construction échoue explicitement si l’injection des personnages dans la
  carte échoue ou si une vignette référencée ne peut pas être synchronisée.
  Les vignettes copiées sont limitées à celles réellement référencées par la
  source personnages.
- Deux tests JavaScript ciblés portent le total à cinq ; l’analyse actuelle et
  le README décrivent désormais la nouvelle couverture.

Ce projet n'a pas de version publiée : les entrées datent les bascules
structurantes.

## [2026-09-13] — Documentation : état actuel séparé des archives

- Ancienne analyse et suivis préservés dans `docs/historique/`, avec avertissement
  de lecture et liens relatifs adaptés ; `docs/analyse-projet.md` devient l’état actuel.
- README corrigé : classeur unique à quatre feuilles, export des relations,
  parcours documentaires, portée réelle des tests et narration publique.
- Inventaire des fichiers de licence et nombre de mineurs actualisés, sans
  changement des licences annoncées ni audit juridique.
- Trois garde-fous documentaires supplémentaires : chiffres de l’analyse,
  séparation historique/courant et liens Markdown locaux (60 tests Python).
- Limites encore ouvertes explicitement documentées : stockage local corrompu,
  erreurs de construction, services externes et couverture navigateur notamment.

## [2026-09-13] — Relations explicites et atelier narratif

- Première extraction éditoriale de 114 relations entre 141 personnages dans
  `data/relations.csv`, avec IDs, type et provenance exacte (champ Parenté).
- Validation des références, symétrie, doublons, auto-relations, cycles parentaux
  et preuves désynchronisées ; nouveaux livrables JSON autonome et feuille Relations.
- Huit tests supplémentaires (57 Python au total), dont la séparation des
  propositions narratives et des livrables canoniques.
- Atelier non canonique de 13 personnages centraux : faits existants sourcés,
  propositions de désirs, enjeux, contradictions et décisions à valider.
- Documentation du périmètre partiel : pas d’inférence par clan et pas de
  conversion automatique des mentions vagues (« croise », « lui doit »…).

## [2026-09-13] — Identifiants stables des personnages

- Migration des 213 personnages et fiches de narration vers un ID permanent,
  attribué une seule fois depuis la numérotation des portraits existants.
- Ajout de `ID` en dernière colonne (17/9 colonnes) et de `id` aux exports
  JSON/GeoJSON/carte, y compris `Feature.id`.
- Jointure de la narration par ID ; libellés du classeur issus de la base.
- Chemins des portraits explicites, conservés lors d’un renommage ; les
  40 chemins auparavant implicites ont été renseignés sans déplacer d’image.
- Six garde-fous supplémentaires : propagation des IDs, format, doublons,
  références orphelines/manquantes, renommage/réordonnancement, chemin invalide.

## [2026-09-13] — La narration devient publique (fichier versionné, classeur unique)

Décision d'auteur : la séparation public/privé instaurée lors de la revue
qualité est levée. Factions, liens au Spot, répliques et arcs S1 rejoignent
le dépôt — sous ODbL, comme le reste de la part fictive (LICENSE-DONNEES).

- **`data/narration.csv` versionné** (213 lignes × 8 colonnes, `;` UTF-8) :
  les 133 fiches d'origine sont revenues de `scripts/historique/
  migrer_corrections.py` (faction libre normalisée via la table FACTIONS de
  `scripts/init_source_csv.py`, nuance conservée dans « Faction (détail) ») ;
  80 fiches nouvelles écrites pour l'occasion (protagonistes restés sans
  narration — JP, Dévon, Gratien, Yvan, Marco, Sylvie, Pisse-Feu… — et les
  quatre lots 173 → 213). Âge apparent = âge réel, comme sur les 133
  historiques.
- **Un seul classeur public** : `base_personnages_fictifs.xlsx` porte
  désormais les feuilles *Personnages* + *Lisez-moi* + *Narration* ; le
  classeur `-complet.xlsx` (`.gitignore`) disparaît, plus de raison d'être.
  `charger_narration()` devient **obligatoire** : un fichier absent fait
  échouer la construction au lieu de produire un classeur amputé.
- **Garde-fous inversés** (toujours 43) : la narration doit être versionnée
  (`git ls-files`), le classeur doit contenir la feuille *Narration* et
  l'ancien classeur complet ne doit plus exister ; la couverture vérifie en
  plus l'alignement des surnoms sur `data/personnages.csv` et l'absence de
  caractères de contrôle. La narration reste hors du CSV/JSON/GeoJSON et de
  la carte (choix de périmètre, test dédié maintenu).
- **CI** : l'étape « La narration n'est pas versionnée » devient « La
  narration est versionnée » ; README et feuille *Lisez-moi* mis à jour.

## [2026-09-13] — Suivi de la revue : bandeau mobile, injection carte, analyse à jour

Trois correctifs issus d'une revue fraîche du projet (état 213 fiches ; aucun
changement dans les données) :

- **Bandeau d'avertissement sur mobile** : à ≤ 820 px, la sidebar devient un
  tiroir fermé et le CSS de base masque `.banner{display:none}` — l'avertissement
  « fiction / adresses inventées / portraits IA » ne s'affichait plus sur
  téléphone. Il est ré-affiché en deuxième ligne d'en-tête sur mobile.
  Garde-fou `test_bandeau_avertissement_visible_sur_mobile`.
- **Injection des données dans la carte** : `re.subn` interprétait le gabarit de
  remplacement — une valeur contenant un saut de ligne, une tabulation ou `\1`
  aurait cassé le JavaScript de la carte (voire fait échouer la construction).
  Le remplacement est désormais une fonction ; garde-fou
  `test_injection_carte_resiste_aux_caracteres_speciaux` (aller-retour réel sur
  une carte temporaire), et le contrôle de la source étendu aux caractères de
  contrôle. Les données actuelles n'en contiennent aucune.
- **`docs/analyse-projet.md`** : suivi n° 2 — chiffres datés (état 173),
  rajeunissement et diversification des rues marqués fermés, bandeau mobile et
  injection marqués corrigés ; portraits (12 verticaux sur 213) et clustering
  restent ouverts.
- **43 garde-fous** (README mis à jour ; le nombre annoncé reste vérifié par un
  test).

## [2026-09-13] — Lot « Cégep / UQAC et Kénogami » : 10 personnages (203 → 213)

Lot mixte : la part des moins de 25 ans était retombée à 10,4 %, juste
au-dessus du garde-fou. Sept jeunes (16-24 ans) et trois adultes qui les
encadrent, sur quatre rues nouvelles (Saint-Vallier, LaFontaine, Dréan à
Chicoutimi ; Saint-Joseph à Kénogami).

- **Colocation étudiante du 318 Saint-Vallier (Chicoutimi)** : Emma Boucher
  (20, sciences humaines, nièce de Fernande), Moussa Diallo (21, informatique
  UQAC), William Lavoie (23, cuisinier, cousin de JP) ; leur propriétaire
  Lucien Gagné (66, oncle de la députée).
- **Autour du cégep** : Maïka Gauthier (19, soins infirmiers et caissière de
  pharmacie), Olivier Brassard (24, coursier-musicien), Diane Perron (58,
  professeure de sociologie, directrice de recherche de Laurie Lavoie).
- **Foyer Simard/Kénogami (Jonquière)** : Karine Simard (41, prof d'éduc et
  entraîneuse de natation), ses enfants Léa (16, nageuse) et Anthony (22,
  apprenti boucher) — sœur et neveux de Nancy Simard.
- Moins de 25 ans : 10,4 % → **13,2 %** ; La Baie 153 / Chicoutimi 41 /
  Jonquière 19 ; mineurs : 9.
- Portraits n° 204 à 213 (IA, 3:2), planche contact à 22 rangées ;
  `N = 213`, `MINEURS` étendu — 41 garde-fous.
- Narration : 10 lignes privées fournies hors dépôt
  (`data/narration-cegep-kenogami.a-coller.csv`).

## [2026-09-13] — Lot « Institutions et famille Desgagné » : 10 personnages (193 → 203)

Une famille sur **trois générations** à Grande-Baie et les services publics
de l'arrondissement (caserne, hôtel de ville, poste de police, aide
juridique, travaux publics), quatre rues nouvelles vérifiées sur OSM
(Monseigneur-Dufour, Saint-Pascal, Aimé-Gravel, Mars).

- **Famille Desgagné (6 + 1 allié)** : Yvette (84, ex-organiste), son fils
  Denis (56, capitaine de la caserne) et sa bru Johanne Gravel (54,
  évaluatrice municipale), leurs enfants Julien (33, prêtre de Grande-Baie,
  branche `presbytère`), Camille (27, pompière-paramédic, branche `caserne`)
  et Samuel (25, apprenti soudeur) ; Réal Gravel (61, contremaître au
  déneigement), frère de Johanne.
- **Institutions** : Nathalie Tremblay (49, directrice d'arrondissement,
  branche `Tremblay/hôtel de ville`), Mathieu Fortin (38, policier
  communautaire, `Fortin/police`), Geneviève Bouchard (44, avocate à l'aide
  juridique, `Bouchard/justice`).
- **Chaîne de construction** : `construire_base.py` **échoue** désormais
  quand un personnage n'a pas de portrait (auparavant simple avertissement,
  invisible en CI — rencontré sur ce lot : fichier nommé `abbe-julien-…`
  pour le nom « Julien Desgagné »). Test dédié
  `test_la_construction_refuse_un_personnage_sans_portrait` — 41 garde-fous.
- Portraits n° 194 à 203 (IA, 3:2), planche contact à 21 rangées.
- Narration : 10 lignes privées fournies hors dépôt
  (`data/narration-institutions-desgagne.a-coller.csv`).

## [2026-09-13] — Lot « Chicoutimi / Jonquière » : 10 personnages (183 → 193)

Réponse au constat géographique de l'analyse (La Baie 136 / Chicoutimi 27 /
Jonquière 10, sur 4 et 5 rues) : dix adultes de tous âges dans les deux
autres arrondissements, sur **six rues nouvelles** vérifiées sur
OpenStreetMap (Nominatim).

- **Chicoutimi (6)** : Gaétan Bossé (58, bouquiniste, rue Bossé), Stéphane
  Bossé (45, cuisinier de casse-croûte) et Marie-Ève Boucher (36, journaliste)
  sur Jacques-Cartier Ouest, Jérémie Côté (31, facteur, rue Sainte-Anne),
  Lise Gauthier (62, infirmière clinicienne, rue du Havre), Valentina Rojas
  (40, épicière latino, rue Bossé).
- **Jonquière (4)** : Fernand (67, retraité de l'aluminerie) et Audrey Lavoie
  (29, apprentie électricienne) sur la rue Davis à Arvida, Nancy Simard (52,
  coiffeuse, Saint-Hubert), Marc Picard (47, arpenteur-géomètre innu, rue du
  Vieux-Pont).
- Répartition : La Baie 143 / **Chicoutimi 34** / **Jonquière 16** ; 8 rues
  dans chacun des deux arrondissements (contre 4 et 5).
- Nouvelles branches : `Lavoie/Arvida`, `Simard/salon`, foyer `Côté/poste`
  étoffé ; nouvelles familles Bossé, Rojas, Picard.
- Portraits n° 184 à 193 (IA, 3:2), planche contact à 20 rangées.
- Tests : `N = 193`, nouveau garde-fou
  `test_les_deux_autres_arrondissements_restent_peuples` (planchers
  d'effectif et de nombre de rues) — 40 garde-fous.
- Narration : 10 lignes privées fournies hors dépôt
  (`data/narration-chicoutimi-jonquiere.a-coller.csv`).

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
