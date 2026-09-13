#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/migrer_corrections.py — application UNE FOIS des corrections de la révision
du 2026-09-12 dans le classeur maître base_personnages_fictifs.xlsx.

Idempotent : chaque correction est appliquée par valeur (une seconde exécution ne
change rien). Après migration, lancer « python3 construire_base.py » pour régénérer
tous les livrables.

Corrections appliquées :
  4. Danny Fortin : déplacé de « 2140, Boulevard Harvey » (Jonquière, 20 km plus
     loin) vers une adresse chicoutimienne cohérente avec son secteur.
  5. Sophie Labbé : « collège de Laurie Lavoie » → « collègue de Laurie Lavoie ».
  6. Conventions : 7 adresses sans numéro → « Lieu-dit : … » ; 5 rôles citant le
     « clan Santini » (interdit par le dictionnaire) reformulés ; 2 noms qui
     contenaient le surnom entre « » vidés (le surnom reste dans sa colonne).
  9. Feuille Narration : complétée à 100 % (173/173 lignes).
 10. Angle mort démographique : 3 mineurs humains ajoutés (9, 13 et 16 ans).
"""
import os
import sys
import shutil

import openpyxl

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(RACINE, 'base_personnages_fictifs.xlsx')
FEUILLE = 'Personnages'
NARR_SHEET = 'Narration'

# ---------------------------------------------------------------- portraits
# Sources PNG des 3 nouveaux personnages (générées par IA, style documentaire).
NOUVEAUX_PORTRAITS = {
    'Léo Cloutier':   ('171-leo-cloutier',       'portraits/nouveaux/lio-cloutier-web.png'),
    'Nour Benali':    ('172-nour-benali',         'portraits/nouveaux/nora-benali-web.png'),
    'Alexandre Lavoie': ('173-alexandre-lavoie',  'portraits/nouveaux/alex-lavoie-web.png'),
}

# Renommages de fichiers imposés par la convention « le surnom ne va PAS dans Nom ».
FICHIERS_RENOMMES = {
    '149-karine-zoom-desrosiers': '149-karine-desrosiers',
    '150-bernard-bunker-tremblay': '150-bernard-tremblay',
}

# ------------------------------------------------------------ corrections #4/#5/#6
CORRECTIONS = {
    # #4 — Danny Fortin : secteur Chicoutimi mais situé géographiquement à Jonquière.
    'Danny Fortin': {
        'Adresse': '590, Rue Racine Est',
        'Latitude': 48.426900,
        'Longitude': -71.053500,
    },
    # #5 — coquille « collège » → « collègue ».
    'Sophie Labbé': {
        'Parenté': 'Célibataire — collègue de Laurie Lavoie',
    },
    # #6a — adresses sans numéro civique : convention « Lieu-dit : … ».
    # (Bernard cumule adresse + renommage du Nom, voir aussi #6c plus bas.)
    'Bernard « Bunker » Tremblay': {
        'Adresse': 'Lieu-dit : chemin forestier du Petit-Parc',
        'Nom': 'Bernard Tremblay',
    },
    'Félix Otis':                  {'Adresse': 'Lieu-dit : baie des Ha! Ha!'},
    'Gaston Ha! Ha!':              {'Adresse': 'Lieu-dit : près de la Pyramide des Ha! Ha!'},
    'Justine Fortin':              {'Adresse': 'Lieu-dit : centre de ski Bec-Scie'},
    'Luc Villeneuve':              {'Adresse': 'Lieu-dit : Base de Bagotville, secteur ouest'},
    'Natasha Vollant':             {'Adresse': 'Lieu-dit : sentier Eucher'},
    'William McKenzie':            {'Adresse': 'Lieu-dit : Base de Bagotville (3e Escadre)'},
    # #6b — le « clan » n'a pas à apparaître dans Rôle : la Famille porte le clan,
    # la feuille Narration porte la faction.
    'Rico Leduc':     {'Rôle': 'Homme de main — recouvrement de dettes'},
    'Julien Gagné':   {'Rôle': 'Chauffeur de voiture de ville'},
    'Nico Santini':   {'Rôle': 'Préposé à la sécurité — restaurant'},
    'Vittorio Santini': {'Rôle': 'Homme d’affaires — restauration et bars'},
    'Enzo Bianchi':   {'Rôle': 'Conseiller en gestion d’entreprise'},
    # #6c — le surnom ne vit que dans la colonne Surnom.
    'Karine « Zoom » Desrosiers':  {'Nom': 'Karine Desrosiers'},
}
# Table de correspondance nouveau nom → ancien nom (et son inverse), pour
# rester idempotent : après la première passe, les « » ont disparu de Nom.
ANCIEN_NOM = {
    'Bernard Tremblay': 'Bernard « Bunker » Tremblay',
    'Karine Desrosiers': 'Karine « Zoom » Desrosiers',
}
ANCIEN_VERS_NOUVEAU = {ancien: nouveau for nouveau, ancien in ANCIEN_NOM.items()}

# --------------------------------------------------------------- #10 mineurs
NOUVEAUX = [
    {
        'Nom': 'Léo Cloutier', 'Surnom': 'Lio', 'Type': 'Humain', 'Age': 9,
        'Rôle': 'Livreur de circulaires — porte-à-porte',
        'Secteur': 'La Baie', 'Adresse': '69, Rue des Bouleaux',
        'Latitude': 48.344620, 'Longitude': -70.897880,
        'Apparence': 'Taches de rousseur, mèche rousse qui dépasse de la tuque',
        'Vêtements': 'Parka d’hiver trop grande, tuque bleue, mitaines trouées',
        'Tic / Objet': 'Sac de toile et liasses de circulaires',
        'Portrait': 'portraits/171-leo-cloutier-web.webp',
        'Famille': 'Cloutier',
        'Parenté': 'Fils de Manon Cloutier — petit frère de Dave',
    },
    {
        'Nom': 'Nour Benali', 'Surnom': None, 'Type': 'Humain', 'Age': 13,
        'Rôle': 'Élève du secondaire — aide au dépanneur',
        'Secteur': 'La Baie', 'Adresse': '1314, Rue Victoria',
        'Latitude': 48.345450, 'Longitude': -70.879750,
        'Apparence': 'Hijab beige, cahiers d’école empilés sous le comptoir',
        'Vêtements': 'Fleece marine et jeans',
        'Tic / Objet': 'Manuels scolaires ouverts sur le comptoir-caisse',
        'Portrait': 'portraits/172-nour-benali-web.webp',
        'Famille': 'Benali',
        'Parenté': 'Fille d’Ahmed et Nadia Benali — sœur d’Hassan',
    },
    {
        'Nom': 'Alexandre Lavoie', 'Surnom': 'Le Cadet', 'Type': 'Humain', 'Age': 16,
        'Rôle': 'Joueur — hockey juvénile',
        'Secteur': 'La Baie', 'Adresse': '147, Avenue Lavoie',
        'Latitude': 48.325180, 'Longitude': -70.877400,
        'Apparence': 'Joue ronde, premier duvet, cheveux sous la tuque',
        'Vêtements': 'Veston de hockey par-dessus un hoodie',
        'Tic / Objet': 'Bâton de hockey et patins éraflés',
        'Portrait': 'portraits/173-alexandre-lavoie-web.webp',
        'Famille': 'Lavoie (JP)',
        'Parenté': 'Fils cadet de Robert et Diane — petit frère de JP',
    },
]

# ----------------------------------------------------------------- #9 narration
# (Faction, Lien Spot, Quote joual, Arc S1, âge apparent) pour TOUT personnage
# absent de la feuille Narration d'origine (40 lignes → 173).
NARR = {
 # --- La Baie ---
 'Alain Côté': ('Poste / Neutre', 'Passe au 427 chaque midi', "J'livre le courrier, pas les secrets.", 'Voit Roger fouiller les boîtes', 46),
 'Alexis Côté': ('Ruelle', 'Fait les rez-de-chaussée du bloc', 'Une porte barrée, c’est juste une opinion.', 'Se fait acheter par Dévon puis dérape', 31),
 'Alexis Gagnon': ('Aréna / Neutre', 'Coéquipier d’Alexandre Lavoie', 'Lève la rondelle, pas tes patins.', 'Tente de sortir le Cadet de la rue', 29),
 'Aline Tremblay': ('Famille / Gratien', 'Mère de Gratien, clope au 3e', 'Mange donc, tu sens la fumée.', 'Coupe les vivres à son fils', 72),
 'Amina Traoré': ('Santé / Propre', 'Pharmacie du quartier, voit les ordonnances', 'Sans papier, j’vends rien, même à toi.', 'Repère les ordonnances détournées', 38),
 'Amélie Martel': ('Ville / Tourisme', 'Vérifie les permis de location', 'L’image du fjord, c’est pas ça.', 'Ferme les locations illégales du bloc', 42),
 'Anne Girard': ('Santé / Propre', 'Soigne les dents du quartier', 'Qui s’est battu, cette fois ?', 'Constate les blessures de Lio', 47),
 'Armand Lacroix': ('Institutions', 'Neveu de Lucien, salon funéraire', 'Une place, j’en garde toujours une.', 'Prépare la première chapelle ardente', 62),
 'Bernard Tremblay': ('Ruelle / Survivaliste', 'Vend des conserves à Dévon', 'Quand ça va péter, tu vas m’revoir.', 'Son abri sert de planque', 51),
 'Bertrand Gagnon': ('Argent', 'Ex-mari de Sylvie, connaît les baux', 'Le problème, c’est jamais la maison, c’est le monde.', 'Tente de racheter le bloc avec elle', 61),
 'Big Jo Bérubé': ("Ruelle d'en Face", 'Cousin de Kevin, travaille pour Dévon', 'Bouge pas. Bon chien.', 'Premier à frapper au Spot', 33),
 'Bobby Gagnon': ('Motards / Louche', 'Reçoit la marchandise volée', "Ça tombe d'un camion, ça se ramasse.", 'Écoule le matériel piraté', 52),
 'Carl Dubé': ('Garage / Neutre', 'Frère de Mélo, tient le garage', "Ton char est mort comme l'hiver.", 'Cache le véhicule volé du réseau', 33),
 'Chantal Gauthier': ('Commerce / Neutre', 'Voit tout le monde au Tim du coin', 'Un double-double, pis tes histoires itou.', 'Refuse sa table à Dévon', 43),
 'Cindy Lavoie': ('Ruelle', 'Estafette de Gratien, fille de Manon', "J'livre, j'pose, j'me sauve.", 'Ouvre une liasse qui contient pas d’la dope', 26),
 'Claude Lavoie': ('Média / Rang', 'Père de Michel, ex-animateur radio', 'En ondes, on dit la vraie vérité.', 'Reprend l’antenne avec Raymond', 70),
 'Corinne Noël': ('Ruelle / Marge', 'Fournit Sam Aubin en motifs', 'La mort, ça se brosse, tu sais.', 'Fait disparaître un trophée gênant', 44),
 'Cécile Truchon': ('Famille / Truchon', 'Mère d’Yvan, garde la caisse', 'Mon fils est pas pire qu’un autre.', 'Décide de parler des cigarettes', 74),
 'Céline Pedneault': ('Port / Neutre', 'Répare les filets avec Réjean', 'Le fjord nous doit rien.', 'Trouve un ballot dans ses filets', 64),
 'Dominic Audet': ('Taxi / Neutre', 'Dépose tout le monde au Spot à 3 h', 'J’tourne pas la tête, j’tourne le coin.', 'Son carnet de courses accuse', 38),
 'Éric Boucher': ("Ruelle d'en Face", 'Frère de Dévon, ferrailleur', 'La ferraille pèse, les secrets itou.', 'Exécute la casse sans poser de question', 37),
 'Fernand Côté': ('Vieux bloc / Port', 'Voisin du Spot, ex-dockeur', 'Au quai, on parlait pas.', 'Reconnaît le conteneur de Sal', 72),
 'Fernande Boucher': ("Ruelle d'en Face / Famille", 'Mère de Dévon et d’Éric', 'Mon gars est dur, mais c’t’un tendre.', 'Vient plaider pour son fils', 62),
 'France Boivin': ('Commerce / Neutre', 'Fleuriste, sœur de Maxime', 'Des fleurs, ça dit tout sans parler.', 'Prépare les couronnes anonymes', 55),
 'François Harvey': ('Hydro / Syndicat', 'Oncle de Mélissa, monteur de ligne', "L'hiver, la ligne décide.", 'Rétablit le courant après la descente', 45),
 'Frère Ézéchiel': ('Église / Marge', 'Harangue Lucien dans la rue', 'La fournaise vous attend, mes agnelets !', 'Prophétise l’incendie du bloc', 71),
 'Félix Otis': ('Fjord / Neutre', 'Neveu de Jeanne Otis, nage en eau glacée', "Quand l'eau m'ordonne, j'obéis.", 'Repêche une preuve dans la baie', 38),
 'Gaston Ha! Ha!': ('Pyramide / Neutre', 'Vit pour la Pyramide des Ha! Ha!', 'Cédez ! Cédez ! Cédez !', 'Voit un échange nocturne au bord de l’eau', 60),
 'Gaston Pelletier': ('Bar du Coin / Famille', 'Père d’Hugo, grand-père de Léa', 'Mon bar, c’tait du monde, pas du bruit.', 'Raconte qui tenait le Coin avant', 74),
 'Gaétan Lavoie': ('Ruelle / Lavoie', 'Père de Chantal, journalier', "Une job, j'prends. Une fierté, j'ai.", 'Refuse que Chantal plonge avec Gratien', 55),
 'Gisèle Truchon': ('Famille / Truchon', 'Conjointe d’Yvan, caissière de route', 'La caisse, j’la compte deux fois.', 'Voit les paquets passer au dépanneur', 48),
 'Guy Tremblay': ('Ruelle', 'Relais d’Yvan sur le Petit-Parc', 'Du Next, du vrai, pas d’la cendre.', 'Se fait pincer avec une cargaison', 39),
 'Hassan Benali': ('Dépanneur / Neutre', 'Fils d’Ahmed et Nadia', 'Crédit ? Mon père dit non en deux langues.', 'Reconnaît les clients de Gratien', 20),
 'Nour Benali': ('Dépanneur / Famille', 'Fait ses devoirs sur le comptoir', 'Maman, quelqu’un veut encore du crédit.', 'Tient le vrai registre des dettes', 13),
 'Hugo Pelletier': ('Bar du Coin', 'Patron du Coin, époux de Sarah', 'Dehors, tu reviendras sobre.', 'Impose le Coin comme zone neutre', 49),
 'Hélène Blackburn': ('Hôpital / Aide', 'Directrice de l’Hôpital de La Baie', 'Un lit, ça se mérite pas, ça se donne.', 'Ouvre les dossiers de surdoses', 63),
 'Hélène Chicoine': ('Famille / Chicoine', 'Mère de Réal', 'Mon fils est doux, comprenez-vous.', 'Réclame Réal après sa disparition', 70),
 'Isabelle Bergeron': ('École / Aide', 'Institutrice primaire, fille de Gilles', 'Les enfants parlent, faut écouter.', 'Signale les bleus de Lio', 44),
 'Jacques Maltais': ('Ville / Argent', 'Conseiller d’arrondissement La Baie', 'La Baie, ça se gère comme un gros frigidaire.', 'Subit les pressions d’expulsion', 63),
 'Jeanne Gagnon': ('Argent / Famille', 'Mère de Sylvie, héritière', 'Les briques meurent pas, les familles oui.', 'Lègue le bloc à la surprise générale', 82),
 'Jeanne Otis': ('Bibliothèque / Neutre', 'Bibliothécaire, tante de Félix', 'Chut. Les livres écoutent tout.', 'Cache Ti-Coune en section jeunesse', 66),
 'Jessica Paradis': ('Locataires / Neutre', 'Locataire de Sylvie Gagnon', 'Mon loyer est payé. En tout cas, j’pense.', 'Témoin des visites d’expulsion', 27),
 'Jessy Bérubé': ('Ruelle / Bérubé', 'Frère de Kevin, entrepôt', "J'porte, j'pose, j'demande rien.", 'Remplace Big Jo quand ça tourne mal', 24),
 'Josée Langlois': ('1er étage', 'Femme du Plombier, secrétaire de chantier', 'La facture va suivre, comme toujours.', 'Photographie les dégâts à son tour', 42),
 'Julie Martel': ('Tourisme / Neutre', 'Guide des croisières, sœur d’Amélie', 'Sur le fjord, pas de Wi-Fi, juste des baleines.', 'Voit un transfert depuis le large', 32),
 'Justine Fortin': ('Bec-Scie / Neutre', 'Patrouilleuse, nièce d’Yves', 'La neige cache tout, sauf les traces.', 'Découvre la planque de Bernard', 37),
 'Karim Al-Hassan': ('Rue / Neutre', 'Cuisinier du camion, mari de Fatima', 'Sans piasse ? Une assiette quand même.', 'Le camion cantine devient QG neutre', 36),
 'Karine Desrosiers': ("Bloc d'en Face", 'Cousine d’Anik, archiviste de plaques', 'Une plaque, c’est une confession en métal.', 'Retrace le VUS de la soirée Chen', 33),
 'Kim Boudreault': ('Urgences / Aide', 'Paramédic, tourne au Spot les nuits de bagarre', 'Respire. Reste avec moi.', 'Témoin des appels coupés au 427', 29),
 'Linda Tremblay': ('Ruelle', 'Conjointe de Gratien, préposée d’entretien', "J'récure, j'vois rien, c'est mon don.", 'Quitte Gratien et parle à Samson', 43),
 'Lise Blackburn': ('CLSC / Aide', 'Travailleuse sociale, collègue de Gigi', 'On peut pas sauver quelqu’un à sa place.', 'Ouvre un dossier sur les Cloutier', 48),
 'Louis Girard': ('Propre', 'Comptable, époux d’Anne', 'Les chiffres mentent pas, le monde oui.', 'Démêle les sociétés-écrans', 50),
 'Luc Villeneuve': ('Bagotville / Marge', 'Guetteur, croise Will', "Dans l'ciel, c'est pas juste des avions.", 'Confond un vol de contrebande avec un OVNI', 49),
 'Lucie Bérubé': ('Famille / Bérubé', 'Mère de Kevin et Jessy', 'Mes gars sont des porteurs, pas des frappeurs.', 'Cache les enfants du quartier', 50),
 'Lucie Côté': ('Vieux bloc', 'Voisine du 425 Victoria', 'Au tri, on jetait tout, même les patrons.', 'Colporte les nouvelles du palier', 70),
 'Léa Pelletier': ('Bar du Coin', 'Serveuse, fille d’Hugo et Sarah', 'Un café, pis oublie pas ton change.', 'Rapporte à Ginette ce qu’elle entend', 21),
 'Léo Cloutier': ('Famille / Ruelle', 'P’tit frère de Ti-Coune', 'Mon grand frère, y’est connu, moé.', 'Voit Dave se faire pognner', 9),
 'Manon Cloutier': ('Station-service / Famille', 'Mère de Dave et Lio', 'Le gaz est cher, les erreurs itou.', 'Cache Dave et ment pour Lio', 41),
 'Manon Lavoie': ('Ruelle / Gratien', 'Mère de Cindy, 92 Prince-Albert', "J'ai rien dit, j'ai rien vu, j'ai survécu.", 'Perd son logement de la rue', 49),
 'Manon Villeneuve': ('Motards / Louves', 'Bras droit de Karine Gagnon', 'Les Louves mordent en silence.', 'Prend la relève si Karine tombe', 44),
 'Marc-André Simard': ("Bloc d'en Face", 'Conjoint d’Anik, opérateur d’usine', "J'vois rien la nuit, j'travaille.", 'Confirme l’alibi d’Anik', 38),
 'Marcel Bouchard': ('Argent / Ruelle', 'Prêteur, Dévon lui doit', "J'prête pas de l'argent, j'prête du temps.", 'Rachète la dette du Spot', 58),
 'Marie-Claude Brassard': ('Urgences / Aide', 'Ambulancière, épouse d’Émile', 'On roule même pour les pires.', 'Transporte Dave après la descente', 39),
 'Martine Lavoie': ('École', 'Directrice de l’école secondaire', 'Ton frère a manqué douze jours.', 'Convoque la famille Lavoie', 55),
 'Maxime Boivin': ('Santé / Propre', 'Vétérinaire du quartier', 'Même les chats ont des histoires.', 'Soigne Pisse-Feu et donne un indice', 40),
 'Nadia Benali': ('Dépanneur / Famille', 'Tient le cahier des dettes', 'Le cahier, c’est ma mémoire, et j’oublie rien.', 'Confie le cahier à Samson', 40),
 'Nancy Dubois': ('Bar du Coin', 'Serveuse, sœur de Patrice', 'Verre cassé, compte cassé.', 'Travaille la soirée de la descente', 36),
 'Natasha Vollant': ('Parc du Fjord', 'Guide innue, sentier Eucher', 'La forêt vous laisse passer, pas voler.', "Guide les flics jusqu'à la planque", 42),
 'Nathalie Bouchard': ('Famille / Chloé', 'Préposée IGA, mère de Chloé', 'Ma fille streame ma vie, fine.', 'Héberge Chloé après la vidéo virale', 48),
 'Normand Boucher': ("Ruelle d'en Face", 'Cousin de Dévon, casse illégale', 'Un char, ça meurt. Les preuves itou.', 'La casse avale la caméra volée', 47),
 'Paule Desbiens': ('Institutions', 'Notaire de La Baie', 'Signez ici, et priez un peu.', 'Trouve l’irrégularité dans le bail', 54),
 'Pauline Fortin': ('Campagne / Neutre', 'Maraîchère, épouse d’Yves', 'Des bleuets, du temps, c’est tout c’que j’vends.', 'Son kiosque voit les boîtes passer', 56),
 'Philippe Villeneuve': ('Hôpital', 'Médecin à l’Hôpital de La Baie', "J'suis médecin, pas juge.", 'Soigne un blessé non déclaré', 59),
 'Pierrette Simard': ("Bloc d'en Face / Famille", 'Mère de Marc-André, ex-caissière IGA', 'À la caisse, on sait tout l’monde.', 'Se souvient des achats suspects', 64),
 'Raymond Gagnon': ('Radio pirate / Marge', 'Pirate radio, écoute Alex T.', 'Ils m’écoutent ? Parfait, j’ai des choses à dire.', 'Diffuse les bandes d’Alex en direct', 58),
 'Réjean Pedneault': ('Port / Neutre', 'Pêche la baie des Ha! Ha! avec Céline', 'Le fjord parle à qui sait r’garder.', 'Repêche le ballot tombé d’un conteneur', 67),
 'Réjean Roy': ('Aide / Famille', 'Mari de Gigi, ex-papetier', 'À l’usine, on s’occupait des nôtres.', 'Accompagne Ginette quand elle doit parler', 66),
 'Richard Villeneuve': ('STS / Neutre', 'Chauffeur d’autobus', 'Prochain arrêt : tes conséquences.', 'La caméra du bus filme la mauvaise course', 61),
 'Rico Leduc': ('Santini / Ruelle', 'Recouvre pour Tony à La Baie', 'Tu payes, ou tu comprends.', 'Envoyé appuyer Dévon au Spot', 36),
 'Rock Côté': ('Port', 'Débardeur, filleul de Fernand', 'Un conteneur, ça s’ouvre toujours.', 'Repère le conteneur de Sal', 50),
 'Rock Gagnon': ('Motards', 'Mécano moto, frère de Karine', 'Une moto, ça ment jamais.', 'Prépare les bécanes de repli', 55),
 'Salvatore Martel': ('Santini / Port', 'Relais conteneurs, croise Yvan', 'Le quai dort jamais.', 'Reçoit le mauvais conteneur', 45),
 'Samuel Joseph': ('Aide / CHSLD', 'Préposé, fils de Mireille', 'Mamie, t’es où encore ?', 'Retrouve Mireille qui cache Ti-Coune', 35),
 'Sarah Pelletier': ('Bar du Coin', 'Barmaid, épouse d’Hugo', 'Pas de mains sur le comptoir, pas d’mains sur moi.', 'Tient la barre pendant la tempête', 44),
 'Serge Potvin': ('Ville / Neutre', 'Opérateur de déneigement', 'La neige tombe pour tout le monde, sauf mon horaire.', 'Sa niveleuse ouvre la ruelle de la descente', 57),
 'Solange Bouchard': ('Quartier / Marge', 'Souverainiste de Grande-Baie', 'La Grande-Baie est souveraine !', 'Mobilise le quartier contre l’expulsion', 63),
 'Sonia Tremblay': ('Famille / Alex', 'Mère d’Alex Tremblay, préposée aux bénéficiaires', 'Mon fils sortira de sa chambre, un jour.', "Débranche l'ordinateur, trouve les preuves", 52),
 'Steve Gauthier': ('Casse', 'Dépeceur, fournit Bobby', "J'enlève juste ce qui dérange.", 'Démontre la voiture d’Antoine', 35),
 'Sylvain Bouchard': ('Aréna', 'Entraîneur hockey junior', 'Sur glace, pas de gang, juste une équipe.', 'Sort les jeunes du recrutement de Dévon', 48),
 'Sylvain Gagné': ('Ruelle / Salon', 'Coiffeur à domicile, conjoint de Johanne', 'J’entends tout sous le casque-séchoir.', 'Coiffe les dames et capte les rumeurs', 40),
 'Thérèse Gagnon': ('Motards / Aînée', 'Mère de Karine et Rock, ex-Louve', 'Les Louves, c’était moi la première.', 'Protège les gamins du quartier', 76),
 'Thérèse Lacroix': ('Église', 'Ex-sacristine, sœur de Lucien', 'Les cierges coûtent cher, les péchés itou.', 'Ouvre la sacristie aux sans-logis', 68),
 'Ti-Paul Côté': ('Ruelle', 'Chiffonnier, copain de Réal', 'Une canette, c’est cinq cennes. Un secret, c’est gratuit.', 'Récupère une preuve dans ses chariots', 55),
 'Tommy Fortin': ('Campagne', 'Journalier à la bleuetière, fils d’Yves', 'Aux bleuets, pas de Wi-Fi, pas d’mensonge.', 'Voit les boîtes de contrebande aux champs', 25),
 'Tony Santini': ('Santini / Quai', 'Lieutenant, neveu de Vittorio', 'Le quai et la casse, même famille.', 'Ordonne la pression sur Dévon', 47),
 'Véronique Côté': ('CPE / Aide', 'Éducatrice, collègue de Mélo', 'Un coco, ça sent quand ça va mal chez nous.', 'Porte plainte après avoir vu Lio', 31),
 'William McKenzie': ('Armée / Bagotville', 'Militaire de la 3e Escadre', 'Règlements, monsieur. Rien que les règlements.', 'Confond un vol de nuit avec un exercice', 28),
 'Yan Couture': ('Art / Musique', 'Guitariste de bar, joue au bingo', 'Une toune pour t’souler, une autre pour t’garder.', 'Sa chanson devient l’hymne du bloc', 33),
 'Yves Fortin': ('Campagne', 'Producteur de bleuets', 'Les bleuets poussent seuls, les hommes non.', 'Compte les passages sur son chemin', 58),
 'Élodie Martel': ('Culture / Neutre', 'Éducatrice au Musée du Fjord', 'Le fjord s’en fiche de nos chicanes.', 'Archive une photo qui gêne', 34),
 'Émile Brassard': ('Caserne / Urgences', 'Pompier, époux de MC', 'On éteint tout, sauf les dettes.', 'Premier sur la fausse alerte du Spot', 41),
 'Émilie Gauthier': ('Commerce / Neutre', 'Gérante du Dollarama', 'Tout est à 1,25, la morale de même.', 'La couronne de Solange sort de son magasin', 34),
 # --- Chicoutimi ---
 'Albert Dufour': ('Ville / Famille', 'Ex-conseiller, père du maire', 'Mon fils m’a dépassé, comme le progrès.', 'Lâche une vieille combine immobilière', 86),
 'André Simard': ('Loi / Direction', 'Directeur du Service de police', 'La loi, c’est un édredon : ça cache rien longtemps.', 'Retient Samson ou le lâche ?', 58),
 'Caroline Otis': ('Argent / Chambre', 'Présidente de la Chambre de commerce', 'Un commerce qui dérange, c’est un commerce.', 'Fait pression sur les permis du Néon', 46),
 'Catherine Samson': ('Loi / Famille', 'Adjointe au palais, épouse de Pierre', 'Au palais, les dossiers ont des yeux.', 'Trouve les sociétés-écrans au greffe', 45),
 'Danny Fortin': ('Santini / Façade', 'Gérant de façade du Néon', 'Bienvenue au Néon : lumière pis oubli.', 'Sa porte d’en arrière filtre les rencontres', 39),
 'Denis Pedneault': ('Média', 'Propriétaire de CKRS, cousin de Réjean', 'En onde, tout le monde est innocent.', 'Vend du temps d’antenne au plus offrant', 59),
 'Enzo Bianchi': ('Santini / Conseiller', 'Conseiller de Vittorio', 'Je suggère, jamais j’ordonne.', 'Négocie la sortie de Vittorio', 55),
 'François Côté': ('Presse', 'Rédacteur en chef du Quotidien', 'Une nouvelle, ça se prouve. Une rumeur, ça se vend.', 'Enterre ou publie le dossier', 51),
 'Gilles Dufour': ('Ville', 'Maire de Saguenay, fils d’Albert', 'Saguenay regarde en avant, surtout en arrière.', 'Pris entre la police et la Chambre', 61),
 'Hélène Samson': ('Loi / Famille', 'Ex-secrétaire de palais, mère de Pierre', "J'ai tapé les aveux de trois générations.", 'Ressort les vieux dossiers Santini', 71),
 'Isabelle Gagné': ('Politique', 'Députée à l’Assemblée nationale', 'À Québec, vos ruelles, c’est abstrait.', 'Promet des fonds puis disparaît', 54),
 'Jonathan Roy': ('Réseau / Louche', 'Fausses identités, boulevard Talbot', 'Qui tu veux être aujourd’hui ? J’ai le papier.', 'Fabrique l’identité du témoin', 41),
 'Julien Gagné': ('Santini', 'Chauffeur de Vittorio', "J'demande pas où on va, c'est mieux.", 'Conduit la mauvaise nuit', 34),
 'Louise Villeneuve': ('Loi / Magistrature', 'Juge à la Cour du Québec', 'La balance penche du côté des preuves.', 'Signe les mandats du bloc', 50),
 'Maria Santini': ('Santini / Famille', 'Matriarche, restaurant familial', 'Mange. Les affaires attendent, les pâtes non.', 'Négocie la clémence en cuisine', 59),
 'Mei Chen': ('Commerces / Famille', 'Préposée d’hôtel, mère de Justin', 'Mon fils se croit riche, il est juste jeune.', 'Héberge les témoins à l’hôtel', 48),
 'Mgr Paul Tremblay': ('Église / Diocèse', 'Évêque, supérieur de Lucien', "L'Église écoute. L'Église se tait. Parfois.", 'Doit muter Lucien au mauvais moment', 68),
 'Nico Santini': ('Santini / Relève', 'Fils de Vittorio et Maria', "J'suis prêt, parrain. J'suis prêt.", 'Envoyé en premier, il flanche', 28),
 'Olivier Savard': ('Presse', 'Journaliste, ex-collègue de JP', 'Ta source, elle s’appelle comment déjà ?', 'Reçoit les bandes d’Alex', 36),
 'Paul-André Côté': ('Santini / Argent', 'Comptable des sociétés-écrans', 'Deux et deux font cinq si je signe.', 'Les livres basculent entre ses mains', 41),
 'Sophie Labbé': ('Aide / Université', 'Psychologue, collègue de Laurie', 'Assieds-toi. On a toute la séance.', 'Évalue les mineurs de l’affaire', 44),
 'Éric Simard': ('Cégep / Naïf', 'Coloc de Justin Chen', 'Wô, c’tait pas supposé aller loin, ça.', 'Témoin gênant de la soirée Chen', 22),
 'Vittorio Santini': ('Santini / Sommet', 'Patriarche, restauration et bars', 'La famille, c’est une entreprise avec des tombes.', 'Propose un deal à Samson', 64),
 # --- Jonquière ---
 'Benoit Larouche': ('ATM / École', 'Prof de cinéma d’Antoine', 'Le cinéma, c’est regarder deux fois.', 'Oblige Antoine à rendre les images', 52),
 'Camille Lefèvre': ('ATM / Art', 'Étudiante en comm, sœur d’Antoine', 'Une photo, ça trahit pas, ça révèle.', 'Tire les clichés qui manquent', 26),
 'Dany Aubin': ('Famille / Aubin', 'Soudeur, frère de Sam', 'La soudure ferme les trous, les familles non.', 'Descend à La Baie soutenir Sam', 32),
 'Gérald Tremblay': ('Aluminerie / Syndicat', 'Délégué syndical, collègue de Mathieu', 'La convention dit ça, et elle a raison.', 'Son grief devient un levier', 54),
 'Jean-Marc Fortin': ('Aluminerie / Direction', 'Directeur d’usine à Arvida', 'Un four ne négocie pas.', "Gère une saisie de conteneurs à l'usine", 57),
 'Mélissa Harvey': ('ATM / Art', 'Étudiante ATM, nièce de François', 'Je filme tout, même ce qui faut pas.', 'Sa perche capte une confession', 26),
 'Nicolas Gagné': ('Aluminerie / Syndiqué', 'Technicien, collègue de Mathieu', 'Le métal pardonne, le contremaître non.', 'Repère des cargaisons marquées', 37),
 'Alexandre Lavoie': ('Famille JP / Aréna', 'Frère cadet de JP, hockey juvénile', "J'vas m'rendre dans la Ligue un jour, moé.", 'Veut que JP revienne à la maison', 16),
}
NARR_COLS = ['Nom', 'Surnom', 'Faction', 'Lien Spot', 'Quote joual', 'Arc S1', 'Age apparent']


def preparer_portraits():
    """Génère les deux gabarits (-web, -vignette) des nouveaux, renomme les 2
    personnages dont le surnom sortait du Nom."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit('Pillow est requis (pip install -r requirements.txt).')

    os.chdir(RACINE)
    # nouveaux
    for nom, (base, src) in NOUVEAUX_PORTRAITS.items():
        if not os.path.exists(src):
            # déjà migré ?
            if os.path.exists(f'portraits/{base}-web.webp'):
                continue
            sys.exit(f'Source portrait introuvable pour {nom} : {src}')
        im = Image.open(src).convert('RGB')
        web = f'portraits/{base}-web.webp'
        im.save(web, 'WEBP', quality=80, method=6)
        ratio = 400 / im.width
        vig = im.resize((400, round(im.height * ratio)), Image.LANCZOS)
        vig.save(f'portraits/{base}-vignette.webp', 'WEBP', quality=85, method=6)
        print(f'  + portrait {nom} → {web}')
    # renommages (les deux gabarits référencés)
    for ancien, nouveau in FICHIERS_RENOMMES.items():
        for suffixe in ('-web.webp', '-vignette.webp'):
            a, b = f'portraits/{ancien}{suffixe}', f'portraits/{nouveau}{suffixe}'
            if os.path.exists(a):
                os.replace(a, b)
                print(f'  ~ {a} → {b}')


def migrer():
    os.chdir(RACINE)
    preparer_portraits()

    wb = openpyxl.load_workbook(XLSX)
    ws = wb[FEUILLE]
    hdr = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(hdr)}
    lignes = {ws.cell(r, idx['Nom'] + 1).value: r
              for r in range(2, ws.max_row + 1)
              if ws.cell(r, idx['Nom'] + 1).value}

    def appliquer(nom_actuel, changements):
        # résoudre le nom : clé actuelle, ancien nom avec guillemets, ou nouveau
        r = lignes.get(nom_actuel)
        if r is None and nom_actuel in ANCIEN_VERS_NOUVEAU:
            r = lignes.get(ANCIEN_VERS_NOUVEAU[nom_actuel])  # déjà renommé
        if r is None and nom_actuel in ANCIEN_NOM:
            r = lignes.get(ANCIEN_NOM[nom_actuel])
        if r is None:
            raise SystemExit(f'Personnage introuvable : {nom_actuel}')
        for col, val in changements.items():
            ws.cell(r, idx[col] + 1, val)
        if 'Nom' in changements:
            lignes[changements['Nom']] = r

    # Passe 1 — renommages de Nom (idempotent : sans effet une fois renommé).
    for ancien, nouveau in ANCIEN_VERS_NOUVEAU.items():
        if ancien in lignes:
            appliquer(ancien, {'Nom': nouveau})

    # Passe 2 — toutes les autres corrections, clés anciennes ou nouvelles
    # acceptées (l'ordre garantit que Bernard/Karine gardent leur adresse/rôle).
    fixes_par_ancien_nom = {}
    for cle, changements in CORRECTIONS.items():
        changements = {k: v for k, v in changements.items() if k != 'Nom'}
        fixes_par_ancien_nom.setdefault(cle, {}).update(changements)
    for cle, changements in fixes_par_ancien_nom.items():
        if changements:
            appliquer(cle, changements)

    # #10 — ajout des mineurs
    for rec in NOUVEAUX:
        if rec['Nom'] not in lignes:
            ws.append([rec.get(k) for k in
                       ['Nom', 'Surnom', 'Type', 'Age', 'Rôle', 'Secteur', 'Adresse',
                        'Latitude', 'Longitude', 'Apparence', 'Vêtements',
                        'Tic / Objet', 'Portrait', 'Famille', 'Parenté']])
            lignes[rec['Nom']] = ws.max_row
            print(f"  + {rec['Nom']} ({rec['Age']} ans) ajouté")
        else:
            r = lignes[rec['Nom']]
            for k, v in rec.items():
                ws.cell(r, idx[k] + 1, v)

    # #9 — narration 100 %
    nw = wb[NARR_SHEET]
    nhdr = [c.value for c in nw[1]]
    nidx = {h: i + 1 for i, h in enumerate(nhdr)}
    narr_existants = {nw.cell(r, nidx['Nom']).value: r
                      for r in range(2, nw.max_row + 1)
                      if nw.cell(r, nidx['Nom']).value}
    # noms effectifs après corrections
    noms = [ws.cell(r, idx['Nom'] + 1).value for r in range(2, ws.max_row + 1)
            if ws.cell(r, idx['Nom'] + 1).value]
    surnoms = {ws.cell(r, idx['Nom'] + 1).value: ws.cell(r, idx['Surnom'] + 1).value
               for r in range(2, ws.max_row + 1)
               if ws.cell(r, idx['Nom'] + 1).value}
    manquants = [n for n in noms if n not in narr_existants]
    if manquants:
        for nom in manquants:
            if nom not in NARR:
                raise SystemExit(f'Narration manquante pour : {nom}')
            faction, lien, quote, arc, age_app = NARR[nom]
            r = nw.max_row + 1
            nw.cell(r, nidx['Nom'], nom)
            nw.cell(r, nidx['Surnom'], surnoms.get(nom))
            nw.cell(r, nidx['Faction'], faction)
            nw.cell(r, nidx['Lien Spot'], lien)
            nw.cell(r, nidx['Quote joual'], quote)
            nw.cell(r, nidx['Arc S1'], arc)
            nw.cell(r, nidx['Age apparent'], age_app)
        print(f'  + {len(manquants)} lignes de narration ajoutées')
    # garde-fou : toute ligne narration doit référencer un personnage existant
    for nom_narr in list(narr_existants) + manquants:
        if nom_narr not in surnoms:
            raise SystemExit(f'Narration référence un personnage inconnu : {nom_narr}')

    wb.save(XLSX)
    print(f'Classeur enregistré : {len(noms)} personnages, '
          f'{len(narr_existants) + len(manquants)} lignes Narration.')


if __name__ == '__main__':
    migrer()
