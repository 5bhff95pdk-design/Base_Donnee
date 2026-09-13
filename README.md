# Base de données de personnages fictifs — La Baie (Saguenay)

Projet personnel de **fiction** : **173 personnages géolocalisés et illustrés**
dans la ville de Saguenay (arrondissements de La Baie, Chicoutimi et
Jonquière, Québec), dont **172 humains et 1 animal**. Les personnages, noms,
situations et numéros civiques sont **entièrement inventés** ; les rues et
les toponymes sont réels (OpenStreetMap).

🗺️ **Carte interactive** : ouvrir [`carte-la-baie-saguenay.html`](carte-la-baie-saguenay.html)
(ou [`carte/index.html`](carte/index.html)).
📇 **Planche contact des 173 portraits** : [`portraits/planche-contact-generale.webp`](portraits/planche-contact-generale.webp).

<a href="portraits/planche-contact-generale.webp"><img src="portraits/planche-contact-generale.webp" alt="Planche contact des portraits" width="480"></a>

> ⚠️ **Avertissement** : numéros civiques fictifs (ne pas utiliser comme
> adresses postales), coordonnées à l'échelle du quartier (± 400 m),
> **portraits générés par IA** — aucune personne réelle photographiée.

---

## Contenu du dépôt

| Fichier / dossier | Description |
|---|---|
| `base_personnages_fictifs.xlsx` | **Base maître** : feuille *Personnages* (**173 lignes × 15 colonnes**), *Lisez-moi* (dictionnaire des données et conventions), *Narration* (faction / lien / réplique / arc, **173 lignes, couverture 100 %** — non exportée publiquement). |
| `base_personnages_fictifs.csv` | Export tableur, séparateur `;`, UTF-8 BOM (accents OK dans Excel FR). Importable Notion / Airtable / SQL. |
| `base_personnages_fictifs.json` | Export code / API, clés minuscules sans accent. |
| `base_personnages_fictifs.geojson` | Points WGS84 pour QGIS, geojson.io, uMap, Mapbox. |
| `carte-la-baie-saguenay.html`, `carte/index.html` | Carte interactive Leaflet (données réinjectées par le script). |
| `carte/vendor/leaflet/` | Bibliothèque **Leaflet 1.9.4 en copie locale (BSD-2)** : le code de la carte ne dépend d'aucun CDN. |
| `carte/portraits/` | Vignettes 400 px servies par la carte (synchronisées par le script). |
| `portraits/` | Deux gabarits WebP par personnage : `-web.webp` (web) et `-vignette.webp` (400 px, carte et planche), plus la planche contact. |
| `construire_base.py` | Générateur **idempotent et reproductible** de tous les livrables. |
| `scripts/migrer_corrections.py` | Journal des corrections de la révision du 2026-09-12 (coquilles, conventions, 3 mineurs ajoutés, narration complétée). |
| `scripts/retirer_archives_git.sh` | Purge optionnelle de l'ancien gabarit « archive » dans l'historique Git. |
| `tests/test_base.py` | Garde-fous (26 tests) couvrant toutes les conventions, lancés en CI. |
| `.github/workflows/validation.yml` | CI : régénération + contrôle de reproductibilité (`git diff` vide) + tests. |
| `LICENSE` / `LICENSE-DONNEES.md` | Trois statuts distincts : code MIT, données ODbL, portraits IA en CC BY 4.0. |

## Colonnes (15)

`Nom` · `Surnom` · `Type` (Humain/Animal) · `Age` · `Rôle` · `Secteur` ·
`Adresse` · `Latitude` · `Longitude` · `Apparence` · `Vêtements` ·
`Tic / Objet` · `Portrait` · `Famille` · `Parenté` — le dictionnaire détaillé
est dans la feuille *Lisez-moi*.

Principales conventions :

- **Surnom** : une cellule vide signifie « pas de surnom » (personnage « rangé
  »), ce n'est pas un oubli. Le surnom ne s'écrit **jamais** dans le `Nom`
  (pas de guillemets « » autour du Nom).
- **Rôle** : métier autonome, sans référence à un autre personnage ni à une
  faction / un clan (le clan va dans `Famille` ; la faction, dans *Narration*).
- **Adresse** : `« Numéro, Rue »` (numéro inventé, rue réelle OSM) ; pour les
  lieux non adressables (plein air, sentier, base militaire) : `Lieu-dit : …`.
- **Vêtements** : `s.o.` = sans objet (ex. un animal), vide = inconnu.
- **Âge** : trois personnages sont mineurs (9, 13 et 16 ans) ; le seul
  personnage de moins de 18 ans qui ne soit pas humain reste le chat
  Pisse-Feu (7 ans en âge animal).

## Démarrage rapide

```bash
# 1. (optionnel) environnement isolé
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 2. ouvrir la carte (double-clic, ou)
python3 -m http.server 8000
#   → http://localhost:8000/carte-la-baie-saguenay.html

# 3. après une modification du classeur maître :
python3 construire_base.py
#    régénère xlsx / csv / json / geojson, réinjecte les données dans les deux
#    cartes, synchronise les vignettes et reconstruit la planche contact.

# 4. contrôler la base :
python3 -m unittest discover -s tests -v
```

### Utilisation hors ligne

Le **code** de la carte est vendorié (`carte/vendor/leaflet/`) : aucun accès à
un CDN n'est nécessaire et la carte s'ouvre sans réseau. Seuls les **fonds de
tuiles** et la recherche Nominatim restent des services en ligne (voir les
licences dans [`LICENSE-DONNEES.md`](LICENSE-DONNEES.md), § 4) ; pour un usage
100 % hors ligne, brancher des tuiles locales (MBTiles / PMTiles).

## Reproductibilité et qualité

- `construire_base.py` n'écrit **aucune donnée volatile** : la date « Généré
  le » est figée au 2026-09-11 (surcharge possible via la variable
  `SOURCE_DATE_EPOCH`) et les métadonnées du classeur sont normalisées.
  Relancer le script deux fois sur une même machine produit des fichiers
  **octet pour octet identiques** (vérifié par la CI en comparant deux
  constructions successives) ; les livrables données/code (xlsx, csv, json,
  geojson, html) sont en outre strictement identiques d'une machine à l'autre.
  Seule la **planche contact WebP** dépend du codec `libwebp` natif : son
  idempotence est garantie sur un même runner, sans comparaison binaire
  inter-environnements (la fonte utilisée est, elle, vendoriée dans
  `assets/fonts/`).
- Les tests vérifient notamment : effectifs et cohérence des 4 exports,
  unicité des noms, adresses avec numéro ou `Lieu-dit :`, rôles sans clan,
  coordonnées dans le bon arrondissement, mineurs présents, couverture
  Narration à 100 %, portraits et planche contact présents, absence de
  gabarit « archive », Leaflet sans CDN, et les trois licences distinguées.

## Provenance et licences

- **Rues et géocodage** : © contributeurs OpenStreetMap via Overpass et
  Nominatim, **ODbL**.
- **Portraits** : images **générées par IA**, personnages fictifs, **CC BY 4.0**.
- **Code** : **MIT** ; carte basée sur **Leaflet 1.9.4 (BSD-2)**.

Le détail des obligations (paternité, share-alike, étiquetage IA, conditions
des tuiles) est dans **[`LICENSE-DONNEES.md`](LICENSE-DONNEES.md)**.
