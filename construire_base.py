#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construire_base.py — régénère tous les livrables à partir de la source texte.

SOURCE DE VÉRITÉ : data/personnages.csv (16 colonnes, UTF-8, « ; »).
Le classeur XLSX n'est plus qu'un livrable généré (il était source ET cible
avant le 2026-09-13 : diff illisible, fusion impossible). La narration vit
dans data/narration.csv, fichier PRIVÉ non versionné (voir .gitignore) : si
elle est absente, le classeur complet n'est tout simplement pas produit.

Idempotent : peut être relancé autant de fois que voulu.
Usage :  python3 construire_base.py

Produit :
  base_personnages_fictifs.xlsx          (public : Personnages + Lisez-moi)
  base_personnages_fictifs-complet.xlsx  (privé  : + Narration, .gitignore)
  base_personnages_fictifs.csv           (; et UTF-8 BOM, compatible Excel FR)
  base_personnages_fictifs.json          (clés minuscules sans accent)
  base_personnages_fictifs.geojson       (points WGS84, QGIS / uMap / Mapbox)
  carte/index.html                       (carte canonique, données réinjectées)
  carte-la-baie-saguenay.html            (dérivée de carte/index.html)
  carte/portraits/                       (vignettes synchronisées)
  portraits/planche-contact-generale.webp

REPRODUCTIBILITÉ : aucune donnée volatile (date système, métadonnées Office)
n'est écrite : relancer le script deux fois produit des fichiers OCTET POUR
OCTET identiques (vérifié en CI : git diff doit rester vide). La date « Généré
le » est figée (DATE_FIGEE) ou surchargée par SOURCE_DATE_EPOCH. Pillow est
nécessaire pour la planche contact ; s'il manque, un avertissement est émis
mais les autres livrables sont quand même générés.
"""
import csv
import datetime
import glob as _glob
import json
import os
import re
import shutil
import sys
import unicodedata
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

try:
    from PIL import Image, ImageDraw
    PIL_OK = True
except Exception:  # Pillow absent : tout sauf la planche reste fonctionnel
    PIL_OK = False

# ------------------------------------------------------------------ chemins
SRC_PERSOS = 'data/personnages.csv'
SRC_NARR = 'data/narration.csv'
SRC_FACTIONS = 'data/factions.txt'
XLSX = 'base_personnages_fictifs.xlsx'
XLSX_COMPLET = 'base_personnages_fictifs-complet.xlsx'
FEUILLE = 'Personnages'
CARTE_CANONIQUE = 'carte/index.html'
CARTE_RACINE = 'carte-la-baie-saguenay.html'
ANIMAUX = {'Pisse-Feu'}

# Date figée pour les livrables reproductibles (jamais de date système).
# Surcharge possible avec la variable d'environnement SOURCE_DATE_EPOCH.
def _date_livrable():
    e = os.environ.get('SOURCE_DATE_EPOCH')
    if e:
        try:
            return datetime.datetime.fromtimestamp(int(e), datetime.timezone.utc)
        except (ValueError, OverflowError):
            pass
    return datetime.datetime(2026, 9, 11, 0, 0, tzinfo=datetime.timezone.utc)


DATE_LIVRABLE = _date_livrable()
PLANCHE = 'portraits/planche-contact-generale.webp'

COLONNES = ['Nom', 'Surnom', 'Type', 'Age', 'Rôle', 'Secteur', 'Adresse',
            'Latitude', 'Longitude', 'Apparence', 'Vêtements', 'Tic / Objet',
            'Portrait', 'Famille', 'Branche', 'Parenté']
LARGEURS = {'Nom': 23, 'Surnom': 19, 'Type': 9, 'Age': 6, 'Rôle': 40, 'Secteur': 13,
            'Adresse': 34, 'Latitude': 11, 'Longitude': 11, 'Apparence': 38,
            'Vêtements': 28, 'Tic / Objet': 28, 'Portrait': 44,
            'Famille': 22, 'Branche': 18, 'Parenté': 28}
CLES_JSON = {'Nom': 'nom', 'Surnom': 'surnom', 'Type': 'type', 'Age': 'age',
             'Rôle': 'role', 'Secteur': 'secteur', 'Adresse': 'adresse',
             'Latitude': 'latitude', 'Longitude': 'longitude',
             'Apparence': 'apparence', 'Vêtements': 'vetements',
             'Tic / Objet': 'tic_ou_objet', 'Portrait': 'portrait',
             'Famille': 'famille', 'Branche': 'branche', 'Parenté': 'parente'}
ENTIERS = {'Age'}
DECIMAUX = {'Latitude', 'Longitude'}
NARR_COLS = ['Nom', 'Surnom', 'Faction', 'Faction (détail)', 'Lien Spot',
             'Quote joual', 'Arc S1', 'Age apparent']

DICO = [
 ('Nom', 'Texte', 'Identité complète, obligatoire et unique.'),
 ('Surnom', 'Texte', 'Vide = la personne n’en a pas. Ce n’est PAS un oubli : dans la base,'
                     ' l’absence de surnom signale un personnage « rangé » (famille, voisins,'
                     ' institutions), par opposition aux personnages de la marge qui en ont tous un.'),
 ('Type', 'Liste', 'Humain | Animal. Permet de filtrer et d’appliquer des règles différentes'
                   ' (la colonne Vêtements ne se lit pas pareil pour un animal).'),
 ('Age', 'Entier', 'Âge réel, en années. Pour un animal : années animales.'),
 ('Rôle', 'Texte', 'Métier ou occupation autonome. Format recommandé : « Métier — précision ».'
                   ' Ne doit référencer ni un autre personnage, ni un lieu de l’intrigue,'
                   ' ni une faction / un clan (ex. interdit : « — clan Santini ») : le clan va'
                   ' dans la colonne Famille, la faction dans la source Narration.'),
 ('Secteur', 'Liste', 'La Baie | Chicoutimi | Jonquière (arrondissements de la ville de Saguenay).'
                      ' Les coordonnées doivent tomber dans le secteur annoncé.'),
 ('Adresse', 'Texte', 'Par défaut « Numéro, Rue » : les NUMÉROS SONT FICTIFS, les RUES sont'
                      ' réelles (extraites d’OpenStreetMap via l’API Overpass). Pour un lieu'
                      ' non adressable (plein air, sentier, base militaire), écrire'
                      ' « Lieu-dit : … » : ce préfixe signale volontairement l’absence de'
                      ' numéro civique.'),
 ('Latitude', 'Décimal', 'WGS84. APPROXIMATIVE : centroïde réel de la rue'
                         ' + décalage déterministe de ±400 m. Précision au quartier, pas au bâtiment.'),
 ('Longitude', 'Décimal', 'WGS84. Même précision que Latitude.'),
 ('Apparence', 'Texte', 'Physique. Pour un animal : pelage.'),
 ('Vêtements', 'Texte', '« s.o. » = sans objet (non applicable, p. ex. un animal).'
                        ' Vide = inconnu mais applicable. Ne pas confondre les deux.'),
 ('Tic / Objet', 'Texte', 'Manie, accessoire ou objet signature.'),
 ('Portrait', 'Texte', 'Chemin relatif du WebP gabarit « -web » (~80 à 150 Ko). Vide = pas encore'
                       ' illustré. Deux gabarits par personnage dans portraits/ : -web.webp'
                       ' (le référencé ici) et -vignette.webp (400 px, carte et planche contact).'
                       ' Découverts automatiquement par slug du nom. Toutes les vignettes sont'
                       ' assemblées dans portraits/planche-contact-generale.webp.'),
 ('Famille', 'Texte', 'Nom du clan / foyer, SANS qualificatif : deux foyers homonymes (les Côté'
                      ' de la ruelle et ceux de la poste) se distinguent par la colonne Branche.'),
 ('Branche', 'Texte', 'Précision au sein de la Famille : « JP », « ruelle », « motards »,'
                      ' « hôtel de ville »… Vide = le foyer est seul de son nom. La paire'
                      ' Famille + Branche identifie un foyer de façon unique.'),
 ('Parenté', 'Texte', 'Lien familial explicite (père de, épouse de, etc.).'),
]


# ------------------------------------------------------------------ outils
def vide(v):
    return v is None or (isinstance(v, str) and not v.strip())


def slug(nom):
    s = unicodedata.normalize('NFKD', nom or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", '-', s).strip('-')
    return s


def lire_csv(chemin, colonnes_attendues=None):
    """Lit un CSV source « ; » UTF-8. Les chaînes vides deviennent None."""
    with open(chemin, newline='', encoding='utf-8') as f:
        lecteur = csv.DictReader(f, delimiter=';')
        if colonnes_attendues and list(lecteur.fieldnames or []) != colonnes_attendues:
            raise SystemExit(
                f"✘ {chemin} : colonnes inattendues\n"
                f"  attendu : {colonnes_attendues}\n"
                f"  trouvé  : {lecteur.fieldnames}")
        return [{k: (v if v not in (None, '') else None) for k, v in row.items()}
                for row in lecteur]


def lire_factions():
    """Vocabulaire contrôlé des factions (data/factions.txt)."""
    if not os.path.exists(SRC_FACTIONS):
        raise SystemExit(f"✘ Vocabulaire des factions introuvable : {SRC_FACTIONS}")
    with open(SRC_FACTIONS, encoding='utf-8') as f:
        return [lg.strip() for lg in f if lg.strip() and not lg.lstrip().startswith('#')]


def portraits_par_nom():
    """Associe chaque *-web.webp au slug contenu dans le nom de fichier."""
    found = {}
    for f in _glob.glob('portraits/*-web.webp'):
        base = os.path.basename(f)
        core = re.sub(r'^\d+-', '', base.replace('-web.webp', ''))
        found[core] = 'portraits/' + base
    return found


# ------------------------------------------------------------------ lecture
def charger_personnages():
    """Lit la source, normalise les types et complète les portraits."""
    if not os.path.exists(SRC_PERSOS):
        raise SystemExit(f"✘ Source introuvable : {SRC_PERSOS} (à lancer depuis la racine)")
    recs = lire_csv(SRC_PERSOS, COLONNES)
    index = portraits_par_nom()
    maj = 0
    manquants = []
    for r in recs:
        r['Type'] = r.get('Type') or ('Animal' if r['Nom'] in ANIMAUX else 'Humain')
        if r['Type'] == 'Animal' and vide(r.get('Vêtements')):
            r['Vêtements'] = 's.o.'
            maj += 1
        for k in ENTIERS | DECIMAUX:
            v = r.get(k)
            if v is None:
                continue
            try:
                r[k] = int(str(v).strip()) if k in ENTIERS else float(str(v).strip())
            except (TypeError, ValueError):
                raise SystemExit(f"✘ {r['Nom']} : « {k} » n’est pas un nombre ({v!r})")
        sl = slug(r['Nom'])
        if sl in index:
            r['Portrait'] = index[sl]
        elif not r.get('Portrait'):
            manquants.append(r['Nom'])
            r['Portrait'] = None
    if maj:
        print(f"  + « s.o. » inscrit aux Vêtements de {maj} animal(aux)")
    if manquants:
        # Échec franc plutôt qu'un simple avertissement : la CI ne lit pas la
        # sortie standard, et un personnage sans portrait passait inaperçu
        # jusqu'aux tests (slug du nom ≠ nom de fichier, ex. « abbe-julien- »).
        raise SystemExit("✘ Portrait introuvable pour : " + ', '.join(manquants)
                         + "\n  → attendu : portraits/<n°>-<slug-du-nom>-web.webp")
    recs.sort(key=lambda r: (r['Secteur'] != 'La Baie', r['Secteur'] or '', str(r['Nom'])))
    return recs


def charger_narration(recs):
    """Source privée : absente → narration simplement non publiée."""
    if not os.path.exists(SRC_NARR):
        print("  · narration absente (source privée) : classeur complet non produit")
        return None
    narr = lire_csv(SRC_NARR, NARR_COLS)
    noms_base = {r['Nom'] for r in recs}
    noms_narr = {r['Nom'] for r in narr}
    if noms_base != noms_narr:
        raise SystemExit("✘ Narration désynchronisée : "
                         f"manquants {sorted(noms_base - noms_narr)} ; "
                         f"orphelins {sorted(noms_narr - noms_base)}")
    valides = lire_factions()
    fautifs = sorted({r['Faction'] for r in narr} - set(valides))
    if fautifs:
        raise SystemExit("✘ Faction(s) hors vocabulaire contrôlé : "
                         f"{fautifs}\n  → corriger data/narration.csv ou compléter "
                         f"{SRC_FACTIONS}")
    for r in narr:
        if r.get('Age apparent') is not None:
            r['Age apparent'] = int(str(r['Age apparent']).strip())
    return narr


# ------------------------------------------------------------------ classeur
def ecrire_personnages(feuille, recs):
    """Feuille « Personnages » : en-tête, données, mise en forme."""
    HF = PatternFill('solid', fgColor='1F3864')
    HFONT = Font(bold=True, color='FFFFFF', size=11)
    TH = Side(style='thin', color='D9D9D9')
    BD = Border(left=TH, right=TH, top=TH, bottom=TH)

    feuille.append(COLONNES)
    for c in range(1, len(COLONNES) + 1):
        cell = feuille.cell(1, c)
        cell.fill = HF
        cell.font = HFONT
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BD
    for r in recs:
        feuille.append([r.get(k) for k in COLONNES])
    for i, k in enumerate(COLONNES, 1):
        feuille.column_dimensions[get_column_letter(i)].width = LARGEURS[k]
    ci = {k: i + 1 for i, k in enumerate(COLONNES)}
    for row in feuille.iter_rows(min_row=2, max_row=feuille.max_row, max_col=len(COLONNES)):
        for cell in row:
            cell.border = BD
            centre = cell.column in (ci['Age'], ci['Latitude'], ci['Longitude'], ci['Type'])
            cell.alignment = Alignment(
                vertical='top',
                wrap_text=cell.column not in (ci['Latitude'], ci['Longitude']),
                horizontal='center' if centre else 'left')
            if cell.column in (ci['Latitude'], ci['Longitude']):
                cell.number_format = '0.000000'
    for rr in range(2, feuille.max_row + 1):
        if rr % 2 == 0:
            for cc in range(1, len(COLONNES) + 1):
                feuille.cell(rr, cc).fill = PatternFill('solid', fgColor='F2F6FB')
    feuille.freeze_panes = 'B2'
    feuille.auto_filter.ref = f"A1:{get_column_letter(len(COLONNES))}{feuille.max_row}"
    feuille.row_dimensions[1].height = 30
    feuille.sheet_view.showGridLines = False


def ecrire_lisez_moi(classeur, recs, avec_narration):
    """Feuille « Lisez-moi » : dictionnaire des données et conventions."""
    HF = PatternFill('solid', fgColor='1F3864')
    HFONT = Font(bold=True, color='FFFFFF', size=11)
    TH = Side(style='thin', color='D9D9D9')
    BD = Border(left=TH, right=TH, top=TH, bottom=TH)

    d = classeur.create_sheet('Lisez-moi')
    d.sheet_view.showGridLines = False
    d.column_dimensions['A'].width = 17
    d.column_dimensions['B'].width = 10
    d.column_dimensions['C'].width = 98
    d['A1'] = 'Base de données de personnages fictifs'
    d['A1'].font = Font(bold=True, size=15, color='1F3864')
    d['A2'] = 'Dictionnaire de données et conventions'
    d['A2'].font = Font(size=11, color='7A8B99')
    d['A4'] = (f"{len(recs)} entrées · {len(COLONNES)} colonnes · "
               f"région du Saguenay (Québec)")
    d['A4'].font = Font(size=10, color='7A8B99')

    r = 6
    for i, t in enumerate(['Colonne', 'Type', 'Description et convention']):
        c = d.cell(r, i + 1, t)
        c.fill = HF
        c.font = HFONT
        c.border = BD
        c.alignment = Alignment(horizontal='center', vertical='center')
    r += 1
    for nom, typ, desc in DICO:
        for i, v in enumerate([nom, typ, desc]):
            c = d.cell(r, i + 1, v)
            c.border = BD
            c.alignment = Alignment(vertical='top', wrap_text=(i == 2), horizontal='left')
            c.font = Font(bold=(i == 0), size=10.5)
        r += 1

    r += 1
    d.cell(r, 1, 'Conventions générales').font = Font(bold=True, size=12, color='1F3864')
    r += 1
    for txt in [
      '• Cellule VIDE  = information applicable mais absente, ou choix assumé (voir Surnom).',
      '• « s.o. »       = sans objet : la colonne ne s’applique pas à cette entrée (ex. Vêtements d’un animal).',
      '• Unicité        : la colonne Nom est la clé. Aucune entrée en double ; le surnom ne'
      ' s’écrit JAMAIS dans Nom (il a sa colonne, sans « »).',
      '• Famille + Branche : la paire identifie un foyer. Deux foyers homonymes (Côté de la'
      ' ruelle / Côté de la poste) partagent la Famille et se distinguent par la Branche.',
      '• Coordonnées    : WGS84. Fictives au bâtiment près — voir la précision dans la fiche Longitude.',
      '• Adresses       : numéros inventés, rues réelles issues d’OpenStreetMap ; les lieux non'
      ' adressables s’écrivent « Lieu-dit : … » (pas de numéro civique).',
      '• Source         : data/personnages.csv est la source de vérité (texte, diffable).'
      ' Ce classeur est un livrable régénéré par construire_base.py : ne pas l’éditer à la main.',
    ]:
        c = d.cell(r, 1, txt)
        c.font = Font(size=10.5)
        c.alignment = Alignment(vertical='center')
        r += 1

    r += 1
    d.cell(r, 1, 'Narration').font = Font(bold=True, size=12, color='1F3864')
    r += 1
    for txt in ([
      '• Couverture      : 100 % des entrées (faction, lien au Spot, réplique, arc S1).',
      '• Statut          : source PRIVÉE (data/narration.csv, non versionnée).' ,
      '• Ce classeur     : la narration est '
      + ('présente (feuille « Narration ») — diffusion interne.'
         if avec_narration else 'VOLONTAIREMENT ABSENTE — diffusion publique.'),
      '• Faction         : vocabulaire contrôlé de '
      + f"{len(lire_factions())} valeurs (data/factions.txt) ; la nuance d’origine"
        " est conservée dans « Faction (détail) ».",
      '• Jamais exportée : ni dans le CSV / JSON / GeoJSON publics, ni dans la carte.',
    ]):
        c = d.cell(r, 1, txt)
        c.font = Font(size=10.5)
        c.alignment = Alignment(vertical='center')
        r += 1

    r += 1
    d.cell(r, 1, 'Provenance').font = Font(bold=True, size=12, color='1F3864')
    r += 1
    for txt in [
      '• Rues et coordonnées  : OpenStreetMap (ODbL), via les API Overpass et Nominatim.',
      '• Vérifications locales : UQAC (bac en psychologie), Cégep de Jonquière — école ATM'
      '   (cinéma et télévision), aluminerie Rio Tinto à Arvida, boulevard Talbot (Chicoutimi-Sud).',
      '• Carte interactive    : Leaflet 1.9.4 (BSD-2), vendorié dans carte/vendor/'
      ' (le code de la carte fonctionne hors ligne ; seules les tuiles restent en ligne).',
      '• Portraits            : images générées par IA ; fiction intégrale. Statut distinct'
      ' dans LICENSE-DONNEES.md.',
      f'• Généré le            : {DATE_LIVRABLE.date().isoformat()} (date figée pour la reproductibilité)',
    ]:
        c = d.cell(r, 1, txt)
        c.font = Font(size=10.5)
        r += 1
    d.freeze_panes = 'A7'


def ecrire_narration(classeur, narr):
    """Feuille « Narration » (classeur complet uniquement)."""
    HF = PatternFill('solid', fgColor='1F3864')
    HFONT = Font(bold=True, color='FFFFFF', size=11)
    TH = Side(style='thin', color='D9D9D9')
    BD = Border(left=TH, right=TH, top=TH, bottom=TH)

    ns = classeur.create_sheet('Narration')
    ns.sheet_view.showGridLines = False
    for i, h in enumerate(NARR_COLS, 1):
        c = ns.cell(1, i, h)
        c.fill = HF
        c.font = HFONT
        c.border = BD
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    widths = {'Nom': 24, 'Surnom': 22, 'Faction': 24, 'Faction (détail)': 28,
              'Lien Spot': 28, 'Quote joual': 42, 'Arc S1': 36, 'Age apparent': 14}
    for i, h in enumerate(NARR_COLS, 1):
        ns.column_dimensions[get_column_letter(i)].width = widths.get(h, 20)
    for i, row in enumerate(narr, 2):
        for j, h in enumerate(NARR_COLS, 1):
            cell = ns.cell(i, j, row.get(h))
            cell.border = BD
            cell.alignment = Alignment(vertical='top', wrap_text=True)
            if i % 2 == 0:
                cell.fill = PatternFill('solid', fgColor='F2F6FB')
    ns.freeze_panes = 'B2'
    ns.auto_filter.ref = f"A1:{get_column_letter(len(NARR_COLS))}{1 + len(narr)}"
    ns.row_dimensions[1].height = 30


def ecrire_xlsx(recs, narr, chemin):
    """Assemble un classeur (public sans Narration, complet avec)."""
    out = openpyxl.Workbook()
    o = out.active
    o.title = FEUILLE
    ecrire_personnages(o, recs)
    ecrire_lisez_moi(out, recs, avec_narration=bool(narr))
    if narr:
        ecrire_narration(out, narr)

    # Métadonnées figées : un classeur régénéré à données identiques doit avoir
    # la même empreinte (pas d'horloge système dans docProps/core.xml).
    out.properties.creator = 'Luc'
    out.properties.lastModifiedBy = 'Luc'
    out.properties.created = DATE_LIVRABLE
    out.properties.modified = DATE_LIVRABLE
    out.properties.title = 'Base de données de personnages fictifs — La Baie (Saguenay)'
    out.properties.keywords = 'fiction; Saguenay; La Baie; OpenStreetMap; ODbL'
    out.save(chemin)
    figer_xlsx(chemin)


def figer_xlsx(path):
    """Rend le .xlsx octet-pour-octet reproductible : openpyxl écrase
    « modified » à l'enregistrement et date toutes les entrées zip à l'horloge
    système. On réécrit l'archive avec une date unique (DATE_LIVRABLE) et un
    docProps/core.xml aux horodatages figés."""
    iso = DATE_LIVRABLE.strftime('%Y-%m-%dT%H:%M:%SZ')
    dt = (DATE_LIVRABLE.year, DATE_LIVRABLE.month, DATE_LIVRABLE.day, 0, 0, 0)
    tmp = path + '.tmp'
    with ZipFile(path) as zin:
        membres = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with ZipFile(tmp, 'w', ZIP_DEFLATED, compresslevel=6) as zout:
        for info, data in membres:
            if info.filename == 'docProps/core.xml':
                core = data.decode('utf-8')
                core = re.sub(r'(<dcterms:created[^>]*>)[^<]*(</dcterms:created>)',
                              rf'\g<1>{iso}\g<2>', core)
                core = re.sub(r'(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)',
                              rf'\g<1>{iso}\g<2>', core)
                data = core.encode('utf-8')
            ni = ZipInfo(info.filename, date_time=dt)
            ni.compress_type = info.compress_type
            ni.external_attr = info.external_attr
            ni.create_system = info.create_system
            zout.writestr(ni, data)
    os.replace(tmp, path)


# ------------------------------------------------------------------ exports
def ecrire_autres(recs):
    with open('base_personnages_fictifs.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=';')
        w.writeheader()
        for r in recs:
            w.writerow({k: ('' if r.get(k) is None else r[k]) for k in COLONNES})
    js = [{CLES_JSON[k]: (r.get(k) if not vide(r.get(k)) else None) for k in COLONNES}
          for r in recs]
    with open('base_personnages_fictifs.json', 'w', encoding='utf-8') as f:
        json.dump(js, f, ensure_ascii=False, indent=2)
    gj = {"type": "FeatureCollection", "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [r['Longitude'], r['Latitude']]},
         "properties": {CLES_JSON[k]: r.get(k) for k in COLONNES if k not in DECIMAUX}}
        for r in recs]}
    with open('base_personnages_fictifs.geojson', 'w', encoding='utf-8') as f:
        json.dump(gj, f, ensure_ascii=False, indent=2)
    return js


def ecrire_cartes(js):
    """Réinjecte les données dans la carte canonique, puis DÉRIVE la copie de
    racine (plus aucune duplication à maintenir : une seule source HTML)."""
    new = 'const PERSOS=' + json.dumps(js, ensure_ascii=False, separators=(',', ':')) + ';'
    if not os.path.exists(CARTE_CANONIQUE):
        print(f"  ✘ {CARTE_CANONIQUE} introuvable")
        return
    with open(CARTE_CANONIQUE, encoding='utf-8') as f:
        source = f.read()
    # Le remplacement est une FONCTION : re.subn interpréterait les séquences
    # présentes dans `new` (\n, \t, \1…) et corromprait le JS — voire planterait
    # — si une valeur de la base contenait un caractère spécial.
    remplace, n = re.subn(r'const PERSOS=\[.*?\];', lambda _: new, source, count=1,
                          flags=re.S)
    if n != 1:
        print(f"  ✘ PERSOS introuvable dans {CARTE_CANONIQUE}")
        return
    with open(CARTE_CANONIQUE, 'w', encoding='utf-8') as f:
        f.write(remplace)
    print(f"  ✔ {CARTE_CANONIQUE} ({len(remplace)} octets)")

    racine = remplace.replace('"vendor/leaflet/', '"carte/vendor/leaflet/')
    racine = racine.replace("const RACINE='../';", "const RACINE='';")
    if racine == remplace:
        print(f"  ✘ dérivation de {CARTE_RACINE} impossible (motifs absents)")
        return
    with open(CARTE_RACINE, 'w', encoding='utf-8') as f:
        f.write(racine)
    print(f"  ✔ {CARTE_RACINE} ({len(racine)} octets, dérivé de carte/index.html)")


def copier_vignettes():
    os.makedirs('carte/portraits', exist_ok=True)
    try:
        for old in _glob.glob('carte/portraits/*'):
            try:
                os.remove(old)
            except OSError as e:
                print(f"  ! suppression impossible {old} : {e}")
        n = 0
        for f in _glob.glob('portraits/*-vignette.webp'):
            shutil.copy(f, 'carte/portraits/' + os.path.basename(f))
            n += 1
        print(f"  ✔ {n} vignettes synchronisées vers carte/portraits/")
    except OSError as e:
        print(f"  ! synchronisation des vignettes impossible : {e}")


def planche_contact(recs, cols=10, larg=240, haut=160, bandeau=34, marge=10):
    """Assemble la planche contact de TOUS les personnages (vignette + nom).

    Livrable portraits/planche-contact-generale.webp, reproductible (ordonnancement
    identique à recs, pas de métadonnée volatile)."""
    if not PIL_OK:
        print("  ! Pillow absent : planche-contact-generale.webp non générée"
              " (pip install -r requirements.txt)")
        return
    cases = []
    for r in recs:
        if not r.get('Portrait'):
            continue
        vig = r['Portrait'].replace('-web.webp', '-vignette.webp')
        if os.path.exists(vig):
            cases.append((vig, r['Nom']))
    if not cases:
        print("  ! aucune vignette trouvée : planche contact ignorée")
        return
    lignes = (len(cases) + cols - 1) // cols
    # Fonte VENDORIÉE (assets/fonts) : une police système différente d'une
    # machine à l'autre changerait le rendu des étiquettes → planche non
    # reproductible. Repli système uniquement si la fonte vendoriée manque.
    police = None
    racine = os.path.dirname(os.path.abspath(__file__))
    candidats = [os.path.join(racine, 'assets', 'fonts', 'DejaVuSans.ttf'),
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                 '/usr/share/fonts/dejavu/DejaVuSans.ttf']
    for cand in candidats:
        if os.path.exists(cand):
            try:
                from PIL import ImageFont
                police = ImageFont.truetype(cand, 15)
                break
            except Exception:
                police = None
    W = cols * larg + (cols + 1) * marge
    H = lignes * (haut + bandeau) + (lignes + 1) * marge
    planche = Image.new('RGB', (W, H), (18, 32, 44))
    draw = ImageDraw.Draw(planche)
    for i, (vig, nom) in enumerate(cases):
        cl, lg = i % cols, i // cols
        x = marge + cl * (larg + marge)
        y = marge + lg * (haut + bandeau + marge)
        with Image.open(vig) as im:
            im = im.convert('RGB')
            # recadrage « couverture » au ratio 3:2 de la case
            sr = max(larg / im.width, haut / im.height)
            im = im.resize((round(im.width * sr), round(im.height * sr)), Image.LANCZOS)
            gx, gy = (im.width - larg) // 2, (im.height - haut) // 2
            im = im.crop((gx, gy, gx + larg, gy + haut))
            planche.paste(im, (x, y))
        draw.rectangle([x, y + haut, x + larg, y + haut + bandeau], fill=(19, 36, 50))
        lib = nom if len(nom) <= 26 else nom[:25] + '…'
        draw.text((x + 6, y + haut + 8), lib, fill=(220, 234, 245), font=police)
    os.makedirs('portraits', exist_ok=True)
    planche.save(PLANCHE, 'WEBP', quality=82, method=6)
    print(f"  ✔ {PLANCHE} ({len(cases)} vignettes, {W}×{H} px)")


def main():
    print("Construction de la base…")
    recs = charger_personnages()
    narr = charger_narration(recs)
    ecrire_xlsx(recs, None, XLSX)
    print(f"  ✔ {XLSX} — {len(recs)} entrées × {len(COLONNES)} colonnes (public, sans Narration)")
    if narr:
        ecrire_xlsx(recs, narr, XLSX_COMPLET)
        print(f"  ✔ {XLSX_COMPLET} — + feuille Narration ({len(narr)} lignes, privé)")
    js = ecrire_autres(recs)
    print(f"  ✔ csv / json / geojson régénérés ({len(recs)} entrées)")
    ecrire_cartes(js)
    copier_vignettes()
    planche_contact(recs)
    print("Terminé.")


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"✘ Échec de la construction : {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
