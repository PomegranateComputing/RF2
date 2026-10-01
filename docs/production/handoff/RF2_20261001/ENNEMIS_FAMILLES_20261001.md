# Ennemis — familles suivantes (Opus → Codex, 01/10)

Ordre du mandat : l'image E de l'infirmier (fait : `ORDY_E_V04` intégré, film de la boucle dans le retour du 01/10),
puis **la famille complète du brancardier**, puis celle du **porte-registre**, puis le roster suivant confirmé. Le
standard est celui d'ENN-V01 (`DEMANDES_20260930/ENNEMIS.md`) : 8 vraies rotations par image, `grAb` aux semelles,
`Scale 0.18`, ancrage des pieds à ±0,7 u sur toutes les images, mort comprise ; lisible à 300 u dans la lumière de
RF01 (couloirs) et RF04 (extérieur). Le code reste tel quel : mêmes lettres, mêmes durées. Les corrections de collision,
d'attaque à travers obstacle, de modèle de corps et de chute du 30/09 restent de mon côté.

## Brancardier (`RFBrancardier`, sprite `BRCD`, 120 images en place)

Rôle : un infirmier qui pousse un brancard ; sa menace est la charge (il prend appui, lance le brancard, frappe à
l'arrivée, se reprend). Collision : rayon 40 (le brancard), hauteur 56 ; figure debout 52–54 u.

| État | Lettres, tics | Ce qui doit se lire |
|---|---|---|
| Repos | `A` 10 | mains sur les poignées |
| Marche | `B C D E` 5 | il pousse ; roues qui grincent (son) |
| Appui (annonce de la charge) | `F` 24 | il se baisse, épaules en avant : le joueur doit comprendre qu'il va charger |
| Charge | `G` 2 / `N` 2 en boucle | course, le brancard devant, jusqu'à 385 u |
| Choc | `O` 8 | le brancard heurte |
| Reprise | `H` 28 | il se redresse, souffle (fenêtre pour le punir) |
| Douleur | `I` 8 | |
| Mort | `J` 7, `K` 8, `L` 10, `M` corps final (**modèle**, `MODELDEF`) | il tombe à côté du brancard ; le brancard reste |

## Porte-registre (`RFPorteRegistre`, sprite `PREG`, 96 images en place ; `PRGS` = le paquet lancé)

Rôle : il porte des registres ficelés et les lance en cloche ; lent. Collision : rayon 22, hauteur 60 ; figure 58 u.

| État | Lettres, tics | Ce qui doit se lire |
|---|---|---|
| Repos | `A` 8 | le paquet contre la poitrine |
| Marche | `B C D E` 5 | lourde, le poids des registres |
| Préparation (annonce) | `F` 26 | il lève le paquet, recule le bras |
| Lancer | `G` 2 | |
| Retour | `N` 12 | |
| Douleur | `H` 5 | |
| Mort | `I` 7, `J` 7, `K` corps final | les registres tombent avec lui |

## Roster suivant

Aucune autre famille n'est confirmée dans les sources. Le boss du banc (le surveillant-chef, `bench/boss/FICHE_BOSS_SURVEILLANT.md`)
est une adaptation déclarée, à dessiner selon sa fiche ; il commande les trois familles ci-dessus.

## Contrôles que je ferai à chaque livraison

Planche face / profil / dos à 128, 256 et 512 u dans RF01 et RF04 (`scripts/production/enemy_views_pk3.py`), film de la
marche à vitesse de jeu (`scripts/production/walk_film.py`, nouvel outil du 01/10), corps au sol, sur une marche et près
d'une porte.
