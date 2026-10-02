# Contrat des ennemis — les trois familles en jeu, et le cadre des nouvelles

Relevé sur `src/zscript/rf/enemies.zs`, `src/MODELDEF` et `src/sprites/enemies/` au commit `61d9b43`. Les fichiers, un
par un (pixels, ancrage, empreinte) : `CONTRATS/E01_ORDY_FICHIERS.csv`, `E02_BRCD_FICHIERS.csv`, `E03_PREG_FICHIERS.csv`.
**Le code ne change pas avec les images** : mêmes lettres, mêmes durées, mêmes événements. Ajouter une pose ne rallonge
pas une attaque : une pose de plus demande une lettre de plus, donc un changement de code, donc un accord préalable.

## Communs aux trois familles

- **Nom des fichiers** : `<SPRITE><LETTRE><ROTATION>.png`, rotations **1 à 8, huit vraies vues, aucun miroir**. La
  numérotation est celle de `ROTATIONS_ETALON_ORDY_A.jpg` : 1 = de face (il regarde la caméra), 5 = de dos ; garder
  pour chaque numéro la vue qu'il montre aujourd'hui.
- **Échelle** : `Scale 0.18` → 1 pixel = 0,18 u (5,556 px par unité). Viktor mesure 56 u (311 px des semelles au sommet
  du crâne dans R2F8). Ne pas changer la taille de toile sans raison : la hauteur visible de la figure est ce qui compte.
- **Ancrage** : chunk PNG `grAb` (x, y) = le point de l'image posé au sol sous l'acteur : x au milieu des appuis, y sur
  la ligne des semelles (colonne `grab` des tables). Une image livrée sans `grAb` est refusée par `verifier_lot.py`.
  Tolérance tenue par les lots en place : semelles à ±0,7 u de la ligne sur toutes les images, chute comprise.
- **PNG RGBA**, pas d'ombre portée peinte, pas de frange.
- **Corps final** : un modèle (`MODELDEF`, `Scale 5 5 5`), posé par le code sur la pente du sol, affiché à la dernière
  lettre de la mort. L'image de cette lettre existe dans le lot (huit rotations) mais n'est pas ce que le joueur voit.
  Un modèle refait remplace `models/rf2_art_01/<famille>.obj` et sa peau `…_skin.png` (mêmes noms, même origine, même
  échelle) ; la dernière pose de chute et le corps doivent avoir la même silhouette.
- **Ce que le code fait déjà** (ne pas le compenser par le dessin) : hauteurs de collision ajustées aux figures, coups
  refusés à travers une fenêtre ou une rambarde, corps réduit dès la chute, cadavres non broyés par les portes, charge
  du brancardier bornée.

## ORDY — `RFOrderly`, l'infirmier (104 images + corps)

En jeu : `ORDY_V03` (Astra, 30/09) avec la pose E refaite `ORDY_E_V04` (Codex, 01/10). Santé 60, rayon 18, hauteur de
collision 54 (figure debout ≈ 52,5 u), vitesse 9, portée de coup 44.

| État | Lettres et tics | Événement du code |
|---|---|---|
| Repos | `A` 10 (boucle) | regarde |
| Marche | `B` 4, `C` 4, `D` 4, `E` 4 (boucle : 16 tics, 0,46 s) | avance à chaque pose ; bruit de pas possible sur `C` et `E` : **les contacts au sol sont C et E** |
| Coup | `F` 10 | se tourne vers la cible, s'arrête (annonce) |
| | `G` 4 | **le coup part au premier tic de G** (8–14 de dégâts s'il est encore devant et à portée) |
| | `H` 14 | retour |
| Douleur | `I` 3 + 4 | cri au second temps |
| Mort | `J` 6, `K` 7, `L` 8 | cri sur J ; ne bloque plus à K ; bruit de chute sur L |
| Corps | `M` | modèle `orderly.obj` |

13 lettres × 8 rotations = 104 fichiers. Toiles actuelles : 141 à 180 × 301 px debout.

## BRCD — `RFBrancardier` (120 images + corps)

En jeu : `BRCD_V02` (Codex, 02/10). Santé 170, **rayon 40** (le brancard), hauteur 56, vitesse 5, masse 700.

| État | Lettres et tics | Événement du code |
|---|---|---|
| Repos | `A` 10 | |
| Marche | `B`, `C`, `D`, `E` 5 chacune | grincement de roue possible sur `C` |
| Appui (annonce) | `F` 24 | se tourne, s'arrête, souffle : le joueur doit comprendre qu'il va charger |
| Charge | `G` 1 puis `G` 2 / `N` 2 en boucle | avance de 11 u tous les 2 tics, 35 pas au plus (385 u) ; frappe (20–28) dès que la cible est dans l'axe à moins de 68 u |
| Choc | `O` 8 | le brancard a touché la cible ou un mur |
| Reprise | `H` 28 | immobile : la fenêtre pour le punir |
| Douleur | `I` 8 | |
| Mort | `J` 7, `K` 8, `L` 10 | |
| Corps | `M` | modèle `brancardier.obj` : l'homme à côté du brancard |

15 lettres × 8 = 120 fichiers. La charge ne part pas au-delà de 450 u.

## PREG — `RFPorteRegistre`, et sa liasse `PRGS` (96 + 2 images + corps)

En jeu : `PREG_V02` (Codex, 02/10) avec `porte_registre.obj` refait. Santé 110, rayon 22, hauteur 60 (figure ≈ 58 u),
vitesse 4.

| État | Lettres et tics | Événement du code |
|---|---|---|
| Repos | `A` 8 | |
| Marche | `B`, `C`, `D`, `E` 5 chacune | |
| Préparation (annonce) | `F` 26 | se tourne, s'arrête : il lève le paquet |
| Lancer | `G` 2 | **la liasse quitte la main au premier tic de G**, à 48 u du sol, en cloche vers la poitrine de la cible |
| Retour | `N` 12 | |
| Douleur | `H` 5 | |
| Mort | `I` 7, `J` 7 | ne bloque plus et bruit de chute sur J |
| Corps | `K` | modèle `porte_registre.obj` |

12 lettres × 8 = 96 fichiers. Liasse `RFRegistryBundle` : `PRGSA0`, `PRGSB0` (une seule vue chacune, 3 tics, en
boucle ; `A` 6 à l'impact), `Scale 0.9`, rayon 6, 9 de dégâts. La main de la pose G doit être à la hauteur d'où part
la liasse (48 u = 267 px au-dessus des semelles).

## Ce que je contrôle à la réception d'une famille

Planche face / profil / dos à 128, 256, 512 u, les quatre poses de marche, l'annonce, l'attaque, la douleur, le corps,
dans RF01 (couloir) et RF04 (extérieur), avant / après aux mêmes caméras ; film de marche de profil à vitesse de jeu ;
chute jusqu'au corps près d'une porte et sur une marche. Les 22 vues par carte et par famille existent pour l'état
actuel : `docs\production\handoff\RF2_20261001\RETOURS_CODEX\LOTS_20261002\` (BRCD, PREG) et la candidate 1605
(`preuves\marche_ORDY_RF04\`).

## Nouvelles familles et boss (N01–N07, B01–B02) : cadre moteur

Rien n'entre en campagne sans le verdict du propriétaire ; tout passe d'abord par le banc. Aucune de ces familles au
Jerma, dans RF06 ni dans la salle d'attente finale.

| Point | Contrat |
|---|---|
| Fichiers | préfixe de 4 lettres à me demander (je vérifie les collisions de noms avec le jeu, le moteur et l'IWAD) ; lettres A–Z puis `[`, `\`, `]` ; rotations 1–8 ; `grAb` aux semelles ; `Scale 0.18` par défaut |
| Emprise | un rayon et une hauteur de collision par famille, fixés avant le dessin : un passage de porte fait 64 u (48 pour les portes étroites), un couloir 96 à 128 ; un rayon de plus de 40 ne passe plus les portes simples |
| États minimaux | repos, marche (4 poses, contacts identifiés), annonce (≥ 10 tics lisibles), action, retour, douleur, mort (3 poses), corps (image ou modèle) |
| Événement | la pose où il se lit est nommée dans la remise ; le tic est le mien |
| Tireurs (Rifleman, Shotgunner) | l'arme suit un modèle retenu de l'arsenal ; la bouche du canon est à une hauteur constante dans la pose de tir (je fais partir le projectile de là) ; une pose d'éclair de bouche séparée si voulu (lettre à part, 2 tics) |
| Boss | planche de silhouette et mécanisme d'abord ; un boss du banc actuel sert de gabarit d'états (entrée, trois attaques annoncées, phase 2, douleur, mort) : `bench/boss/FICHE_BOSS_SURVEILLANT.md` |
| Banc | `JOUER_RF2_BOSS_ESSAI.cmd` aujourd'hui ; un banc de familles (rotations, déplacement, obstacle, attaque, douleur, mort, corps) est en construction de mon côté et recevra chaque famille avant toute carte |
