# Relations entre personnages — conventions et périmètre

## Ce qui est intégré

La source `data/relations.csv` contient une **première extraction éditoriale de
114 relations explicites, reliant 141 des 213 personnages**. Elle est volontairement
partielle : l’absence d’un lien ne signifie pas que les personnages ne se connaissent
pas. Les 72 personnages sans lien dans cette tranche ne sont pas déclarés isolés
socialement. Tous les textes de Parenté et de narration sont conservés.

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

`cousin_de` est disponible pour compléter la table, sans occurrence dans cette
première extraction. Les inverses sont des conventions de lecture, pas des lignes
ajoutées automatiquement. Les liens symétriques se stockent une seule fois, avec
le plus petit ID lexical en Source_ID. Ainsi, deux membres d’un couple ne créent
pas deux relations redondantes.

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

Cette tranche privilégie les familles des personnages initiaux, les filiations
explicitement énoncées et certains liens de couple, travail et colocation. Elle
n’épuise ni les liens de cousinage, ni les grands-parents, ni les relations d’intrigue.

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
