# Licences — données, portraits, code

Ce projet mélange trois types de créances aux **statuts juridiques distincts**.
Le fichier [`LICENSE`](LICENSE) (MIT) ne couvre que le **code** ; ce document
détaille les deux autres statuts.

| Élément | Fichiers concernés | Statut |
|---|---|---|
| **Code** | `construire_base.py`, `scripts/`, `tests/`, code JS des cartes, la bibliothèque Leaflet | **MIT** (voir `LICENSE`) ; Leaflet est en **BSD-2-Clause** (`carte/vendor/leaflet/LICENSE`) |
| **Données** | `base_personnages_fictifs.xlsx`, `.csv`, `.json`, `.geojson`, données injectées dans les cartes (noms de rues, toponymes, géométries, coordonnées dérivées) | **ODbL 1.0** — base dérivée d'OpenStreetMap |
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
- Les personnes fictives mineures (3 personnages de 9, 13 et 16 ans) sont
  traitées comme tous les autres personnages : illustrations non réalistes de
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
