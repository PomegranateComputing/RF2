# Rapport de livraison — RF2 MAPS V1

Statut : **cartes construites, contrôles statiques réussis, validation runtime restante**. Ce statut ne vaut pas approbation artistique.

## Fichiers et périmètre

23 WAD UDMF (`RF01`–`RF23`), 1 PK3 de campagne, sources TEXTMAP, données de découpage, atlas, matériaux de construction, outils et lanceurs Windows. Toutes les géométries sont nouvelles. Aucun WAD de RF1 ou de Sans Destination n'est réutilisé.

PK3 SHA-256 : `68876cd5a6ca0bd2a01be4d1b0baca744306ad3d1a972c54bba1bc0b541f978b`.

Somme des géométries avant construction de nœuds : 19,854 linedefs, 1,546 secteurs. 46 secrets. RF01–RF22 : 437 / 861 / 1285 ennemis placés, respectivement en facile / moyen / difficile. RF23 : aucun ennemi ni placement d'arme ou munition. Ce sont des inventaires, pas des mesures de durée ou de qualité.

## Vérifications exécutées

| Contrôle | Résultat |
|---|---|
| Reconstruction des 23 géométries | OK |
| Clé disponible avant porte, sortie inaccessible sans clé | OK sur les données générées et sur le PK3 relu |
| Accès aux objets, aux deux secrets et à la sortie | OK statique, marches ≤ 24 unités |
| Structure WAD et limites des lumps | OK |
| Boucles de secteurs fermées, références de côtés/sommets | OK |
| Objets à l'intérieur d'un unique secteur | OK |
| Textures/flats référencées présents dans le PK3 | OK |
| Verrou bleu 2 vérifié contre LOCKDEFS UZDoom | OK |
| Enchaînement RF01 → RF23 et écran final sans RF24 | OK dans MAPINFO |
| ZDBSP 1.19, `-X -g -w` | 23 réussites, aucun avertissement |
| Lecture indépendante des WAD après ZDBSP | 23 réussites |
| ZIP/PK3 et hashes | Vérifiés lors du conditionnement |

ZDBSP a été compilé depuis sa source officielle et exécuté dans l'environnement de construction. `ZDBSP_BUILD.json` contient ses sorties. Les WAD livrés comprennent TEXTMAP, ZNODES et ENDMAP. Après modification de géométrie, ne pas réutiliser ces nœuds : reconstruire.

## Vérifications non réalisées

Le binaire UZDoom Linux 5.0.1 échoue au démarrage dans ce conteneur avec un signal 11, y compris sur Freedoom sans le pack. Un serveur graphique local ne peut pas établir ses sockets. Logs conservés dans `CONTAINER_*`. Cela n'établit ni que les maps fonctionnent en jeu ni qu'elles échouent : le lancement ne les atteint pas.

- Traversée réelle, collisions au rayon exact du joueur, usage des portes et retour après clé : **NON TESTÉ EN MOTEUR**.
- Rendu, visibilité, lumière, textures dans le renderer : **NON TESTÉ EN MOTEUR**.
- Compilation MAPINFO par le moteur et passage effectif vers RFEND : **NON TESTÉ EN MOTEUR**.
- Sauvegarde/chargement, mort/reprise, audio, options, FPS : **NON TESTÉ**.
- Scripts CMD/PowerShell sur Windows : **NON EXÉCUTÉS ICI** ; chemins relatifs, archives et hashes contrôlés à la construction.

La recette Windows télécharge deux archives effectivement récupérées pendant la construction. Les noms `uzdoom.exe`, `uzdoom.pk3`, `freedoom2.wad` et la structure des distributions ont été inspectés. Le script ne modifie aucune politique d'exécution persistante ; le contournement de politique de `PREPARER.cmd`/`CHOISIR_CARTE.cmd` est limité au processus PowerShell lancé.

## Production restante

C'est une première passe orthogonale texturée. Les acteurs, armes, sons et HUD sont ceux de l'IWAD de test. Le FN FAL, Viktor et le bestiaire propres au FPS restent à intégrer. Il reste à approfondir l'architecture et les vues propres à chaque lieu, ajouter les props et la narration environnementale détaillée, puis équilibrer avec les armes réelles. La durée de chaque carte doit être mesurée pendant les parcours.

La prochaine opération concrète est `C:\PROJECTS\RF2_UZDOOM_MAPS_V1\JOUER.cmd`, puis la validation de RF01 sans commandes de triche. Le reste est détaillé dans `docs/HOW_TO_COMPLET.md`.
