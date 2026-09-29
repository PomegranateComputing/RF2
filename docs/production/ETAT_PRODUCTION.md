# RF2 — état de production actif

Document d'état de la production de campagne ouverte le 27 septembre 2026. Il remplace les priorités des mandats du
23, 25 et 26 septembre lorsqu'elles demandaient de refaire un élément désormais accepté. Mis à jour à chaque jalon ;
ce n'est pas un journal.

## 1. Verdict du propriétaire (27 septembre 2026)

Retour explicite du propriétaire, transmis par le pack `RF2_PRODUCTION_20260927` :

- **RF01 accepté** : carte, parcours et rencontres ; armes ; bras de Viktor en sweat noir ; sons améliorés.
- **Seule retouche demandée sur RF01 : les visuels des ennemis** (plus sombres, plus beaux, plus aboutis), sans
  changer leur gameplay.
- Nouveau travail autorisé : menus artistiques (RF2-UI-01), puis RF02–RF23 au standard RF01, un peu plus sombres,
  sales et étranges dans la suite, sans noircir RF01.
- Même bras et même manche de sweat noir pour tout l'arsenal. Musique : plus tard (aucune musique nouvelle).
- Sans Destination : arrêté. Fable : relais ponctuel seulement.

Portée de cette acceptation : c'est le jugement du propriétaire sur le build joué. Elle ne prouve ni une audition
exhaustive de chaque ressource ni une revue indépendante par l'agent. Le rapport `docs/RF2_ART_01_REVUE.md` (« aucune
écoute ») est antérieur à ce retour. Les nouvelles candidates (ennemis retouchés, menus, RF02…) **ne sont pas
approuvées** tant que le propriétaire ne l'a pas dit.

## 2. Référence acceptée (ne pas modifier)

| Élément | Valeur |
|---|---|
| Tag | `rf01-owner-accepted-20260927` → `5b53d9eaaaf088f49ae98f667fc1d575779dc74e` (branche `art/rf2-art-01-integration`) |
| Build | `dist\review\RF2_ART_REVIEW_20260926_1451\RF2_ART_REVIEW.pk3`, SHA-256 `04bdd0ae918761370c7620318f6e2add8bd1e1ac0acf88d55741c8be1883544f` |
| Construit depuis | `e1d007c` ; `5b53d9e` ne diffère que par `docs/RF2_ART_01_REVUE.md`. Contenu du pk3 = `src/` à `5b53d9e`, 1 146 fichiers, 0 écart (vérifié le 27/09) : aucune dépendance non suivie |
| Lanceur | `JOUER_RF2_ART_REVIEW.cmd` → `dist\review\LATEST.txt` → ce build ; config `user\uzdoom_art_review.ini`, sauvegardes `user\savegames_art_review` |
| Protection | pk3, `BUILD_INFO.json` et `LATEST.txt` en lecture seule ; `scripts/export_review.py` refuse désormais de réécrire `LATEST.txt` |
| Moteur | UZDoom 5.0.1 `uzdoom.exe` SHA-256 `1c76e2d1…1f49`, `uzdoom.pk3` `f1a1d319…eb82a`, OpenAL `soft_oal.dll` `4e2d830d…e0e8` |
| IWAD | Freedoom 0.13.0 `freedoom2.wad` SHA-256 `a8772e08…cd4b` |
| Renderer / config | configuration de revue copiée de `user\uzdoom.ini` ; aucun autoload (sections vides, pas d'`autoexec.cfg`) |

`main` reste à `6e1a31b` (base ancienne, non déplacée). La production part de la branche `prod/rf2-campaign`, issue du
tag. Chaque candidate reçoit son build et son lanceur (`scripts/export_candidate.py`, `JOUER_RF2_<LOT>.cmd`).

## 3. Rôles

| Zone | Écrivain |
|---|---|
| Maps, acteurs, scripts, audio en jeu, UI runtime, builds, rapports | Opus 5.5 (unique intégrateur de `C:\PROJECTS\RF2_UZDOOM`) |
| Sources et exports artistiques des lots attribués | Astra. Espace actif depuis le 29/09 (confirmé) : `C:\PROJECTS\RF2_UZDOOM\incoming\astra\`, où Astra écrit seule ; ses livraisons figées restent où elles ont été remises. Anciens worktrees (`RF2_UZDOOM_ASTRA_20260927`, `…_ARSENAL_20260928`, `…_RF01_TEXTURES_1940_20260928`) conservés, plus utilisés pour les remises |
| Acceptation artistique | Propriétaire |
| Fable | Tâche bornée attribuée explicitement, puis relais |

Contrats de transmission : `docs/production/handoff/`.

## 4. Ordres historiques (ne plus exécuter)

Clos par le verdict du 27/09 : refaire le pistolet, le son ou le parcours RF01 (mandats du 25 et du 26), relancer les
prompts du pack `RF2_ART_PASS_20260925`, reprendre les priorités Fable/RF01 du 23/09. Les deux captures du 25/09 sont
des preuves d'un ancien défaut, pas une cible. Les rapports et preuves RF01 existants restent valables pour ce qu'ils
mesurent.

## 5. Lots

| Lot | Contenu | Statut |
|---|---|---|
| Socle | Référence figée, branche de production, contrats, renvois réparés | fait (27/09) |
| RF2-ART-02 | Ennemis RF01, visuel seulement (Astra) | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED — `JOUER_RF2_ART-02.cmd`, build `RF2_ART-02_20260927_1356`, `docs/RF2_ART_02_INTEGRATION.md` |
| RF2-UI-01 | Menus artistiques, mort et reprise (art d'Astra) | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED — `JOUER_RF2_UI-01.cmd`, build `RF2_UI-01_20260927_1407`, `docs/RF2_UI_01_INTEGRATION.md` |
| RF2-CANON-01 | Fidélité au roman : matrice, fiches de scène | matrice active `docs/production/CANON_FIDELITE.md` ; CAN-001 à CAN-004 non intégrés |
| RF2-MAP-02 | RF02 complet | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED — `JOUER_RF2_MAP-02_RF02.cmd` (départ direct) / `JOUER_RF2_MAP-02.cmd`, build cumulatif, `docs/RF2_MAP_02_INTEGRATION.md` ; figures humaines attendues d'Astra |
| Campagne | RF03–RF23 dans l'ordre | remplacé par le mandat du 27/09 soir ci-dessous |

### Mandat du 27/09 soir (`C:\PROJECTS\RF2_CORRECTIONS_ET_SUITE_20260927`)

Revue jouée de RF02 par le propriétaire (dix captures). Autorisés : retouches de combat, mêlée (pied-de-biche),
équilibrage, décor, placements, UI défectueuse. Accord d'Elvis donné selon le propriétaire. Troisième niveau
narratif : Luna Park (ID technique RF04), sans écraser le blockout RF03 (Batignolles).

| Lot | Agent | Base | Fichiers possédés | Résultat attendu | État |
|---|---|---|---|---|---|
| RF01-PAN | Opus | tag `rf01-owner-accepted-20260927` | `scripts/mapkit/rf01.py` (panneaux), `src/maps/RF01.wad`, `udmf.py` (`texwidth=`), `materials.py` (`sign()`), `patches/rf01/RFSIGN*` | 13 panneaux lisibles ; registre vérifié en jeu : **lisible, aucun défaut** (`RF01_REGISTRE_VERIFICATION.md`) | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED — `JOUER_RF2_RF01-PAN.cmd`, build isolé `RF2_RF01-PAN_20260928_0725` (remplace 2245), `docs/RF2_RF01_PAN.md` ; porté sur `prod/rf2-campaign` |
| HUD-02 | Opus | `prod/rf2-campaign` | `src/zscript/rf/hud.zs`, `src/graphics/hud/viktor/` | portrait de Viktor en six états (commande du propriétaire) | candidate `RF2_HUD-02_20260927_2230` |
| RF02-A | Opus + Astra | `prod/rf2-campaign` | Opus : `scripts/mapkit/rf02.py`, runtime ; Astra : ressources | tranche de rue de référence | en cours — 23 enseignes accrochées (`e1e176c`, relevé 21/23) ; lot Astra `RF2_MAP_02` importé en HD (`7ceaf38`) ; V01–V10 et tranche de référence à faire ; `docs/RF2_RF02_A.md` |
| RF02-B | Astra produit, Opus intègre | idem | modèles tram/voie/props (Astra), collisions/ancrages (Opus) | tram complet sur rails, poussette, objets fixés | poussette (`51a7912`) et tram sur rails (`499244d`) intégrés, `docs/RF2_RF02_B.md` ; tableau des départs, barrage, Cochin : modèles attendus |
| RF02-C | Opus + Astra | idem | idem | parcours complet, figures F02-01…08, Luna Park | figures F02-01…08 placées (`9510b39`), `docs/RF2_RF02_C.md` ; entrée de Luna Park : modèle attendu |
| COMBAT-02 | Opus runtime, Astra présentation/audio | idem | `src/zscript/rf/weapons.zs`, rencontres | sons et retours d'armes, pied-de-biche, difficulté | pied-de-biche intégré et vérifié (`85fc6a1`), `docs/RF2_COMBAT_02.md` ; ressenti des armes à feu, rencontres, mesures : à faire |
| SUITE-03 | Opus + Astra | RF02 figé | `scripts/mapkit/rf04.py` (nouveau), campagne | premier segment Luna Park jouable | à faire |
| RF01-TEXTURES-1940 | Opus intègre, Astra produit | `candidate/rf01-textures-1940` (tag accepté + socle) | Opus : `TEXTURES.rf01`, affectations RF01, `MODELDEF` ; Astra : images | matières « Sainte-Anne 1940 » (mandat du 28/09) | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED — `JOUER_RF2_RF01_TEXTURES_1940.cmd` → build isolé **`RF2_RF01_TEXTURES_1940_20260929_1606`** (`67485285…`, commit `fadb3d8`), `docs/RF2_RF01_TEXTURES_1940.md`. Choix B du propriétaire : trois soubassements distincts d'Astra (écarts 19,9 / 30,8 / 29,8 ; 28,6 / 37,8 / 43,5 dans le jeu), enduit, carrelage, côté de table, à 8 px/u ; 4 décals d'usure reçus mais trop discrets, non intégrés ; RF01 A et B PASS ; RF02 identique au build accepté. Retours à Astra `handoff/RF01-TEXTURES-1940/RETOUR_OPUS_1.md` et `RETOUR_OPUS_2.md` (décals à reprendre, sang-de-bœuf plus sombre seulement sur demande du propriétaire, puis lot complet). Candidate 1745 conservée (`…_1745\JOUER.cmd`). Pas porté sur `prod/rf2-campaign` avant le lot complet et la revue du propriétaire |
| RF2-ARSENAL | Opus mène, Astra produit | tag accepté + socle (worktree d'Astra `RF2_UZDOOM_ASTRA_ARSENAL_20260928`) | Opus : contrat moteur, banc d'essai séparé ; Astra : W03 Manufrance Rapid, W04 Manurhin MR73 | deux armes jouables sur un banc d'essai hors campagne (`JOUER_RF2_ARSENAL_ESSAI.cmd`) | **Contrat v2** (29/09, seul en vigueur ; `docs/production/handoff/RF2-ARSENAL/CONTRAT.md`, identique sur `bench/rf2-arsenal` `d200735` ; copie `C:\PROJECTS\RF2_ARSENAL_20260928_CONTRAT_OPUS\`, v1 conservée et marquée remplacée). **W03 Rapid (4+1) et W04 MR73 de la livraison V01 d'Astra intégrés au banc et vérifiés au banc** : `JOUER_RF2_ARSENAL_ESSAI.cmd` → `dist\arsenal\RF2_ARSENAL_ESSAI_20260929_1545` (`5aaec05f…`), sondes armes, répliques (repères provisoires) et armes suivantes PASS ; W05 FAMAS et W09 Scorpion en essai ; W10 = le pied-de-biche du jeu, réemployé tel quel et éprouvé au banc. Défauts d'image renvoyés à Astra (recul, extraction MR73 sans geste, étuis tirés identiques aux cartouches intactes) ; `docs/RF2_ARSENAL_BANC.md`, retour `handoff/SUITE-20260929/RETOUR_OPUS.md`. **Aucun son écouté.** Répliques de Viktor : pas de prise. Aucune arme en campagne ni dans les cartes |

## 6. Matrice de couverture réelle

Statuts : `INVENTORIED`, `IN_PRODUCTION`, `INTEGRATED`, `RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED`, `OWNER_ACCEPTED`.
Un statut vaut pour un périmètre et une version.

### Cartes

| Carte | Titre (repère V1) | État | Preuve / build | Verdict |
|---|---|---|---|---|
| RF01 | Sainte-Anne - Les portes ouvertes | OWNER_ACCEPTED (carte, armes, bras, sons) ; ennemis : retouche en cours | build 20260926_1451 | accepté 27/09 hors ennemis |
| RF02 | Paris - Rue de service | RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED (carte produite, 15 scènes du texte, 7 vagues) ; figures humaines manquantes | `RF2_MAP-02_20260927_1543`, traversées A et B PASS, film | — |
| RF03–RF23 | voir `agent/specs/MAPS_V1_INVENTORY.md` | INVENTORIED (blockouts V1, ennemis Freedoom) ; RF02 finit sur l'écran titre tant que RF03 n'est pas produit | — | — |

### Arsenal (liste du dossier maître, `legacy/import/RF2_DOSSIER_MAITRE.md` §10)

| Arme | État |
|---|---|
| Browning Hi-Power | OWNER_ACCEPTED (RF01) — master du bras et de la manche |
| FN FAL | OWNER_ACCEPTED (RF01) |
| Pied-de-biche (`RFCrowbar`) | INTEGRATED sur `prod/rf2-campaign` (COMBAT-02, `85fc6a1`) ; réemployé comme W10 de l'arsenal ; non jugé par le propriétaire |
| Fusil à pompe : W03 Manufrance Rapid 12/70, tube 4 + 1 | banc d'essai seulement (V01 d'Astra, vérifié au banc, non écouté) ; hors campagne |
| Revolver : W04 Manurhin MR73 Gendarmerie | banc d'essai seulement (V01 d'Astra, vérifié au banc, non écouté) ; hors campagne |
| FAMAS F1 (W05) | master de travail d'Astra ; mécanique éprouvée au banc sur images d'essai |
| Scie Black & Decker Scorpion (W09) | master de travail d'Astra ; mécanique éprouvée au banc sur images d'essai ; alimentation à décider par le propriétaire |
| Browning M2 .50, pistolet taser | INVENTORIED (seconde vague) ; références préparatoires d'Astra pour la M2HB (présentation joueur à préciser) |
| RPG (W07) | références préparatoires d'Astra (RPG-7V) |
| Lance-flammes | INVENTORIED, demande à reconfirmer ; M2-2 proposé par Astra (références seulement) |

### Ennemis

| Famille | Utilisée par | État |
|---|---|---|
| Infirmier `RFOrderly` (ORDY) | RF01 | gameplay accepté ; visuel : candidate RF2-ART-02 à juger |
| Brancardier `RFBrancardier` (BRCD) | RF01 | idem |
| Porte-Registre `RFPorteRegistre` (PREG, liasse PRGS) | RF01 | idem |
| Rifleman, Shotgunner, Custodian (roster du dossier maître §14) | — | INVENTORIED |
| Monstres Freedoom des blockouts RF02–RF22 | blockouts | provisoires, à remplacer carte par carte |

### Audio

| Élément | État |
|---|---|
| Sons RF01 (66 fichiers, mix) | OWNER_ACCEPTED — référence sonore |
| Lit `RFAMB01` (déclaré comme musique dans MAPINFO, joué en fond d'ambiance) | existant, inventorié ; traitement musical différé |
| `$MUSIC_RUNNIN` (Freedoom) en `defaultmap` pour RF03–RF22, `$MUSIC_READ_M` à la fin | existant, inventorié ; non supprimé, traitement différé (RF02 reprend le fond RFAMB01) |
| Sons de lieu RF02 (TSF, téléphone, moteurs, cloche, feu, rue) | synthèse provisoire d'Opus, non écoutée par un humain ; demandés à Astra |

### UI

| Écran | État |
|---|---|
| Menu principal, pause, chargement, sauvegarde, options, crédits, confirmations, mort et reprise | candidate RF2-UI-01 (RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED) |
| HUD, titre de niveau, fin de niveau | RF01 accepté |

## 7. Reprise

Voir la dernière section « Reprise » de ce fichier après chaque jalon : commit, lot en cours, dépendance, prochaine
action.

- 27/09 — socle posé sur `prod/rf2-campaign`. Prochaine action : RF2-UI-01 (structure) et RF2-MAP-02 (fiche, carte).
- 27/09 après-midi — lots Astra ART-02 et UI-01 intégrés chacun sur sa branche candidate, exportés, joués de bout en
  bout (RF01 A et B PASS avec chaque build). UI-01 re-exporté en 1407 : le moteur affichait « Player died. » à une
  mort sans attaquant (obituaires du moteur traduits). Matrice de fidélité au roman écrite (lecture intégrale).
  Branche `prod/rf2-campaign` = cumul (socle + ART-02 + UI-01 + outils). Prochaine action : carte RF02
  (`scripts/mapkit/rf02.py`), puis candidate RF2-MAP-02.
- 27/09 soir — RF02 produit sur `prod/rf2-campaign` : carte, matières, sons de lieu, scènes, vagues ; traversées A et
  B PASS ; RF01 rejoué sur le même build (A et B PASS, objectifs identiques). Défauts du code partagé corrigés hors
  RF01 ; un défaut de RF01 accepté prouvé et signalé sans correction (panneaux muraux invisibles, preuve dans la
  candidate MAP-02). Prochaine action : retours du propriétaire sur ART-02, UI-01, MAP-02 ; figures RF02 d'Astra ;
  décision sur l'ordre RF03/Luna Park ; puis RF03.
- 28/09 matin — RF01-PAN : vues dans le moteur de la candidate 2245 → plaques visibles mais 11 sur 13 pas contre
  leur mur (coordonnées hors de la grille, deux dans l'embrasure tournées vers la porte, une au milieu du couloir) et
  quatre textes coupés dans la texture. Relevé outillé (`scripts/production/rf01_sign_survey.py` : source acceptée
  0/13, candidate 13/13), plaques reposées sur leur mur ou leur linteau, textures corrigées, texture entière ajustée
  à la ligne. Candidate `RF2_RF01-PAN_20260928_0725` (sha256 `1439a27e…`) : 26 vues avant/après et 7 portes
  ouvertes, rapport `docs/RF2_RF01_PAN.md`. Correction portée sur `prod/rf2-campaign` (RF01.wad identique à celui
  de la candidate, RF02 inchangé). Prochaine action : lots RF02-A/B (livraisons Astra), COMBAT-02.
- 28/09 matin (suite) — RF02-A : les 23 enseignes de RF02 avaient la même erreur que RF01 (4 u du mur, texture
  coupée ; Port-Royal sans mur) : testée dans le moteur puis corrigée à la source (`e1e176c`). Lot Astra `RF2_MAP_02`
  importé en présentation HD (`7ceaf38`, contrôles d'empreintes, patch d'échelles, RF02 A et B PASS). Lot
  `RF2_MAP_02_REPRISE` (figures, pied-de-biche) terminé côté Astra, à intégrer ensuite. Nouveau mandat du
  propriétaire : passe de textures RF01 « Sainte-Anne 1940 » ; inventaire de 60 surfaces, contrat et 52 captures de
  la base remis à Astra ; branche `candidate/rf01-textures-1940` créée. Prochaine action : premier ensemble Astra
  (chambre, couloir), intégration des figures et du pied-de-biche, V01–V10.
- 28/09 après-midi — lot Astra `RF2_MAP_02_REPRISE` intégré : figures F02-01…08 placées dans RF02 (`9510b39`),
  pied-de-biche (COMBAT-02, `85fc6a1`, essais en jeu cas par cas). RF02-B : poussette et tram d'Astra (le tram sur de
  vrais rails, son volume jouable gardé invisible dans la carte, `499244d`). V01–V10 reconstitués aux cadrages du
  propriétaire, avant/après (`2d44f86`). Scène du ticket fiabilisée (cône d'usage). Aucune nouvelle livraison d'Astra
  pour la passe de textures RF01 à cette heure. Prochaine action : lisibilité de l'interface (messages, attribution,
  relecture, compteurs), rencontres et mesures de difficulté, puis Luna Park dès les modèles d'Astra.
- 29/09 — mandat « Suite Opus/Fable » (`C:\PROJECTS\RF2_SUITE_V01_20260928\`). Arsenal : V01 W03/W04 d'Astra
  contrôlé (3665 fichiers) et lu tel quel par le banc (`bench/rf2-arsenal`) ; son adaptateur de barillet reporté dans
  le constructeur ; règle de changement d'arme tenue par le code (l'arme engageait au tic de la demande) ; Rapid 4+1
  partout ; captures classées par le tic qu'elles montrent et films à son natif ; builds `…_1532` (revue) et `…_1545`
  (lanceur) ; W05/W09/W10 éprouvés au banc, le W10 réel compris. Contrat v2, seul en vigueur, sur les deux branches.
  RF01 : envoi d'Astra du 29/09 comparé dans le moteur, six matières intégrées (candidate 1606), décals retenus.
  Retours à Astra déposés dans son espace (`incoming/astra/RF2_SUITE_20260929/RETOUR_OPUS.md`, `RETOUR_OPUS_2.md`).
  Aucun son écouté ; aucune nouvelle candidate approuvée. Ce mandat ne remplace pas les corrections RF02 ni la
  production MAP03 : leur ordre sur cette branche est inchangé, aucune arme du banc n'entre dans les cartes. Prochaine
  action : décals et lot complet RF01 d'Astra (nouvelle candidate datée), V02 W03/W04 si Astra corrige, W05/W09
  animés, prises de Viktor ; décisions du propriétaire : alimentation de la scie, sang-de-bœuf.
