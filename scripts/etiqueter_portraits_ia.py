#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Étiquette les portraits comme images générées par IA (métadonnées XMP).

Pourquoi un script séparé : les portraits ne sont pas des livrables générés,
ce sont des **sources** committées. Réécrire ces images avec Pillow les
réencoderait (perte de qualité, octets différents, dépendance au codec) à chaque
exécution. On insère donc le paquet XMP **au niveau du conteneur RIFF** : la
donnée image (chunk `VP8 `) est recopiée telle quelle, sans aucun réencodage.

Ce que l'étiquette contient (`XMP ` chunk, format étendu « VP8X ») :

- `Iptc4xmpExt:DigitalSourceType` = `trainedAlgorithmicMedia` : la valeur
  normalisée de l'IPTC pour un média produit par un système entraîné
  (source unique reconnue par les plateformes et les outils de catalogage) ;
- le titre (nom du personnage) et une description en français rappelant qu'il
  s'agit d'un **personnage de fiction** et d'une **image générée par IA** ;
- les droits : CC BY 4.0, avec le lien de la licence, et l'attribution
  « Projet La Baie (Saguenay) ».

L'étiquetage vit ainsi **dans le fichier** : une vignette sortie du dépôt,
recopiée dans un document ou un diaporama, garde sa mention d'origine.

Idempotent : un fichier déjà étiqueté avec le paquet attendu n'est pas réécrit.
Usage :  python3 scripts/etiqueter_portraits_ia.py [--verifier]

  --verifier   ne modifie rien, sort en erreur si une image n'est pas étiquetée
               (utilisé par les tests et par la CI).
"""
import csv
import glob
import os
import struct
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PERSOS = os.path.join(RACINE, 'data', 'personnages.csv')
GABARITS = ('*-web.webp', '*-vignette.webp')
DOSSIERS = ('portraits', os.path.join('carte', 'portraits'))

# Drapeaux du chunk VP8X (bit 0 = poids faible du premier octet).
BIT_ICCP, BIT_ALPHA, BIT_EXIF, BIT_XMP = 0x20, 0x10, 0x08, 0x04
MARQUEUR = 'trainedAlgorithmicMedia'
LICENCE = 'https://creativecommons.org/licenses/by/4.0/'
ATTRIBUTION = 'Projet La Baie (Saguenay)'
DESCRIPTION = ('Portrait d’un personnage de fiction du projet La Baie (Saguenay), '
               'entièrement généré par intelligence artificielle. Aucune personne '
               'réelle n’a été photographiée ; toute ressemblance avec une personne '
               'existante serait fortuite. Adresses et situations sont inventées.')


# ------------------------------------------------------------------ XMP
def _xml(texte):
    return (texte.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def paquet_xmp(nom=None, identifiant=None, titre=None):
    """Paquet XMP déterministe (aucun horodatage) pour un portrait."""
    if titre is None:
        titre = (f'{nom} ({identifiant}) — personnage fictif' if nom and identifiant
                 else (nom or 'Portrait de personnage fictif'))
    langues = (f'<rdf:li xml:lang="x-default">{_xml(titre)}</rdf:li>'
               f'<rdf:li xml:lang="fr-CA">{_xml(titre)}</rdf:li>')
    return (
        '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '  <rdf:Description rdf:about=""\n'
        '    xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        '    xmlns:xmp="http://ns.adobe.com/xap/1.0/"\n'
        '    xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/"\n'
        '    xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/">\n'
        f'   <dc:title><rdf:Alt>{langues}</rdf:Alt></dc:title>\n'
        f'   <dc:description><rdf:Alt><rdf:li xml:lang="fr-CA">{_xml(DESCRIPTION)}'
        '</rdf:li></rdf:Alt></dc:description>\n'
        f'   <dc:creator><rdf:Seq><rdf:li>{_xml(ATTRIBUTION)}</rdf:li></rdf:Seq></dc:creator>\n'
        f'   <dc:rights><rdf:Alt><rdf:li xml:lang="fr-CA">Portrait généré par IA — '
        f'{_xml(ATTRIBUTION)}, CC BY 4.0</rdf:li></rdf:Alt></dc:rights>\n'
        '   <xmp:CreatorTool>Générateur d’images par intelligence artificielle</xmp:CreatorTool>\n'
        '   <xmpRights:Marked>True</xmpRights:Marked>\n'
        f'   <xmpRights:WebStatement>{LICENCE}</xmpRights:WebStatement>\n'
        f'   <Iptc4xmpExt:DigitalSourceType>http://cv.iptc.org/newscodes/'
        f'digitalsourcetype/{MARQUEUR}</Iptc4xmpExt:DigitalSourceType>\n'
        '  </rdf:Description>\n'
        ' </rdf:RDF>\n'
        '</x:xmpmeta>\n'
        '<?xpacket end="w"?>'
    ).encode('utf-8')


# ------------------------------------------------------------------ conteneur RIFF
def lire_chunks(data):
    """Découpe un fichier WebP en (fourcc, corps). Lève ValueError si invalide."""
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        raise ValueError('ce n’est pas un fichier WebP (RIFF/WEBP)')
    pos, chunks = 12, []
    while pos + 8 <= len(data):
        fourcc = data[pos:pos + 4]
        taille = struct.unpack('<I', data[pos + 4:pos + 8])[0]
        if pos + 8 + taille > len(data):
            raise ValueError(f'chunk {fourcc!r} tronqué')
        chunks.append((fourcc, data[pos + 8:pos + 8 + taille]))
        pos += 8 + taille + (taille & 1)
    return chunks


def ecrire_chunks(chunks):
    corps = b''.join(
        fourcc + struct.pack('<I', len(donnees)) + donnees + (b'\0' if len(donnees) % 2 else b'')
        for fourcc, donnees in chunks)
    return b'RIFF' + struct.pack('<I', 4 + len(corps)) + b'WEBP' + corps


def dimensions(chunks):
    for fourcc, corps in chunks:
        if fourcc == b'VP8X':
            return (int.from_bytes(corps[4:7], 'little') + 1,
                    int.from_bytes(corps[7:10], 'little') + 1)
        if fourcc == b'VP8 ':
            if corps[3:6] != b'\x9d\x01\x2a':
                raise ValueError('en-tête VP8 inattendu')
            return (struct.unpack('<H', corps[6:8])[0] & 0x3FFF,
                    struct.unpack('<H', corps[8:10])[0] & 0x3FFF)
        if fourcc == b'VP8L':
            bits = int.from_bytes(corps[1:5], 'little')
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError('dimensions introuvables')


def drapeaux(chunks):
    """Drapeaux VP8X correspondant aux chunks réellement présents."""
    vus = {fourcc for fourcc, _ in chunks}
    valeur = 0
    if b'ICCP' in vus:
        valeur |= BIT_ICCP
    if b'ALPH' in vus:
        valeur |= BIT_ALPHA
    if b'EXIF' in vus:
        valeur |= BIT_EXIF
    return valeur


def paquet_present(data):
    """Retourne le paquet XMP du fichier, ou None."""
    for fourcc, corps in lire_chunks(data):
        if fourcc == b'XMP ':
            return corps
    return None


def inserer_xmp(data, paquet):
    """Insère (ou remplace) le chunk XMP sans toucher à la donnée image.

    Le format étendu « VP8X » est créé s'il manque, et le chunk `XMP ` est
    placé en fin de fichier, conformément à l'ordre recommandé par la
    spécification WebP (après la donnée image et `EXIF`).
    """
    chunks = lire_chunks(data)
    autres = [(fourcc, corps) for fourcc, corps in chunks if fourcc not in (b'VP8X', b'XMP ')]
    larg, haut = dimensions(chunks)
    valeur = drapeaux(autres) | BIT_XMP
    entete = bytes([valeur, 0, 0, 0]) + (larg - 1).to_bytes(3, 'little') + (haut - 1).to_bytes(3, 'little')
    return ecrire_chunks([(b'VP8X', entete)] + autres + [(b'XMP ', paquet)])


# ------------------------------------------------------------------ application
def personnages_par_portrait():
    """Chemin Portrait → (Nom, ID), pour titrer chaque image."""
    correspondance = {}
    with open(SRC_PERSOS, newline='', encoding='utf-8') as f:
        for ligne in csv.DictReader(f, delimiter=';'):
            if ligne.get('Portrait'):
                correspondance[ligne['Portrait']] = (ligne['Nom'], ligne['ID'])
    return correspondance


def cibles():
    fichiers = []
    for dossier in DOSSIERS:
        for gabarit in GABARITS:
            fichiers += glob.glob(os.path.join(RACINE, dossier, gabarit))
    return sorted(set(fichiers))


def etiqueter(verifier=False):
    correspondance = personnages_par_portrait()
    ajoutes, remplaces, deja, ignores = 0, 0, 0, []
    for chemin in cibles():
        relatif = os.path.relpath(chemin, RACINE)
        # La vignette porte le même titre que le portrait correspondant.
        source = relatif.replace('-vignette.webp', '-web.webp')
        source = source if source.startswith('portraits/') else 'portraits/' + os.path.basename(source)
        nom, identifiant = correspondance.get(source, (None, None))
        paquet = paquet_xmp(nom, identifiant)
        with open(chemin, 'rb') as f:
            data = f.read()
        try:
            present = paquet_present(data)
        except ValueError as e:
            ignores.append(f'{relatif} ({e})')
            continue
        if present == paquet:
            deja += 1
            continue
        if verifier:
            ignores.append(f'{relatif} : étiquette {"absente" if present is None else "périmée"}')
            continue
        nouveau = inserer_xmp(data, paquet)
        with open(chemin, 'wb') as f:
            f.write(nouveau)
        if present is None:
            ajoutes += 1
        else:
            remplaces += 1
    return ajoutes, remplaces, deja, ignores


def main(argv):
    verifier = '--verifier' in argv
    if not os.path.isdir(os.path.join(RACINE, 'portraits')):
        raise SystemExit('✘ lancer le script depuis le dépôt (portraits/ introuvable)')
    ajoutes, remplaces, deja, ignores = etiqueter(verifier)
    if verifier:
        if ignores:
            print(f'✘ {len(ignores)} image(s) sans étiquette IA à jour :')
            for ligne in ignores[:20]:
                print('   -', ligne)
            return 1
        print(f'✔ {deja} image(s) étiquetées « {MARQUEUR} » (aucune modification).')
        return 0
    print(f'✔ {ajoutes} étiquette(s) ajoutée(s), {remplaces} remplacée(s), '
          f'{deja} déjà à jour.')
    if ignores:
        print('  ! ignoré(s) :', ', '.join(ignores))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
