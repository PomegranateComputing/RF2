# Demande ENN-V01 — ennemis : une famille complète d'abord

| | |
|---|---|
| ID, version | ENN-V01 (suite de RF2-ART-02, candidate `RF2_ART-02_20260927_1356`, intégrée au cumul) |
| Priorité | **P1** avec le Rapid — retour du propriétaire : « les ennemis restent à améliorer » ; le gain doit se voir en marche, attaque, douleur et mort, de face et de côté |
| Base | ligne `prod/rf2-campaign` (`23808c6`), build cumulé `RF2_CUMUL_20260929_1801` (`5115307c…`) ; code `src/zscript/rf/enemies.zs` ; sprites `src/sprites/enemies/` ; modèles de mort `MODELDEF` |
| Règle | adaptation acceptée : personnel de Sainte-Anne qui continue sa procédure ; jamais le couple, les patients, la maladie, ni une force occulte (`CANON_FIDELITE.md` §2) |

## Ce qu'Opus a mesuré sur tes fichiers (audit du 30/09, 461 PNG)

Les pieds tombent au sol à ±0,7 unité sur toutes les images ; la largeur de tête reste la même d'une image à l'autre
(pas de changement d'échelle, pas de saut latéral). Les variations de hauteur sont des changements de pose (lancer du
porte-registre +6, choc du brancardier −9, frappe de l'infirmier −3,5), pas des erreurs de dessin. **Les défauts
d'ancrage et de proportion vus en jeu sont d'abord de mon côté** : modèle de mort 1,19 fois plus haut que les sprites
qu'il remplace (brancardier 41,6 contre 34,9), saut du corps à la dernière image de mort (rayon réduit d'un coup),
flottement sur les marches (règle du moteur, rayon du brancardier 40), boîtes de collision plus hautes que la tête
(7 à 12 unités), réglage de rendu `gl_spriteclip` à vérifier. Je les corrige et je te renvoie des captures en situation
avant de te demander de redessiner quoi que ce soit.

### Vérifié dans le moteur (30/09, après l'audit)

Réglage de rendu du propriétaire (`gl_spriteclip=-1`, « anamorphique ») contre le réglage `1` : les 12 images de
l'infirmier, côte à côte, face caméra, 1920×1080, même distance : **hauteurs dessinées identiques** (rapport 1,000 ; 1,006
au plus). Les images debout (marche, douleur, retour) mesurent toutes 171 à 175 px : pas de changement d'échelle d'une
image à l'autre au sol plat. Le rendu n'explique donc pas la plainte ; mes corrections portent sur le modèle de mort
(échelle 5 5 5 au lieu de 5 5 6), le corps réduit dès le début de la chute (plus de saut à la dernière image), les
hauteurs de collision (infirmier 54, porte-registre 60, brancardier 56), les coups à travers une fenêtre ou une rambarde
(refusés), les cadavres écrasés par une porte (restent tels quels), la charge du brancardier (lancée à 450 au plus).

## Ce que je te demande : la première famille complète, l'infirmier (`RFOrderly`, sprite `ORDY`)

C'est la famille la plus nombreuse (RF01 : 14 à 20 ; RF02 : 14 à 18 ; RF04 : la majorité). Le standard qu'elle fixe
sera ensuite étendu au brancardier et au porte-registre, pas avant.

| | Actuel (consommé par le jeu) | Attendu |
|---|---|---|
| Rôle | infirmier de Sainte-Anne, pression rapprochée, frappe qu'on peut esquiver | inchangé |
| États et images | `A` repos (10 tics) ; marche `B C D E` (4 tics chacune) ; armé `F` (10) ; frappe `G` (4) ; retour `H` (14) ; douleur `I` (3+4) ; mort `J` (6) `K` (7, ne bloque plus) `L` (8) ; `M` corps final **dessiné par un modèle** (MODELDEF), pas par le sprite | mêmes lettres et mêmes durées (le code n'a pas à changer) ; une marche qui se lit de face et de côté (appuis, bras) ; un armé qui prévient ; une douleur lisible ; une mort qui tombe **au sol**, sans changer de taille |
| Rotations | 8 vraies rotations par image (1 à 8), aucune en miroir | 8, sans miroir |
| Toile, échelle | PNG 140–361 × 69–302 px, `grAb` aux semelles (y = hauteur − 2 ou − 3), `Scale 0.18` ; précompensation verticale 1/1,2 de RF2-ART-02 (contrat §5) | inchangé : même `Scale`, même précompensation, `grAb` aux semelles ; hauteur visible debout ≈ 52–53 unités (un homme de 1,70 m à côté de Viktor, 56) |
| Ancrage | pieds à ±0,7 u | idem, sur **toutes** les images, mort comprise |
| Distances | vu de 64 à 800 unités ; en combat surtout 64–300 | lisible à 300 dans la lumière de RF01 (couloirs 90–130) et de RF04 (extérieur 150–165) |
| Lumière | pas de lumière peinte dans le sprite qui contredise la pièce | ombres propres légères, pas de contre-jour peint |

Livrer aussi, pour la fin de la mort, **le modèle du corps** (OBJ + atlas) s'il change, à la même échelle que les
sprites : je règle son échelle verticale de mon côté (le 1,19 mesuré), dis-moi seulement si ta géométrie a changé.

## Exemples de défauts à regarder avec moi (captures à venir dans ce dossier)

Je fais les captures en situation après mes corrections (même build pour toi et moi) : face et côté, marche, armé,
frappe, douleur, mort, à 128, 256 et 512 unités, dans RF01 (couloir, cour) et RF04 (extérieur). Tu ne corriges que ce
qui reste faux sur ces captures-là.

## Les figures de RF02 (non hostiles)

Les adultes mesurent 60,5 à 68,4 unités (le contrat disait environ 54) ; le reflet de Viktor 68,4 contre 56 pour le
joueur. Hypothèse : la précompensation 1/1,2 manque sur les figures. À vérifier ensemble sur une capture avant toute
reprise ; pas urgent.

## Fichiers attendus

`incoming/astra/ENNEMIS/ORDY_V02/` : les PNG (mêmes noms `ORDY<frame><rot>.png`), le modèle de mort s'il change,
manifeste avec `target_relpath`, sommes, planche de contrôle (face, profil, dos ; toutes les images).
