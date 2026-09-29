# RF2-ARSENAL — contrat moteur, version 2 (29/09/2026)

Document de référence commun à Opus (intégration, banc) et Codex Astra (production des armes). Il remplace la
version 1 du 28/09 (sha256 `2acc1329…`, reçue par Astra ; conservée sous `CONTRAT_V1_20260928.md` dans le dossier de
transmission, marquée remplacée). Mandats : `C:\PROJECTS\RF2_SUITE_V01_20260928\` (`RF2_SUITE_OPUS_FABLE.md`,
`RF2_SUITE_ASTRA.md`, `08_ADDENDUM_REPLIQUES_VIKTOR.md`). Rien ici ne vaut verdict du propriétaire ; aucune arme
n'entre dans la campagne dans ce lot.

Mise à jour du 29/09, 16 h (même version, complétée, rien de retiré) : lot W05_W09_W10_V01 reçu (§0, §1), durées
et repères W10 (§4), règle 8 (§5), tableau §8 mis à jour, corrections communes du master (§9).

## 0. Espaces et versions

| | |
|---|---|
| Espace actif d'Astra | `C:\PROJECTS\RF2_UZDOOM\incoming\astra\` (Astra n'écrit que là ; confirmé le 29/09) |
| Livraisons figées | restent où elles ont été remises ; Opus consomme une copie contrôlée fichier par fichier (`scripts/arsenal/import_astra_lot.py`, fiche `art/rf2_arsenal_astra/IMPORT_<lot>.json`) |
| Banc | branche `bench/rf2-arsenal` du dépôt `C:\PROJECTS\RF2_UZDOOM` ; construction `scripts/arsenal/build_bench.py` ; lanceur `JOUER_RF2_ARSENAL_ESSAI.cmd` |
| Base du banc | `dist/arsenal/base/RF2_BASE_src_23773520f797.pk3`, sha256 `a03fad5f…` (jeu construit depuis `src/`, Browning et FAL identiques au build accepté) |
| Lot consommé | W03/W04 V01 (sha256 de `SHA256SUMS.txt` : voir la fiche d'import) ; V02 seulement pour un changement d'asset |
| Lot reçu | W05_W09_W10_V01 (fiches `IMPORT_W05_W09_W10_V01.json` et `…_W10_REEMPLOI.json`) : W10 = les 5 poses et 12 sons de la base, identiques octet pour octet, rien à importer ; W05/W09 = masters de travail, rien que le banc puisse charger |

## 1. Décisions fixées

| Sujet | Décision | Origine |
|---|---|---|
| W03 | Manufrance Rapid de chasse 12/70, canon lisse 700 mm, **tube 4 + chambre 1** (RGA BE050) | Astra, `DECISIONS_V01.md` ; extrait RGA conservé, ligne BE050 relue par Opus dans le CSV conservé (pas une vérification indépendante du RGA) |
| W04 | Manurhin MR73 Gendarmerie 4 pouces, poignée bois, six .357 Magnum | contrat v1, V01 |
| Recharge partielle W04 | règle **(a)** : l'extraction retire tout ; cartouches intactes rendues à la réserve ; étuis perdus ; puis une à une | propriétaire (`LIRE_D_ABORD.md`), V01 |
| Répliques | Manurhin « Police, Milice, prête à tirer ! » + ricanement ; fusil « Y a les bons et les mauvais chasseurs ! » ; une fois par campagne, à la première acquisition effective | propriétaire, `08_ADDENDUM_REPLIQUES_VIKTOR.md` |
| Suite | W05 FAMAS (F1 si rien d'autre n'est fixé), W09 Scorpion (scie alternative Black & Decker, pas circulaire), W10 pied-de-biche ; puis W06 M2 .50, W07 RPG, W08 lance-flammes | `RF2_SUITE_ASTRA.md` ; dossier maître §arsenal |
| W10 | le pied-de-biche du jeu (`RFCrowbar`, COMBAT-02) réemployé tel quel : poses, sons, code et réglages inchangés | Astra, `W10_REUSE_RECORD.json` ; identité vérifiée par Opus |
| Alimentation W09 | proposition d'Astra : câble vers une alimentation portée fictionnelle, aucun modèle à batterie inventé. **À décider par le propriétaire** (ressource limitée ou non, arrêt à vide). En attendant, le banc fait tourner la scie sans ressource | Astra, `POUR_OPUS.md` du lot W05_W09_W10_V01 |
| Campagne | aucune activation ; placement, équilibrage, munitions de campagne : étape ultérieure | mandats |

## 2. Présentation

Convention FAL inchangée pour toutes les armes à feu : toile 1536×1024 RGBA, XScale 6.8, YScale 8.16, Offset −750,−460,
flash sur son propre calque, même toile. Manche noire continue jusqu'au bord en 16:9, 21:9 et 4:3. Le banc vérifie
les collisions de noms de sprites et de chemins avec la base, le moteur et l'IWAD ; il refuse un module qui en a.

## 3. Fichier d'animation (`rf2-bench-animation/1`)

Tel que décrit dans `bench/arsenal/README.md`, avec l'extension V01 désormais lue nativement par le banc :

- `files` : image → chemin dans la livraison ; le module range chaque fichier à son `target_relpath` du manifeste.
- Revolver : `rig_layers.chambers` (6 listes, une image par pose du barillet), `rig_layers.hands` (6 listes, une image
  par étape de main), optionnel `rig_layers.chambers_fired` (même forme : image de l'étui tiré) ; par image :
  `chamber_pose` (0 = aucun calque, 1…n) et `hand_stage` (0 = pas de main, 1…n). Sprites `RMC1…RMC6` (chambres :
  poses puis étuis tirés) et `RMH1…RMH6` (mains), calques 101–106 (culots) et 107 (main).
- Culots visibles : chambres 1…(Étuis + Cartouches) ; étuis tirés d'abord (image `chambers_fired` si livrée), puis
  cartouches intactes ; après l'extraction, les seules cartouches chargées. La main suit la chambre en cours de
  remplissage (Cartouches + 1 à l'étape 1).
- Le tir reste **un seul** événement `shot` ; une introduction = **un** événement `shell_in` / `round_in`.

## 4. Durées en vigueur (V01 ; ajustables avec Astra, tout changement aligne événements et sons)

| | Séquences (tics à 35/s) |
|---|---|
| Rapid | tir 9 ; pompe 11 (`pump_back` à +4, `pump_fwd` à +7) ; recharge : entrée 6, une cartouche 12 (engagement à +6 de chaque cycle), sortie 6 ; premier engagement 12 tics après la demande de recharge |
| MR73 | tir 14 ; recharge complète 85 (ouverture 10, extraction 4, six introductions de 10 avec engagement à la 5e étape de main, fermeture 11) ; premier engagement 19 tics après la demande |
| Pied-de-biche | coup 22 depuis l'entrée en Fire (au tic de l'appui) : armé 5, course 3 (balayage au tic 5), impact 2 (**un** coup au tic 8), poursuite 4, retour 8 (changement d'arme permis, pas de second coup) ; prêt au tic 22. Mesuré au banc sur `RFCrowbar` : 5 / 8 / 22 |

## 5. Règles de jeu du banc (les mêmes dans l'image, le code et le HUD)

1. Le compte ne change qu'aux images d'événement : chargé + réserve + tiré reste constant.
2. **Engagement et changement d'arme** : une cartouche engagée (événement passé) avant la demande de changement
   finit son geste, puis l'arme est rangée à son point prévu (`ready_point`). Aucun engagement au tic de la demande ni
   après ; rien après le rangement effectif ; rien après la mort. Éprouvé au banc 2 et 1 tics avant, au tic même, 1
   et 2 tics après le point d'engagement : cartouche annulée avant et au tic, finie avant pour +1 et +2.
3. Détente pendant la recharge : la cartouche en cours finit, puis sortie de recharge (pompe si la chambre est vide)
   et tir.
4. Chambre vide, tube non vide : la détente fait une course de pompe sans tir. Tout vide : clic.
5. Réserve vide : aucune recharge ne commence ; réserve courte : on charge ce qu'il y a.
6. Sauvegarde pendant une animation : chargement avec les mêmes compteurs, la même séquence et les mêmes calques ; la
   recharge reprend et finit.
7. HUD d'essai, panneau d'arme : `4+1 | 24` (tube + chambre | réserve), `6 | 18` (barillet | réserve) ; panneau de
   diagnostic complémentaire.
8. Dégâts, dispersion, portées et cadences du banc : provisoires, pour la revue ; aucun n'est un équilibrage.

## 6. Preuves

- Une capture d'écran peut montrer un état plus ancien que le tic demandé (une image en attente de capture n'est
  pas redessinée) : le banc inscrit le tic dans chaque image (bande en haut à gauche, `scripts/arsenal/ticcode.py`)
  et journalise ce que chaque image montre ; captures et films sont classés par le tic qu'ils montrent.
- Preuve sonore : le son sorti du moteur (OpenAL, écrivain WAV) pendant la même session que l'image, calé par le
  bip de synchronisation du tic 1. Une piste reconstruite depuis un journal reste une prévisualisation étiquetée.
- Écoute : dire qui a écouté quoi, avec quel matériel ; à défaut, « à écouter ».

## 7. Répliques de Viktor (addendum)

Astra livre les prises (principale et variante par réplique), le ricanement séparé avec son repère temporel, masters,
exports 16 bits 48 kHz mono, sous-titres exacts, crédits et provenance. Opus relie le déclenchement à l'acquisition
effective (pas au ramassage d'un doublon, au changement d'arme, à une dotation technique ni à un chargement), avec
un état par arme persistant entre maps et sauvegardes, remis à zéro par une nouvelle campagne, joué une seule fois
par la file de dialogue avec le sous-titre ; la prise complète et ses éléments séparés ne sont jamais joués ensemble.

## 8. Armes suivantes : ce que le banc éprouvera

| | Mécanique au banc | Événements attendus (en plus de `raise`, `cloth`) |
|---|---|---|
| W05 FAMAS | chargeur (comme le FAL), sélecteur de tir à décider avec la bible (coup par coup / rafale), cadence propre | `shot` (un par cartouche), `dry`, `mag_out`, `mag_in`, `seat` (engagement du chargeur), `bolt` si la culasse est manœuvrée |
| W09 Scorpion | outil de contact continu : départ, marche à vide en boucle, contact (dégâts par intervalle dans une fenêtre de portée, jamais à travers un obstacle), arrêt ; le son de boucle s'arrête au relâchement, au rangement et à la mort | `start`, `loop` (boucle), `contact` (boucle ou coups), `stop` ; alimentation : voir §1 |
| W10 pied-de-biche | le vrai `RFCrowbar` de la base (réemploi) : touche la cible devant, s'arrête au pilier (aucun dégât derrière), rate dans le vide sans bouffée ni son d'impact ; repères §4 | déjà dans le jeu : `rf/crowbar/swing`, `…/flesh`, `…/metal`, `…/wood` ; raté = aucun son d'impact |

Les réglages de ces armes au banc servent la revue ; ils ne sont pas un équilibrage. Le banc garde aussi un pied-de-biche
générique (`RFBenchCrowbar`, images d'essai) : il éprouve la mécanique de mêlée du constructeur, pas l'arme du jeu.

## 9. Corrections communes du master (relevées sur W03/W04 V01, à porter sur W05, W09 et toute arme suivante)

1. **Recul lisible** : une vraie pose ou un `offset` par image de tir (le Rapid bouge de 3 à 9 px, le MR73 de 1 à 2 px
   sur 1536 : le banc ajoute un recul d'essai, `bench/arsenal/presentation/W03_W04_V01.json`).
2. **Un geste de main pour chaque changement d'état** : aucun objet qui apparaît ou disparaît seul (MR73 : extraction
   sans poussée de la tige). FAMAS : chargeur retiré et engagé par la main de soutien derrière la poignée, levier
   d'armement sous la poignée de transport ; Scorpion : doigt sur la gâchette au départ et relâché à l'arrêt.
3. **État visible = état du jeu** : tiré ou intact (`chambers_fired` pour le MR73), chargeur engagé ou non, scie en
   marche (lame et moteur qui bougent) ou arrêtée.
4. **Sortie de main entre deux gestes**, jamais de main flottante ; objets tenus entièrement dans le cadre ou sortis
   franchement (MR73 chambre 4, étape 1 : seule la pointe de la cartouche dépasse).
5. **Manche noire jusqu'au bord** en 16:9, 21:9 et 4:3 ; même prise et même manche que FAL/Browning.
6. **Axe de l'arme** : la bouche vise le centre de l'écran comme le FAL ; le master FAMAS de travail pointe nettement
   vers le haut à gauche, à vérifier dans le cadre du banc avant de décliner les poses.
7. **Sons** : un événement par geste, aligné sur son image ; boucles (scie) avec départ, boucle sans clic de raccord,
   arrêt ; rien n'est déclaré écouté sans écoute.
