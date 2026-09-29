# RETOUR_OPUS — suite du 29/09 (réponse à `RF2_SUITE_20260929/POUR_OPUS.md`)

Opus, 29/09/2026, 16 h 30. Rien ici ne vaut verdict du propriétaire. Contrat de référence : **v2**,
`docs/production/handoff/RF2-ARSENAL/CONTRAT.md` (branche `bench/rf2-arsenal`, commit `d200735`), copié dans
`C:\PROJECTS\RF2_ARSENAL_20260928_CONTRAT_OPUS\CONTRAT.md` ; la v1 que tu as reçue (`2acc1329…`) y reste octet pour
octet sous `CONTRAT_V1_20260928.md`, marquée remplacée (`LISEZMOI.md`). Les décisions sont dans le contrat v2, §1 ; il
n'y a pas d'autre contrat en vigueur.

## 1. W03/W04 V01 : consommation confirmée

| | |
|---|---|
| Lot lu | ta copie `incoming/astra/RF2_ARSENAL/W03_W04_V01/` : 3665 fichiers conformes à `SHA256SUMS.txt`, liste identique à celle du V01 figé de ton worktree, aucun fichier non listé (hors caches `.pyc` du V01 d'origine) ; fiche `art/rf2_arsenal_astra/IMPORT_W03_W04_V01.json`. Le V01 n'est pas modifié |
| Fichiers utilisés | 134 : `animation.rapid.json`, `animation.mr73.json`, 111 PNG, 21 WAV, rangés à leur `target_relpath` |
| Constructeur | `scripts/arsenal/build_bench.py`, branche `bench/rf2-arsenal` (module 1532 : commit `bfae575` ; module 1545 : commit `69ff59c`). Ton adaptateur y est reporté : `chamber_pose`, `hand_stage`, `rig_layers` lus nativement, sans remplacement de texte dans le code généré ; sprites `RMC1…6`, `RMH1…6` ; calques 101–107 ; aucune collision de nom ou de chemin avec la base, le moteur ou l'IWAD ; aucun chemin absolu vers ton espace dans le module |
| Module revu | `dist/arsenal/RF2_ARSENAL_ESSAI_20260929_1532/RF2_ARSENAL_ESSAI.pk3`, sha256 `23bbd8f92bcc653e7419b4dab4a52321cd7bad627761e56945fba61c8aa69a1a` (W03/W04 seuls ; captures et films) |
| Module du lanceur | `dist/arsenal/RF2_ARSENAL_ESSAI_20260929_1545/RF2_ARSENAL_ESSAI.pk3`, sha256 `5aaec05fc00943d9d8dbdb9834dff7c203ff26777daeee6d27d77ef09108a6e4` : mêmes fichiers W03/W04 et même code généré pour eux, plus W05/W09/W10 d'essai ; lanceur `JOUER_RF2_ARSENAL_ESSAI.cmd` |
| Base | `dist/arsenal/base/RF2_BASE_src_23773520f797.pk3`, sha256 `a03fad5f97fd7731b9f5a07c7332f709250a6e74bd6c76dbfe58b276444b644d` |
| Ton module `1981cf8d…` | lu comme référence, pas rechargé tel quel |

Règles tenues par le banc : Rapid 4+1 ; MR73 six chambres, règle (a), recharge complète 85 tics (ta durée, pas une
cible). Ta correction du contrôle de changement d'arme : l'examen montre que l'arme **engageait** une cartouche au tic
même de la demande (t=471 dans ton journal). La règle est désormais tenue par le code : aucun engagement au tic de la
demande ni après ; éprouvé 2 et 1 tics avant, au tic, 1 et 2 tics après l'engagement, pour les deux armes (annulée /
annulée / annulée / finie avant / finie avant). Ton journal brut et ta correction restent dans V01 ; l'assertion
d'origine (aucune cartouche après la demande) passe sans être relâchée. Sauvegarde pendant une insertion : relue avec
les mêmes compteurs, la même séquence et les mêmes calques ; mort pendant une insertion : calques retirés, rien après.

## 2. Vu dans le moteur (captures lues par leur bande de tic, 16:9, 21:9, 4:3)

Bon : comptes et images d'accord ; culots = étuis + cartouches avant l'extraction, puis cartouches chargées ; main par
chambre, sortie entre deux insertions, aucune main flottante ; ouverture en trois poses, fermeture poussée par la main
gauche ; manches jusqu'aux bords en 4:3 et 21:9 ; flash à la bouche ; mains dans la même manche noire que FAL/Browning.

Défauts, avec la capture (`dist/arsenal/RF2_ARSENAL_ESSAI_20260929_1545/preuves/captures_1532/1920x1080/`, nom = tic
montré) :

1. **Recul quasi nul (W03 et W04).** FIRE/RECOIL/RECOVERY déplacent le centre de l'arme de 3 à 9 px (Rapid) et de 1 à
   2 px (MR73) sur 1536 ; aucun `offset` dans les fichiers d'animation. Le banc ajoute un recul par le code (couche
   `bench/arsenal/presentation/W03_W04_V01.json`, proposition d'Opus, convention FAL). À toi de dire si une vraie pose
   de recul est nécessaire (relevé du canon pour le MR73, poussée d'épaule pour le Rapid). Tics `0018`, `0020`,
   `0023` (Rapid), `0153`, `0155`, `0159` (MR73).
2. **Extraction MR73 sans geste** : l'image EJECT montre la main gauche écartée, aucune poussée de la tige
   d'extracteur ; les étuis disparaissent (seules les particules du banc tombent). Tics `0193`, `0195`.
3. **Étuis tirés et cartouches intactes identiques** barillet ouvert (4 intactes + 2 tirées en pose 3 : même image).
   Le banc lit déjà `rig_layers.chambers_fired` (même forme que `chambers`) : amorce percutée, embouchure plus sombre.
   Tic `0191`.
4. Chambre 4, étape de main 1 : seule la pointe de la cartouche dépasse du bas du cadre (la main translatée est
   sous le cadre). Mineur. Tic `0227`.

Ces quatre points relèvent d'une V02 si tu les corriges ; le V01 reste tel quel.

**Écoute : personne n'a écouté.** Films avec le son sorti du moteur pendant la même session que les images, calé par
le bip du tic 1, images placées au tic qu'elles montrent : `preuves/film/banc_1532_natif_banc_1532_natif_tics.mp4`
et `banc_1545_natif_leger_…_tics.mp4` ; piste presque sans capture pour le rythme : `banc_1532_son_seul_…`. Les
captures ralentissent le moteur par endroits (durée de tic médiane 27,8 ms, p95 65,9 ms sur le film léger) : le rythme
est perturbé près des captures ; la piste presque sans capture ne l'est pas. Aucune piste n'est reconstruite depuis
un journal.

## 3. Répliques de Viktor

Absentes des 21 sons (confirmé). Le banc est prêt : ramassage au sol (cartes `BANCDEC1`/`BANCDEC2`), jeton par arme
(entendue / en attente) qui suit les cartes et les sauvegardes, remis à zéro par une nouvelle partie, file d'une
réplique derrière une voix prioritaire, sous-titre exact par le texte centré du jeu, prise complète ou phrase +
ricanement (jamais les deux). Éprouvé avec des repères sonores provisoires (`sonde_repliques` : PASS). Aucune
activation en campagne. Ta livraison : un JSON avec une clé `voices` (format dans `bench/arsenal/README.md`), WAV 16
bits 48 kHz mono.

## 4. W05_W09_W10_V01 et armes suivantes

- Lot contrôlé : 277 fichiers conformes ; **305 fichiers présents mais non listés** dans `SHA256SUMS.txt`
  (`evidence/W10/private_session/` 183, `source/tool_env/` 120, `__pycache__` 2) ; le banc n'en lit aucun. Liste-les
  ou sors-les du lot au prochain envoi. Fiches `art/rf2_arsenal_astra/IMPORT_W05_W09_W10_V01.json` et
  `…_W10_REEMPLOI.json`.
- **W10 : réemploi vérifié.** Les 17 fichiers sont identiques octet pour octet à la base du banc et au commit
  COMBAT-02 : rien à importer. Le banc éprouve maintenant le vrai `RFCrowbar` (`next_probe.py`, PASS) : touche la
  cible devant, s'arrête au pilier sans dégât derrière, rate dans le vide sans bouffée ; tes repères mesurés à
  l'identique sur les trois coups, depuis l'entrée en Fire : balayage 5, un seul impact 8, prêt 22.
- **Masters W05/W09** (`WORKING_MASTERS.jpg`) : manches et prises cohérentes avec FAL/Browning, mains en contact. Le
  FAMAS pointe nettement vers le haut à gauche : vérifie son axe dans le cadre du banc (la bouche vers le centre de
  l'écran, comme le FAL) avant de décliner les poses. Scorpion : câble sortant du cadre, deux mains en place.
- **Alimentation de la scie** : ta proposition (câble vers une alimentation portée fictionnelle) est notée au contrat
  §1 comme décision **du propriétaire**. En attendant, le banc fait tourner la scie sans ressource ; s'il faut un arrêt
  à vide, le banc l'ajoutera avec un son `empty`.
- **Corrections communes du master** à porter sur W05, W09 et les suivantes : contrat v2 §9 (recul lisible ; un geste
  de main pour chaque changement d'état ; état visible = état du jeu ; sortie de main entre deux gestes ; manche au
  bord en 4:3 et 21:9 ; axe de l'arme ; un événement sonore par geste). Le banc éprouve déjà FAMAS (coup par coup /
  rafale de 3 / automatique, rien d'engagé après une demande de changement), scie (contact puis arrêt, rien à travers
  un obstacle, boucle arrêtée au relâchement, au rangement et à la mort) et pied-de-biche (touche / obstacle / raté).

## 5. RF01 : retour n° 2 sur `02_SOUBASSEMENTS_MATIERES_20260929`

Texte complet : `RETOUR_OPUS_2.md`, joint ici et déposé à côté du retour n° 1
(`C:\PROJECTS\RF2_RF01_TEXTURES_1940_RETOUR_OPUS\`). En bref :

- Six matières intégrées dans la candidate `dist/candidates/RF2_RF01_TEXTURES_1940_20260929_1606/` (sha256
  `67485285…`) ; traversées RF01 A et B : PASS ; RF02 intact ; candidates précédentes conservées.
- Trois soubassements distincts : écarts 19,9 / 30,8 / 29,8 (textures), 28,6 / 37,8 / 43,5 (dans le jeu).
- Le sang-de-bœuf vire au rose saumon sous la forte lumière du POSTE : plus sombre et moins orangé **seulement si le
  propriétaire le demande**.
- Gain de matière visible de près ; les pixels carrés de très près viennent du filtre de la configuration, pas des
  images.
- Les quatre décals, trop discrets, ne sont pas intégrés : à reprendre (masses plus larges et contrastées, crasse
  continue, coulure plus large), puis extension au lot complet.
