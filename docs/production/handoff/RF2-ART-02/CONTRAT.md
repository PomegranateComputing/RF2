# RF2-ART-02 — ennemis RF01, retouche visuelle seulement (Opus → Astra)

Préparé le 27/09/2026 par Opus (intégrateur). Fichier lisible depuis
`C:\PROJECTS\RF2_UZDOOM\docs\production\handoff\RF2-ART-02\CONTRAT.md`. Le manifeste machine est
`BASE_MANIFEST.json` à côté.

## 1. Lot

- **Inclus** : les images des trois familles de RF01 et, si utile, la liasse lancée ; les poses terminales (modèles
  OBJ + skins) si leur retouche est nécessaire pour la cohérence.
- **Exclu** : classes, placements, IA, hitbox (`Radius`/`Height`), santé, dégâts, vitesses, états et durées, drops,
  triggers, sons, carte RF01, armes, HUD, système de pose des corps (`RFBody`).
- **Fin** : les trois familles complètes (tous les frames × 8 rotations listés ci-dessous), sources, manifeste,
  crédits, avant/après à réglages égaux, séquences en jeu, vues autour du corps. Candidate : `OWNER_REVIEW_REQUIRED`.

## 2. Base

| | |
|---|---|
| Commit | `5b53d9eaaaf088f49ae98f667fc1d575779dc74e` = tag `rf01-owner-accepted-20260927` |
| Ton worktree | `C:\PROJECTS\RF2_UZDOOM_ASTRA_20260927`, branche `art/rf2-art-02-astra` (créé par toi à 12:22, même commit) |
| Build de référence joué | `C:\PROJECTS\RF2_UZDOOM\dist\review\RF2_ART_REVIEW_20260926_1451\RF2_ART_REVIEW.pk3` (lecture seule) |
| Moteur | `C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe`, IWAD `C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad` |
| Commandes qui marchent (dans ton worktree) | `pwsh scripts/build.ps1` ; `python scripts/devrun.py --norun` ; `python scripts/devrun.py --map RF01 --name lineup +rf_dev_weapons 1` (les trois familles côte à côte dans la cour, puis tirs) ; `python scripts/devrun.py --map RF01 --name corpse +rf_dev_corpse 1 +r_drawplayersprites 0 +screenblocks 12` (chaque famille tuée sur 7 appuis, 4 côtés + plongée, Z journalisé) ; `RF_DEV_HIDDEN=1` pour un bureau invisible. `devrun` copie `user\uzdoom.ini` : s'il manque dans ton worktree, copie celui de `C:\PROJECTS\RF2_UZDOOM\user\uzdoom.ini` (ne modifie pas l'original). |
| Pipeline existant | `art/rf2_art_01/enemies/production.py --workers 4` (rig SDF articulé + `material_atlas.png`, 8 angles réels, 5 px/unité, précompensation verticale 1,2, grAb après recadrage) ; `corpses.py --family all` pour les OBJ |

## 3. Consommateurs (vérifié dans les 23 WAD le 27/09)

Seul **RF01** place ces classes (16 infirmiers, 2 brancardiers, 2 porte-registres, 2 infirmiers morts de décor, 5
`RFWaveSpot`). RF02–RF22 sont encore des blockouts peuplés de monstres Freedoom. Consommateurs de code :

| Sprite | Classes | Remarque |
|---|---|---|
| `ORDY` | `RFOrderly`, `RFOrderlyCorpse` (frame M), `RFWaveSpot` (args 1) | M = pose terminale : modèle `orderly.obj` + sprite de repli |
| `BRCD` | `RFBrancardier`, `RFWaveSpot` (args 2) | M terminal : `brancardier.obj` |
| `PREG` | `RFPorteRegistre`, `RFWaveSpot` (args 3) | K terminal : `porte_registre.obj` |
| `PRGS` | `RFRegistryBundle` (liasse lancée, frames A/B, 3 tics chacune) | facultatif |

Outils de dev qui les font apparaître : `rf_dev_weapons`, `rf_dev_corpse`, `rf_dev_perf 2`, `rf_dev_art_combat`,
sonde sonore. **RF02 réutilisera probablement ces familles** (poursuite depuis Sainte-Anne) : ta retouche s'y
propagera, c'est voulu.

## 4. États et durées (tics à 35/s) — ne pas changer

| Famille | Repos | Marche | Attaque | Douleur | Mort |
|---|---|---|---|---|---|
| ORDY | A 10 | B C D E × 4 | F 10 (armé) → G 4 (coup) → H 14 | I 3 + 4 | J 6, K 7, L 8, **M** terminal |
| BRCD | A 10 | B C D E × 5 | F 24 (arc-bouté) → G 1 ; charge G/N × 2 en boucle ; impact O 8 ; récupération H 28 | I 8 | J 7, K 8, L 10, **M** terminal |
| PREG | A 8 | B C D E × 5 | F 26 (préparation) → G 2 (lancer) → N 12 | H 5 | I 7, J 7, **K** terminal |

Chaque frame existe en **8 rotations réelles** (1 = face, puis sens des rotations du moteur), sans miroir. Tailles et
grAb actuels par fichier : `BASE_MANIFEST.json` (champ `grAb` = décalage x,y ; le y place les pieds sur le sol).

## 5. Échelle et ancrage

- `Scale 0.18` pour les trois classes ; PNG exporté à 5 px par unité de carte avec précompensation verticale 1,2
  (étirement vertical du pixel du moteur). Hauteur visible debout proche de l'actuelle : garder la silhouette dans la
  boîte de collision (`Radius`/`Height` : ORDY 18/60, BRCD 40/64, PREG 22/70).
- Pieds sur la ligne de sol dans **tous** les frames debout (grAb y = bas des pieds). Pas de variation de taille entre
  frames ou rotations.
- Poses terminales : si tu changes un OBJ, garde Z minimal = 0, pivot au centre du corps, même échelle
  (`MODELDEF` : `Scale 5 5 6`, `CorrectPixelStretch`). Donne l'emprise du corps couché (t = avant/pieds, s = gauche,
  en unités) : `enemies.zs` appelle `RFBody.Settle(self, tmin, tmax, smin, smax)` avec ORDY −30.5 33.3 −19.4 23.2,
  BRCD −49.1 33.3 −47.3 13.7, PREG −31.3 37.9 −19.2 23.6. Toute nouvelle emprise = proposition runtime séparée.
- Lumière : `lightmode 8`, lumières dynamiques ×1,3 à ×1,6 près des lampes (`r_dynlights`) : garder de la marge dans
  les clairs (la blouse ne doit pas rebrûler au blanc). Pas de correction de gamma, pas de fumée pour masquer.

## 6. Direction (rappel de la directive du 27/09)

Mêmes familles, mêmes rôles, mêmes signes de reconnaissance (infirmier en blouse ; brancardier et son brancard sur
roues, porteur et charge peu séparables ; porte-registre au torse chargé de registres et liasses). Plus sombres =
plus inquiétants et plus précis : volumes, visages, mains, plis, poids des étoffes, cuir, métal, usure située. Pas de
zombie générique, pas de faction ni de monstruosité ajoutée, pas de noircissement global. Un seul master par famille
pour tous les frames et rotations.

## 7. Références jointes

- `refs_acceptees_20260926/` : captures du build accepté (alignement des trois familles, tir, cadavres sur sol plat,
  escalier, mur, perron, cadrage du bras). Ce sont les références **actuelles**, pas un défaut à reproduire.
- Bras/manche validés : `src/graphics/weapons/browning/*.png`, `src/graphics/weapons/fal/*.png` (pour la cohérence des
  valeurs de peau et de noir textile).
- Les deux captures du pack du 25/09 montrent l'ancien défaut ; ne pas les viser.

## 8. Livraison attendue (Astra → Opus)

Dans ton worktree, `incoming/astra/RF2_ART_02/` (convention actuelle) :

- `manifest.json` : une ligne par export — chemin dans le lot, cible exacte sous `src/`, action (remplacement),
  consommateur (classe, frame, rotation), dimensions, grAb, SHA-256 de l'export **et** du fichier de base remplacé
  (celui de `BASE_MANIFEST.json`), source/master, outil et version, crédit, preuve.
- `runtime/` : les PNG (noms de lumps identiques à l'existant : `ORDYA1.png`…), éventuels OBJ/skins.
- `patch/` séparé (facultatif) : toute proposition runtime (emprise des corps, MODELDEF) avec sa raison.
- `evidence/` : avant/après à cadrage et lumière égaux, séquence de chaque famille en jeu, cadavres autour/en plongée.
- Sources et crédits reproductibles (pas de WAD, pas de config personnelle, pas de copie de `src` entier).

Opus importe fichier par fichier dans le périmètre, compare chaque empreinte de base à l'arbre courant, reconstruit
et vérifie en jeu (hash `RF01.wad`, diff des comportements vide, séquences, cadavres, parcours A/B).
