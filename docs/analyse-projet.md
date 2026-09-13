# Analyse du projet — Base de données de personnages fictifs (La Baie / Saguenay)

**Objet** : revue complète du dépôt `5bhff95pdk-design/Base_Donnee` — données,
code, outillage, reproductibilité, licences et carte interactive.
**Date de l'analyse** : 2026-09-13 · **Branche** : `arena/01a09830-base-donnee`
**Point de départ** : commit `6066631` (merge de la PR #2, « 13 correctifs »)

> Méthode : lecture intégrale du code (`construire_base.py`, `tests/`, workflows),
> exécution réelle de la chaîne de construction et des tests, puis analyse
> statistique des 173 enregistrements (JSON / XLSX / GeoJSON / feuille Narration).
> Les chiffres ci-dessous sont issus de ces exécutions, pas de la documentation.
> Commandes rejouables : voir [Annexe A](#annexe-a--ce-qui-a-été-vérifié).

---

## 1. Verdict en une page

**Un projet personnel au niveau d'ingénierie rarement atteint à cette échelle.**
La reproductibilité octet-pour-octet, la CI qui la vérifie, les 27 garde-fous
qui encodent les *conventions éditoriales* (et pas seulement le format), la
séparation nette des trois régimes de licence et l'absence totale de dépendance
réseau pour le code de la carte sont des choix de professionnel.

Les marges de progression ne sont **pas** dans l'outillage : elles sont
**éditoriales** (vocabulaire non contrôlé, démographie, réalisme géographique) et
**structurelles** (le classeur binaire est à la fois la source et le produit ;
le dépôt traîne un workflow obsolète).

| Axe | Appréciation | Note indicative |
|---|---|---|
| Reproductibilité & CI | Exemplaire, vérifiée par l'exécution | ★★★★★ |
| Qualité & complétude des données | Très bonne ; intégrité référentielle solide | ★★★★☆ |
| Garde-fous / tests | Couvrent les conventions, pas seulement le schéma | ★★★★☆ |
| Documentation | Claire et honnête ; quelques dérives de chiffres | ★★★★☆ |
| Licences & conformité | Trois statuts bien distincts ; **une contradiction à lever** | ★★★☆☆ |
| Carte interactive | Riche et hors ligne ; pas de recherche par personnage | ★★★☆☆ |
| Hygiène du dépôt | Propre, mais source binaire + workflow mort | ★★★☆☆ |
| Réalisme « narratif » | Solide sur le fond, perfectible sur la démographie | ★★★☆☆ |

**Les 5 choses à faire d'abord** : (1) lever la contradiction Narration « non
exportée publiquement » / présente dans le XLSX public ; (2) supprimer le
workflow `relay-drive-archive.yml` ; (3) sortir la source de vérité du binaire ;
(4) normaliser les vocabulaires `Faction` et `Famille` ; (5) rajeunir la
population (4 personnes de moins de 20 ans sur 173).

---

## 2. Ce que contient réellement le projet

### 2.1 Inventaire mesuré

| Élément | Valeur constatée |
|---|---|
| Entrées | **173** (172 humains + 1 animal, le chat Pisse-Feu, 7 ans) |
| Colonnes | 15, conformes à la liste canonique (test dédié) |
| Exports | `xlsx` (51 Ko) · `json` (87 Ko) · `geojson` (119 Ko) · `csv` (42 Ko, `;` + BOM) |
| Feuille Narration | 173 lignes, 4 champs narratifs **à 100 %** + `Age apparent` |
| Portraits | 173 × 2 gabarits (`-web` 16,7 Mo / `-vignette` 3,4 Mo) + planche contact 2510×3682 (1,7 Mo) |
| Cartes | 2 fichiers HTML (94 Ko chacun), identiques à 2 lignes près |
| Poids de l'arbre de travail | **25,7 Mo** → portraits **20,9 Mo (79 %)**, carte 3,5 Mo (13 %), polices 0,7 Mo |
| `.git` | 22 Mo (dépôt écrasé en un seul commit : l'historique == l'arbre) |
| Tests | **27** (et non 26 comme annoncé dans le README) |
| CI | Verte sur `main` (20 s), 2 PR fusionnées, historique de runs disponible |

### 2.2 Chaîne de production

```
base_personnages_fictifs.xlsx  (SOURCE et… CIBLE)
        │
        ├─ charger()      : lecture, normalisation, auto-détection des portraits
        ├─ ecrire_xlsx()  : réécrit le classeur + Lisez-moi + Narration
        │   └─ figer_xlsx() : réécrit le zip avec une date unique (reproductibilité)
        ├─ ecrire_autres(): csv (; + BOM) · json (clés ASCII) · geojson (WGS84)
        ├─ reinjecter_carte() : remplace `const PERSOS=[…]` dans les 2 HTML
        ├─ copier_vignettes() : portraits/*-vignette.webp → carte/portraits/
        └─ planche_contact()  : assemblage WebP, fonte vendoriée (DejaVu)
```

Le script est **idempotent par construction** : aucune date système, aucune
métadonnée Office volatile, `SOURCE_DATE_EPOCH` respecté.

---

## 3. Reproductibilité et CI — le point le plus fort

**Vérifié par l'exécution, pas seulement annoncé :**

1. `python3 construire_base.py` → les empreintes SHA-256 des 526 livrables
   (xlsx, csv, json, geojson, html, webp) sont **strictement identiques** avant
   et après construction ;
2. une seconde exécution consécutive ne change **aucun octet** ;
3. `git status` reste **vide** après reconstruction : les livrables commités
   sont bien à jour ;
4. `python3 -m unittest discover -s tests -v` → **27 tests, OK** (0,3 s) ;
5. la CI reproduit exactement ce triptyque (build 1 / build 2 / `git diff` vide /
   tests) et exclut à juste titre la planche WebP de la comparaison binaire
   inter-machines (codec `libwebp` natif).

C'est rare et précieux : la plupart des projets de données « générés » polluent
leur historique à chaque exécution. Ici, **la reproductibilité est un invariant
testé**, et la police est vendoriée précisément pour que le rendu de la planche
ne dépende pas de la machine.

**Réserves mineures**

- Le test `test_pas_d_horloge_dans_le_xlsx` fige la chaîne `2026-09-11T00:00:00Z`
  en dur : si quelqu'un construit avec `SOURCE_DATE_EPOCH`, la construction est
  correcte mais **le test échoue**. Le test devrait dériver la date attendue de
  la même source que le script.
- La CI ne tourne que sur `push`/`pull_request`. Aucune exécution programmée :
  une dépendance qui casse (openpyxl, Pillow, runner GitHub) ne serait détectée
  qu'au prochain commit.
- Pas de matrice de versions Python (3.12 seulement), pas de cache d'autres
  chemins : acceptable à cette échelle.

---

## 4. Qualité des données

### 4.1 Complétude (sur 173 entrées)

| Colonne | Vides | Remarque |
|---|---|---|
| Nom, Type, Âge, Rôle, Secteur, Adresse, Coordonnées, Apparence, Tic/Objet, Portrait, Famille, Parenté | **0** | Rien ne manque |
| Vêtements | 1 | = `s.o.` pour l'animal — **convention respectée** |
| Surnom | 76 (44 %) | **Choix assumé et documenté**, pas un oubli |

Aucune donnée manquante non assumée : c'est le résultat d'un vrai travail de
reprise (les 13 correctifs du 2026-09-12), et c'est verrouillé par les tests.

### 4.2 Conventions — toutes vérifiées par les tests

- Surnom jamais dans `Nom` (pas de « ») ✓
- Adresse = `Numéro, Rue` **ou** `Lieu-dit : …` (7 cas, préfixe explicite) ✓
- Rôle sans référence à un clan / une faction ✓
- Coordonnées dans la boîte de l'arrondissement déclaré ✓ (dont le cas Danny
  Fortin, corrigé et désormais testé nommément)
- Narration absente des exports publics json/geojson ✓

### 4.3 Intégrité référentielle — contrôle inédit

Test maison : extraction des relations explicites de `Parenté`
(*fils/fille/époux/frère/sœur/père/mère/oncle/nièce/cousin… de **X***) puis
résolution de **X** dans la base.

> **85 liens sur 88 résolus.** Les 3 non résolus (« Mère de JP », « Père de JP »,
> « Sœur de JP ») pointent vers *Jean-Philippe Lavoie* via son **surnom** « JP » —
> sémantiquement valides, simplement incomparables à la colonne `Nom`.

Autrement dit : **la généalogie est cohérente**, ce qui est remarquable pour 173
personnages écrits à la main. Aucune coordonnée n'est dupliquée (173 points
distincts, donc le mécanisme d'étalement des marqueurs de la carte ne se
déclenche jamais).

### 4.4 Démographie — l'angle mort persistant

| Indicateur | Valeur |
|---|---|
| Âges | 7 → 86 ans (moyenne 46,4 · médiane 45 pour les humains) |
| Moins de 20 ans | **4** (9, 13, 16 ans + 1 enfant de 9 ans) → **2,3 %** |
| 20-29 ans | 21 · 30-39 : 37 · 40-49 : 40 · 50-59 : 33 · 60-69 : 23 · 70+ : 14 |
| Équilibre femmes/hommes | ≈ équilibré (proxy `Parenté` : 54 marqueurs féminins / 53 masculins) |
| Patronymes | 61 distincts pour 173 (Lavoie 12, Tremblay 11, Côté 9, Gagnon 9) → **réaliste pour le Saguenay** |
| Prénoms | 154 distincts (Hélène ×3, Manon ×3) → très bonne diversité |

La correction du 2026-09-12 a ajouté 3 mineurs, **mais le déficit reste massif** :
une vraie population compte ~20 % de moins de 20 ans, et l'intrigue elle-même
convoque aréna, CPE, école et cégep. Il manque une **cohorte de 12-25 ans**
(joueurs de hockey, élèves, étudiants de l'ATM, jeunes de la ruelle), et
quelques 20-35 ans pour densifier la tranche active.

### 4.5 Géographie — concentration marquée

| Secteur | Personnages | Rues distinctes |
|---|---|---|
| La Baie | 136 (79 %) | ~33 |
| Chicoutimi | 27 | **4** (Racine Est 14, Bégin, Talbot, Bd de l'Université) |
| Jonquière | 10 | 5 (Price, Harvey, Saint-Dominique, Saint-Hubert, Alumineries) |

- **42 rues seulement** pour 173 personnages → 4,1 par rue ;
- Rue Victoria : **18 personnages** sur ~500 m ; Rue Racine Est : **14** ;
- 7 lieux-dits (plein air, base militaire, sentier) correctement préfixés.

Pour de la fiction, une forte concentration est un choix défendable (elle fabrique
un « quartier »). Mais 14 personnages sur une seule rue de Chicoutimi, et 27
Chicoutimiens sur 4 rues, se voit à l'écran comme un artefact. Recommandation :
élargir à 8-12 rues par arrondissement secondaire, et documenter la règle de
densité maximale par rue.

### 4.6 Narration — le maillon faible côté vocabulaire

La feuille `Narration` est complète (173/173, 4 champs remplis, aucune réplique
ou arc dupliqué) et riche (répliques en joual, ~33 caractères en moyenne).
Mais :

- **`Faction` n'est pas un vocabulaire contrôlé : 128 valeurs distinctes pour 173
  personnages**, dont des quasi-doublons et des variantes de casse :
  `Ruelle` (8) / `Ruelle d'en Face` (5) / `Bloc d'en Face` (2) / `Bloc d'en face` (1)
  / `Ruelle / Louche` / `Ruelle / Marge` / `Ruelle / Lavoie`… Une faction devrait
  être ~8-12 entrées, filtrables ; ici c'est du texte libre.
- `Age apparent` : 139/173 identiques à l'âge réel, 8 écarts > 5 ans — usage
  cohérent, mais le champ n'est documenté nulle part (ni README, ni `Lisez-moi`).
- Le README décrit la narration comme « non exportée publiquement » — **alors que
  le classeur XLSX qui la contient est commité et public** (§ 6.1).

### 4.7 Portraits

- **173 / 173** présents dans les deux gabarits, numérotation `01`→`173`
  **sans trou**, 173 vignettes synchronisées dans `carte/portraits/`, aucun
  gabarit « archive » orphelin.
- **Formats sources hétérogènes** : 116 × 1200×654, 24 × 1536×1024,
  14 × 1200×669, **10 × 1024×1536 (portrait)**, 3 × 1537×1023…
- Conséquence : la planche contact recadre tout en 3:2 (240×160) → les 10
  portraits au format portrait perdent l'essentiel de leur cadrage, et les
  vignettes héritent de 5 ratios différents (400×218, 400×266, 400×600…).
- Aucune contrainte n'est testée sur les dimensions (le test ne vérifie que la
  largeur de la planche, 2510 px).

---

## 5. Code et outillage

### 5.1 Ce qui est bien

- Un **seul script de 410 lignes**, sans dépendance exotique (openpyxl + Pillow),
  avec une sortie console lisible et des messages d'erreur utiles.
- `figer_xlsx()` est une vraie trouvaille : openpyxl réécrit `modified` et date
  les entrées zip à l'horloge système — le script repasse derrière pour figer les
  deux. C'est ce qui rend la reproductibilité possible malgré le format binaire.
- Le script **dégrade proprement** : sans Pillow, tout est généré sauf la planche.
- Les tests sont **nominaux et explicatifs** : chaque garde-fou cite le constat
  qui l'a motivé (« #4 Danny Fortin… », « #6 clan dans le Rôle… »). C'est de la
  documentation exécutable.
- `.gitattributes` (EOL par type, binaire explicite), `.gitignore` (gabarit
  archive exclu par exception), script de purge `git-filter-repo` fourni.

### 5.2 Dette technique identifiée

| # | Point | Gravité | Recommandation |
|---|---|---|---|
| 1 | **Le XLSX est la source ET la sortie** : aller-retour openpyxl à chaque build ; diff Git illisible, fusion impossible en cas de conflit, perte des commentaires/mises en forme manuelles | Haute | Passer la source en **texte versionnable** (CSV/JSON/YAML dans `data/`), le XLSX devenant un livrable généré. Le script sait déjà tout régénérer : la bascule est peu coûteuse |
| 2 | `ecrire_xlsx()` fait **98 lignes** (données + mise en forme + 2 feuilles annexes) | Moyenne | Découper : `ecrire_personnages()`, `ecrire_lisez_moi()`, `ecrire_narration()` |
| 3 | Fichiers ouverts sans `with` (json, geojson, HTML) et `ResourceWarning` dans les tests | Faible | Utiliser `with open(...)` partout |
| 4 | Identifiants accentués (`centré`), variables globales de module | Faible | Cosmétique ; un formateur (ruff/black) réglerait l'ensemble |
| 5 | **Aucun linter / formateur / pre-commit**, pas de `CONTRIBUTING`, pas de `CHANGELOG`, aucun tag/release | Moyenne | Ajouter `ruff` + pre-commit et un `CHANGELOG.md` : l'historique est aujourd'hui réduit à un commit, l'intention des 13 correctifs n'est lisible que dans `scripts/migrer_corrections.py` |
| 6 | Deux HTML dupliqués (`carte-la-baie-saguenay.html` et `carte/index.html`), réinjectés par regex | Moyenne | Générer l'un depuis l'autre (ou documenter noir sur blanc « ne jamais éditer la copie ») ; le test vérifie la présence de `PERSOS`, pas l'égalité des deux fichiers |
| 7 | `re.subn(r'const PERSOS=\[.*?\];')` non échappé : une valeur contenant `];` casserait silencieusement l'injection | Faible | Vérifié : aucune valeur n'en contient. Ajouter un test ou ancrer sur des marqueurs `/*PERSOS_START*/` |

---

## 6. Licences, conformité et dépôt

### 6.1 ⚠ Contradiction à lever en priorité

`LICENSE-DONNEES.md` et le README expliquent que la feuille *Narration*
(factions, liens, répliques, arcs — le cœur dramaturgique) est
« **non exportée publiquement** ». C'est vrai des exports `json` / `geojson` /
carte. Mais **`base_personnages_fictifs.xlsx`, commité, contient bien les 173
lignes de Narration**. Quiconque clone le dépôt obtient les répliques et les arcs.

Deux issues possibles :
- **la narration est destinée à rester privée** → produire deux classeurs :
  `…-public.xlsx` (sans Narration) commité, et le classeur maître complet
  conservé hors dépôt (ou dans un dépôt privé) ;
- **elle est destinée à être publique** → corriger la documentation, qui induit
  aujourd'hui le lecteur (et d'éventuels réutilisateurs) en erreur.

### 6.2 Ce qui est exemplaire

- **Trois régimes distincts et documentés** : code MIT · données dérivées d'OSM
  en ODbL · portraits IA en CC BY 4.0, avec mention de paternité prête à l'emploi.
- **Étiquetage IA** explicite à trois endroits (README, `LICENSE-DONNEES.md`,
  bandeau de la carte) + avertissement « numéros civiques fictifs ».
- Leaflet **vendorié avec sa licence BSD-2**, et un **test** interdit toute
  réintroduction de CDN (unpkg/jsdelivr/cdnjs/googleapis).
- Attribution OSM correcte sur les 8 fonds de carte, dont Esri et CARTO.

### 6.3 Hygiène du dépôt

- **À supprimer : `.github/workflows/relay-drive-archive.yml`.** Ce workflow
  (154 lignes) est un vestige d'infrastructure : il télécharge un ZIP Google
  Drive, l'empaquette et **force-pousse un tag temporaire** avec
  `permissions: contents: write`, un `workflow_dispatch` libre et une
  temporisation de 25 min. Il se déclenche sur `arena/01a097bf-base-donnee`,
  une branche qui n'existe plus. Il n'a aucun lien avec le projet : **surface
  d'attaque inutile + bruit** dans l'onglet Actions.
- Le dépôt est écrasé en **un seul commit** : les 13 correctifs de septembre ne
  sont traçables que via `scripts/migrer_corrections.py` (bien écrit, idempotent,
  mais qui restera un exécutable à usage unique dans l'historique — à conserver
  comme trace, et à compléter d'un `CHANGELOG.md`).
- Aucun secret ni identifiant en dur dans le code ou les workflows (le seul jeton
  utilisé est le `GITHUB_TOKEN` prêté par Actions) ; la promesse « fiction
  intégrale » est tenue côté contenu : aucun portrait n'est référencé comme une
  photo, et les avertissements figurent à trois endroits.

---

## 7. La carte interactive

### 7.1 Ce qui est en place

Leaflet 1.9.4 vendorié, 8 fonds de carte (OSM, HOT, OSM-FR, OpenTopoMap,
CyclOSM, CARTO clair/sombre, Esri Satellite), marqueurs par catégorie
(quartiers, repères, voisinage, personnages, animaux, mes repères), filtres par
catégorie et par famille (84 familles cliquables avec tracé en pointillé pour
les foyers de 2+ membres), recherche de lieux via Nominatim (bornée au
Saguenay–Lac-Saint-Jean, `countrycodes=ca`), repères personnels persistés en
`localStorage`, export GeoJSON + CSV des repères, géolocalisation, échelle
métrique, responsive jusqu'au mobile (sidebar en tiroir).

### 7.2 Limites

| Limite | Impact | Correctif suggéré |
|---|---|---|
| **La recherche ne porte que sur Nominatim** : taper « Lavoie » ou « La Biche » ne retourne rien, alors qu'il y a 12 Lavoie et un surnom « La Biche » | Recherche inutilisable pour le cœur du projet | Ajouter une recherche locale sur `nom` / `surnom` / `famille` / `rôle` (et garder Nominatim en second plan) |
| **173 marqueurs sans clustering** | Au zoom arrière, La Baie devient une tache (18 points sur la rue Victoria) | `Leaflet.markerCluster` (vendorié) ou regroupement par rue/îlot |
| Pas de filtre par âge, secteur, type ou faction | La base est riche, la carte n'en expose qu'une partie | Réutiliser la mécanique des cases à cocher déjà en place |
| Popup construite par concaténation dans `innerHTML` | Autos-XSS possible via le nom d'un repère saisi (`prompt`) — risque **faible** (données locales, attaquant = utilisateur) mais gratuit à corriger | Échapper les valeurs (ou `textContent`) avant injection |
| Aucun lien vers le portrait `-web` (seule la vignette s'affiche) | On ne peut pas voir le portrait en grand depuis la carte | Rendre la vignette cliquable |
| Le bandeau d'avertissement est `display:none` sur grand écran | Le message « fiction / IA / adresses inventées » n'apparaît qu'en mobile | L'afficher en pied de sidebar plutôt que de le masquer |

---

## 8. Plan d'action priorisé

### P1 — À faire maintenant (≤ 1 h)

1. **Lever la contradiction Narration** (§ 6.1) : soit deux classeurs, soit
   correction de la documentation. *Décision éditoriale à trancher.*
2. **Supprimer `.github/workflows/relay-drive-archive.yml`** (§ 6.3).
3. **Corriger le README** : « 26 tests » → « 27 garde-fous ».

### P2 — Hygiène et robustesse (≈ demi-journée)

4. Sortir la source de vérité du XLSX vers un format texte versionnable
   (`data/personnages.csv` ou `.json`) ; le XLSX redevient un pur livrable.
5. Ajouter `ruff` (+ pré-commit) et un `CHANGELOG.md` ; découper
   `ecrire_xlsx()`.
6. Découpler le test de date figée de `SOURCE_DATE_EPOCH` ; ajouter une
   exécution CI programmée (hebdomadaire) pour détecter la casse de dépendances.
7. Échapper les valeurs injectées dans les popups ; afficher le bandeau
   d'avertissement sur desktop.

### P3 — Qualité des données (itérations éditoriales)

8. **Normaliser `Faction`** en 8-12 valeurs contrôlées (avec variantes de casse
   fusionnées) + test CI sur le vocabulaire autorisé ; documenter `Age apparent`.
9. **Normaliser `Famille`** : 40 libellés « singleton » sur 84 et 38 qualificatifs
   entre parenthèses (`Côté (ruelle)`, `Gagnon (motards)`) — convention utile
   mais non documentée. Passer à `famille` + `branche/bloc`, et documenter.
10. **Rajeunir la population** : viser ~15 % de moins de 25 ans (ajouter une
    cohorte aréna / école / cégep ATM / ruelle), sans toucher aux 3 mineurs déjà
    validés par les tests.
11. **Diversifier les rues** de Chicoutimi (4 → ~10) et de Jonquière (5 → ~8).
12. **Uniformiser les portraits** : fixer un ratio de génération (3:2 paysage) ou
    adapter le recadrage de la planche contact au ratio d'origine ; ajouter un
    test sur les dimensions.

### P4 — Carte (itérations produit)

13. Recherche locale par personnage (nom / surnom / famille / rôle) — **le plus
    gros gain d'usage**.
14. Clustering des marqueurs + filtres âge / secteur / type.
15. Portrait en grand au clic sur la vignette.

---

## 9. Conclusion

Le projet tient sa promesse : **173 personnages géolocalisés et illustrés, une
source unique, des livrables reproductibles et testés**. Sur le plan
ingénierie — reproductibilité bit-à-bit vérifiée en CI, conventions encodées
dans 27 tests, licences séparées, zéro dépendance CDN — il est au niveau d'un
projet maintenu par une équipe, et les correctifs de septembre montrent une vraie
capacité d'auto-critique (les tests citent chacun le défaut qu'ils verrouillent).

Ses fragilités sont **structurelles et éditoriales**, pas techniques : un classeur
binaire comme source de vérité, des vocabulaires libres là où il faudrait des
listes fermées, une pyramide des âges trop vieille, une concentration géographique
visible, et un workflow obsolète à jeter. Aucune de ces failles n'est coûteuse à
fermer — **le P1/P2 se traite en une demi-journée**, et le P3 par itérations
éditoriales, chacune verrouillée par un nouveau garde-fou, comme le projet sait
déjà le faire.

---

## Annexe A — Ce qui a été vérifié

| Vérification | Commande | Résultat |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests -v` | **27 tests · OK** (0,3 s) |
| Construction | `python3 construire_base.py` | 173 entrées, 173 lignes Narration, 2 cartes, 173 vignettes, planche 2510×3682 |
| Idempotence | 2 constructions + `sha256sum` de 526 livrables | **Empreintes identiques** |
| Livrables à jour | `git status --short` après reconstruction | **Arbre propre** |
| Unicité / complétude | analyse des 4 exports | 173 partout, 0 doublon de nom, 0 coordonnée dupliquée |
| Intégrité généalogique | résolution des liens `Parenté` | **85/88** (3 via le surnom « JP ») |
| Portraits | énumération `01`→`173` | aucun trou, 2 gabarits × 173, 0 archive orpheline |
| Hors ligne | `grep` CDN + présence `carte/vendor/leaflet/` | aucun CDN (test dédié vert) |
| CI | `gh run list` | dernière exécution sur `main` : **success** (20 s) |

**Non vérifiable dans cet environnement** (réseau sortant limité au miroir pip) :
la validation des coordonnées contre les géométries de rues OpenStreetMap
(Overpass/Nominatim inaccessibles). Un script optionnel
`scripts/verifier_geocodage.py` — qui interrogerait Overpass pour chaque rue et
contrôlerait l'écart au centroïde, avec l'assertion « < 500 m » — serait un
complément de CI utile.

## Annexe B — Statistiques détaillées

<details open>
<summary>Distribution des âges (humains, 172)</summary>

| Tranche | Effectif |
|---|---|
| 0-9 | 1 |
| 10-19 | 3 |
| 20-29 | 21 |
| 30-39 | 37 |
| 40-49 | 40 |
| 50-59 | 33 |
| 60-69 | 23 |
| 70-79 | 12 |
| 80-89 | 2 |

Moyenne 46,4 · médiane 45,0 · min 9 · max 86.
</details>

<details>
<summary>Principaux clans (84 familles, 40 ne comptant qu'un seul membre)</summary>

Santini 10 · Lavoie (JP) 6 · Lapointe (Marco) 6 · Tremblay (Gratien) 5 ·
Gagnon (motards) 5 · Benali 4 · Desrosiers-Simard 4 · Lacroix 4 · Bérubé 4 ·
Truchon 4 · Boucher 4 · Pelletier (bar) 4 · Fortin 4 …
6 familles s'étendent sur plusieurs arrondissements (Lavoie (JP) sur les trois).
</details>

<details>
<summary>Répartition géographique</summary>

La Baie 136 · Chicoutimi 27 · Jonquière 10.
42 rues distinctes (4,1 personnages/rue) : Rue Victoria 18 · Rue Racine Est 14 ·
Chemin Saint-Anicet 9 · Avenue du Port 9 · Rue Prince-Albert 8 · Rue Saint-Denis 8 ·
Boulevard Talbot 7 · Rue du Docteur-Desgagné 6. 7 adresses en « Lieu-dit : ».
</details>

<details>
<summary>Narration</summary>

173 lignes · 4 champs à 100 % · `Age apparent` : 139/173 = âge réel, 8 écarts > 5 ans ·
**128 valeurs de `Faction` distinctes** (Ruelle 8, Sous-sol 5, Ruelle d'en Face 5,
1er étage 4, Famille JP 4, Famille Marco 4, Bar du Coin 4…) · longueur moyenne
d'une réplique : 33 caractères · 1 doublon (`« T'as-tu mangé? »`).
</details>
