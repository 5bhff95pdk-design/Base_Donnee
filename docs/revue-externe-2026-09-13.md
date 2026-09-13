# Revue externe — 2026-09-13

**Statut : avis externe ponctuel, non canonique, hors de la chaîne de génération.**
Ce document ne modifie aucune source, n'est pas lu par `construire_base.py` et
n'entre dans aucun livrable. Il consigne une lecture critique du dépôt
(personnages, narration, relations, carte, tests, licences) et des propositions
d'amélioration. L'auteur peut le conserver, le résumer ou le supprimer.
La section [5 bis](#5-bis-suivi--corrections-appliquées-le-2026-09-13) consigne
les corrections appliquées le jour même et ce qui reste ouvert.

- **Périmètre lu** : [`README`](../README.md), [`CHANGELOG`](../CHANGELOG.md),
  [`analyse actuelle`](analyse-projet.md) et [archive](historique/analyse-173-personnages.md),
  [`géographie`](geographie-provenance.md), [`relations`](relations-personnages.md),
  [`atelier S1`](atelier-saison-1.md), [`13 fiches`](propositions-personnages-centraux.md),
  [`LICENSE-DONNEES`](../LICENSE-DONNEES.md), [`data/personnages.csv`](../data/personnages.csv),
  [`data/narration.csv`](../data/narration.csv), [`data/relations.csv`](../data/relations.csv),
  [`carte/index.html`](../carte/index.html), [`atelier/index.html`](../atelier/index.html),
  [`construire_base.py`](../construire_base.py), [`relations.py`](../relations.py),
  [`tests/test_base.py`](../tests/test_base.py), workflow CI et tests navigateur.
- **Méthode** : lecture du code, exécution reproductible de la chaîne complète,
  mesures calculées sur les sources, contrôle visuel du livrable image.

---

## 1. Vérifications exécutées (et résultats)

| Contrôle | Commande | Résultat observé |
|---|---|---|
| Construction complète | `python3 construire_base.py` | Terminée en ~5 s : classeur 4 feuilles, 4 exports, 2 cartes, atelier, 213 vignettes, planche 2510 × 4498 px |
| Reproductibilité | `git status` après construction | **Aucun diff** : les livrables commités sont exactement ce que produit la source actuelle |
| Garde-fous Python | `python -m unittest discover -s tests` | **62 tests, OK** |
| Lint | `ruff check .` | **All checks passed** |
| Régressions JS | `node --test tests/carte.test.cjs` | **6 tests, 6 passés** |
| CI distante | `gh run list` | Dernier run `main` : **success** (46 s) ; les 8 PR de la journée sont fusionnées |

Deux constructions successives ont produit des octets identiques : l'idempotence
annoncée est réelle, y compris pour le `.xlsx` (métadonnées figées) et la planche
contact. C'est la qualité la plus rare de ce dépôt : **la documentation ne ment
pas**. Les chiffres du README, de `docs/analyse-projet.md` et du classeur sont
vérifiés par des tests qui échouent réellement quand la réalité change.

**Non vérifiable ici** : les 14 tests Playwright n'ont pas pu être exécutés
(installation de Chromium impossible dans cet environnement sans accès réseau) ;
l'API Nominatim et les tuiles sont également inaccessibles. Les points
correspondants restent donc « déclarés, non constatés ».

---

## 2. Ce qui est solide

1. **Séparation source / livrables.** `data/personnages.csv` est la source, tout
   le reste est régénérable et vérifié en CI par comparaison d'octets. C'est une
   architecture de projet de données, pas de « dossier de fichiers ».
2. **Identifiants permanents et registre des retraits.** Jointure de la narration
   par `ID`, `data/ids-retires.txt`, refus explicite des IDs dupliqués, invalides
   ou réutilisés : la dette de renommage est traitée avant d'exister.
3. **Vocabulaire contrôlé des factions** (17 valeurs) avec conservation de la
   nuance d'origine : on gagne un champ filtrable sans perdre l'information.
4. **Relations sourcées.** Chaque lien porte son type, ses deux extrémités et la
   preuve textuelle exacte (`Extrait` comparé au champ `Parenté`), avec refus des
   cycles, des auto-relations et des preuves périmées. Le sens est éditorial, il
   n'est pas deviné par le programme.
5. **Copie de racine dérivée.** `carte-la-baie-saguenay.html` est un dérivé
   mécanique de `carte/index.html`, contrôlé par test : plus de double vérité.
6. **Échappement systématique** avant toute injection dans `innerHTML` (données,
   repères utilisateur, réponses Nominatim), et remplacement par fonction pour
   éviter l'interprétation des séquences d'échappement à l'injection.
7. **Robustesse du stockage local** : JSON corrompu ignoré, quotas traités,
   modification annulée si l'écriture échoue.
8. **Écriture réellement écrite.** 213 arcs et 213 répliques **toutes
   distinctes** ; les citations tiennent en 20–57 caractères et sonnent juste
   (« Un gardien, c'est un mur avec des opinions. », « Bienvenue au Néon :
   lumière pis oubli. »). Le vocabulaire matériel est d'époque et de lieu
   (Pontiac Grand Prix, sacoche aux trois écrans cassés, conserves de 1998,
   clope à la fenêtre) : c'est ce qui donne au monde sa densité.
9. **L'atelier de scènes** est la bonne réponse au vrai problème du projet. Les
   5 moteurs de tension, la « pression » choisie de préférence **parmi les
   personnages reliés**, le témoin imposé, les questions de jeu et la consigne de
   sortie forment un dispositif d'écriture crédible — et la règle affichée
   (« une absence de lien structuré n'est pas une absence de relation ») est
   exactement la bonne mise en garde.
10. **Honnêteté documentaire.** Les limites (pas de Firefox/Safari, mobile ≠
    tactile, tuiles non testées, extraction partielle, propositions non
    canoniques) sont écrites dans le dépôt, avant d'être demandées. L'archive
    historique est isolée et signalée.

---

## 3. Faiblesses et risques, par ordre d'importance

### 3.1 La couverture des relations est en dessous de ce que la base sait déjà

Mesures : **114 liens, 141 personnages reliés, 72 sans aucun lien** (dont 36
« Célibataire » sans mention). Composition : `parent_de` 57 (50 %), `conjoint_de`
19, `fratrie` 15, `collegue_de` 9, `superieur_de` 7, `colocataire_de` 4, puis
`ex_conjoint_de`, `enseignant_de`, `locataire_de` (1 chacun). Le graphe est donc
**familial et vertical** ; le versant « monde du travail, voisinage, dette,
influence » — celui qui porte l'intrigue — reste à structurer.

Point précis : **28 personnages déclarent en prose un lien de famille nommé
(`Parenté`) sans figurer dans `data/relations.csv`**, alors que l'autre extrémité
existe bien dans la base et que le champ `Extrait` est déjà là. Exemples
vérifiés : P032 « Père d'Isabelle » (P049), P092 « Mère de Marc-André Simard »
(P043), P130 « Sœur de Julie Martel » (P096), P188 « Tante de Steve et Chantal
Gauthier » (P118/P135), P180 « Neveu d'Amina Traoré » (P083), P208 « Neveu
d'Émile Brassard » (P076). La règle du projet permet d'ajouter ces liens **sans
inventer quoi que ce soit** (`Preuve_ID` = l'une des deux extrémités). En comptant
large, une vingtaine est immédiatement extractible ; une dizaine demande une
désambiguïsation d'homonymes de prénom (« Lucien » = P022 Lacroix ou P210 Gagné ;
« Steve » = P018 ou P118 ; « Camille/Samuel/Julien » = deux foyers Desgagné).

Effet secondaire mesurable : la table actuelle est **incohérente avec elle-même**
sur des cas identiques. P197 « Fille de Denis et Johanne » produit deux liens
`parent_de` vers P195/P196, mais P049 « Fille de Gilles Bergeron » n'en produit
aucun. Ce n'est pas une limite de périmètre assumée, c'est une règle
d'extraction appliquée de façon variable.

### 3.2 La planche contact abîme 12 portraits sur 213

La planche recadre chaque case au ratio 3:2 en « couverture » (centrage
destructif). Or 12 vignettes sources sont au format portrait : 11 en 400 × 600 et
1 en 400 × 499. Vérification visuelle sur le livrable généré : **5 de ces cases
perdent franchement le visage** (Ahmed Benali, Anik Desrosiers, Dave Cloutier,
Sam Aubin, Justin Chen) et montrent un buste coupé — le lecteur de la planche ne
peut plus identifier la personne, ce qui est la seule fonction de cette planche.

`docs/analyse-projet.md` note « les ratios des portraits ne sont pas tous
uniformes » : c'est exact, mais ce n'est pas le ratio qui pose problème, c'est le
**recadrage destructif** appliqué par `planche_contact()`. Correction d'environ
dix lignes : pour les sources dont le ratio est inférieur à 1,4 (portrait),
afficher l'image entière en `contain` sur un fond sombre, plutôt qu'un
`crop` centré. Aucune donnée n'est à retoucher.

### 3.3 Portraits photoréalistes de mineurs dans un monde de dettes, de violence et de honte

La source est propre — aucune scène explicite : sur l'ensemble de la narration,
on relève 5 occurrences de « jeune », 2 de « mort », 2 de « bagarre », 1 de
« gaz », 1 de « mineur » et rien de sexuel ni de graphique. La sensibilité est
ailleurs : **9 mineurs (9 à 17 ans), décrits avec leur école, leur sport et leur
adresse fictive**, chacun doté d'un arc inséré dans la trame de la dette et de
l'intimidation (Nour, 13 ans, « Tient le vrai registre des dettes » ; Léo, 9 ans,
« Voit Dave se faire pognner »). L'atelier va plus loin : `choisirAutres()` tire
la « pression » au hasard parmi 212 personnages et **ne filtre pas les mineurs** —
rien n'empêche une scène « Le prix du service » de placer un enfant de 9 ans en
position de créancier ou de menace. Le `docs/atelier-saison-1.md` énonce
pourtant la bonne règle (« Nour et les autres mineurs restent des personnes à
protéger, pas des outils narratifs ») : elle est écrite, mais pas outillée.

Deux recommandations, non exclusives :
- **règle d'atelier outillée** : les mineurs ne peuvent pas être la « pression »
  des moteurs « dette » et « limite » ; ils restent point de vue ou témoin, avec
  un marqueur visible dans l'interface ;
- **règle d'image** : réserver aux personnages mineurs un style non photoréaliste
  (ou une vignette traitée : désaturation/illustration), ou éviter les portraits
  d'enfants en une de la planche contact et dans toute promotion. C'est le seul
  point du projet où une diffusion large pourrait coûter cher, indépendamment de
  la loi.

### 3.4 Adresses fictives, rues réelles, marques réelles : la couche de risque est là

Le dispositif actuel est plus prudent qu'il n'y paraît : numéros inventés,
coordonnées décalées de ± 400 m, bandeau « fiction / IA » présent sur la carte et
sur mobile, avertissements dans le README et le classeur. Trois points à
renforcer :

1. **La formule de non-ressemblance manque pour les noms et les organisations.**
   `LICENSE-DONNEES.md` la contient pour les portraits (« toute ressemblance…
   fortuite »), pas pour les personnes, les commerces ou les entreprises. Or la
   base cite des organisations réelles dans des rôles et des secteurs nommés
   (Rio Tinto/Arvida, Postes Canada, Tim Hortons, Cégep de Jonquière, UQAC,
   Le Quotidien). Une phrase du type *« Toute ressemblance avec des personnes,
   des entreprises ou des organisations réelles serait fortuite ; les marques
   citées le sont à titre de contexte »* coûte deux minutes et couvre le risque
   le moins bien couvert aujourd'hui.
2. **Les popups affichent six décimales** (`48.345235, -70.879521`), soit une
   précision au mètre, juste sous une adresse fictive. Quatre décimales
   (~11 m) suffisent pour l'usage et disent mieux ce que la donnée est.
3. **Le bandeau mobile existe, mais pas dans le popup.** Un lecteur qui n'ouvre
   la carte que par un marqueur partagé ne voit ni le bandeau ni le README. Une
   ligne « Adresse fictive — personnage de fiction » dans la fiche du popup
   ferme la boucle.

### 3.5 Divers, plus mineurs

- **Le dépôt pèse 65 Mo** (dont 29 Mo de `portraits/` et 28 Mo de `.git`) pour
  un projet individuel. Les masters `-web.webp` (1024–1536 px, 101 Ko en moyenne)
  sont justifiés ; la **planche contact, elle, est une image dérivée de 2,4 Mo**
  qui est régénérable, exclue du contrôle CI « livrables à jour » et reproductible
  seulement sur un même runner. La sortir du dépôt (artefact de CI ou livrable
  hors Git) allégerait sans rien perdre.
- **`Sous-sol` est une faction à un seul membre** alors que 17 valeurs sont
  canoniques : soit c'est un poste narratif volontaire (l'atelier du sous-sol),
  soit c'est un reste de normalisation. À trancher explicitement.
- **Deux factions « fourre-tout »** — `Neutre` (7) et `Propre` (4) — décrivent
  moins un milieu qu'une position morale. Utile pour filtrer, faible pour écrire.
- **`Branche` est parfois le prénom du personnage** (Alex, Chantal, Chloé,
  Gratien, Johanne, Marco, Michel) : la paire Famille + Branche cesse alors de
  désigner un foyer pour désigner une personne, ce que la convention du README
  ne prévoit pas.
- **Imagerie datée** : les portraits « web » sont bien dimensionnés, mais un
  encodage AVIF ou une qualité WebP plus basse (moyenne 101 Ko pour 1200 px)
  diviserait le poids par deux sans perte visible.
- **Métadonnées d'IA** : l'étiquetage « généré par IA » vit dans le README, la
  licence et l'interface, mais **pas dans les fichiers d'image** (pas de bloc
  XMP/IPTC `digitalSourceType = trainedAlgorithmicMedia`). Exigé par plusieurs
  plateformes, absent ici.
- **Le `.xlsx` ne porte aucune mention de fiction** dans ses propriétés
  (auteur « Luc », titre). Le classeur va pourtant circuler plus loin que le
  dépôt : une ligne `description` dans `docProps/core.xml` (déjà maîtrisé par
  `figer_xlsx`) suffirait.

---

## 4. Propositions, par rapport valeur/effort

| # | Action | Effort | Effet |
|---|---|---|---|
| 1 | Recadrage `contain` des 12 vignettes portrait dans la planche | ~10 lignes | Supprime un défaut visible sur le seul livrable « catalogue » |
| 2 | Étendre `data/relations.csv` aux ~28 liens déjà écrits dans `Parenté` | 1 h éditoriale | 141 → ~169 personnages reliés ; corrige l'incohérence d'extraction |
| 3 | Garde-fou « mineurs » dans l'atelier (jamais « pression » sur dette/limite) | ~15 lignes | Aligne l'outil sur la règle déjà écrite dans `docs/atelier-saison-1.md` |
| 4 | Phrase de non-ressemblance (personnes, entreprises) + mention « adresse fictive » dans le popup + coordonnées à 4 décimales | ~30 min | Ferme les trois risques juridiques les moins couverts |
| 5 | Métadonnées d'IA dans les WebP et une description dans le classeur | ~1 h | Étiquetage automatique, portable hors du dépôt |
| 6 | `relations.csv` : élargir aux liens non familiaux (voisinage, dette, emploi) issus des champs `Lien Spot` / `Arc S1`, en conservant la preuve | plus lourd | Donne à l'atelier une matière qui ne soit pas seulement généalogique |
| 7 | Décider du sort de `Sous-sol`, `Neutre`, `Propre` et du sens de `Branche` | décision, pas code | Vocabulaire stable avant la saison 1 |

**Ce que je ne recommande pas** : ajouter des personnages, migrer la pile
technique, ajouter une base de données ou un serveur d'API. Le dépôt n'a aucun
problème d'infrastructure ; il a un problème de distribution narrative.

---

## 5. Opinion

Techniquement, c'est un projet **au-dessus du niveau habituel d'un projet
personnel** : source unique diffable, génération idempotente vérifiée par
comparaison d'octets, 62 garde-fous qui contrôlent la documentation autant que
les données, CI verte, absence de dépendance CDN, avertissements de fiction
présents dans tous les livrables. La conservation des preuves, des IDs stables,
du registre des retraits et de l'archive historique montre une discipline que
beaucoup de projets d'équipe n'ont pas. La carte, l'atelier et la planche contact
sont trois sorties distinctes pour une même source, et le périmètre
« narration publique dans le dépôt, absente des exports géographiques » est
correctement arbitré et testé.

Mon avis tient en deux phrases. **La rigueur n'est pas ce qui manque : c'est ce
qui est excédentaire.** Le projet a construit une chaîne d'archivage et de
vérification de niveau professionnel pour un corpus qui n'a pas encore produit
une seule scène. Le risque principal n'est pas la dette technique — il n'y en a
presque pas — c'est la **dispersion** : 213 personnages, 64 familles, 17
factions, 114 liens, 13 fiches proposées, et zéro épisode. Chaque nouvelle
campagne d'enrichissement augmente le coût d'entrée dans le récit.

Ma recommandation principale est donc un **gel des ajouts de contenu** jusqu'à
ce qu'un épisode existe : aucune fiche P214+, aucune faction nouvelle, aucun
personnage « central » de plus. Les trois points de vue retenus
(JP / Chloé / Kevin) et le test de scène en trois versions décrit dans
[`atelier-saison-1.md`](atelier-saison-1.md) sont la bonne méthode ; il faut
juste les exécuter. Le seul indicateur qui compte pour les 30 prochains jours
n'est pas « 220 personnages » ni « 150 relations », c'est **« une scène écrite
et jouée par quelqu'un d'autre que l'auteur »**.

Deuxième avis, plus tranchant : certaines propositions de `docs/propositions-personnages-centraux.md`
(désir / enjeu / contradiction / décision) sont déjà de la matière de scénario et
suffisent — il ne faut pas les étendre à 213 fiches. L'élargissement de cette
méthode à tout le corpus serait le prochain piège : il produirait une
documentation riche sur des personnages que personne ne verra jamais agir.

Enfin, sur le plan éditorial, la vraie force de ce dépôt est la **matière
locale** : la Pyramide des Ha! Ha!, le chemin Saint-Anicet, l'aluminerie, le
hockey mineur, le joual des répliques. Ce matériau-là n'a pas besoin de plus de
personnages pour fonctionner ; il a besoin d'une première scène ancrée dans une
adresse, un objet et une dette. Le reste du dépôt est prêt depuis longtemps.

---

## 5 bis. Suivi — corrections appliquées le 2026-09-13

| Point de la revue | État | Ce qui a changé |
|---|---|---|
| 3.2 Planche contact | **Corrigé** | `ajuster_vignette_planche()` : les 12 vignettes verticales sont affichées entières (fond sombre), les paysage gardent le recadrage couverture. Garde-fou Python. |
| 3.1 Relations incomplètes | **Corrigé en partie** | 41 liens déclarés en prose ajoutés après résolution des prénoms ambigus : 155 relations, 176 personnages reliés. Trois types documentés (`oncle_de`, `grand_parent_de`, `parrain_de`). Reste : les liens d’intrigue (dettes, voisinage, influence) décrits hors de `Parenté`. |
| 3.3 Mineurs | **Corrigé** | `MODES_SANS_MINEUR=['dette','limite']` et `pressionAutorisee()` dans l’atelier, repère « mineur, à protéger » dans les faits de scène, mention dans la légende. 4 tests JS dédiés. |
| 3.4 Mentions de fiction | **Corrigé** | Clause de non-ressemblance (personnes, entreprises, organisations) dans `LICENSE-DONNEES.md` et le README ; « Personnage de fiction — adresse inventée » dans chaque fiche ; coordonnées affichées à 4 décimales. Garde-fou Python. |
| 3.5 Métadonnées d’IA dans les images | **Ouvert** | Aucun bloc XMP/IPTC `trainedAlgorithmicMedia` dans les WebP. |
| 3.5 Poids du dépôt | **Ouvert** | La planche contact (2,4 Mo dérivés) reste versionnée. |
| 3.5 Factions et `Branche` | **Ouvert** | `Sous-sol`, `Neutre`, `Propre` et les branches auto-référentielles attendent une décision d’auteur. |
| 5. Gel des ajouts et premier épisode | **Ouvert** | Recommandation éditoriale, hors du périmètre des corrections techniques. |

## 6. Limites de cette revue

- Les tests navigateur, les tuiles, Nominatim et la cohérence des rues avec OSM
  n'ont pas pu être rejoués sans réseau dans cet environnement : les points
  correspondants sont évalués par lecture du code, pas constatés.
- Les mesures démographiques (part de personnages féminins ≈ 68/213, soit 32 %)
  reposent sur une reconnaissance des prénoms, donc approximatives.
- La conformité juridique (ODbL, CC BY 4.0, étiquetage IA, tuiles) n'est pas un
  avis juridique ; les remarques portent sur le risque et la lisibilité.
- Un clone superficiel ne permet pas de vérifier l'état de l'historique distant
  (purge des anciens gabarits « archive » annoncée par
  [`scripts/retirer_archives_git.sh`](../scripts/retirer_archives_git.sh)).
