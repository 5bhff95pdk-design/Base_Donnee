# Licences — données, portraits, code

Ce projet mélange trois types de contenus aux **statuts juridiques distincts**.
Le fichier [`LICENSE`](LICENSE) (MIT) ne couvre que le **code** ; ce document
détaille les deux autres statuts.

| Élément | Fichiers concernés | Statut |
|---|---|---|
| **Code** | `construire_base.py`, `relations.py`, `scripts/`, `tests/`, code JS des cartes, la bibliothèque Leaflet | **MIT** (voir `LICENSE`) ; Leaflet est en **BSD-2-Clause** (`carte/vendor/leaflet/LICENSE`) |
| **Données** | `data/personnages.csv`, `data/narration.csv`, `data/relations.csv`, `relations_personnages.json`, `base_personnages_fictifs.xlsx`, `.csv`, `.json`, `.geojson`, données injectées dans les cartes (noms de rues, toponymes, géométries, coordonnées dérivées) | **ODbL 1.0** — base dérivée d'OpenStreetMap |
| **Portraits** | `portraits/*-web.webp`, `portraits/*-vignette.webp`, `planche-contact-generale.webp`, vignettes de `carte/portraits/` | Images **générées par IA**, personnages fictifs, mises à disposition en **CC BY 4.0** |

---

## 1. Données — ODbL 1.0 (Open Database License)

Les **noms de rues, toponymes et géométries** sont extraits d'**OpenStreetMap**
via les API **Overpass** (rues) et **Nominatim** (géocodage) :

- © les contributeurs d'OpenStreetMap — https://www.openstreetmap.org/copyright
- Les bases de données dérivées de données OSM sont publiées sous
  **Open Database License (ODbL) 1.0** :
  https://opendatacommons.org/licenses/odbl/1-0/
- Résumé des obligations en français : https://vvlibri.org/fr/licence/odbl/1-0

Les **noms de personnages, âges, rôles, parentés, factions, répliques,
numéros civiques et portraits** sont entièrement **fictifs** ; la part
fictive est elle aussi versée sous ODbL par simplicité de réutilisation de la
base composite. Les coordonnées sont approximatives (centroïde de rue réel +
décalage déterministe de ± 400 m) et les numéros civiques inventés : **rien
ici ne doit être utilisé comme adresse postale réelle**.

**Personnes, entreprises et organisations.** Les personnages, surnoms,
situations et adresses sont imaginaires : **toute ressemblance avec des
personnes réelles serait fortuite**. Des **noms d'entreprises, de marques et
d'établissements réels** (transport, commerce, industrie, enseignement,
médias) apparaissent comme contexte géographique et social du Saguenay. Ils
sont cités à titre descriptif : **aucune affiliation, aucun partenariat,
aucun mandat et aucune mise en cause** ne sont suggérés, et ces mentions ne
constituent pas une source d'information sur ces organisations.

### Mention de paternité minimale à reprendre en cas de réutilisation

> Base de personnages fictifs — La Baie (Saguenay), © Luc, sous ODbL.
> Contient des données © les contributeurs d'OpenStreetMap, sous ODbL.
> Portraits : images générées par IA, sous CC BY 4.0.

En vertu du **partage à l'identique (share-alike)** de l'ODbL, toute base
dérivée doit rester sous ODbL (le code qui *lit* la base n'est pas soumis à
cette obligation).

---

## 2. Portraits — images générées par IA, CC BY 4.0

Tous les portraits ont été **générés par intelligence artificielle**. Ce ne
sont **pas des photographies de personnes réelles** : toute ressemblance avec
une personne existante serait fortuite.

- Les images sont mises à disposition sous
  **Creative Commons Attribution 4.0 International (CC BY 4.0)** :
  https://creativecommons.org/licenses/by/4.0/deed.fr
- Mention recommandée : *« Portrait généré par IA — projet La Baie, CC BY 4.0 »*.
- Pour un usage public au Canada, vérifier les obligations d'**étiquetage des
  contenus générés par IA** prévues par la réglementation en vigueur.

### Étiquette IA intégrée aux fichiers (XMP)

L'étiquetage ne dépend pas d'un texte accompagnateur : **il est écrit dans
chaque image**. Les 426 portraits (`-web.webp` et `-vignette.webp`), leurs copies
servies par la carte et la planche contact portent un paquet **XMP** contenant :

| Champ | Valeur |
|---|---|
| `Iptc4xmpExt:DigitalSourceType` | `trainedAlgorithmicMedia` (valeur normalisée IPTC : média produit par un système entraîné) |
| `dc:title` | nom du personnage et ID, p. ex. « Chantal Lavoie (P008) — personnage fictif » |
| `dc:description` | rappel que le portrait est généré par IA, qu'aucune personne réelle n'a été photographiée et que toute ressemblance serait fortuite |
| `dc:rights` / `xmpRights:WebStatement` | CC BY 4.0 et lien de la licence |
| `dc:creator` | attribution « Projet La Baie (Saguenay) » |

Une vignette extraite du dépôt (copiée dans un document, un diaporama ou un
réseau social) garde donc sa mention d'origine. L'insertion se fait au niveau du
conteneur **RIFF/WebP** (`scripts/etiqueter_portraits_ia.py`) : la donnée image
n'est jamais réencodée, et un test vérifie qu'un second passage ne change rien.
Les propriétés du classeur (`base_personnages_fictifs.xlsx`) portent la même
mention, pour le cas où seul le tableur circule.
- Les personnes fictives mineures (9 personnages humains de 9 à 17 ans) sont
  traitées comme tous les autres personnages : illustrations générées par IA de
  personnages de fiction, sans aucune donnée personnelle réelle.

L'ancien gabarit « archive » (`portraits/<nn>-<slug>.webp` sans suffixe,
~140 Ko par image, ≈ 24 Mo au total) n'était référencé par aucun livrable :
il n'est plus versionné (voir `.gitignore` et `scripts/retirer_archives_git.sh`).

---

## 3. Code — MIT

Voir le fichier [`LICENSE`](LICENSE). Le code intègre **Leaflet 1.9.4** en
copie locale (`carte/vendor/leaflet/`) sous licence **BSD 2-Clause**, ©
Volodymyr Agafonkin et contributeurs.

La planche contact est composée avec la police **DejaVu Sans**, vendoriée dans
`assets/fonts/` sous licence **Bitstream Vera** (les modifications DejaVu sont
dans le domaine public) — voir `assets/fonts/LICENSE.txt`.

## 4. Fonds de carte et services en ligne

Le code de la carte fonctionne **hors ligne** (Leaflet est vendorié), mais les
**fonds de tuiles** restent servis en ligne, chacun selon ses propres
conditions :

| Fond | Conditions |
|---|---|
| OpenStreetMap standard, OSM Humanitaire (HOT), OSM France, CyclOSM | © contributeurs OpenStreetMap, **ODbL** |
| OpenTopoMap | **CC BY-SA** (© OpenTopoMap, données SRTM/OSM) |
| CARTO Positron / Dark Matter | gratuit avec **attribution** CARTO |
| Esri World Imagery | imagerie © Esri (Maxar, Earthstar Geographics), usage gratuit avec attribution |
| Recherche d'adresses | **Nominatim**, données **ODbL**, politique d'usage nominatim.openstreetmap.org |

Pour un usage **100 % hors ligne**, télécharger des tuiles MBTiles/PMTiles
libres (OSM sous ODbL) et brancher un lecteur local dans la carte.
