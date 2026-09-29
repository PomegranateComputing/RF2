# RF2-ARSENAL — banc d'essai

**Statut (29/09/2026) : W03 Manufrance Rapid et W04 Manurhin MR73 de la livraison V01 d'Astra intégrés au banc et
vérifiés au banc ; W05 FAMAS et W09 Scorpion en images et sons provisoires ; W10 = le pied-de-biche du jeu, réemployé
tel quel. Aucun son écouté. Rien ici ne vaut accord du propriétaire.** Aucune arme n'entre dans la campagne, les cartes,
les inventaires ou les lanceurs acceptés. Contrat de référence : `docs/production/handoff/RF2-ARSENAL/CONTRAT.md` (v2) ;
mode d'emploi et format des fichiers : `bench/arsenal/README.md`.

## Lancer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_ARSENAL_ESSAI.cmd` | stand de tir `ARSENAL` ; **4** Rapid, **5** MR73, **6** FAMAS (essai), **7** Scorpion (essai), **8** pied-de-biche d'essai, **1–3** Browning, FAL, pied-de-biche du jeu ; **R** recharger ; tir secondaire : sélecteur du FAMAS ; console `map BANCDEC1` : découverte des armes au sol et répliques |

Build `dist\arsenal\RF2_ARSENAL_ESSAI_20260929_1545\` : module `RF2_ARSENAL_ESSAI.pk3` (sha256 `5aaec05f…`, 186
fichiers, commit `69ff59c` de `bench/rf2-arsenal`), chargé par-dessus la base figée
`dist\arsenal\base\RF2_BASE_src_23773520f797.pk3` (sha256 `a03fad5f…` ; Browning et FAL identiques au build accepté).
Configuration `user\uzdoom_arsenal_essai.ini`, sauvegardes `user\savegames_arsenal_essai`, journal
`user\logs_arsenal_essai\` : la partie normale et ses sauvegardes ne sont pas touchées.

## Fichiers réellement importés

| Lot d'Astra | Contrôle | Ce que le banc lit |
|---|---|---|
| W03/W04 V01 (`incoming/astra/RF2_ARSENAL/W03_W04_V01/`) | 3665 fichiers conformes à `SHA256SUMS.txt`, même liste que le V01 figé du worktree d'Astra (`art/rf2_arsenal_astra/IMPORT_W03_W04_V01.json`) | 134 fichiers : `animation.rapid.json`, `animation.mr73.json`, 111 PNG, 21 WAV, rangés à leur `target_relpath` ; plus la couche de présentation du banc `bench/arsenal/presentation/W03_W04_V01.json` (recul, noms courts ; la livraison n'est pas modifiée) |
| W05_W09_W10_V01 (`incoming/astra/RF2_ARSENAL/W05_W09_W10_V01/`) | 277 fichiers conformes ; 305 non listés (session moteur privée d'Astra, bibliothèque Python, caches), non lus (`IMPORT_W05_W09_W10_V01.json`) | rien : W10 = 5 poses et 12 sons identiques octet pour octet à la base (`…_W10_REEMPLOI.json`), déjà dans le jeu ; W05/W09 = masters de travail |
| Répliques de Viktor | absentes des 21 sons V01 ; aucune prise livrée | repères sonores provisoires du banc |

Le module d'Astra `RF2_ARSENAL_W03_W04_V01.pk3` (`1981cf8d…`) a servi de référence ; son adaptateur (`chamber_pose`,
`hand_stage`) est reporté dans le constructeur du banc, qui lit le V01 sans remplacement de texte dans le code généré.

## Vu, entendu, vérifié

| | |
|---|---|
| Vérifié par script sur ce module | `sonde_armes` PASS : compte conservé, capacités (Rapid 4+1, MR73 6), premier engagement 12 tics (Rapid) et 19 tics (MR73) après la demande de recharge, changement d'arme 2 et 1 tics avant, au tic, 1 et 2 tics après l'engagement (annulée / annulée / annulée / finie avant / finie avant, assertion d'origine non relâchée), réserve courte et vide, sauvegarde pendant une insertion relue avec les mêmes calques, mort pendant une insertion (calques retirés, rien après). `sonde_repliques` PASS (repères provisoires) : une réplique par arme à la première acquisition, doublons muets, file derrière une voix prioritaire, état suivi entre cartes et sauvegardes, remis à zéro par une nouvelle partie. `sonde_armes_suivantes` PASS : FAMAS 1 / 3 / automatique, aucun chargeur engagé après une demande de changement, tir à vide ; scie : contact devant la cible, rien à travers le pilier, boucle arrêtée au relâchement, au rangement et à la mort ; pied-de-biche d'essai et **vrai `RFCrowbar`** : touche / obstacle / raté, rien derrière le pilier, repères mesurés 5 (balayage) / 8 (impact, un seul) / 22 (prêt) = ceux d'Astra |
| Vu (Opus, captures lues par leur bande de tic, 16:9, 21:9, 4:3 ; module 1532, mêmes fichiers W03/W04) | comptes et images d'accord ; culots = étuis + cartouches avant l'extraction puis cartouches chargées ; main par chambre ; manches aux bords ; flash à la bouche. Défauts ci-dessous |
| Entendu | **rien** : aucun son n'a été écouté, ni par Opus ni par Astra |
| Film à son natif | `preuves/film/` : son sorti du moteur pendant la même session que les images, calé par le bip du tic 1, images placées au tic qu'elles montrent. Les captures ralentissent le moteur par endroits (tic médian 27,8 ms, p95 65,9 ms) : rythme perturbé près des captures ; la piste presque sans capture (`banc_1532_son_seul`) ne l'est pas. Non écouté |

## Défauts restants (retour à Astra, `RETOUR_OPUS.md` du 29/09)

1. Recul quasi nul dans les images (Rapid 3–9 px, MR73 1–2 px sur 1536) : le banc ajoute un recul d'essai.
2. MR73 : extraction sans geste de main (les étuis disparaissent).
3. MR73 : étuis tirés et cartouches intactes identiques barillet ouvert (`chambers_fired` attendu).
4. MR73 chambre 4, étape de main 1 : seule la pointe de la cartouche dépasse du bas du cadre (mineur).
5. W05/W09 : images et sons d'essai ; alimentation de la scie à décider (contrat §1).
6. Répliques : aucune prise.

## Choix déclarés

- Rapid **4+1** (RGA BE050, décision V01) ; MR73 six chambres, recharge partielle règle (a), recharge complète 85 tics
  (durée de V01, pas une cible à défendre).
- Munitions du banc distinctes de celles du jeu ; dégâts, dispersion, portées, cadences : **provisoires**, pas un
  équilibrage.
- HUD du banc : panneau d'arme `4+1 | 24` (tube + chambre | réserve), `6 | 18` (barillet | réserve), `25 | 75`
  (chargeur | réserve, avec le mode) ; panneau de diagnostic en haut à droite ; bande de tic en haut à gauche.

## Restes et limites

- Non testé par script : la pause (menu) ; l'écoute.
- UZDoom 5.0.1 ignore `+logfile` : le lanceur écrit le journal depuis la sortie standard.
- Restent pour l'intégration : emplacements, classes et munitions de campagne, équilibrage, apparitions, progression.
- Builds conservés : `_20260928_1807` (défaut de compte trouvé par la sonde), `_1818`, `_1822` (dessins provisoires,
  Rapid 5+1 d'alors), `_20260929_1532` (W03/W04 V01 seuls), `_1545` (actuel).

## Preuves

`dist\arsenal\RF2_ARSENAL_ESSAI_20260929_1545\` : `BUILD_INFO.json`, `genere\`, `preuves\PROVENANCE.txt` (ce qui vient
de quel module), `sonde_armes.*`, `sonde_repliques.*`, `sonde_armes_suivantes.*`, `sonde_armes_suivantes_w10reel.*`,
`captures_1532\`, `film\`.
