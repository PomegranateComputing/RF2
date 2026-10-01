# Reflet de Viktor dans RF02 — mesure du 01/10 (build 1821)

| Mesure | Valeur |
|---|---|
| Sprite | `src/sprites/rf02_figures/R2F8A1…A8.png`, toile 512 × 448, `grAb` 256, 424, `Scale 0.18` (acteur `RFViktorMirror`, `src/zscript/rf/figures.zs`, `+ONLYVISIBLEINMIRRORS`, suit le joueur) |
| Hauteur dessinée | lignes opaques 45 à 423 : 378 px → **68 u** des semelles au sommet (A1 à A8 : 377–378 px, pas de dérive) |
| Références du jeu | joueur `Height 56`, yeux `ViewHeight 41` ; infirmier ORDY 53 u ; figures RF02 F02-01…07 : 60–64 u |
| En moteur | vitrine-miroir latérale de la pharmacie (x 1536–1600, y 576–592), regard horizontal à 30, 70 et 130 u du verre : l'horizon de l'écran (yeux du joueur) coupe le reflet **à la poitrine** ; la tête est derrière les bocaux (`reflet_rf02_miroir_pharmacie.jpg`, vues `reflet_rf02_vues.json`) |
| Identité | autre visage que le master du HUD : cheveux bruns courts, pull ras du cou, sans anneaux (`reflet_rf02_visage_vs_master.jpg` : master à gauche, tête du reflet au centre, reflet entier à droite) |

Lecture : 68 / 56 = 1,21, le facteur d'étirement vertical du moteur (1,2) appliqué une fois de trop dans le dessin.
Correction retenue : nouveau `R2F8` (Codex) à **311 px (56 u)**, visage du master, tenue de jeu ; échelle et
ancrage inchangés côté moteur. Les mêmes images servent aux miroirs de la salle de danse (RF04, RF05), où l'acteur
`RFViktorMirror` est aussi placé.
