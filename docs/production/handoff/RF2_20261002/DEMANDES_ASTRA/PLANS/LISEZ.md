# Plan commun RF04 / RF05, coupes et dimensions — état construit au 02/10

Dessinés depuis les sources des cartes (`scripts/production/map_plans.py`, à relancer après toute modification) : ce
sont les volumes réellement jouables aujourd'hui. **C'est une reconstruction jouable, pas un relevé** : aucun plan coté
du Luna Park de la porte Maillot n'est authentifié (voir `references/LUNA_PARK_REFERENCES.md` du pack). Les formes
viennent du panorama de 1910 et des cartes postales citées ; les scènes viennent du roman ; les dimensions sont
choisies pour le jeu.

| Fichier | Contenu |
|---|---|
| `RF04_plan.png` | le parc : sol ouvert (vert), masses fermées (brun, plus clair = plus haut), pièces couvertes (bleu), portes (rouge), dalles — ponts, linteaux, toits (cadre jaune) ; grille de 256 u |
| `RF05_plan.png` | le même parc et, au nord, le sous-sol de la sous-station (sol à −192) |
| `RF04_coupe_A_bassin_quai.png` | d'ouest en est par le milieu du bassin : crête ouest et voie haute, tréteaux, esplanade, bassin (−96), Brooklyn |
| `RF04_coupe_B_sud_nord.png` | du sud au nord par l'axe du bassin : portes à dômes, bassin, rampe du Water Chute, tour, ruelle |
| `RF04_coupe_C_grand_huit.png` | le long des tréteaux : voie, quai (+96), rampe de levage |
| `RF04_coupe_D_salle.png` | la salle de danse et son aile |
| `RF05_coupe_E_escalier_sous_station.png`, `RF05_coupe_F_sous_sol.png` | la descente depuis la ruelle ; galeries, sous-station, atelier |
| `RF05_coupe_G_galerie_des_departs.png`, `H_baie`, `I_atelier`, `J_caniveau` | les deux boucles de maintenance ajoutées le 02/10 : l'escalier et la galerie des départs (+96), sa baie sur la roue, sa redescente dans l'atelier ; le caniveau entre les deux galeries |
| `RF06_plan.png` | le couloir : chambres, salle des peaux, descente, carrefour et « autre aile », deux virages, le jour |
| `RF06_coupe_K_chambre_des_vannes.png`, `L_passerelles`, `M_boucle` | les volumes ajoutés le 02/10 : la chambre des vannes (passerelles et fosse), la boucle d'inspection de la salle des peaux |
| `RF04_RF05_DIMENSIONS.md` | emprise, sol et hauteur libre de chaque zone |

32 u = 1 m. Le nord est en haut. L'origine (0, 0) est l'angle sud-ouest du parc.

## Correspondance avec le graphe du pack

| Nœud du pack | Dans la carte |
|---|---|
| Porte de service et guérite | CHEMIN DE SERVICE (à l'est, entrée au sud), AVANT-COUR et GUÉRITE (pointeuse, clefs, barrière) |
| Allée principale | ESPLANADE, entrée par le passage de Brooklyn |
| Brooklyn : façade et coulisse | façade de 256 × 192 u sur l'esplanade ; COULISSE câblée derrière (deux planches déclouées vers des ateliers) |
| Bassin Niagara | BASSIN en creux (−96), balustrade, deux passerelles, flaque et chaussure, RAMPE et TOUR au nord |
| Quai du grand huit | QUAI à +96 sous la voie ; tréteaux à l'ouest, rampe de levage au nord ; vue croisée sur le bassin |
| Marquise et salle de danse | MARQUISE, tourniquets au compteur, SALLE (miroirs, juke-box, estrade), LOGE, couloir de SERVICE |
| Passage derrière la piste | RUELLE au nord, remises, porte de la sous-station |
| Sous-station | RF04 : la porte et le vestibule ; RF05 : escalier, palier, salle voûtée, galeries, puits d'air, magasin, transformateurs et pompes |

La boucle de retour depuis la salle (porte latérale vers la ruelle) et le contrechamp derrière Brooklyn existent.

## Vues prises dans le moteur

23 vues de la zone du parc (`P01`…`P23` : première vue, bassin, chaussure, balustrade, Brooklyn, coulisse, charpente,
quai, mât, rampe et tour, marquise, salle, ruelle, guérite, crête ouest, portes à dômes), 13 de RF05, 9 de RF06 :
`dist\candidates\RF2_CUMUL_20261001_1605\preuves\vues_RF04_pilote\`, `vues_RF05\`, `vues_RF06\` ; état après la passe des
portes : `dist\candidates\RF2_PORTES_20261002_1018\preuves\portes\`. Les cadrages sont listés avec leurs coordonnées dans
`docs\production\handoff\RF2_20261001\vues\*.json` : je peux reprendre exactement les mêmes sur une nouvelle version.

## Volumes ajoutés le 02/10 (adaptations déclarées : le roman donne les lieux, pas leur plan)

Tous sont habillés de matières existantes ; ce sont eux qui attendent en priorité des coupes et des modules d'Astra.

| Carte | Volume | Dimensions | Fonction | Ce qu'il faudrait dessiner |
|---|---|---|---|---|
| RF05 | Voûte de la sous-station (proposition de la session de revue) | berceau de 512 u de portée, clef à +192 u au-dessus du sol, trois nervures | remplace le plafond en gradins | intrados de brique, nervures, clefs |
| RF05 | Galerie des départs | escalier de 8 marches (16 × 12 u) depuis les transformateurs, galerie à +96 u (48 à 64 u de large, 80 u sous plafond), baie de 64 × 64 u dans le mur est de la nef, escalier de 8 marches vers l'atelier | boucle électrique : contrechamp haut du moteur et de la roue, retour par l'établi | garde-corps de fer simple (aujourd'hui la rambarde parisienne `RF2_RAMB`, à remplacer), isolateurs et départs de câbles, limon et marches de bois |
| RF05 | Caniveau de la conduite des pompes | 64 × 320 u, trois marches de 8 u vers 24 u d'eau, 88 u sous plafond | boucle hydraulique courte entre la galerie ouest et la galerie nord | conduite et colliers (aujourd'hui un volume carré), suintements, ligne d'eau |
| RF05 | Chemin de câbles de la nef (session de revue) | tablette à +104 u sur consoles le long du mur est | réseau lisible depuis les tableaux | consoles, câbles |
| RF04/RF05 | Cadres de la coulisse de Brooklyn (session de revue) | trois portiques de bois, 80 u de passage, 88 u de haut | charpente de l'envers du décor | assemblages, fixations |
| RF06 | Retrait de service | 96 × 96 u, 120 u sous plafond, collecteur de 32 × 64 × 72 u | premier élargissement, côté parc | collecteur, vannes, raccords |
| RF06 | Boucle d'inspection (session de revue) | deux volées de 4 marches de 16 u, galerie basse à −48 u | second niveau sur la peinture soulevée | regard, enduit en coupe |
| RF06 | Second seuil | passage réduit à 64 u, linteau à 76 u, sur 32 u | autre épaisseur d'enduit | chambranle d'enduit épais |
| RF06 | Chambre des vannes | passerelle haute (80 × 176 u), six marches de 8 u, passerelle basse (80 × 144 u), fosse de 96 × 384 u à 96 u sous la passerelle basse (144 u sous la haute), deux colonnes montantes, collecteur | retrait technique : la conduite quitte le couloir, descend, remonte, revient | garde-corps, colonnes, collecteur, échelons, eau au fond |
| RF06 | Nervures du premier virage | quatre nervures de 16 u sur le mur sud | relief que balaie le faisceau | nervure et son pied |
| RF06 | Fente du dernier tronçon | 32 × 32 u à 36 u du sol, dans le mur est | relation impossible : on y voit la cage d'escalier de « l'autre aile », qui se trouve 1 200 u à l'ouest | encadrement de la fente ; la cage elle-même (marches, garde-corps, ampoule) |

La conduite blanche est maintenant continue : elle longe le couloir des chambres, a un piquage dans le retrait de
service, quitte la descente pour la chambre des vannes, revient plus bas, passe au-dessus du joueur aux deux virages et
descend jusqu'au jour. C'est le repère d'échelle demandé par le dossier ; son dessin (colliers, raccords, peinture
blanche écaillée) revient à Astra.

**Limite du moteur relevée le 02/10** : un portail de ligne ne s'affiche que sans décalage de hauteur (les variantes
alignées sur le sol ou le plafond restent noires dans UZDoom 5.0.1). La fente montre donc un lieu situé à la même
altitude qu'elle ; une vue sur la chambre 404, 190 u plus haut, n'est pas possible par ce moyen.

## Points à arrêter ensemble avant les grandes façades

1. **Échelle du parc.** L'esplanade fait 40 × 66 m, le bassin 12 × 34 m, la tour 6 × 4 m à +320 u (10 m). C'est petit
   pour un parc d'attractions réel, mais c'est ce qui donne une traversée de la durée voulue. Si le plan artistique
   demande plus d'emprise (grand huit plus long, bassin plus large), le dire maintenant : je déplace les constantes de
   `luna_park.py`, les rencontres et les parcours suivent.
2. **Grand huit.** Aujourd'hui : une voie haute à +384 u sur la crête ouest et nord, des tréteaux, un quai, une rampe de
   levage ; pas de boucle complète lisible. Une élévation d'Astra (profil de la voie, points hauts, descente) me
   permettrait de construire la silhouette.
3. **Entrée publique.** Seul le revers des portes à dômes est dans la carte (au sud) ; la façade publique est la fin de
   RF02. À décider : un cadrage commun pour que les deux cartes montrent le même édifice.
4. **Attractions de l'esplanade.** Kiosque, manège, mât de la tour aérienne (nacelles en boîtes) : volumes simples, à
   remplacer par des modules dessinés (emprises du tableau).
5. **RF05, parc rallumé.** Mêmes volumes ; ce qui change : ampoules, enseigne, train, miroirs. Les ampoules sont des
   lumières du moteur placées par moi : une carte des points lumineux souhaités suffit.
6. **RF06.** Longueur du parcours : 3 456 u (108 m), sol de 0 à −224 u. Le « second virage pas assez large pour la
   longueur parcourue » est rendu par la géométrie ; une coupe d'Astra pour les repères (conduite, ampoule) guiderait
   les prochaines retouches.
