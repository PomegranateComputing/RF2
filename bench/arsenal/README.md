# Banc d'essai de l'arsenal (RF2-ARSENAL)

Module séparé, **hors campagne**, pour voir et entendre les armes d'Astra dans UZDoom 5.0.1 avant toute intégration. Il se
charge par-dessus un build figé du jeu ; aucun lanceur accepté ne le charge ; aucune carte, aucun inventaire, aucune
classe de la campagne n'est modifié. Contrat de référence : `docs/production/handoff/RF2-ARSENAL/CONTRAT.md` (v2).

## Lancer

`JOUER_RF2_ARSENAL_ESSAI.cmd` : stand de tir `ARSENAL`, difficulté normale. Configuration `user\uzdoom_arsenal_essai.ini`
(copie de `user\uzdoom.ini`, qui n'est pas modifié), sauvegardes `user\savegames_arsenal_essai`, journal
`user\logs_arsenal_essai\`.

Touches : **4** Rapid (W03), **5** MR73 (W04), **6** FAMAS (W05), **7** Scorpion (W09), **8** pied-de-biche d'essai
(W10), **1–3** Browning, FAL, pied-de-biche du jeu ; **R** recharger ; **tir secondaire** : sélecteur du FAMAS.
Carte de découverte des répliques : console `map BANCDEC1` (armes posées au sol, sortie vers `BANCDEC2`).

HUD : le panneau d'arme affiche le compte de l'arme d'essai (`4+1 | 24` tube + chambre | réserve ; `6 | 18` barillet |
réserve ; `25 | 75` chargeur | réserve et le mode) ; le panneau de diagnostic (en haut à droite) donne la source des
images, les répliques, la séquence, l'image et sa durée, le contrôle du compte, le dernier impact ; la bande en haut à
gauche est le tic de jeu de l'image (lue par les scripts de preuve).

Stand : couloir clair (lumière 224) et sombre (56), cibles à 128, 256, 512, 896 unités ; mur du fond (tir à bout
portant) ; dans la salle de tir, un pilier de 16 unités avec une cible juste derrière et une cible témoin à la même
distance (armes de contact).

## Construire

```
python scripts/arsenal/build_bench.py --delivery incoming/astra/RF2_ARSENAL/<lot> [--presentation bench/arsenal/presentation/<lot>.json]
```

- Une arme absente de la livraison reste en images et sons **provisoires** (`bench/arsenal/placeholder/`).
- Les fichiers sont rangés à leur `target_relpath` du manifeste de la livraison (chemins du futur import).
- Collisions de noms de sprites et de chemins contrôlées contre la base, les pk3 du moteur et l'IWAD : refus s'il y en a.
- `--presentation` : couche du banc appliquée sans modifier la livraison (recul par le code, noms courts).
- Contrôle d'une livraison avant usage : `python scripts/arsenal/import_astra_lot.py <lot> [--origin <livraison figée>]`.
- `--scratch fichier.pk3` : module seul, sans build daté ni lanceur (développement, vérifications d'Astra).

## Fichier d'animation (`rf2-bench-animation/1`)

Clés communes : `weapon`, `name`, `tag` (nom court du HUD), `class`, `kind`, `sprite`, `flash_sprite`, `files` (image →
chemin) ou `file_prefix`, `canvas`, `scale`, `offset`, `slot`, `ammo`, `flash`, `sounds` (événement → fichiers WAV 16
bits 48 kHz mono ; plusieurs = tirage), `sequences` (nom → images : `image`, `tics` ≥ 1, et au besoin `event`,
`offset` [x, y], `ready_point`). Exemples : `bench/arsenal/placeholder/*.json` ; livraison réelle :
`incoming/astra/RF2_ARSENAL/W03_W04_V01/animation.rapid.json`, `animation.mr73.json`.

| `kind` | Séquences | Événements exigés | Particularités |
|---|---|---|---|
| `pump` (W03) | ready, fire, pump, dry, reload_start, reload_shell, reload_end | un `shot` ; `pump_back`, `pump_fwd` ; un `shell_in` | `capacity` : `tube`, `chamber` |
| `revolver` (W04) | ready, fire, dry, reload_open, reload_eject, reload_round, reload_close | un `shot` ; un `eject` ; un `round_in` | `rig_layers` : `chambers` (6 × poses), `hands` (6 × étapes), `chambers_fired` (optionnel) ; par image `chamber_pose`, `hand_stage` |
| `magazine` (W05) | ready, fire, dry, reload (+ reload_empty, mode optionnels) | un `shot` ; un `seat` par recharge | `capacity.magazine`, `burst` ; sélecteur sur le tir secondaire |
| `saw` (W09) | ready, start, run, stop | `start`, `stop` | `contact` : `range`, `damage`, `every` ; son `loop` en boucle |
| `melee` (W10) | ready, swing | un `strike` (fenêtre de contact) | `contact` : `range`, `damage` ; son `miss` |

Répliques de Viktor : fichier JSON de la livraison avec une clé `voices` :
`{"voices": {"manurhin": {"take": wav, "phrase": wav, "sneer": wav, "sneer_at_ms": n, "mode": "take"|"split"}, "chasseurs": {"take": wav}}}`.

## Règles (identiques dans l'image, le code et le HUD d'essai)

Contrat v2 §5. En bref : le compte ne change qu'aux images d'événement ; aucun engagement (cartouche, chargeur) au tic
d'une demande de changement d'arme ni après, ni après la mort ; la cartouche engagée avant la demande finit son geste ;
détente pendant la recharge : la cartouche en cours finit, puis tir ; réserve vide : pas de recharge ; sauvegarde
pendant une animation : mêmes compteurs, séquence et calques au chargement. Scie : le son de boucle s'arrête au
relâchement, au rangement et à la mort ; rien n'est touché à travers un obstacle.

## Preuves

| Script | Ce qu'il fait |
|---|---|
| `bench_probe.py` | W03/W04 : compteurs, tir à vide, recharges, interruption par tir, changement d'arme 2 et 1 tics avant, au tic, 1 et 2 tics après l'engagement, réserve courte et vide, sauvegarde pendant une insertion (calques relus), mort pendant une insertion |
| `voice_probe.py` | répliques : premier ramassage, doublon, voix prioritaire, interruption, changement de carte, chargement après, chargement avant (rejouée), nouvelle partie |
| `next_probe.py` | W05 : coup par coup, rafale, automatique, changement avant engagement, vide ; W09 : contact, pilier, arrêt du son (relâchement, rangement, mort) ; W10 : touche, obstacle, raté |
| `bench_shots.py` | une capture par état, étiquetée par le tic qu'elle montre (bande de tic), jeu ralenti (`wait 10; i_timescale 0.1` différé + `cl_capfps 1`, méthode d'Astra) ; 16:9, 21:9, 4:3 |
| `bench_film.py` | film avec le son sorti du moteur (OpenAL), chaque image placée au tic qu'elle montre sur l'horloge du moteur ; rapport de régularité des tics |

Aucun script ne juge le rendu ni le son. Une capture d'écran peut montrer un état plus ancien que le tic demandé (une
image en attente de capture n'est pas redessinée) : seules les images lues par leur bande de tic font foi.
