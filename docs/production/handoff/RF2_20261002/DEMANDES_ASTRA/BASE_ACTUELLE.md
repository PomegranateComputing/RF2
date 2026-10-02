# Base actuelle de RF2 — relevé du 02/10/2026

## Dépôt et builds

| | |
|---|---|
| Dépôt | `C:\PROJECTS\RF2_UZDOOM`, branche `prod/rf2-campaign` ; `main` et le tag `rf01-owner-accepted-20260927` intacts |
| HEAD à ce relevé | `61d9b43` (les empreintes de base des manifestes de ce dossier sont celles de `src/` à ce commit) |
| Modifications en cours | aucune dans `src/` ; documents de la consigne de préservation en cours d'enregistrement |
| Build joué par `JOUER_RF2_CUMUL*.cmd` | `dist\candidates\RF2_CUMUL_20261001_1605` (`0efa3726…`) |
| Build le plus récent | `dist\candidates\RF2_PORTES_20261002_1018` (`469418f2…`, lanceurs `JOUER_RF2_PORTES*.cmd`) : mêmes sources que HEAD ; c'est la référence visuelle pour tes « avant » |
| Référence acceptée | `dist\review\RF2_ART_REVIEW_20260926_1451` (RF01, `JOUER_RF2_ART_REVIEW.cmd`), jamais modifiée |
| Build 1821 du 30/09 | historique ; base du pack, plus la base de travail |
| Moteur | UZDoom 5.0.1, IWAD Freedoom 0.13.0 ; rendu du propriétaire : `gl_texture_filter 6`, `gl_spriteclip -1` |

## Ce qui a changé depuis le 1821 (ce que le pack ne pouvait pas savoir)

- **Campagne** : RF01 → RF02 → RF04 → RF05 → RF06 → RF07, une planche entre deux chapitres, écran de fin après RF07.
- **RF04 et RF05 recomposés** (01/10) sur un seul parc (`scripts/mapkit/luna_park.py`) : esplanade, bassin du Water
  Chute et sa tour, grand huit (tréteaux, rampe de levage, quai), Brooklyn et sa coulisse, kiosque, manège, salle de
  danse et son aile, ruelle derrière la piste, sous-station. RF05 : sous-sol voûté au nord, galeries, puits d'air,
  magasin d'enseignes, transformateurs et pompes ; le train vide monte la rampe. Voir `PLANS/`.
- **RF06 recomposé** : six moments, deux explorations latérales, sans combat.
- **RF07 construite** (Jerma, l. 733–765 de l'ancien EPUB), sans combat, ressources provisoires. RF08–RF12 découpées.
- **Reflets de Viktor** : le vrai Viktor partout (R2F8 V02 ; R4V2, R4V3 pour les deux autres tenues), 56 u.
- **Ennemis** : ORDY V03 + E V04, BRCD V02, PREG V02 et son corps.
- **Portes** (02/10) : toutes les portes, grilles, rideaux et façades des 23 cartes reprises ; dormants et linteaux
  fixes, images de porte recomposées à la taille de chaque ouverture (`docs/RF2_PORTES_20261002.md`).
- **Transitions** : système de planches et cinq planches en jeu.
- **Banc du boss** : hors campagne (`JOUER_RF2_BOSS_ESSAI.cmd`). **Banc des armes** : inchangé dans ses mécanismes.

## Lots intégrés (relevés d'import, `docs/production/handoff/…/IMPORT_<lot>.json`)

| Date | Lot | Fichiers | Auteur |
|---|---|---|---|
| 27–29/09 | RF2-ART-02 (ennemis RF01), RF2-UI-01 (menus), RF2_MAP_02 et sa reprise (RF02 : façades, figures, pied-de-biche, tram, landau), RF01 textures 1940 | (imports antérieurs à l'outil de relevé) | Astra |
| 30/09 | `ORDY_V03` 106, `RF01_OXBLOOD_DECALS_V03` 5, `LUNA_V01_TRANCHE01` 16 | 127 | Astra |
| 01/10 13 h | `R2F8_V02` 8, `R4V2_R4V3_V01` 16, `ORDY_E_V04` 8, `RF02_PHARMACIE_01` 1, `LOT_CORRECTIONS_01` 4, `LUNA_PILOTE_01` 6, `COMIC_RF01_RF02_01` 1 | 44 | Codex |
| 01/10 16 h | `LUNA_PILOTE_02` 15, `BROOKLYN_ARCH_V02` 1, `RF4_FACADES_V02` 3, `RFDSTN1_V05` 1, quatre planches, `RF05_RF06_MATERIALS_01` 6, `RF05_MACHINES_01` 7, `AUDIO_TIMING_01` 8 sons de campagne | 45 | Codex |
| 02/10 | `BRCD_V02` 120, `PREG_V02` 97, `RF04_SHOE_V02` 1, `RF05_DIALS_V02` 2, `RF06_FLATS_01` 2 | 222 | Codex |

L'origine de chaque fichier en jeu figure dans la colonne `origine` des tables `CONTRATS/*_FICHIERS.csv`.

## Ce qui reste provisoire (dessiné par Opus pour faire tourner les cartes)

- RF07 entier : `RF7_*` (graffitis, façade, béton, terrasse, moquette, verre, NO FUTURE, mer), Elvis `R7EV`, sommier `R7SB`.
- RF04/RF05 : gardien `R4G1`, juke-box `R4JB`, nacelles de la tour aérienne (boîtes), flaque `RF4_FLAQ`, guérite, vitres,
  affiches `RF4_AFF*`, enseignes SALLE DE DANSE, piquets, courroie, levier `RF5_LEV*`, fusibles `RF5_FUS*`, enseigne
  `RF5_LUN*`, escalier `RF5_ESCA`, train `R5TR`, enveloppe `R5EN`.
- RF06 : numéros `RF6_N*`, cinq `RF6_ER*`, le jour `RF6_JOUR`, lit de la chambre 404.
- RF02 : objets frustes de l'audit (`../RF2_20261001/audit_rf02/AUDIT_RF02.md`) : ambulance, fontaine, sacs de sable,
  matelas, entrée du Luna Park, rails, plafond du tram.
- Portes : trumeaux et fins de façade (poteau répété, pièce de mur nu) ; porte à badge des blockouts.
- Banc du boss : le surveillant-chef.

## Règles qui ne changent pas

Le Jerma entier et RF06 sans combat ; Elvis, le gardien, la jeune femme, les couples ne sont jamais des cibles. Les
armes nouvelles restent sur leur banc. Rapid 4+1, barillet six chambres du MR73, cadence de la Scorpion inchangés. Pas
de musique nouvelle. Rien n'est accepté artistiquement sans le verdict du propriétaire sur une candidate nommée.
