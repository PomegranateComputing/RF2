# Contrat d'intégration RF2

Les géométries sont neuves. Le pack de démonstration emploie les classes natives de l'IWAD. Ce choix rend les WAD inspectables sans les ressources de l'ancien FPS et **ne définit pas le bestiaire canonique du roman**.

| Numéro DoomEd | Classe de référence | Traitement RF2 |
|---|---|---|
| 1 | Player 1 start | Viktor Ardent via le PlayerPawn approuvé du FPS |
| 5 | BlueCard | Conserver comme contrôle bleu ou remapper en cohérence avec LOCKDEFS |
| 2002 | Chaingun | Emplacement d'arme automatique de test ; brancher le FN FAL réel |
| 2001 | Shotgun | Fusil à pompe approuvé |
| 82 | SuperShotgun | Arme lourde de proximité de test, à arbitrer |
| 2048 / 2049 | ClipBox / ShellBox | Remapper aux munitions réellement consommées par les armes RF2 |
| 2011 / 2012 | Stimpack / Medikit | Soin natif, remplaçable |
| 2018 / 2019 | GreenArmor / BlueArmor | Protection native de test |
| 2013 | Soulsphere | Récompense secrète de test à adapter |
| 3004 / 9 | Zombieman / ShotgunGuy | Opposition armée de test |
| 3001 / 3002 / 58 | DoomImp / Demon / Spectre | Opposition de test, pas attribution canonique |
| 69 / 66 | HellKnight / Revenant | Opposition renforcée de test |

La porte finale utilise **Door_LockedRaise (13), tag 100, vitesse 16, délai 150, verrou 2**. Le verrou 2 correspond à BlueCard dans le LOCKDEFS Doom fourni par UZDoom 5.0.1. Les panneaux secrets utilisent **Door_Raise (12), tags 200 et 201**. Le panneau de fin utilise **Exit_Normal (243)**. La découverte d'un secret emploie le bit secteur **1024**.

Le FN FAL est obligatoire dans le FPS final. Aucun dessin, sprite, son ou code d'arme FAL validé n'était disponible parmi les sources de cette livraison ; aucun faux FAL n'a été fabriqué en renommant la Chaingun. Le mapping doit être vérifié dans le vrai build avant de déclarer cette intégration terminée.

Échelle : maillage de 64 unités, passages principaux de 192, passages secrets de 64, plafonds intérieurs 160–256, extérieurs 384 ; reliefs franchissables par marches de 16. Référence joueur Doom : rayon 16, hauteur 56. Si Viktor utilise d'autres dimensions, revalider les collisions et les portes avec sa définition réelle.
