BASE DE DONNÉES DE PERSONNAGES FICTIFS — LA BAIE (SAGUENAY)
===========================================================
Projet personnel de fiction. 140 personnages géolocalisés et photographiés.
Généré le 2026-09-11.


CONTENU
-------
base_personnages_fictifs.xlsx   Base maître. Feuille « Personnages » (160 lignes x 15
                                colonnes) + « Lisez-moi » + « Narration ».
base_personnages_fictifs.csv    Export tableur. Séparateur « ; », UTF-8 BOM (accents OK
                                dans Excel FR). Import Notion / Airtable / SQL.
base_personnages_fictifs.json   Export code / API. Clés minuscules sans accent.
base_personnages_fictifs.geojson  Points WGS84. Ouvrable dans QGIS, geojson.io, uMap, Mapbox.
carte-la-baie-saguenay.html     Carte interactive Leaflet. À ouvrir dans un navigateur.
construire_base.py              Script idempotent : relit le .xlsx et régénère csv / json /
                                geojson, réinjecte les données dans la carte et synchronise
                                les vignettes vers carte/portraits/.
portraits/                      3 gabarits WebP par personnage + planche-contact-generale.webp
                                  .webp          qualité 85 (archive / impression)
                                  -web.webp      qualité 80 (web, ~80 Ko)  <- celui référencé
                                  -vignette.webp 400 px (~12 Ko)            <- celui de la carte
COLONNES (15)
-------------
Nom | Surnom | Type | Age | Rôle | Secteur | Adresse | Latitude | Longitude |
Apparence | Vêtements | Tic / Objet | Portrait | Famille | Parenté
Détail et conventions dans la feuille « Lisez-moi » du classeur.


AVERTISSEMENTS IMPORTANTS
-------------------------
1. ADRESSES : les numéros civiques sont FICTIFS, les rues sont RÉELLES (extraites
   d'OpenStreetMap via l'API Overpass). Ne pas utiliser comme adresses postales.
2. COORDONNÉES : WGS84, précision au QUARTIER (centroïde réel de la rue + décalage
   déterministe de +-400 m), pas au bâtiment.
3. PORTRAITS : images générées par intelligence artificielle, pas des photographies
   de personnes réelles. Toute ressemblance serait fortuite. Pour un usage public,
   vérifier les obligations de mention de contenu généré (loi canadienne).
4. Les personnages, noms et situations sont entièrement fictifs.


CARTES ET FONDS UTILISÉS (licences)
-----------------------------------
Leaflet 1.9.4            BSD-2
Tuiles OpenStreetMap     (c) contributeurs OpenStreetMap, ODbL
OSM Humanitaire (HOT)    ODbL
OSM France               ODbL
OpenTopoMap              CC-BY-SA
CyclOSM                  ODbL
CARTO Positron / Dark    gratuit avec attribution
Esri World Imagery       imagerie (c) Esri, usage gratuit avec attribution
Géocodage                Nominatim (ODbL)
Données de rues          API Overpass (ODbL)


UTILISATION RAPIDE
------------------
Carte      : double-cliquer carte-la-baie-saguenay.html (connexion requise pour les
             tuiles et Leaflet via CDN).
Régénérer  : modifier base_personnages_fictifs.xlsx puis
             python3 construire_base.py
Servir     : python3 -m http.server 8000   (puis ouvrir http://localhost:8000/carte-la-baie-saguenay.html)
