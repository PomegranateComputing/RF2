# Routage des sons d'armes — campagne et banc (Opus → Codex, 01/10)

Ce que le moteur fait de chaque son d'arme, pour que les remplacements se posent sans retouche de code. Les mesures
ci-dessous sont des **mesures de signal** (format, durée, crête, RMS, position de la crête) ; aucune écoute n'a été
faite dans cet environnement, elles ne jugent pas le rendu.

## Règles du moteur (UZDoom 5.0.1, code actuel)

| Événement | Canal | Drapeaux | Conséquence pour le fichier |
|---|---|---|---|
| Tir (`shot`, `fire`) | `CHAN_WEAPON` | `CHANF_OVERLAP` | les tirs se superposent (rafale, cadence) : la queue d'un tir ne coupe pas le suivant ; trois variantes tirées au hasard (`$random`) |
| Mécanique (culasse, chargeur, barillet, pompe, cartouche, sélecteur, toile, sortie de l'arme) | `CHAN_ITEM` | aucun | **un seul son mécanique à la fois** : l'événement suivant coupe le précédent ; un son plus long que l'intervalle entre deux images d'animation sera tronqué |
| Étui éjecté (`shell`) | `CHAN_ITEM` | volume 0,5 | partage le canal mécanique |
| Impacts de balle (`rf/impact/*`) | `CHAN_BODY` de l'impact | volume 0,85 | joué au point d'impact, atténué par la distance ; matière : plâtre, bois, métal, chair |
| Pied-de-biche (coup, matière touchée) | `CHAN_WEAPON` / `CHAN_BODY` | — | le coup et la matière se superposent |
| Scie (W09) | `start` et `contact` sur `CHAN_ITEM`, `loop` sur `CHAN_WEAPON` en boucle | `CHANF_LOOP` | la boucle tourne tant que la détente est tenue et s'arrête net au relâchement (`stop`) |
| Réverbération | zones de la carte (environnements EAX par pièce, rue, couloir) | — | livrer **sec** : pas de pièce ni d'écho dans le fichier, une queue naturelle courte suffit |

Le son part sur l'image d'animation qui le porte (fichier d'animation `rf2-bench-animation/1` au banc, états ZScript en
campagne). **Il doit commencer dans les 10 premières ms du fichier** : un silence en tête retarde le bruit par rapport
au geste (35 images par seconde : 100 ms = 3,5 images).

## Format et niveaux attendus

WAV PCM mono 48 kHz 16 bits (master plus profond chez toi). Tirs : crête vers −2 dBFS, attaque immédiate ; mécanique :
crête −10 à −16 dBFS, cohérente entre armes ; toile et sortie d'arme : −20 dBFS ; étuis : −24 dBFS ; impacts : −7 à
−9 dBFS. Ces repères sont ceux des fichiers en place (tableaux ci-dessous) ; s'en écarter est possible, dis-le dans
`POUR_OPUS.md`.

## Noms (ce que le jeu lit)

| Arme | Noms SNDINFO | Fichiers (`target_relpath`) |
|---|---|---|
| FAL (campagne) | `rf/fal/shot` (3 variantes), `shell` (3), `dry`, `raise`, `cloth`, `latch`, `mag_out`, `mag_in`, `seat`, `action` | `sounds/fal/<nom>.wav`, `shot_01…03`, `shell_01…03` |
| Browning (campagne) | `rf/browning/fire` (3), `slide`, `dry` | `sounds/browning/fire_01…03.wav`, `slide.wav`, `dry.wav` |
| Pied-de-biche (campagne) | `rf/crowbar/swing` (3), `flesh` (3), `metal` (3), `wood` (3) | `sounds/crowbar/swing_01…03`, `hit_<matière>_01…03.wav` |
| Rapid 4+1 (W03, banc) | `rf/bench/rapid/shot` (3), `pump_back`, `pump_fwd`, `shell_in` (2), `dry`, `cloth`, `raise` | `sounds/rapid/…` |
| MR73 (W04, banc) | `rf/bench/mr73/shot` (3), `cyl_open`, `cyl_close`, `round_in` (2), `eject`, `dry`, `cloth`, `raise` | `sounds/mr73/…` |
| FAMAS (W05, banc) | `rf/bench/w05/shot` (3), `dry`, `mag_out`, `mag_in`, `seat`, `bolt`, `mode`, `cloth`, `raise` | `sounds/famas/…` |
| Scie Scorpion (W09, banc) | `rf/bench/w09/start`, `loop`, `contact`, `stop`, `cloth`, `raise` | `sounds/scorpion/…` |
| Pied-de-biche d'essai (W10, banc) | `rf/bench/w10/swing`, `miss`, `raise` | `sounds/bench/w10/…` |

Le fonctionnement des armes ne change pas (Rapid 4+1, barillet de six chambres du MR73, cadence réparée du Scorpion) :
seuls les fichiers sont remplacés. Un événement nouveau se propose dans `POUR_OPUS.md`, Opus le route.

## Ce que montrent les fichiers en place (signal)

- Beaucoup de sons mécaniques ont **~100 ms de silence en tête** (crête à 90–160 ms : `dry`, `raise`, `mag_out`,
  `round_in`, `mode`, `pump_fwd`…) : à reprendre (voir plus haut).
- La boucle de la scie (`scorpion/loop`, 1 s) a sa crête à 914 ms : un niveau qui monte vers la fin produit un ressaut
  au point de bouclage ; une boucle de niveau constant, raccord sans clic.
- Le FAMAS tire plus bas (−5,5 dBFS, 210 ms) que les autres armes (−1,8 à −3,8 dBFS).

### Campagne (`src/sounds`, build de développement du 01/10)

| Fichier | Format | Durée (ms) | Crête (dBFS) | RMS (dBFS) | Crête à (ms) |
|---|---|---|---|---|---|
| `browning/dry.wav` | 48000 Hz, 16 bits, mono | 374 | -15.0 | -41.2 | 102 |
| `browning/fire.wav` | 48000 Hz, 16 bits, mono | 490 | -2.2 | -24.6 | 6 |
| `browning/fire_01.wav` | 48000 Hz, 16 bits, mono | 490 | -2.2 | -24.6 | 6 |
| `browning/fire_02.wav` | 48000 Hz, 16 bits, mono | 490 | -2.2 | -24.9 | 2 |
| `browning/fire_03.wav` | 48000 Hz, 16 bits, mono | 490 | -2.2 | -25.0 | 2 |
| `browning/slide.wav` | 48000 Hz, 16 bits, mono | 224 | -15.0 | -36.4 | 38 |
| `crowbar/hit_flesh_01.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -25.0 | 8 |
| `crowbar/hit_flesh_02.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -22.9 | 9 |
| `crowbar/hit_flesh_03.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -24.1 | 9 |
| `crowbar/hit_metal_01.wav` | 48000 Hz, 16 bits, mono | 468 | -5.1 | -27.0 | 1 |
| `crowbar/hit_metal_02.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -27.8 | 1 |
| `crowbar/hit_metal_03.wav` | 48000 Hz, 16 bits, mono | 468 | -5.2 | -30.8 | 1 |
| `crowbar/hit_wood_01.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -25.3 | 2 |
| `crowbar/hit_wood_02.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -25.1 | 2 |
| `crowbar/hit_wood_03.wav` | 48000 Hz, 16 bits, mono | 468 | -5.0 | -26.0 | 3 |
| `crowbar/swing_01.wav` | 48000 Hz, 16 bits, mono | 464 | -10.0 | -30.0 | 119 |
| `crowbar/swing_02.wav` | 48000 Hz, 16 bits, mono | 464 | -10.0 | -30.1 | 115 |
| `crowbar/swing_03.wav` | 48000 Hz, 16 bits, mono | 464 | -10.0 | -30.8 | 110 |
| `fal/action.wav` | 48000 Hz, 16 bits, mono | 247 | -11.0 | -28.1 | 101 |
| `fal/cloth.wav` | 48000 Hz, 16 bits, mono | 341 | -20.0 | -38.9 | 78 |
| `fal/dry.wav` | 48000 Hz, 16 bits, mono | 374 | -15.0 | -41.2 | 102 |
| `fal/latch.wav` | 48000 Hz, 16 bits, mono | 224 | -12.0 | -33.4 | 38 |
| `fal/mag_in.wav` | 48000 Hz, 16 bits, mono | 224 | -10.5 | -31.9 | 38 |
| `fal/mag_out.wav` | 48000 Hz, 16 bits, mono | 347 | -13.0 | -29.3 | 107 |
| `fal/raise.wav` | 48000 Hz, 16 bits, mono | 240 | -15.0 | -38.6 | 104 |
| `fal/seat.wav` | 48000 Hz, 16 bits, mono | 281 | -12.0 | -30.4 | 94 |
| `fal/shell_01.wav` | 48000 Hz, 16 bits, mono | 256 | -24.0 | -41.4 | 8 |
| `fal/shell_02.wav` | 48000 Hz, 16 bits, mono | 215 | -24.0 | -41.2 | 2 |
| `fal/shell_03.wav` | 48000 Hz, 16 bits, mono | 191 | -24.0 | -42.4 | 2 |
| `fal/shot_01.wav` | 48000 Hz, 16 bits, mono | 630 | -1.8 | -22.8 | 14 |
| `fal/shot_02.wav` | 48000 Hz, 16 bits, mono | 630 | -1.8 | -21.3 | 14 |
| `fal/shot_03.wav` | 48000 Hz, 16 bits, mono | 630 | -1.8 | -22.6 | 2 |
| `impact/flesh_01.wav` | 48000 Hz, 16 bits, mono | 118 | -9.0 | -23.0 | 7 |
| `impact/flesh_02.wav` | 48000 Hz, 16 bits, mono | 183 | -9.0 | -22.7 | 8 |
| `impact/flesh_03.wav` | 48000 Hz, 16 bits, mono | 135 | -9.0 | -22.4 | 8 |
| `impact/metal_01.wav` | 48000 Hz, 16 bits, mono | 244 | -8.0 | -24.6 | 5 |
| `impact/metal_02.wav` | 48000 Hz, 16 bits, mono | 143 | -8.0 | -23.9 | 4 |
| `impact/metal_03.wav` | 48000 Hz, 16 bits, mono | 119 | -8.0 | -24.9 | 5 |
| `impact/plaster_01.wav` | 48000 Hz, 16 bits, mono | 645 | -7.0 | -25.0 | 11 |
| `impact/plaster_02.wav` | 48000 Hz, 16 bits, mono | 594 | -7.0 | -25.6 | 14 |
| `impact/plaster_03.wav` | 48000 Hz, 16 bits, mono | 535 | -7.0 | -26.8 | 6 |
| `impact/wood_01.wav` | 48000 Hz, 16 bits, mono | 255 | -7.0 | -25.1 | 3 |
| `impact/wood_02.wav` | 48000 Hz, 16 bits, mono | 258 | -7.0 | -24.9 | 3 |
| `impact/wood_03.wav` | 48000 Hz, 16 bits, mono | 266 | -7.0 | -26.3 | 3 |

### Banc (build d'essai 1901, `RF2_ARSENAL_ESSAI.pk3`)

| Fichier | Format | Durée (ms) | Crête (dBFS) | RMS (dBFS) | Crête à (ms) |
|---|---|---|---|---|---|
| `sounds/bench/w10/miss.wav` | 48000 Hz, 16 bits, mono | 250 | -20.0 | -32.8 | 91 |
| `sounds/bench/w10/raise.wav` | 48000 Hz, 16 bits, mono | 320 | -24.0 | -37.3 | 157 |
| `sounds/bench/w10/swing.wav` | 48000 Hz, 16 bits, mono | 250 | -20.0 | -33.1 | 120 |
| `sounds/famas/bolt.wav` | 48000 Hz, 16 bits, mono | 220 | -14.0 | -35.2 | 110 |
| `sounds/famas/cloth.wav` | 48000 Hz, 16 bits, mono | 210 | -22.0 | -40.6 | 114 |
| `sounds/famas/dry.wav` | 48000 Hz, 16 bits, mono | 446 | -18.0 | -44.9 | 102 |
| `sounds/famas/mag_in.wav` | 48000 Hz, 16 bits, mono | 220 | -16.0 | -37.1 | 90 |
| `sounds/famas/mag_out.wav` | 48000 Hz, 16 bits, mono | 260 | -15.0 | -35.1 | 127 |
| `sounds/famas/mode.wav` | 48000 Hz, 16 bits, mono | 446 | -20.0 | -46.9 | 102 |
| `sounds/famas/raise.wav` | 48000 Hz, 16 bits, mono | 220 | -20.0 | -43.2 | 116 |
| `sounds/famas/seat.wav` | 48000 Hz, 16 bits, mono | 170 | -13.0 | -28.8 | 82 |
| `sounds/famas/shot_01.wav` | 48000 Hz, 16 bits, mono | 210 | -5.5 | -23.7 | 14 |
| `sounds/famas/shot_02.wav` | 48000 Hz, 16 bits, mono | 210 | -5.5 | -23.2 | 14 |
| `sounds/famas/shot_03.wav` | 48000 Hz, 16 bits, mono | 210 | -5.5 | -23.7 | 15 |
| `sounds/mr73/cloth.wav` | 48000 Hz, 16 bits, mono | 327 | -23.0 | -41.7 | 73 |
| `sounds/mr73/cyl_close.wav` | 48000 Hz, 16 bits, mono | 357 | -14.5 | -36.7 | 40 |
| `sounds/mr73/cyl_open.wav` | 48000 Hz, 16 bits, mono | 337 | -16.0 | -39.1 | 32 |
| `sounds/mr73/dry.wav` | 48000 Hz, 16 bits, mono | 357 | -18.0 | -41.9 | 102 |
| `sounds/mr73/eject.wav` | 48000 Hz, 16 bits, mono | 392 | -17.0 | -42.4 | 137 |
| `sounds/mr73/raise.wav` | 48000 Hz, 16 bits, mono | 327 | -22.0 | -46.3 | 100 |
| `sounds/mr73/round_in_01.wav` | 48000 Hz, 16 bits, mono | 357 | -20.0 | -46.1 | 102 |
| `sounds/mr73/round_in_02.wav` | 48000 Hz, 16 bits, mono | 357 | -20.7 | -45.5 | 102 |
| `sounds/mr73/shot_01.wav` | 48000 Hz, 16 bits, mono | 340 | -3.5 | -27.1 | 1 |
| `sounds/mr73/shot_02.wav` | 48000 Hz, 16 bits, mono | 340 | -3.5 | -26.8 | 1 |
| `sounds/mr73/shot_03.wav` | 48000 Hz, 16 bits, mono | 400 | -3.8 | -28.1 | 1 |
| `sounds/rapid/cloth.wav` | 48000 Hz, 16 bits, mono | 327 | -23.0 | -41.7 | 73 |
| `sounds/rapid/dry.wav` | 48000 Hz, 16 bits, mono | 357 | -17.0 | -43.1 | 102 |
| `sounds/rapid/pump_back.wav` | 48000 Hz, 16 bits, mono | 327 | -13.0 | -35.6 | 72 |
| `sounds/rapid/pump_fwd.wav` | 48000 Hz, 16 bits, mono | 412 | -12.0 | -37.2 | 157 |
| `sounds/rapid/raise.wav` | 48000 Hz, 16 bits, mono | 327 | -22.0 | -46.3 | 100 |
| `sounds/rapid/shell_in_01.wav` | 48000 Hz, 16 bits, mono | 357 | -16.0 | -35.1 | 87 |
| `sounds/rapid/shell_in_02.wav` | 48000 Hz, 16 bits, mono | 357 | -16.7 | -35.9 | 87 |
| `sounds/rapid/shot_01.wav` | 48000 Hz, 16 bits, mono | 530 | -3.2 | -24.3 | 1 |
| `sounds/rapid/shot_02.wav` | 48000 Hz, 16 bits, mono | 530 | -3.2 | -25.6 | 2 |
| `sounds/rapid/shot_03.wav` | 48000 Hz, 16 bits, mono | 530 | -3.2 | -26.2 | 2 |
| `sounds/scorpion/cloth.wav` | 48000 Hz, 16 bits, mono | 200 | -23.0 | -41.4 | 114 |
| `sounds/scorpion/contact.wav` | 48000 Hz, 16 bits, mono | 105 | -12.5 | -19.6 | 48 |
| `sounds/scorpion/loop.wav` | 48000 Hz, 16 bits, mono | 1000 | -16.0 | -22.9 | 914 |
| `sounds/scorpion/raise.wav` | 48000 Hz, 16 bits, mono | 220 | -20.0 | -43.2 | 116 |
| `sounds/scorpion/start.wav` | 48000 Hz, 16 bits, mono | 230 | -16.0 | -21.7 | 90 |
| `sounds/scorpion/stop.wav` | 48000 Hz, 16 bits, mono | 190 | -18.0 | -30.1 | 6 |

## Films de référence au son natif

Sortie son du moteur enregistrée par le moteur lui-même (`scripts/film.py` : capture WAV d'OpenAL, images au même
horloge ; ni micro ni haut-parleur), dans ton dossier `handoff/RETOURS_OPUS/films/` :

| Film | Contenu |
|---|---|
| `art_combat2` | combat de campagne RF01 (FAL, Browning, impacts), 42 tirs |
| `bench_v01_natif_c` | banc d'essai, armes d'essai, 6 tirs |
| `ref_son_campagne_20261001` | combat de campagne sur le build du 01/10 (s'il est joint : enregistré après ce document) |

Mesures produites par `scripts/production/sound_levels.py`.
