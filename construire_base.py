#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construire_base.py — régénère tous les livrables à partir du .xlsx maître.

Idempotent : peut être relancé autant de fois que voulu.
Usage :  python3 construire_base.py

Produit :
  base_personnages_fictifs.xlsx    (+ feuilles « Lisez-moi » et « Narration » si présente)
  base_personnages_fictifs.csv     (; et UTF-8 BOM, compatible Excel FR)
  base_personnages_fictifs.json    (clés minuscules sans accent)
  base_personnages_fictifs.geojson (points WGS84, pour QGIS / geojson.io / uMap)
  carte-la-baie-saguenay.html + carte/index.html (données réinjectées)
"""
import openpyxl, json, csv, re, datetime, os, shutil, glob as _glob, unicodedata
from copy import copy
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

XLSX  = 'base_personnages_fictifs.xlsx'
FEUILLE = 'Personnages'
ANIMAUX = {'Pisse-Feu'}

COLONNES = ['Nom','Surnom','Type','Age','Rôle','Secteur','Adresse',
            'Latitude','Longitude','Apparence','Vêtements','Tic / Objet','Portrait','Famille','Parenté']
LARGEURS = {'Nom':23,'Surnom':19,'Type':9,'Age':6,'Rôle':40,'Secteur':13,
            'Adresse':34,'Latitude':11,'Longitude':11,'Apparence':38,'Vêtements':28,'Tic / Objet':28,'Portrait':44,
            'Famille':22,'Parenté':28}
CLES_JSON = {'Nom':'nom','Surnom':'surnom','Type':'type','Age':'age',
             'Rôle':'role','Secteur':'secteur','Adresse':'adresse','Latitude':'latitude',
             'Longitude':'longitude','Apparence':'apparence','Vêtements':'vetements','Tic / Objet':'tic_ou_objet','Portrait':'portrait',
             'Famille':'famille','Parenté':'parente'}
NUMERIQUES = {'Age'}
COORDS = {'Latitude','Longitude'}
NARR_COLS = ['Nom','Surnom','Faction','Lien Spot','Quote joual','Arc S1','Age apparent']

DICO = [
 ('Nom','Texte','Identité complète, obligatoire et unique.'),
 ('Surnom','Texte','Vide = la personne n\'en a pas. Ce n\'est PAS un oubli : dans la base,'
                   ' l\'absence de surnom signale un personnage « rangé » (famille, voisins,'
                   ' institutions), par opposition aux personnages de la marge qui en ont tous un.'),
 ('Type','Liste','Humain | Animal. Permet de filtrer et d\'appliquer des règles différentes'
                 ' (la colonne Vêtements ne se lit pas pareil pour un animal).'),
 ('Age','Entier','Âge réel, en années. Pour un animal : années animales.'),
 ('Rôle','Texte','Métier ou occupation autonome. Format recommandé : « Métier — précision ».'
                 ' Ne doit référencer ni un autre personnage ni un lieu de l\'intrigue.'),
 ('Secteur','Liste','La Baie | Chicoutimi | Jonquière (arrondissements de la ville de Saguenay).'),
 ('Adresse','Texte','« Numéro, Rue ». Les NUMÉROS SONT FICTIFS, les RUE sont réelles'
                    ' (extraites d\'OpenStreetMap via l\'API Overpass).'),
 ('Latitude','Décimal','WGS84, 6 décimales. APPROXIMATIVE : centroïde réel de la rue'
                       ' + décalage déterministe de ±400 m. Précision au quartier, pas au bâtiment.'),
 ('Longitude','Décimal','WGS84, 6 décimales. Même précision que Latitude.'),
 ('Apparence','Texte','Physique. Pour un animal : pelage.'),
 ('Vêtements','Texte','« s.o. » = sans objet (non applicable, p. ex. un animal).'
                     ' Vide = inconnu mais applicable. Ne pas confondre les deux.'),
 ('Tic / Objet','Texte','Manie, accessoire ou objet signature.'),
 ('Portrait','Texte','Chemin relatif du WebP (gabarit « -web », ~80 Ko). Vide = pas encore photographié.'
               ' Trois gabarits par personnage dans portraits/ : .webp (archive), -web.webp (web),'
               ' -vignette.webp (400 px, casting/carte). Découvert automatiquement par slug du nom.'),
 ('Famille','Texte','Nom du clan / foyer. Permet de grouper les proches sur la carte.'),
 ('Parenté','Texte','Lien familial explicite (père de, épouse de, etc.).'),
]

def vide(v): return v is None or (isinstance(v,str) and not v.strip())

def slug(nom):
    s = unicodedata.normalize('NFKD', nom or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", '-', s).strip('-')
    return s

def portraits_par_nom():
    """Associe chaque *-web.webp au slug contenu dans le nom de fichier."""
    found = {}
    for f in _glob.glob('portraits/*-web.webp'):
        base = os.path.basename(f)
        core = re.sub(r'^\d+-', '', base.replace('-web.webp', ''))
        found[core] = 'portraits/' + base
    return found

def charger():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb[FEUILLE]
    hdr = [c.value for c in ws[1]]
    recs = [dict(zip(hdr,[c.value for c in r])) for r in ws.iter_rows(min_row=2)
            if any(c.value is not None for c in r)]
    narr = []
    if 'Narration' in wb.sheetnames:
        nw = wb['Narration']
        nh = [c.value for c in nw[1]]
        narr = [dict(zip(nh,[c.value for c in r])) for r in nw.iter_rows(min_row=2)
                if any(c.value is not None for c in r)]
    if 'Type' not in hdr:
        for r in recs:
            r['Type'] = 'Animal' if r['Nom'] in ANIMAUX else 'Humain'
        print(f"  + colonne « Type » créée ({sum(1 for r in recs if r['Type']=='Animal')} animal, "
              f"{sum(1 for r in recs if r['Type']=='Humain')} humains)")
    index = portraits_par_nom()
    maj = 0
    manquants = []
    for r in recs:
        for k in list(r):
            if k not in COLONNES: del r[k]
        r['Type'] = r.get('Type') or ('Animal' if r['Nom'] in ANIMAUX else 'Humain')
        if r['Type']=='Animal' and vide(r.get('Vêtements')):
            r['Vêtements']='s.o.'; maj+=1
        for k in NUMERIQUES|COORDS:
            if r.get(k) is not None: r[k]=type(r[k])(r[k])
        sl = slug(r['Nom'])
        if sl in index:
            r['Portrait'] = index[sl]
        elif not r.get('Portrait'):
            manquants.append(r['Nom'])
            r['Portrait']=None
        for k in COLONNES:
            if k in r and isinstance(r[k],str) and not r[k].strip(): r[k]=None
    if maj: print(f"  + « s.o. » inscrit aux Vêtements de {maj} animal(aux)")
    if manquants: print(f"  ! portraits introuvables : {', '.join(manquants)}")
    recs.sort(key=lambda r:(r['Secteur']!='La Baie', r['Secteur'] or '', str(r['Nom'])))
    return recs, narr

def ecrire_xlsx(recs, narr):
    out=openpyxl.Workbook(); o=out.active; o.title=FEUILLE
    HF=PatternFill('solid',fgColor='1F3864'); HFONT=Font(bold=True,color='FFFFFF',size=11)
    TH=Side(style='thin',color='D9D9D9'); BD=Border(left=TH,right=TH,top=TH,bottom=TH)
    o.append(COLONNES)
    for c in range(1,len(COLONNES)+1):
        cell=o.cell(1,c); cell.fill=HF; cell.font=HFONT
        cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True); cell.border=BD
    for r in recs: o.append([r.get(k) for k in COLONNES])
    for i,k in enumerate(COLONNES,1): o.column_dimensions[get_column_letter(i)].width=LARGEURS[k]
    ci={k:i+1 for i,k in enumerate(COLONNES)}
    for row in o.iter_rows(min_row=2,max_row=o.max_row,max_col=len(COLONNES)):
        for cell in row:
            cell.border=BD
            centré = cell.column in (ci['Age'],ci['Latitude'],ci['Longitude'],ci['Type'])
            cell.alignment=Alignment(vertical='top',wrap_text=cell.column not in (ci['Latitude'],ci['Longitude']),
                                     horizontal='center' if centré else 'left')
            if cell.column in (ci['Latitude'],ci['Longitude']): cell.number_format='0.000000'
    for rr in range(2,o.max_row+1):
        if rr%2==0:
            for cc in range(1,len(COLONNES)+1): o.cell(rr,cc).fill=PatternFill('solid',fgColor='F2F6FB')
    o.freeze_panes='B2'; o.auto_filter.ref=f"A1:{get_column_letter(len(COLONNES))}{o.max_row}"
    o.row_dimensions[1].height=30; o.sheet_view.showGridLines=False

    d=out.create_sheet('Lisez-moi'); d.sheet_view.showGridLines=False
    d.column_dimensions['A'].width=17; d.column_dimensions['B'].width=10; d.column_dimensions['C'].width=98
    d['A1']='Base de données de personnages fictifs'; d['A1'].font=Font(bold=True,size=15,color='1F3864')
    d['A2']='Dictionnaire de données et conventions'
    d['A2'].font=Font(size=11,color='7A8B99')
    d['A4']=f"{len(recs)} entrées · {len(COLONNES)} colonnes · région du Saguenay (Québec)"
    d['A4'].font=Font(size=10,color='7A8B99')
    r=6
    for i,t in enumerate(['Colonne','Type','Description et convention']):
        c=d.cell(r,i+1,t); c.fill=HF; c.font=HFONT; c.border=BD
        c.alignment=Alignment(horizontal='center',vertical='center')
    r+=1
    for nom,typ,desc in DICO:
        for i,v in enumerate([nom,typ,desc]):
            c=d.cell(r,i+1,v); c.border=BD
            c.alignment=Alignment(vertical='top',wrap_text=(i==2), horizontal='left')
            c.font=Font(bold=(i==0),size=10.5)
        r+=1
    r+=1
    d.cell(r,1,'Conventions générales').font=Font(bold=True,size=12,color='1F3864'); r+=1
    for txt in [
      '• Cellule VIDE  = information applicable mais absente, ou choix assumé (voir Surnom).',
      '• « s.o. »       = sans objet : la colonne ne s\'applique pas à cette entrée (ex. Vêtements d\'un animal).',
      '• Unicité        : la colonne Nom est la clé. Aucune entrée en double.',
      '• Coordonnées    : WGS84. Fictives au bâtiment près — voir la précision dans la fiche Longitude.',
      '• Adresses       : numéros inventés, rues réelles issues d\'OpenStreetMap.',
      '• Narration      : feuille séparée (Faction, Lien Spot, Quote joual, Arc S1) — pas exportée en GeoJSON public.',
    ]:
        c=d.cell(r,1,txt); c.font=Font(size=10.5); c.alignment=Alignment(vertical='center'); r+=1
    r+=1
    d.cell(r,1,'Provenance').font=Font(bold=True,size=12,color='1F3864'); r+=1
    for txt in [
      '• Rues et coordonnées  : OpenStreetMap (ODbL), via les API Overpass et Nominatim.',
      '• Vérifications locales : UQAC (bac en psychologie), Cégep de Jonquière — école ATM',
      '   (cinéma et télévision), aluminerie Rio Tinto à Arvida, boulevard Talbot (Chicoutimi-Sud).',
      '• Carte interactive    : Leaflet 1.9.4 (BSD-2) + tuiles © OpenStreetMap contributors.',
      '• Portraits            : images générées par IA ; fiction intégrale.',
      f'• Généré le            : {datetime.date.today().isoformat()}',
    ]:
        c=d.cell(r,1,txt); c.font=Font(size=10.5); r+=1
    d.freeze_panes='A7'

    if narr:
        ns=out.create_sheet('Narration'); ns.sheet_view.showGridLines=False
        for i,h in enumerate(NARR_COLS,1):
            c=ns.cell(1,i,h); c.fill=HF; c.font=HFONT; c.border=BD
            c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        widths={'Nom':24,'Surnom':22,'Faction':28,'Lien Spot':28,'Quote joual':42,'Arc S1':36,'Age apparent':14}
        for i,h in enumerate(NARR_COLS,1):
            ns.column_dimensions[get_column_letter(i)].width=widths.get(h,20)
        for i,row in enumerate(narr,2):
            for j,h in enumerate(NARR_COLS,1):
                cell=ns.cell(i,j,row.get(h)); cell.border=BD
                cell.alignment=Alignment(vertical='top', wrap_text=True)
                if i%2==0: cell.fill=PatternFill('solid',fgColor='F2F6FB')
        ns.freeze_panes='B2'
        ns.auto_filter.ref=f"A1:{get_column_letter(len(NARR_COLS))}{1+len(narr)}"
        ns.row_dimensions[1].height=30

    out.save(XLSX)

def ecrire_autres(recs):
    with open('base_personnages_fictifs.csv','w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=COLONNES,delimiter=';'); w.writeheader()
        for r in recs: w.writerow({k:('' if r.get(k) is None else r[k]) for k in COLONNES})
    js=[{CLES_JSON[k]:(r.get(k) if not vide(r.get(k)) else None) for k in COLONNES} for r in recs]
    json.dump(js,open('base_personnages_fictifs.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
    json.dump({"type":"FeatureCollection","features":[{"type":"Feature",
        "geometry":{"type":"Point","coordinates":[r['Longitude'],r['Latitude']]},
        "properties":{CLES_JSON[k]:r.get(k) for k in COLONNES if k not in COORDS}} for r in recs]},
        open('base_personnages_fictifs.geojson','w',encoding='utf-8'),ensure_ascii=False,indent=2)
    return js

def copier_vignettes():
    os.makedirs('carte/portraits',exist_ok=True)
    for old in _glob.glob('carte/portraits/*'): os.remove(old)
    for f in _glob.glob('portraits/*-vignette.webp'):
        shutil.copy(f,'carte/portraits/'+os.path.basename(f))
    print(f"  ✔ {len(_glob.glob('carte/portraits/*-vignette.webp'))} vignettes synchronisées vers carte/portraits/")

def reinjecter_carte(js):
    new='const PERSOS='+json.dumps(js,ensure_ascii=False,separators=(',',':'))+';'
    for f in ['carte-la-baie-saguenay.html','carte/index.html']:
        if not os.path.exists(f):
            continue
        h=open(f,encoding='utf-8').read()
        h2,ct=re.subn(r'const PERSOS=\[.*?\];',new,h,count=1,flags=re.S)
        if ct!=1: print(f"  ✘ PERSOS introuvable dans {f}"); continue
        open(f,'w',encoding='utf-8').write(h2)
        print(f"  ✔ {f} ({len(h2)} octets)")

if __name__=='__main__':
    print("Construction de la base…")
    recs, narr=charger()
    ecrire_xlsx(recs, narr)
    js=ecrire_autres(recs)
    print(f"  ✔ {len(recs)} entrées × {len(COLONNES)} colonnes écrites en xlsx / csv / json / geojson")
    if narr: print(f"  ✔ feuille Narration conservée ({len(narr)} lignes)")
    reinjecter_carte(js)
    copier_vignettes()
    print("Terminé.")
