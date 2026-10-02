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
| `RF06_plan.png` | le couloir : chambres, salle des peaux, descente, carrefour et « autre aile », deux virages, le jour |
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
