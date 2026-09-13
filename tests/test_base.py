# -*- coding: utf-8 -*-
"""
tests/test_base.py — garde-fous de la base de personnages fictifs.

Lancé par la CI (.github/workflows/validation.yml) après régénération :
    python -m unittest discover -s tests -v

Couvre : effectifs annoncés, conventions d'écriture (adresses, rôles, surnoms,
famille + branche), cohérence géographique, couverture complète de la
narration (source publique versionnée), portraits et planche contact, carte
hors ligne et dérivation de la copie de racine, licences distinctes,
versionnement de la narration dans Git, et reproductibilité des livrables
(le « git diff » vide est vérifié par la CI après deux constructions
successives).
"""
import csv
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
os.chdir(RACINE)
sys.path.insert(0, str(RACINE))

import construire_base as cb  # noqa: E402  (date figée, colonnes, source)

N = 213                      # nombre canonique d'entrées
COLONNES = cb.COLONNES       # 17 colonnes (identifiant stable inclus)
MINEURS = {'Léo Cloutier': 9, 'Nour Benali': 13, 'Alexandre Lavoie': 16,
           # cohorte « jeunes » du 2026-09-13 (aréna, école, restaurant familial)
           'Jade Boivin': 12, 'Noah Traoré': 14, 'Thomas Bergeron': 15,
           'Sofia Santini': 16, 'Maude Pedneault': 17,
           'Léa Simard': 16}
SRC_PERSOS = cb.SRC_PERSOS
SRC_NARR = cb.SRC_NARR
SRC_FACTIONS = cb.SRC_FACTIONS

# Boîtes approximatives par arrondissement (validées sur les rues réelles).
BOITES = {
    'La Baie':     (48.28, 48.381, -71.02, -70.75),
    'Chicoutimi':  (48.38, 48.45,  -71.12, -71.00),
    'Jonquière':   (48.40, 48.45,  -71.30, -71.15),
}


def charger_xlsx(chemin='base_personnages_fictifs.xlsx'):
    wb = openpyxl.load_workbook(chemin)
    ws = wb['Personnages']
    hdr = [c.value for c in ws[1]]
    recs = [dict(zip(hdr, [c.value for c in r]))
            for r in ws.iter_rows(min_row=2)
            if any(c.value is not None for c in r)]
    return wb, recs


def lire_csv_source(chemin):
    with open(chemin, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=';'))


class TestEffectifsEtFormats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wb, cls.recs = charger_xlsx()

    def test_nombre_entrees(self):
        self.assertEqual(len(self.recs), N, f'le classeur doit contenir {N} entrées')

    def test_les_quatre_exports_ont_le_meme_effectif(self):
        with open('base_personnages_fictifs.json', encoding='utf-8') as f:
            js = json.load(f)
        with open('base_personnages_fictifs.geojson', encoding='utf-8') as f:
            gj = json.load(f)
        with open('base_personnages_fictifs.csv', encoding='utf-8-sig') as f:
            lignes = list(csv.DictReader(f, delimiter=';'))
        self.assertEqual(len(js), N)
        self.assertEqual(len(gj['features']), N)
        self.assertEqual(len(lignes), N)

    def test_colonnes_canoniques(self):
        hdr = [c.value for c in self.wb['Personnages'][1]]
        self.assertEqual(hdr, COLONNES)
        self.assertEqual(len(COLONNES), 17)


class TestSourceTexte(unittest.TestCase):
    """La source de vérité est un CSV texte, pas le classeur binaire."""

    @classmethod
    def setUpClass(cls):
        cls.src = lire_csv_source(SRC_PERSOS)

    def test_source_presente_et_complete(self):
        self.assertTrue(os.path.exists(SRC_PERSOS))
        self.assertEqual(len(self.src), N)
        with open(SRC_PERSOS, newline='', encoding='utf-8') as f:
            self.assertEqual(csv.DictReader(f, delimiter=';').fieldnames, COLONNES)

    def test_source_lisible_en_lf(self):
        """Fins de ligne Unix : un diff Git reste lisible ligne à ligne."""
        with open(SRC_PERSOS, 'rb') as f:
            self.assertNotIn(b'\r\n', f.read(), 'la source doit être en LF')

    def test_source_et_exports_ont_le_meme_effectif(self):
        with open('base_personnages_fictifs.json', encoding='utf-8') as f:
            self.assertEqual(len(json.load(f)), len(self.src))

    def test_aucune_valeur_ne_casse_l_injection_carte(self):
        """« ]; » terminerait prématurément la regex de réinjection PERSOS ;
        un caractère de contrôle (saut de ligne, tabulation) casserait la
        chaîne JS et serait invisible dans un diff."""
        for r in self.src:
            for v in r.values():
                if isinstance(v, str):
                    self.assertNotIn('];', v, f'{r["Nom"]} : valeur contenant « ]; »')
                    controles = [c for c in v if ord(c) < 0x20]
                    self.assertFalse(controles,
                                     f'{r["Nom"]} : caractère(s) de contrôle {controles!r}')

    def test_vocabulaire_factions_est_propre(self):
        with open(SRC_FACTIONS, encoding='utf-8') as f:
            valeurs = [lg.strip() for lg in f if lg.strip() and not lg.lstrip().startswith('#')]
        self.assertGreaterEqual(len(valeurs), 8)
        self.assertEqual(len(valeurs), len(set(valeurs)), 'faction en double')
        for v in valeurs:
            self.assertEqual(v, v.strip())
            self.assertNotIn('/', v.replace(' / ', ''), f'« {v} » : séparateur ambigu')



class TestIdentifiants(unittest.TestCase):
    def test_ids_sources_et_exports(self):
        source = {r['ID']: r['Nom'] for r in cb.charger_personnages()}
        self.assertEqual(len(source), N)
        self.assertEqual(set(source), {r['ID'] for r in cb.charger_narration(cb.charger_personnages())})
        with open('base_personnages_fictifs.json', encoding='utf-8') as f:
            self.assertEqual(source, {r['id']: r['nom'] for r in json.load(f)})
        with open('base_personnages_fictifs.geojson', encoding='utf-8') as f:
            features = json.load(f)['features']
        self.assertEqual(source, {r['id']: r['properties']['nom'] for r in features})
        for r in features:
            self.assertEqual(r['id'], r['properties']['id'])
        with open('base_personnages_fictifs.csv', encoding='utf-8-sig') as f:
            self.assertEqual(source, {r['ID']: r['Nom'] for r in csv.DictReader(f, delimiter=';')})
        self.assertEqual(source, {r['ID']: r['Nom'] for r in charger_xlsx()[1]})
        wb = openpyxl.load_workbook(cb.XLSX)
        lignes = list(wb['Narration'].values)
        narr = [dict(zip(lignes[0], r)) for r in lignes[1:]]
        self.assertEqual(source, {r['ID']: r['Nom'] for r in narr})
        for fichier in (cb.CARTE_CANONIQUE, cb.CARTE_RACINE):
            h = Path(fichier).read_text(encoding='utf-8')
            donnees = json.loads(re.search(r'const PERSOS=(\[.*?\]);', h, re.S)[1])
            self.assertEqual(source, {r['id']: r['nom'] for r in donnees})

    def test_ids_invalides_refuses(self):
        for identifiant in (None, '', 'P000', 'P01', 'P0001', 'p001', 'P001 ', 'Pabc'):
            with self.subTest(identifiant=identifiant), self.assertRaises(SystemExit):
                cb.valider_ids([{'ID': identifiant}], 'test')
        cb.valider_ids([{'ID': 'P001'}, {'ID': 'P1000'}], 'test')

    def test_doublons_refuses(self):
        rows = cb.lire_csv(SRC_PERSOS, COLONNES)
        with patch.object(cb, 'lire_csv', return_value=[rows[0], rows[0]]):
            with self.assertRaisesRegex(SystemExit, 'ID en double'):
                cb.charger_personnages()
        narr = cb.lire_csv(SRC_NARR, cb.NARR_COLS)
        with patch.object(cb, 'lire_csv', return_value=[narr[0], narr[0]]):
            with self.assertRaisesRegex(SystemExit, 'ID en double'):
                cb.charger_narration(rows)

    def test_narration_orpheline_ou_manquante_refusee(self):
        rows = cb.charger_personnages()
        narr = cb.lire_csv(SRC_NARR, cb.NARR_COLS)
        for variante in (narr[1:], [dict(narr[0], ID='P999'), *narr[1:]]):
            with patch.object(cb, 'lire_csv', return_value=variante):
                with self.assertRaisesRegex(SystemExit, 'Narration désynchronisée'):
                    cb.charger_narration(rows)

    def test_renommage_et_reordre_conservent_les_liens(self):
        rows = cb.lire_csv(SRC_PERSOS, COLONNES)
        original = dict(rows[0])
        rows[0]['Nom'] = 'Nouveau nom sans fichier correspondant'
        rows[0]['Surnom'] = 'Nouveau surnom'
        with patch.object(cb, 'lire_csv', return_value=list(reversed(rows))):
            charges = cb.charger_personnages()
        perso = next(r for r in charges if r['ID'] == original['ID'])
        self.assertEqual(perso['Portrait'], original['Portrait'])
        avant = next(r for r in cb.lire_csv(SRC_NARR) if r['ID'] == original['ID'])
        apres = next(r for r in cb.charger_narration(charges) if r['ID'] == original['ID'])
        self.assertEqual(apres['Nom'], perso['Nom'])
        self.assertEqual(apres['Surnom'], perso['Surnom'])
        for champ in ('Faction', 'Arc S1', 'Quote joual'):
            self.assertEqual(apres[champ], avant[champ])

    def test_chemin_portrait_invalide_refuse(self):
        rows = cb.lire_csv(SRC_PERSOS, COLONNES)
        rows[0]['Portrait'] = 'portraits/fichier-inexistant-web.webp'
        with patch.object(cb, 'lire_csv', return_value=rows):
            with self.assertRaisesRegex(SystemExit, 'Portrait introuvable'):
                cb.charger_personnages()


class TestRelations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persos = cb.charger_personnages()
        cls.liens = cb.relations.charger(cls.persos)

    def test_source_relations_et_provenance(self):
        self.assertGreater(len(self.liens), 0)
        base = {r['ID']: r for r in self.persos}
        for lien in self.liens:
            self.assertEqual(lien['Extrait'], base[lien['Preuve_ID']]['Parenté'])
        self.assertEqual(self.liens, cb.relations.valider(self.liens, self.persos))

    def test_relations_references_et_types_invalides(self):
        for champ, valeur in [('Source_ID', 'P999'), ('Cible_ID', 'P999'),
                               ('Preuve_ID', 'P999'), ('Type', 'invente'),
                               ('Champ_source', 'Arc S1'), ('Extrait', 'preuve inventée'),
                               ('Extrait', ''), ('Extrait', None)]:
            with self.subTest(champ=champ, valeur=valeur), self.assertRaises(SystemExit):
                cb.relations.valider([dict(self.liens[0], **{champ: valeur})], self.persos)
        ligne = dict(self.liens[0])
        del ligne['Extrait']
        with self.assertRaises(SystemExit):
            cb.relations.valider([ligne], self.persos)

    def test_relations_doublons_et_symetrie(self):
        lien = next(r for r in self.liens if r['Type'] == 'conjoint_de')
        with self.assertRaisesRegex(SystemExit, 'en double'):
            cb.relations.valider([lien, lien], self.persos)
        inverse = dict(lien, Source_ID=lien['Cible_ID'], Cible_ID=lien['Source_ID'])
        with self.assertRaisesRegex(SystemExit, 'symétrique'):
            cb.relations.valider([inverse], self.persos)

    def test_relations_auto_liens_et_cycles(self):
        lien = next(r for r in self.liens if r['Type'] == 'parent_de')
        with self.assertRaisesRegex(SystemExit, 'auto-relation'):
            cb.relations.valider([dict(lien, Cible_ID=lien['Source_ID'])], self.persos)
        inverse = dict(lien, Source_ID=lien['Cible_ID'], Cible_ID=lien['Source_ID'])
        with self.assertRaisesRegex(SystemExit, 'cycle de parenté'):
            cb.relations.valider([lien, inverse], self.persos)

    def test_relations_survivent_aux_renommages(self):
        lien = self.liens[0]
        persos = [dict(r, Nom='Nom modifié') if r['ID'] == lien['Source_ID'] else dict(r)
                  for r in self.persos]
        charges = cb.relations.valider(list(reversed(self.liens)), persos)
        self.assertEqual(charges, self.liens)
        export = cb.relations.serialiser(charges, persos)
        self.assertEqual(export['relations'][0]['source_nom'], 'Nom modifié')
        self.assertEqual(export['relations'][0]['source_id'], lien['Source_ID'])

    def test_relations_exports_et_feuille(self):
        attendu = cb.relations.serialiser(self.liens, self.persos)
        self.assertEqual(json.loads(cb.relations.EXPORT.read_text(encoding='utf-8')), attendu)
        wb, _ = charger_xlsx()
        lignes = list(wb['Relations'].values)
        self.assertEqual(len(lignes) - 1, len(self.liens))
        for original, valeurs in zip(self.liens, lignes[1:]):
            ligne = dict(zip(lignes[0], valeurs))
            for cle in cb.relations.COLONNES:
                self.assertEqual(ligne[cle], original[cle])
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'relations.json'
            with patch.object(cb.relations, 'EXPORT', chemin):
                cb.relations.exporter(self.liens, self.persos)
                premier = chemin.read_bytes()
                cb.relations.exporter(self.liens, self.persos)
                self.assertEqual(premier, chemin.read_bytes())

    def test_relations_source_absente_ou_malformee(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / 'relations.csv'
            with patch.object(cb.relations, 'SOURCE', chemin):
                with self.assertRaisesRegex(SystemExit, 'introuvable'):
                    cb.relations.charger(self.persos)
                chemin.write_text('Mauvaise;Entete\n', encoding='utf-8')
                with self.assertRaisesRegex(SystemExit, 'en-tête'):
                    cb.relations.charger(self.persos)
                chemin.write_text(';'.join(cb.relations.COLONNES) + '\n', encoding='utf-8')
                with self.assertRaisesRegex(SystemExit, 'source vide'):
                    cb.relations.charger(self.persos)

    def test_propositions_separees_des_livrables(self):
        texte = Path('docs/propositions-personnages-centraux.md').read_text(encoding='utf-8')
        self.assertIn('non canonique', texte)
        ids = re.findall(r'^## (P[0-9]+) —', texte, re.M)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(10 <= len(ids) <= 15)
        self.assertLessEqual(set(ids), {r['ID'] for r in self.persos})
        # Les formulations proposées ne doivent pas apparaître dans les sources
        # ni les livrables ; seul ce document constitue l'atelier éditorial.
        propositions = re.findall(r'^- \*\*Désir :\*\* (.+)$', texte, re.M)
        self.assertEqual(len(propositions), len(ids))
        wb, _ = charger_xlsx()
        contenu = ' '.join(str(c.value) for feuille in wb for row in feuille for c in row)
        for fichier in (SRC_PERSOS, SRC_NARR, str(cb.relations.EXPORT),
                        'base_personnages_fictifs.json', cb.CARTE_CANONIQUE):
            contenu += Path(fichier).read_text(encoding='utf-8')
        for proposition in propositions:
            self.assertNotIn(proposition, contenu)


class TestConventions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wb, cls.recs = charger_xlsx()

    def test_noms_uniques(self):
        noms = [r['Nom'] for r in self.recs]
        doublons = {n for n in noms if noms.count(n) > 1}
        self.assertFalse(doublons, f'noms en double : {doublons}')

    def test_pas_de_surnom_incruste_dans_le_nom(self):
        for r in self.recs:
            self.assertNotIn('«', r['Nom'], f'{r["Nom"]} : surnom dans Nom')
            self.assertNotIn('»', r['Nom'], f'{r["Nom"]} : surnom dans Nom')
        bernard = next(r for r in self.recs if r['Nom'] == 'Bernard Tremblay')
        karine = next(r for r in self.recs if r['Nom'] == 'Karine Desrosiers')
        self.assertEqual(bernard['Surnom'], 'Bunker')
        self.assertEqual(karine['Surnom'], 'Zoom')

    def test_adresses_avec_numero_ou_lieu_dit(self):
        for r in self.recs:
            ad = str(r['Adresse']).strip()
            avec_num = re.match(r'^\d+[\s,]', ad)
            lieu_dit = ad.startswith('Lieu-dit :')
            self.assertTrue(avec_num or lieu_dit,
                            f'{r["Nom"]} : adresse sans numéro ni « Lieu-dit : » → {ad!r}')
        pour = ['Bernard Tremblay', 'Félix Otis', 'Gaston Ha! Ha!', 'Justine Fortin',
                'Luc Villeneuve', 'Natasha Vollant', 'William McKenzie']
        for nom in pour:
            self.assertTrue(next(r for r in self.recs if r['Nom'] == nom)['Adresse']
                            .startswith('Lieu-dit :'))

    def test_roles_sans_clan(self):
        for r in self.recs:
            role = str(r['Rôle'])
            self.assertNotRegex(role.lower(), r'\bclan\b', f'{r["Nom"]} : {role}')
            self.assertNotIn('Santini', role, f'{r["Nom"]} : Rôle cité la famille → {role}')
        vittorio = next(r for r in self.recs if r['Nom'] == 'Vittorio Santini')
        self.assertEqual(vittorio['Famille'], 'Santini')

    def test_pas_la_coquille_college(self):
        for r in self.recs:
            for champ in ('Parenté', 'Rôle'):
                v = r.get(champ)
                if isinstance(v, str):
                    self.assertNotIn('collège de', v, f'{r["Nom"]} : coquille « collège »')
        sophie = next(r for r in self.recs if r['Nom'] == 'Sophie Labbé')
        self.assertIn('collègue de Laurie Lavoie', sophie['Parenté'])

    def test_famille_et_branche(self):
        """Le qualificatif entre parenthèses est devenu une colonne à part."""
        for r in self.recs:
            for champ in ('Famille', 'Branche'):
                v = r.get(champ)
                if v:
                    self.assertNotIn('(', str(v),
                                     f'{r["Nom"]} : parenthèses dans {champ} → {v}')
                    self.assertNotIn(')', str(v),
                                     f'{r["Nom"]} : parenthèses dans {champ} → {v}')
        # la paire Famille + Branche regroupe les personnes d'un même foyer :
        # elle doit être cohérente avec la source, et regrouper (~100 foyers
        # pour 213 personnes) sans être vide.
        foyers = [(r['Famille'], r['Branche'] or '') for r in self.recs]
        avec_la_source = [(r['Famille'], r['Branche'] or '')
                          for r in lire_csv_source(SRC_PERSOS)]
        self.assertEqual(foyers, avec_la_source, 'Famille/Branche divergent de la source')
        self.assertEqual(len(set(foyers)), len(set(avec_la_source)))
        self.assertLess(len(set(foyers)), len(foyers))
        self.assertGreater(len(set(foyers)), 1)
        cindy = next(r for r in self.recs if r['Nom'] == 'Cindy Lavoie')
        self.assertEqual(cindy['Famille'], 'Tremblay')
        self.assertEqual(cindy['Branche'], 'Gratien')


class TestGeographie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.recs = charger_xlsx()

    def test_coordonnees_dans_le_bon_arrondissement(self):
        for r in self.recs:
            lat, lon = float(r['Latitude']), float(r['Longitude'])
            amin, amax, omin, omax = BOITES[r['Secteur']]
            self.assertTrue(amin <= lat <= amax and omin <= lon <= omax,
                            f'{r["Nom"]} ({r["Secteur"]}) hors boîte : {lat},{lon}')

    def test_danny_fortin_est_bien_a_chicoutimi(self):
        d = next(r for r in self.recs if r['Nom'] == 'Danny Fortin')
        self.assertEqual(d['Secteur'], 'Chicoutimi')
        self.assertLess(float(d['Longitude']), -71.0)
        self.assertNotIn('Harvey', str(d['Adresse']))

    def test_les_deux_autres_arrondissements_restent_peuples(self):
        """Chicoutimi et Jonquière comptaient 27 et 10 personnages sur 4 et 5
        rues (analyse du 2026-09-13) ; le lot du même jour les a portés à 34 et
        16 sur 8 et 8 rues. On ne redescend plus sous ces planchers."""
        def rues(secteur):
            return {str(r['Adresse']).split(',', 1)[1].strip()
                    for r in self.recs if r['Secteur'] == secteur
                    and not str(r['Adresse']).startswith('Lieu-dit')}
        effectifs = {s: sum(1 for r in self.recs if r['Secteur'] == s)
                     for s in ('Chicoutimi', 'Jonquière')}
        self.assertGreaterEqual(effectifs['Chicoutimi'], 34, effectifs)
        self.assertGreaterEqual(effectifs['Jonquière'], 16, effectifs)
        self.assertGreaterEqual(len(rues('Chicoutimi')), 8, sorted(rues('Chicoutimi')))
        self.assertGreaterEqual(len(rues('Jonquière')), 8, sorted(rues('Jonquière')))


class TestDemographie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.recs = charger_xlsx()

    def test_des_mineurs_humains_existent(self):
        humains = [r for r in self.recs if r['Type'] == 'Humain']
        mineurs = [r for r in humains if int(r['Age']) < 18]
        self.assertEqual({r['Nom'] for r in mineurs}, set(MINEURS))
        for nom, age in MINEURS.items():
            self.assertEqual(int(next(r for r in self.recs if r['Nom'] == nom)['Age']), age)
        ages = sorted(int(r['Age']) for r in humains)
        self.assertEqual(ages[0], 9)

    def test_cohorte_jeune_maintenue(self):
        """La base plafonnait à 6 % de moins de 25 ans (11/172, analyse du
        2026-09-13) : la cohorte ajoutée porte la part à ≥ 10 %, et on ne
        redescend plus sous ce seuil sans le décider explicitement."""
        humains = [r for r in self.recs if r['Type'] == 'Humain']
        jeunes = [r for r in humains if int(r['Age']) < 25]
        part = len(jeunes) / len(humains)
        self.assertGreaterEqual(part, 0.10,
                                f'{len(jeunes)}/{len(humains)} humains de moins de 25 ans '
                                f'({part:.1%}) : cohorte jeune érodée')

    def test_un_seul_animal(self):
        animaux = [r for r in self.recs if r['Type'] == 'Animal']
        self.assertEqual([r['Nom'] for r in animaux], ['Pisse-Feu'])


class TestNarration(unittest.TestCase):
    """La narration est une source PUBLIQUE : versionnée, complète dans le
    classeur, mais volontairement absente des exports géo et de la carte."""

    @classmethod
    def setUpClass(cls):
        cls.narr = lire_csv_source(SRC_NARR)
        _, cls.recs = charger_xlsx()

    def test_source_narration_versionnee(self):
        """Filet de sécurité : la narration doit rester versionnée dans Git."""
        self.assertTrue(os.path.exists(SRC_NARR),
                        f'{SRC_NARR} absente : la narration est publique, elle '
                        'doit vivre dans le dépôt')
        with open('.gitignore', encoding='utf-8') as f:
            self.assertNotIn('data/narration.csv', f.read(),
                             'data/narration.csv ne doit plus être ignoré')
        try:
            suivi = subprocess.run(['git', 'ls-files', SRC_NARR],
                                   capture_output=True, text=True, timeout=15).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            self.skipTest('git indisponible')
        self.assertEqual(suivi, SRC_NARR,
                         f'{SRC_NARR} n’est pas suivi par Git : narration manquante au dépôt !')

    def test_classeur_avec_narration(self):
        """Le classeur contient la feuille Narration, ancien classeur
        « complet » retiré du dépôt."""
        classeur = 'base_personnages_fictifs.xlsx'
        self.assertIn('Narration', openpyxl.load_workbook(classeur).sheetnames)
        with zipfile.ZipFile(classeur) as z:
            xml = ''.join(z.read(n).decode('utf-8', 'ignore')
                          for n in z.namelist() if n.endswith('.xml'))
        for attendu in ('Quote joual', 'Arc S1', 'Lien Spot', 'Faction (détail)'):
            self.assertIn(attendu, xml, f'« {attendu} » absente du classeur')
        complet = 'base_personnages_fictifs-complet.xlsx'
        self.assertFalse(os.path.exists(complet),
                         f'{complet} n’a plus de raison d’être : un seul classeur public')

    def test_narration_pas_exportee(self):
        """Choix de périmètre : la narration ne va ni dans le GeoJSON ni
        dans le JSON ni dans la carte — seule la feuille Narration la porte."""
        with open('base_personnages_fictifs.geojson', encoding='utf-8') as fh:
            gj = json.load(fh)
        for feat in gj['features']:
            self.assertNotIn('faction', feat['properties'])
            self.assertNotIn('quote', str(feat['properties']).lower())
        with open('base_personnages_fictifs.json', encoding='utf-8') as fh:
            js = fh.read().lower()
        self.assertNotIn('arc s1', js)
        self.assertNotIn('quote joual', js)

    def test_couverture_et_vocabulaire(self):
        noms_base = {r['ID'] for r in self.recs}
        noms_narr = {lg['ID'] for lg in self.narr}
        self.assertEqual(noms_narr, noms_base,
                         f'manquants : {noms_base - noms_narr} ; orphelins : {noms_narr - noms_base}')
        for lg in self.narr:
            for champ in ('Faction', 'Lien Spot', 'Quote joual', 'Arc S1'):
                self.assertTrue(str(lg.get(champ) or '').strip(),
                                f'{lg["Nom"]} : champ Narration vide « {champ} »')
            self.assertTrue(str(lg.get('Faction (détail)') or '').strip(),
                            f'{lg["Nom"]} : détail de faction perdu')
        # vocabulaire contrôlé : plus jamais 128 valeurs libres
        with open(SRC_FACTIONS, encoding='utf-8') as f:
            valides = {lg.strip() for lg in f if lg.strip() and not lg.lstrip().startswith('#')}
        fautifs = {lg['Faction'] for lg in self.narr} - valides
        self.assertFalse(fautifs, f'factions hors vocabulaire : {fautifs}')
        # Les libellés du classeur suivent la base par ID, même après renommage.
        base = {r['ID']: r for r in self.recs}
        for lg in cb.charger_narration(self.recs):
            self.assertEqual(lg['Nom'], base[lg['ID']]['Nom'])
            self.assertEqual(lg['Surnom'], base[lg['ID']]['Surnom'])
        # pas de caractère de contrôle (les mêmes règles que la source)
        for lg in self.narr:
            for champ in ('Nom', 'Surnom', 'Faction', 'Faction (détail)',
                          'Lien Spot', 'Quote joual', 'Arc S1'):
                self.assertFalse(any(ord(c) < 32 for c in (lg.get(champ) or '')),
                                 f'{lg["Nom"]} : caractère de contrôle dans « {champ} »')


class TestPortraits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.recs = charger_xlsx()

    def test_deux_gabarits_pour_chaque_personnage(self):
        for r in self.recs:
            web = r['Portrait']
            self.assertTrue(web and os.path.exists(web),
                            f'{r["Nom"]} : portrait web manquant ({web})')
            vig = web.replace('-web.webp', '-vignette.webp')
            self.assertTrue(os.path.exists(vig), f'{r["Nom"]} : vignette manquante ({vig})')

    def test_pas_de_gabarit_archive(self):
        archives = [f for f in glob.glob('portraits/*.webp')
                    if not f.endswith('-web.webp')
                    and not f.endswith('-vignette.webp')
                    and not f.endswith('planche-contact-generale.webp')]
        self.assertEqual(archives, [], f'gabarits archive non référencés : {archives}')

    def test_planche_contact_generee(self):
        self.assertTrue(os.path.exists('portraits/planche-contact-generale.webp'))
        try:
            from PIL import Image
            with Image.open('portraits/planche-contact-generale.webp') as im:
                self.assertEqual(im.width, 2510)  # 10 colonnes × 240 px + marges
        except ImportError:
            self.skipTest('Pillow absent')

    def test_nouveaux_portraits_numerotes(self):
        for base in ('171-leo-cloutier', '172-nour-benali', '173-alexandre-lavoie',
                     '174-maude-pedneault', '183-jade-boivin',
                     '184-gaetan-bosse', '193-marc-picard',
                     '194-yvette-desgagne', '203-julien-desgagne',
                     '204-emma-boucher', '213-karine-simard'):
            self.assertTrue(os.path.exists(f'portraits/{base}-web.webp'), base)
            self.assertTrue(os.path.exists(f'portraits/{base}-vignette.webp'), base)

    def test_la_construction_refuse_un_personnage_sans_portrait(self):
        """Le script se contentait d'un avertissement « portraits introuvables »
        (invisible en CI) : un slug de fichier différent du nom laissait un
        personnage sans photo. Désormais, échec franc."""
        import importlib
        cb = importlib.import_module('construire_base')
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, 'p.csv')
            with open(SRC_PERSOS, encoding='utf-8') as fh:
                lignes = fh.read().splitlines()
            fantome = lignes[1].split(';')
            fantome[0] = 'Personne Inexistante'
            fantome[12] = ''
            with open(src, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join([lignes[0], ';'.join(fantome)]) + '\n')
            ancien = cb.SRC_PERSOS
            cb.SRC_PERSOS = src
            try:
                with self.assertRaises(SystemExit) as cm:
                    cb.charger_personnages()
                self.assertIn('Personne Inexistante', str(cm.exception))
            finally:
                cb.SRC_PERSOS = ancien

    def test_police_vendoriee_pour_la_planche(self):
        self.assertTrue(os.path.exists('assets/fonts/DejaVuSans.ttf'))
        self.assertTrue(os.path.exists('assets/fonts/LICENSE.txt'))


class TestCarte(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('carte/index.html', encoding='utf-8') as f:
            cls.canonique = f.read()
        with open('carte-la-baie-saguenay.html', encoding='utf-8') as f:
            cls.racine = f.read()

    def test_leaflet_vendore_en_local(self):
        for fichier in ('carte/vendor/leaflet/leaflet.js', 'carte/vendor/leaflet/leaflet.css',
                        'carte/vendor/leaflet/LICENSE'):
            self.assertTrue(os.path.exists(fichier), fichier)
        cdn = re.compile(r'https?://[^"\' ]*(unpkg|jsdelivr|cdnjs|googleapis)', re.I)
        for h in (self.canonique, self.racine):
            self.assertIsNone(cdn.search(h), 'dépendance CDN pour le code')
        self.assertIn('"vendor/leaflet/leaflet.js"', self.canonique.replace("'", '"'))
        self.assertIn('"carte/vendor/leaflet/leaflet.js"', self.racine.replace("'", '"'))

    def test_persos_injectes_dans_les_deux_cartes(self):
        for h in (self.canonique, self.racine):
            m = re.search(r'const PERSOS=(\[.*?\]);', h, flags=re.S)
            self.assertIsNotNone(m, 'PERSOS introuvable')
            self.assertEqual(len(json.loads(m.group(1))), N, 'effectif PERSOS')

    def test_la_carte_de_racine_est_derivee_de_la_canonique(self):
        """Une seule source HTML : la copie de racine ne doit pas diverger."""
        attendu = (self.canonique.replace('"vendor/leaflet/', '"carte/vendor/leaflet/')
                                .replace("const RACINE='../';", "const RACINE='';"))
        self.assertEqual(attendu, self.racine,
                         'carte-la-baie-saguenay.html diverge de carte/index.html')

    def test_valeurs_echappees_dans_le_html(self):
        """Les données et les saisies ne doivent pas entrer telles quelles dans innerHTML."""
        self.assertIn('const esc=', self.canonique)
        self.assertGreaterEqual(self.canonique.count('${esc('), 8,
                                'échappement HTML insuffisant')

    def test_injection_carte_resiste_aux_caracteres_speciaux(self):
        """re.subn interprétait le gabarit de remplacement : une valeur contenant
        un saut de ligne, une tabulation ou « \\1 » aurait cassé le JS de la carte
        (ou fait planter la construction). Le remplacement est désormais une
        fonction — vérifié par un aller-retour d'injection réel sur carte temporaire."""
        mechant = 'ligne1\nligne2\t« guillemets » back\\slash \\1 $&'
        js = [{'nom': mechant}]
        with tempfile.TemporaryDirectory() as tmp:
            canon = os.path.join(tmp, 'canonique.html')
            with open(canon, 'w', encoding='utf-8') as f:
                f.write('<script src="vendor/leaflet/leaflet.js"></script>\n'
                        "<script>const RACINE='../';const PERSOS=[];</script>")
            ancien_c, ancien_r = cb.CARTE_CANONIQUE, cb.CARTE_RACINE
            cb.CARTE_CANONIQUE = canon
            cb.CARTE_RACINE = os.path.join(tmp, 'racine.html')
            try:
                cb.ecrire_cartes(js)
            finally:
                cb.CARTE_CANONIQUE, cb.CARTE_RACINE = ancien_c, ancien_r
            with open(canon, encoding='utf-8') as f:
                h = f.read()
            m = re.search(r'const PERSOS=(\[.*?\]);', h, flags=re.S)
            self.assertIsNotNone(m, 'PERSOS introuvable après injection')
            self.assertEqual(json.loads(m.group(1))[0]['nom'], mechant,
                             'aller-retour JSON corrompu par l’injection')

    def test_bandeau_avertissement_visible_sur_mobile(self):
        """À ≤ 820 px, la sidebar devient un tiroir FERME et le CSS de base masque
        .banner : sans règle de rappel, l'avertissement « fiction / adresses
        inventées / portraits IA » ne s'affiche plus sur téléphone. La media query
        mobile doit ré-afficher le bandeau d'en-tête."""
        self.assertIn('Portraits générés par intelligence artificielle', self.canonique)
        for nom, h in (('carte/index.html', self.canonique),
                       ('carte-la-baie-saguenay.html', self.racine)):
            m = re.search(r'@media\(max-width:820px\)\{', h)
            self.assertIsNotNone(m, f'{nom} : media query 820 px introuvable')
            i, profondeur = m.end(), 1
            while profondeur > 0:
                profondeur += (h[i] == '{') - (h[i] == '}')
                i += 1
            self.assertRegex(h[m.end():i], r'\.banner\{[^}]*display:block',
                             f'{nom} : bandeau non ré-affiché sur mobile')

    def test_licence_leaflet_presente(self):
        with open('carte/vendor/leaflet/LICENSE', encoding='utf-8') as fh:
            self.assertIn('BSD', fh.read())


class TestDocumentationEtLicences(unittest.TestCase):
    def test_analyse_actuelle_chiffres(self):
        texte = Path('docs/analyse-projet.md').read_text(encoding='utf-8')
        persos = cb.charger_personnages()
        narr = cb.charger_narration(persos)
        liens = cb.relations.charger(persos)
        propositions = Path('docs/propositions-personnages-centraux.md').read_text(encoding='utf-8')
        chiffres = {
            'Personnages': len(persos),
            'Humains': sum(r['Type'] == 'Humain' for r in persos),
            'Animal': sum(r['Type'] == 'Animal' for r in persos),
            'Mineurs humains': sum(r['Type'] == 'Humain' and r['Age'] < 18 for r in persos),
            'Familles': len({r['Famille'] for r in persos}),
            'Foyers Famille/Branche': len({(r['Famille'], r['Branche']) for r in persos}),
            'Colonnes Personnages': len(cb.COLONNES),
            'Fiches Narration': len(narr),
            'Colonnes Narration': len(cb.NARR_COLS),
            'Factions autorisées': len(cb.lire_factions()),
            'Relations explicites structurées': len(liens),
            'Personnages reliés dans cette tranche': len({r[k] for r in liens
                                                         for k in ('Source_ID', 'Cible_ID')}),
            'Propositions de personnages centraux': len(re.findall(r'^## P[0-9]+ —',
                                                                   propositions, re.M)),
        }
        for secteur in {r['Secteur'] for r in persos}:
            chiffres[secteur] = sum(r['Secteur'] == secteur for r in persos)
        for libelle, valeur in chiffres.items():
            with self.subTest(indicateur=libelle):
                self.assertIn(f'| {libelle} | {valeur} |', texte)
        total = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]).countTestCases()
        self.assertIn(f'| Python | {total} |', texte)

    def test_documentation_distingue_archive_et_actuel(self):
        archive = Path('docs/historique/analyse-173-personnages.md').read_text(encoding='utf-8')
        actuel = Path('docs/analyse-projet.md').read_text(encoding='utf-8')
        readme = Path('README.md').read_text(encoding='utf-8')
        self.assertIn('Document historique, non représentatif de l’état actuel', archive[:1000])
        self.assertIn('(../analyse-projet.md)', archive[:1000])
        self.assertIn('(historique/analyse-173-personnages.md)', actuel)
        self.assertIn('publique et versionnée', actuel)
        self.assertIn('non canonique', actuel)
        self.assertNotIn('régénère les deux classeurs', readme)
        licences = Path('LICENSE-DONNEES.md').read_text(encoding='utf-8')
        mineurs = [r for r in cb.charger_personnages() if r['Type'] == 'Humain' and r['Age'] < 18]
        self.assertIn(f'{len(mineurs)} personnages humains', licences)

    def test_liens_markdown_locaux(self):
        from urllib.parse import unquote, urlsplit
        documents = [Path('README.md'), Path('CHANGELOG.md'), Path('LICENSE-DONNEES.md'),
                     *Path('docs').rglob('*.md')]
        for document in documents:
            texte = document.read_text(encoding='utf-8')
            # Vérifie les cibles fichier des liens Markdown inline ; les ancres
            # et liens distants restent hors de ce contrôle sans réseau.
            for cible in re.findall(r'\]\(([^)]+)\)', texte):
                url = urlsplit(cible)
                if url.scheme or url.netloc or not url.path:
                    continue
                chemin = document.parent / unquote(url.path)
                with self.subTest(document=str(document), lien=cible):
                    self.assertTrue(chemin.exists(), f'Lien local cassé : {chemin}')

    def test_readme_est_a_jour(self):
        self.assertTrue(os.path.exists('README.md'))
        self.assertFalse(os.path.exists('README.txt'), 'README.txt fait doublon')
        with open('README.md', encoding='utf-8') as fh:
            h = fh.read()
        for mot in (str(N), 'ODbL', 'MIT', 'générées par IA', 'planche-contact-generale',
                    'Lieu-dit', 'data/personnages.csv', 'Famille', 'Branche'):
            self.assertIn(mot, h, f'README.md oublie « {mot} »')

    def test_readme_annonce_le_bon_nombre_de_tests(self):
        """Le README annonçait « 26 tests » : la doc ne doit plus dériver."""
        total = unittest.defaultTestLoader.loadTestsFromModule(
            sys.modules[__name__]).countTestCases()
        with open('README.md', encoding='utf-8') as fh:
            h = fh.read()
        annonces = {int(n) for n in re.findall(r'(\d{2,3})\s+(?:tests|garde-fous)', h)}
        self.assertTrue(annonces, 'le README doit annoncer un nombre de tests')
        self.assertIn(total, annonces, f'README annonce {annonces} ; {total} réellement exécutés')

    def test_trois_statuts_de_licence_distincts(self):
        self.assertTrue(os.path.exists('LICENSE-DONNEES.md'))
        with open('LICENSE-DONNEES.md', encoding='utf-8') as fh:
            d = fh.read()
        for mot in ('MIT', 'ODbL', 'OpenStreetMap', 'CC BY 4.0', 'IA'):
            self.assertIn(mot, d, f'LICENSE-DONNEES.md oublie « {mot} »')
        with open('LICENSE', encoding='utf-8') as fh:
            self.assertIn('MIT License', fh.read())

    def test_lisez_moi_annonce_le_bon_effectif_et_la_source(self):
        wb, _ = charger_xlsx()
        textes = ' '.join(str(c.value) for row in wb['Lisez-moi'].iter_rows() for c in row
                          if c.value)
        self.assertIn(f'{N} entrées', textes)
        self.assertNotIn('140 personnages', textes)
        self.assertNotIn('160 lignes', textes)
        self.assertIn('data/personnages.csv', textes)

    def test_outillage_present(self):
        for f in ('requirements.txt', 'requirements-dev.txt', '.gitignore', '.gitattributes',
                  '.pre-commit-config.yaml', 'CHANGELOG.md', 'ruff.toml',
                  '.github/workflows/validation.yml', 'scripts/retirer_archives_git.sh'):
            self.assertTrue(os.path.exists(f), f'{f} absent')


class TestReproductibilite(unittest.TestCase):
    def test_pas_d_horloge_dans_le_xlsx(self):
        """La date attendue est dérivée du script : le test suit SOURCE_DATE_EPOCH."""
        iso = cb.DATE_LIVRABLE.strftime('%Y-%m-%dT%H:%M:%SZ')
        with zipfile.ZipFile('base_personnages_fictifs.xlsx') as z:
            core = z.read('docProps/core.xml').decode('utf-8')
        self.assertIn(iso, core)
        created = re.search(r'<dcterms:created[^>]*>([^<]+)</dcterms:created>', core).group(1)
        modified = re.search(r'<dcterms:modified[^>]*>([^<]+)</dcterms:modified>', core).group(1)
        self.assertEqual(created, modified)


if __name__ == '__main__':
    unittest.main(verbosity=2)
