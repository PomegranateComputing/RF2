# Banc d'essai de l'arsenal (RF2-ARSENAL)

Module séparé, **hors campagne**, pour voir et entendre W03 (Manufrance Rapid) et W04 (Manurhin MR73) dans UZDoom 5.0.1
avant toute intégration. Il se charge par-dessus un build figé du jeu ; aucun lanceur accepté ne le charge ; aucune
carte, aucun inventaire, aucune classe de la campagne n'est modifié.

## Lancer

`JOUER_RF2_ARSENAL_ESSAI.cmd` (à la racine du dépôt) : ouvre directement le stand de tir `ARSENAL`, difficulté
normale. Configuration `user\uzdoom_arsenal_essai.ini` (copie de `user\uzdoom.ini` au premier lancement, qui n'est pas
modifié), sauvegardes `user\savegames_arsenal_essai`, journal `user\logs_arsenal_essai\essai_<date>.log`.

Touches : **4** Rapid, **5** MR73, **1** Browning, **2** FAL, **3** pied-de-biche (références), **R** recharger.
En haut à droite, le panneau d'essai : source des images (livraison ou PROVISOIRE), compteur de l'arme
(`tube n + chambre n | réserve n`, ou `barillet ooo... | réserve n` : `o` cartouche, `x` étui tiré, `.` vide), séquence
et image en cours avec leur durée, tirs, contrôle du compte, dernier impact sur une cible. Le panneau d'arme du HUD RF
(en bas à droite) ne connaît que le FAL : pour les armes d'essai il n'affiche que la réserve.

Stand : couloir clair (lumière 224) et couloir sombre (56), une cible à 128, 256, 512 et 896 unités dans chacun (bande
pavée au sol), mur du fond de la salle de tir pour le tir à bout portant. Les cibles ne tombent jamais ; chaque tir
est rapporté (touches, dégâts).

## Construire

```
python scripts/arsenal/build_bench.py [--delivery DOSSIER ...] [--base PK3]
```

- Sans `--delivery` : images et sons **provisoires** (dessins étiquetés, bips), valeurs de départ du contrat.
- Avec `--delivery` : le script cherche dans le dossier un fichier d'animation par arme (JSON avec `"weapon": "W03"` ou
  `"W04"` et `"sequences"`), et prend images et sons relatifs à ce fichier ou au dossier. Une arme absente de la
  livraison reste provisoire (affiché).
- Base : build figé du commit courant (`dist\arsenal\base\RF2_BASE_<commit>.pk3`), ou `--base`.
- Sortie : `dist\arsenal\RF2_ARSENAL_ESSAI_<date>_<heure>\` (module, `BUILD_INFO.json`, `JOUER.cmd`, code généré dans
  `genere\`), et `JOUER_RF2_ARSENAL_ESSAI.cmd` vers le plus récent. Aucun build précédent n'est réécrit.

Contrôles : `python scripts/arsenal/bench_probe.py --base … --module …` (compteurs et transitions, PASS/FAIL) ;
`python scripts/arsenal/bench_shots.py --base … --module … --out DOSSIER` (captures à des instants choisis en 16:9,
21:9, 4:3). Aucun script ne juge l'image ou le son.

## Fichier d'animation (`rf2-bench-animation/1`)

Exemples complets : `placeholder/W03_rapid.json`, `placeholder/W04_mr73.json`.

| Clé | Sens |
|---|---|
| `weapon`, `name`, `class` | `W03`/`W04`, nom affiché, `RFBenchRapid`/`RFBenchMR73` |
| `kind` | `pump` ou `revolver` (choisit la mécanique) |
| `sprite`, `flash_sprite` | `RFRP`/`RPFX`, `RFMR`/`MRFX` (contrat §2) |
| `file_prefix` ou `files` | chemin des images : `file_prefix + image + ".png"`, ou table `image → chemin` |
| `canvas`, `scale`, `offset` | toile 1536×1024, XScale 6.8 / YScale 8.16, Offset -750,-460 (convention FAL) ; la taille réelle de chaque PNG est lue, une toile élargie à droite garde l'origine |
| `capacity` | Rapid : `tube`, `chamber` (0/1) ; MR73 : `cylinder` (6) |
| `ballistics` | `pellets`, `damage` (par plomb/balle), `spread` [h, v] en degrés — valeurs de banc |
| `ammo` | classe, nom, réserve donnée au départ |
| `flash` | `image`, `tics` |
| `chamber_layers` | MR73 : six images, une cartouche chacune, même toile que la pose barillet ouvert |
| `sounds` | `événement → [fichiers]` (plusieurs = tirage aléatoire), WAV 16 bits 48 kHz mono |
| `sequences` | `nom → [images]` ; chaque image : `image`, `tics` (entier ≥ 1), et au besoin `event`, `offset` [x, y] (recul par `A_WeaponOffset`, repos 0,32), `ready_point` (changement d'arme permis à cette image), `chambers` (MR73 : couches de chambre visibles) |

Séquences et événements exigés par le banc (refus explicite sinon) :

| | Séquences | Événements obligatoires |
|---|---|---|
| Rapid (`pump`) | `ready`, `fire`, `pump`, `dry`, `reload_start`, `reload_shell`, `reload_end` | un seul `shot` (dans `fire`) ; `pump_back` et `pump_fwd` dans `pump` ; un `shell_in` dans `reload_shell` |
| MR73 (`revolver`) | `ready`, `fire`, `dry`, `reload_open`, `reload_eject`, `reload_round`, `reload_close` | un seul `shot` ; un `eject` dans `reload_eject` ; un `round_in` dans `reload_round` |

Autres événements reconnus : `dry`, `cyl_open`, `cyl_close` ; tout autre nom (`cloth`, `hammer`…) joue son son s'il
existe et s'inscrit au journal.

## Mécanique (déclarée, identique dans l'image, le code et le HUD d'essai)

**Rapid.** Un tir vide la chambre et y laisse un étui ; la pompe (`pump_back`) éjecte l'étui, (`pump_fwd`) chambre
une cartouche du tube. Chambre vide et tube non vide : la détente fait une course de pompe sans tir. Tout vide : clic.
Recharge : une cartouche à la fois dans le tube (`shell_in`) ; elle s'arrête tube plein, réserve vide, sur une
pression de détente (la cartouche en cours finit, puis tir) ou sur un changement d'arme (aux images `ready_point`) ;
si la chambre est vide à la fin, une course de pompe la remplit (le tube perd alors une cartouche : une seconde
recharge le complète). Capacité provisoire 5 + 1 : **à fixer par Astra** avec une source concordante.

**MR73.** Six chambres. Recharge partielle, règle **(a)** : l'ouverture éjecte tout, les cartouches intactes
retournent à la réserve, les étuis tombent ; puis une cartouche à la fois (`round_in`) jusqu'à six ou réserve vide ;
une pression de détente ferme le barillet après la cartouche en cours, puis tire. Les six couches de chambre suivent
le nombre réellement chargé.

**Commun.** Le compte ne bouge qu'aux images d'événement ; chargé + réserve + tiré reste constant (contrôlé par le
banc : « compte juste ») ; pas de tir pendant la recharge ; clic sans projectile ; sauvegarde et chargement rendent
les mêmes compteurs.

Dégâts, dispersion, réserve de départ : **valeurs de banc provisoires**, pas un équilibrage.
