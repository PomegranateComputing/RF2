# RF04 — relevé du plan avant recomposition (01/10/2026)

Retour du propriétaire du 01/10 : RF04 ne donne pas l'identité du Luna Park ; le plan et les ressources sont à reprendre.
Références : `03_LUNA_PARK_REFERENCES_20261001.md` ; images regardées : panorama d'ensemble vers 1910 (BHVP, reproduction
Wikimedia), carte postale « 344 Paris - La Porte Maillot et Luna Park » (Carnavalet CP9), photographie de Roger Schall,
1935 (Carnavalet PH1945, wagonnets du grand huit) ; copies de travail dans `C:\PROJECTS\RF2_UZDOOM_CODEX_ART_20261001\references\`.

**Aucun plan coté du parc n'est établi.** La disposition ci-dessous est une **reconstruction à l'échelle du jeu**,
composée à partir des volumes et des relations visibles sur ces images et ordonnée par le roman (l. 451–551). Elle
n'est pas un relevé.

## Ce que montrent les images (relations spatiales)

| Image | Ce qui est documenté | Ce que la carte en reprend |
|---|---|---|
| Panorama vers 1910 | façade publique au sud : deux portes monumentales « LUNA PARK » à piliers coiffés de dômes, entre elles un pavillon à arcades ; à gauche un restaurant à pignon | le revers des portes et du pavillon ferme le sud de l'esplanade (vu de l'intérieur) |
| Panorama | une grande esplanade ouverte, un long bassin à balustrades dans l'axe nord-sud, des passerelles, des barques | l'esplanade et le bassin vide au centre (le Niagara du roman) |
| Panorama | le Water Chute : une rampe raide qui descend d'une tour dans le bassin | la rampe et sa tour au nord du bassin ; les rochers de la cascade au pied |
| Panorama | des montagnes de rochers artificiels qui ferment le parc sur trois côtés, portant les voies du grand huit sur des charpentes en croix | rochers à l'ouest et au nord ; la charpente et la voie au-dessus, contre le ciel |
| Panorama | une tour à nacelles au milieu de l'esplanade ; un pavillon oriental au fond | le mât d'une tour aérienne dans l'esplanade ; la salle de danse au nord-ouest, façade orientale (reconstruction) |
| Carte postale CP9 | côté rue : piliers couronnés à drapeaux, grand arc, grille et haie, masse de rochers visible depuis la porte Maillot | l'entrée de fin de RF02 et la planche RF02 → RF04 ; dans RF04, les grilles fermées vues de l'intérieur |
| Schall 1935 | wagonnets ronds à deux places, voie en planches, garde-corps et treillis de bois peints en blanc, à hauteur d'homme | quai d'embarquement et train de trois voitures (RF05), échelle des voitures et des garde-corps |

## Plan existant (30/09) → recomposition

| Volume du 30/09 | Sort |
|---|---|
| A chemin de service (bande à l'est) | **gardé** dans son rôle : il longe désormais la palissade est, derrière les attractions |
| B guérite, barrière, pointeuse, clefs | **gardés** (mécanismes et scènes inchangés), déplacés au bout nord du chemin |
| Hangar | **supprimé** (sans appui dans le texte ni les images) |
| C allée étroite | **remplacée** par l'esplanade ; première ouverture large sur le parc après la barrière |
| Couloir technique | **gardé** : derrière la façade Brooklyn, à l'est de l'esplanade |
| D bassin du Niagara (carré à l'ouest) | **déplacé** au centre, en long bassin nord-sud avec balustrade, passerelles, escalier sud et rochers de cascade au nord ; chaussure au fond près de la cascade |
| E champ de poteaux des montagnes russes | **remplacé** par une charpente le long de l'ouest (deux files de poteaux, voie au-dessus) et un quai surélevé au nord-ouest, relié à la voie qui monte dans les rochers |
| F salle de danse (nord-est) | **déplacée** au nord-ouest, à côté du quai ; marquise et tourniquets devant sa porte sud |
| G sous-station (nord-ouest) | **déplacée** au nord-est : porte dans le pied des rochers du nord, au bout du passage herbeux derrière la piste ; RF05 suit sous cette porte |

## Liaisons de jeu reconstruites

1. Porte du personnel (sud-est) → chemin de service vers le nord, rails étroits, rail tiède (scène) → guérite au bout.
2. Pointage, clef, barrière ouverte → le passage entre deux bâtiments → **première vue** : de l'angle nord-est de
   l'esplanade, le bassin vide dans toute sa longueur, la rampe et sa tour, la charpente des montagnes russes sur le ciel
   à l'ouest, le mât de la tour aérienne, au sud le revers des portes LUNA PARK.
3. Le long de la façade Brooklyn (côté est), entrée sous le pont de décor → couloir technique (câbles) → sortie au
   sud-est, près des portes.
4. Escalier sud du bassin → fond du bassin (ligne d'algues à hauteur d'épaule) → la chaussure dans la flaque, au pied
   de la cascade → remontée par les rochers de la cascade.
5. Sous la charpente (ouest) → escalier du quai (nord-ouest) → quai, vue sur le bassin et l'esplanade.
6. Marquise et tourniquets (compteur 617 → 618) → salle de danse (miroirs, trois tenues, juke-box) → porte latérale.
7. Passage herbeux derrière la piste, au pied des rochers du nord → porte de la sous-station (clef) → RF05.

Rencontres E1–E6 reprises sur ce terrain, difficulté comparable à RF02. RF04 (fermé) et RF05 (rallumé) partagent la même
implantation : un seul module de géométrie pour les deux (`scripts/mapkit/luna_park.py`).
