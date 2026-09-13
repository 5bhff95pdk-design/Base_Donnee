# Relations entre personnages — conventions et périmètre

## Ce qui est intégré

La source `data/relations.csv` contient une **extraction éditoriale de
155 relations explicites, reliant 176 des 213 personnages**. Elle est volontairement
partielle : l’absence d’un lien ne signifie pas que les personnages ne se connaissent
pas. Les 37 personnages sans lien dans cette tranche ne sont pas déclarés isolés
socialement. Tous les textes de Parenté et de narration sont conservés.

La seconde passe (2026-09-13) a structuré **41 liens déjà écrits en prose** dans
le champ `Parenté` : fratries, cousinages, oncles et tantes, grands-parents et
un filleul qui étaient déclarés nommément mais absents de la table, alors que
l’autre extrémité existait dans la base. Aucun lien n’a été déduit : chaque
ligne reprend le texte exact de la fiche citée. Les cas où un prénom seul reste
ambigu (« Lucien », « Steve », « Julien ») ont été résolus avec la Famille, la
Branche et le secteur des fiches concernées, puis relus un par un.

La construction produit :

- une feuille **Relations** filtrable dans `base_personnages_fictifs.xlsx`, avec
  IDs, noms actuels, type et texte de provenance ;
- `relations_personnages.json`, export autonome, schéma versionné `1`, comprenant
  le vocabulaire des relations, leur inverse de lecture et leur provenance.

Les relations ne sont pas injectées dans les exports géographiques ni dans la
carte. Les traits de familles déjà présents sur la carte restent un regroupement
par Famille/Branche, **pas une représentation de cette nouvelle table**.

## Source de vérité

| Colonne | Sens |
|---|---|
| Source_ID | ID du personnage à gauche de la relation |
| Type | Type contrôlé, défini dans `relations.py` |
| Cible_ID | ID du personnage à droite |
| Preuve_ID | ID de la fiche qui décrit explicitement le lien |
| Champ_source | `Parenté` pour cette première tranche |
| Extrait | Copie exacte du champ Parenté de la fiche citée |

Exemple : `P033 → parent_de → P001`, attesté par le champ Parenté de P001,
« Fils de Robert et Diane ». L’identification est aussi cohérente avec la fiche
de Robert Lavoie (P033), « Père de JP ». Le texte de preuve est conservé tel quel,
même s’il décrit plusieurs liens : chacun occupe une ligne distincte.

Les correspondances de noms courts ont été relues avec les fiches concernées ;
le générateur n’interprète pas les prénoms et ne devine pas les liens.

## Sens et symétrie

| Type stocké | Lecture source → cible | Lecture inverse | Symétrique |
|---|---|---|---|
| parent_de | source parent de cible | enfant_de | Non |
| conjoint_de | union actuelle décrite dans la source | conjoint_de | Oui |
| ex_conjoint_de | ancienne union décrite | ex_conjoint_de | Oui |
| fratrie | frère ou sœur de | fratrie | Oui |
| cousin_de | cousin ou cousine de | cousin_de | Oui |
| collegue_de | collègue de | collegue_de | Oui |
| colocataire_de | colocataire de | colocataire_de | Oui |
| superieur_de | supérieur ou patron de | subordonne_de | Non |
| locataire_de | source locataire de cible | bailleur_de | Non |
| enseignant_de | source enseignant de cible | eleve_de | Non |
| oncle_de | source oncle ou tante de cible | neveu_de | Non |
| grand_parent_de | source grand-parent de cible | petit_enfant_de | Non |
| parrain_de | source parrain ou marraine de cible | filleul_de | Non |

`oncle_de`, `grand_parent_de` et `parrain_de` ont été ajoutés pour couvrir des
liens que le champ Parenté énonce explicitement sans les réduire à une
filiation : « Neveu de Lucien et Thérèse Lacroix », « Petite-fille de Réjean et
Céline Pedneault », « Filleul de Fernand Côté ». Sans eux, ces liens
restaient en prose et hors de la table ; ils ne doivent **pas** servir à
convertir une simple cohabitation ou un partage de clan en lien de famille.

`cousin_de` n’était disponible qu’en théorie dans la première extraction : il
porte désormais 13 relations. Les inverses sont des conventions de lecture, pas
des lignes ajoutées automatiquement. Les liens symétriques se stockent une seule
fois, avec le plus petit ID lexical en Source_ID. Ainsi, deux membres d’un couple
ne créent pas deux relations redondantes.

`conjoint_de` regroupe époux/épouse et conjoint/conjointe : le texte source conserve
la nuance. `parent_de` ne distingue pas les filiations biologique et adoptive.
Aucun mariage, lien de fratrie, lien grand-parental ou lien professionnel n’est
inféré du seul partage d’un clan, d’une adresse, d’un parent ou d’un lieu de travail.

## Validation et mise à jour

1. Ajouter uniquement un lien déjà explicité dans une source canonique.
2. Retrouver les deux IDs ; sélectionner le type, son sens et la fiche de preuve.
3. Copier intégralement son champ Parenté dans Extrait.
4. Lancer `python3 construire_base.py`, puis les tests.

La construction refuse : source absente/vide, mauvais en-tête, champ vide,
référence inconnue, type inconnu, auto-relation, doublon, ordre symétrique incorrect,
preuve non liée aux extrémités, extrait périmé et cycle de filiation.

**Limite de la validation :** la correspondance exacte d’un extrait ne prouve pas
à elle seule que l’interprétation humaine est correcte. Le contrôle du sens du lien
reste éditorial ; le programme ne comprend pas la prose. Il ne contrôle pas non
plus toutes les contradictions familiales ou chronologiques possibles.

Un changement de Nom/Surnom ne modifie pas les IDs ; les noms des livrables sont
relus dans la base. Si le champ Parenté change, la construction s’arrête pour
inviter à relire les relations concernées avant de recopier le nouvel extrait.
Ne pas actualiser les preuves en masse sans relecture.

## Liens laissés en attente

Cette extraction couvre désormais les filiations, les fratries, les couples, les
cousinages, les liens oncle/tante, grand-parentaux, de parrainage, ainsi que
certains liens de travail et de colocation énoncés dans Parenté. Elle n’épuise
pas les relations d’intrigue, ni les liens décrits uniquement dans la narration
(voisinage, dettes, influences), ni les proximités non nommées.

Exemples à qualifier avant une éventuelle intégration :

- **P119 Jonathan Roy → P028 Alex Tremblay** : « croise Alex Tremblay » ne permet
  pas de conclure à une amitié, une alliance ou une hostilité.
- **P151 Vittorio Santini → P009 Dévon Boucher** : « tient Dévon à distance » ne
  précise pas une hiérarchie contractuelle ou une rivalité permanente.
- **P115 Marcel Bouchard / P009 Dévon Boucher** : « Dévon lui doit » suggère une
  dette, mais sa nature et sa temporalité restent à préciser avant d’introduire
  un type créancier/débiteur.
- **P158 Danny Fortin / Lady Dynamite** : conserver la mention narrative ; ne pas
  la convertir automatiquement en lien de faction ou en relation hiérarchique.

Pour la suite, décider si les relations d’intrigue doivent porter une saison,
un épisode, une période et un statut (fait, rumeur, perception). Le schéma actuel
ne prétend pas représenter ces dimensions.

## Séparation des propositions

`docs/propositions-personnages-centraux.md` propose treize personnages centraux
avec désirs, enjeux, contradictions, oppositions et choix. **Ce document est
non canonique et n’est pas une source du générateur.** Ses nouvelles idées ne
figurent ni dans la table de relations ni dans la narration. Elles nécessitent
une validation de l’auteur avant toute intégration.
