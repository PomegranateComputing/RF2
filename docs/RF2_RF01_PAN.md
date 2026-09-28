# RF01-PAN — les 13 panneaux muraux de RF01

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Lot séparé demandé par le mandat du 27/09 soir (« corrige aussi
les 13 panneaux RF01 dans un lot séparé »). Rien ici ne vaut accord du propriétaire. Le build RF01 accepté et son
lanceur `JOUER_RF2_ART_REVIEW.cmd` sont inchangés.

## Jouer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_RF01-PAN.cmd` | écran titre ; « Nouvelle partie » : RF01 avec les panneaux |

Build `dist\candidates\RF2_RF01-PAN_20260928_0725\RF2_RF01-PAN.pk3`, sha256
`1439a27e8be3136d0b5054649f5c91946b7c65a6a1785127e30724dfcfed93fc`, commit `7c4767a` (branche
`candidate/rf01-pan`, partie du tag `rf01-owner-accepted-20260927`). Build isolé : c'est le RF01 accepté
(`04bdd0ae…`) dont ne diffèrent que `maps/RF01.wad` et cinq textures de plaques (`patches/rf01/RFSIGN1, 2, 7, 8,
9.png`) ; aucun autre fichier du pk3 ne change. Profil et sauvegardes séparés (`user\uzdoom_rf01pan.ini`,
`user\savegames_rf01pan`).

La candidate précédente `RF2_RF01-PAN_20260927_2245` (conservée) rendait les plaques visibles mais pas à leur place ;
son message de commit (« contre leur mur ») était faux pour 11 plaques sur 13. Elle est remplacée par celle-ci.

## Défaut constaté sur le build accepté

1. **Hauteur** : les 13 plaques sont dessinées sous le sol. Le décalage vertical était écrit négatif et non
   multiplié par l'échelle de la texture (4 pixels par unité) ; le moteur le lit positif et en pixels.
2. **Position** : relevé sur la géométrie de la carte (`scripts/production/rf01_sign_survey.py`), 0 plaque sur 13
   n'était tenue par un mur ou un linteau. Les coordonnées de `sign()` ne tombaient pas sur la grille de 16 unités
   des murs (4 à 21 unités d'écart, plus les 4 unités de décollement voulues) ; REGISTRES et CHAPELLE étaient dans
   l'embrasure de leur porte, sous le linteau, tournées vers la porte ; ADMISSIONS pendait au milieu du couloir, à
   65 unités de tout mur.
3. **Textures** : quatre textes dépassaient de leur texture (CONSULTATIONS, LOGE DU PORTIER, PAVILLON OUEST,
   GALERIE NORD) ; PAVILLON EST touchait le bord.
4. **Largeur** : les lignes de décor sont raccourcies de 2 unités à chaque bout ; les 4 dernières unités de chaque
   plaque (bordure et dernière lettre) étaient coupées.

## Relevé et correction (source : `scripts/mapkit/rf01.py`)

Appel `sign(x, y, côté, texture, bas)` : x/y = face du mur ; côté = mur qui porte la plaque vu de la pièce vers
laquelle elle est tournée. Au-dessus d'une porte, le bas de la plaque est au-dessus du linteau ou de la hauteur
d'ouverture de la porte (plafond voisin le plus bas − 4). Les emplacements suivent les commentaires de l'auteur de la
carte (« à côté de la porte de service », « au-dessus de l'ouverture du vestibule », « au-dessus de la porte de la
cour », « côté hall de la grille »).

| # | Plaque | Avant (appel, bas) | Après (appel, bas) | Tenue par | Tournée vers |
|---|---|---|---|---|---|
| 1 | PAVILLON OUEST | (132, −376, W), 92 | (128, −400, W), 132 | grille 20 (ouverte à 124) | hall des admissions |
| 2 | ADMISSIONS | (−60, −368, S), 96 — milieu du couloir | (96, −400, E), 136 | linteau de la grille 20 (128) | couloir du pavillon ouest |
| 3 | PAVILLON EST | (400, 8, S), 96 — à moitié devant le passage | (432, 0, S), 84 | mur à côté du passage | arcade |
| 4 | PAVILLON EST | (768, 200, E), 84 | inchangée | mur | couloir |
| 5 | LINGERIE | (1404, 400, E), 120 — devant l'ouverture | (1408, 336, E), 120 | mur à côté de la porte de service | salle commune |
| 6 | GALERIE NORD | (384, 660, S), 120 — à moitié devant la grille | (416, 656, S), 120 | mur à côté de la grille 45 (ouverte à 220) | galerie |
| 7 | REGISTRES | (−4, 704, E), 120 — dans l'embrasure | (0, 704, W), 152 | linteau (144) | galerie nord |
| 8 | CHAPELLE | (−164, 384, E), 100 — dans l'embrasure | (−160, 384, W), 136 | linteau (128) | couloir ouest |
| 9 | CONSULTATIONS | (−48, −100, N), 96 | (−48, −80, N), 96 | mur | consultations |
| 10 | CONSULTATIONS | (132, −184, W), 100 | (128, −176, W), 116 | grille 30 (ouverte à 108) | hall des admissions |
| 11 | LOGE DU PORTIER | (432, −448, S), 120 | inchangée | mur | hall des admissions |
| 12 | SORTIE | (352, −440, S), 136 | (352, −448, S), 136 | linteau du vestibule (128) | hall des admissions |
| 13 | PAVILLON EST | (352, −96, N), 136 | (352, −80, N), 136 | linteau de la porte 10 (128) | hall des admissions |

La plaque 3 est abaissée de 12 unités : son haut touchait le plafond de l'arcade ; elle est maintenant à la hauteur de
la plaque 4, sa jumelle.

Autres fichiers : `scripts/mapkit/udmf.py` (`decor_line(..., texwidth=)` : la texture entière est ajustée à la ligne
par `scalex_mid`) ; `scripts/mapkit/materials.py` (`sign()` réduit le texte pour qu'il tienne dans la bordure
émaillée ; RFSIGN1, 2, 7, 8, 9 régénérées, les cinq autres identiques à l'octet).

`src/maps/RF01.wad` : lignes, secteurs et objets identiques au build accepté ; seuls diffèrent les 26 côtés des
plaques (hauteur, ajustement horizontal, secteur) et leurs 26 sommets (les plaques 4 et 11 passent seulement de 4 à
1 unité du mur).
Contrôle statique de la carte inchangé (7523 cellules atteintes, clés 1 et 2, sortie atteinte).

## Vérification dans le moteur

Même liste de vues sur le build accepté et sur la candidate : pour chaque plaque, une vue de face et une vue de biais
(45°), caméra à hauteur d'yeux (41) sur le sol de la pièce vers laquelle la plaque est tournée, reculée seulement à
travers des cellules ouvertes (ni mur, ni porte, ni meuble, 16 unités de dégagement de chaque côté). Pour ces prises,
les monstres et personnages sont rendus invisibles (pas supprimés), pour qu'aucun ne se trouve entre la caméra et la
plaque. Outils : `scripts/production/rf01_sign_views.py`, `scripts/production/view_check_pk3.py` (pk3 de contrôle
chargé après le build ; le build n'est pas modifié). 1600×900.

| Contrôle | Build accepté | Candidate 0725 |
|---|---|---|
| Plaques visibles (26 vues) | 0 / 13 | 13 / 13 |
| Texte complet, bordure entière | — | 13 / 13 |
| Plaque sur son mur ou son linteau | — | 13 / 13 (relevé : 13 tenues et lisibles) |
| Portes ouvertes (7 plaques au-dessus ou à côté d'une porte) | — | aucune plaque dans une ouverture |
| Traversées RF01 A et B (`scripts/e2e_rf01.py --pk3`) | PASS (acceptation) | A PASS (56 points, 16 ennemis tués, sortie), B PASS (sauvegarde, relance, chargement, mort, reprise) |

Le registre de RF01 a été vérifié sur le build accepté (`docs/production/RF01_REGISTRE_VERIFICATION.md` : lisible de
toutes les positions essayées). Ce lot ne touche pas au registre : les objets de la carte sont identiques à l'octet.

## Ligne cumulative

La même correction est portée sur `prod/rf2-campaign` (commit séparé) : `RF01.wad` y est régénéré à l'identique de
celui de la candidate ; RF02 régénéré avec le même `udmf.py` est inchangé. Les prochaines candidates cumulatives
porteront donc les panneaux ; le build accepté reste tel quel.

## Preuves (dossier `evidence\` de la candidate)

- `planches\planche_panneaux_1…5.jpg` : les 26 vues, build accepté à gauche, candidate à droite ;
  `planche_portes_ouvertes.jpg` : les 7 plaques liées à une porte, porte ouverte.
- `captures\accepte_RF2_ART_REVIEW_1451\`, `captures\candidate_RF01-PAN_0725\`,
  `captures\candidate_RF01-PAN_0725_portes_ouvertes\` : captures brutes nommées par vue.
- `releve\releve_panneaux_source_acceptee.txt` (0/13), `releve\releve_panneaux_candidate.txt` (13/13), listes de
  vues.
- `textures\` : les dix textures d'origine, et les cinq corrigées avant/après.
- `controles.txt` : empreintes, contenu du pk3 comparé au build accepté, comparaison des blocs de la carte,
  traversées.

## Limites

- Lisibilité jugée sur captures fixes en 1600×900, pas en jeu à d'autres résolutions ; aucun avis du propriétaire.
- Hauteurs et côtés choisis par Opus d'après la géométrie et les commentaires de l'auteur de la carte : ADMISSIONS
  et PAVILLON OUEST étiquettent la même grille, chacune de son côté ; GALERIE NORD garde le côté voulu par l'auteur
  (vers la galerie), à côté de la grille et non dessus, puisque la grille s'ouvre jusqu'à 220.
- Les plaques au-dessus d'une porte (1, 2, 7, 8, 10, 12, 13) sont plus hautes qu'avant (116 à 152) : lisibles de
  loin, moins de près sans lever les yeux.
- RF02 a le même défaut de largeur (texture coupée de 4 unités) et ses enseignes sont à 4 unités du mur : à traiter
  dans le lot RF02-A (`texwidth=`, décollement), pas ici.
