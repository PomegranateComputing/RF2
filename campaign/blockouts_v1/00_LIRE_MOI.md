# RED FLAGS 2 — 23 nouvelles cartes UZDoom

Adaptation de **La Couleur de la Grenade**. Livraison du 23 septembre 2026.

**Le pack contient de vrais WAD UDMF, pas seulement des plans.** Première passe de level design : architecture orthogonale, matériaux originaux simples, rencontres, deux secrets par carte, badge bleu, porte et sortie. Les cartes RF01 à RF23 sont reliées en campagne ; RF23 est un épilogue sans ennemis.

## Lancer sous Windows

1. Extraire le dossier `RF2_UZDOOM_MAPS_V1` de l'archive dans `C:\PROJECTS`.
2. Double-cliquer `C:\PROJECTS\RF2_UZDOOM_MAPS_V1\JOUER.cmd`.
3. Au premier lancement, la préparation télécharge **UZDoom 5.0.1 Windows x64** et **Freedoom 0.13.0** depuis leurs distributions officielles, contrôle les SHA-256 puis installe les fichiers dans ce dossier. Environ 54 Mo de téléchargement ; Internet requis une fois.
4. Dans le menu : **Nouvelle partie**, puis choisir la difficulté. L'entrée est **RF01**, Sainte-Anne.

Pour ouvrir directement une des 23 cartes : `CHOISIR_CARTE.cmd`. Pour consulter les plans : `ATLAS.html`.

Tout reste sous `C:\PROJECTS\RF2_UZDOOM_MAPS_V1` : moteur, dépendances, configuration, captures et sauvegardes. Aucune installation système ni droits administrateur requis. Les autres projets et leurs fichiers ne sont pas utilisés.

## Contenu livré

- `build/RF2_MAPS_V1.pk3` : campagne complète, cartes, matériaux et écran de fin.
- `maps/RF01.wad` à `maps/RF23.wad` : cartes éditables, avec nœuds compilés.
- `src/RFxx/TEXTMAP` : sources UDMF lisibles ; `layout.json` décrit les lieux et le découpage initial.
- `resources/` : 30 surfaces, deux écrans et MAPINFO.
- `ATLAS.html`, `previews/` : plans géométriques et légendes.
- `docs/` : correspondance avec le roman, installation détaillée, intégration et reprise.
- `tools/` : reconstruction, empaquetage et validation Python.
- `evidence/` : rapports sur les fichiers réellement livrés.

## Ce que signifie V1

Il s'agit d'une **base de cartes texturée**, pas de la direction artistique finale du FPS. Les ennemis, armes, sons et HUD de démonstration viennent de Freedoom ; avec un IWAD Doom II, ils viennent de Doom II. **Le FN FAL et les acteurs RF2 définitifs ne sont pas fournis dans ce pack de cartes.** Le slot automatique est identifié pour leur intégration, sans prétendre qu'une mitrailleuse de test est un FAL. Le personnage à incarner reste Viktor Ardent ; aucun nouveau modèle de Viktor n'est inventé ici.

Les 23 WAD sont acceptés par ZDBSP et passent les vérifications statiques de géométrie, clés, sorties, ressources et objets. **Le parcours en jeu, le rendu, les sauvegardes et les lanceurs Windows restent à vérifier sur le PC de jeu** : UZDoom Linux échoue au démarrage dans l'environnement de construction, y compris sans ce pack. Aucune durée de jeu ni performance n'est annoncée.

Lire `docs/HOW_TO_COMPLET.md` pour l'intégration au projet UZDoom vivant.
