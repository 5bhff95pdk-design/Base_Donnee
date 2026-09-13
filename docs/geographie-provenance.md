# Géographie — provenance et limites

## Périmètre

La base utilise des rues et des toponymes réels de Saguenay, mais les numéros
civiques et les personnages sont fictifs. Les points ne désignent pas une
personne ni un bâtiment réel : ils servent à situer un personnage à l’échelle du
quartier.

Les données géographiques intégrées dans les livrables sont donc un assemblage
à deux niveaux :

- **référence réelle** : noms de rues, toponymes et contexte cartographique
  issus d’OpenStreetMap et de ses services associés ;
- **construction fictionnelle** : numéros, personnages et coordonnées
  approximatives utilisées par le récit.

## Ce que les tests garantissent

Les garde-fous vérifient que :

- le secteur déclaré est l’un des trois arrondissements attendus ;
- la latitude et la longitude tombent dans la boîte approximative du secteur ;
- une adresse possède un numéro ou le préfixe explicite `Lieu-dit :` ;
- les exports GeoJSON utilisent WGS84 et conservent l’ID permanent ;
- les avertissements sur les adresses fictives sont présents dans la
  documentation et la carte.

Ces contrôles ne constituent pas une validation administrative des limites
municipales et ne garantissent pas qu’une rue n’a pas changé dans OSM depuis la
création de la fiche.

## Avant une diffusion publique

Avant de publier une nouvelle version destinée à un public large :

1. vérifier les nouveaux noms de rues avec OpenStreetMap ;
2. noter la date et le service utilisés pour cette vérification dans le journal
   de changement ;
3. contrôler que les coordonnées restent décalées et non interprétables comme
   des adresses réelles ;
4. conserver l’attribution OSM et les conditions propres aux fonds de carte,
   Nominatim et aux fournisseurs de tuiles ;
5. ne jamais présenter les points comme des adresses postales ou comme la
   localisation de personnes réelles.

Une future évolution pourrait ajouter un manifeste de provenance par rue avec
la date de vérification. Ce manifeste n’est pas encore une source du générateur
et son absence ne doit pas être interprétée comme une validation récente.
