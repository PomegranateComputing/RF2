# RF2-ARSENAL — contrat moteur d'Opus pour Astra (W03 Manufrance Rapid, W04 Manurhin MR73)

Mandat du 28/09 (`C:\PROJECTS\RF2_ARSENAL_20260928`, `04_OPUS_FABLE.md`, `05_ASTRA.md`). Astra produit les armes ;
Opus fixe le contrat moteur, monte le banc d'essai séparé et éprouve les livraisons. Aucune arme n'entre dans la
campagne, les maps, les inventaires normaux ou les lanceurs acceptés dans ce lot. Les valeurs ci-dessous sont
relevées dans le dépôt réel ; ce qui n'y est pas encore fixé est marqué **À FIXER** avec la personne qui le fixe.

## 0. Base

- Dépôt `C:\PROJECTS\RF2_UZDOOM`, branche `prod/rf2-campaign`, commit `f9a5c0e` au moment de ce contrat.
- Browning et FAL de référence : ceux du build RF01 accepté (tag `rf01-owner-accepted-20260927`, pk3 `04bdd0ae…`,
  `JOUER_RF2_ART_REVIEW.cmd`). Leurs images, déclarations et sons n'ont pas changé depuis (diff vide jusqu'à
  `f9a5c0e`).
- Moteur UZDoom 5.0.1 ; 35 tics par seconde ; FOV joueur 90 ; résolutions éprouvées dans les preuves récentes :
  1920×1080 (référence), 1440×1080 (4:3), 2560×1080 (21:9), 2560×1440, 3840×2160, 1600×900.

## 1. Masters à utiliser (autorité pour les mains et le hoodie)

| Source | Chemin (dépôt) | Nature |
|---|---|---|
| FAL, rig 2D en couches | `art/rf2_art_01/weapons/fal_legacy_source/` : `layers/arm_l.png`, `arm_l2.png` (manche continue), `arm_r.png`, `body.png`, `housing.png`, `knob.png`, `mag.png`, `mag_fresh.png`, `flash.png` ; `rigcomp.py` (composition), `animation.json` (poses), `reference/master_origin.md` | master articulé : **c'est la convention à reprendre** (une frame = une composition de couches, pas une image régénérée) |
| FAL, réparation de manche | `incoming/astra/RF01_P0_FAL/` (preuve `evidence/RF2_FAL_SLEEVE_REPAIR.png`, `source/`) | manche noire continue acceptée |
| Browning | `art/rf2_art_01/weapons/browning/master.png`, `master_raw.png` (1536×1024), `animation.json`, `export_browning.py` | master de la main droite et du hoodie |
| Exports acceptés | `src/graphics/weapons/fal/RF2_FAL_*_A0.png` (1536×1024), `src/graphics/weapons/browning/0?_BHP_*.png` (1672×941) | rendu final, frame par frame |
| Captures du propriétaire | `C:\PROJECTS\RF2_ARSENAL_20260928\references\` | rendu en jeu |

Si un fichier manque dans ton espace, demande-le ; copie ces sources dans ton worktree et ne modifie pas l'original.

## 2. Présentation (valeurs réelles)

| | FAL (et pied-de-biche) | Browning |
|---|---|---|
| Type | sprites d'arme (calque `PSP_WEAPON`), 2D | idem |
| Toile par frame | 1536×1024 RGBA | 1672×941 RGBA |
| Échelle | XScale 6.8, YScale 8.16 | XScale 6, YScale 7.2 (et non 6.8/8.16 comme le dit l'en-tête de `TEXTURES.weapons`) |
| Décalage | Offset -750, -460 | Offset -700, -300 |
| Flash | frame à part `RFMZ A0`, même toile et même décalage, dessinée sur le calque flash (`A_GunFlash`), 2 tics, `Bright` | `BHFX A0`, 2 tics |
| Mouvement du recul | par le code (`A_WeaponOffset`) : FAL (1,35) → (2,39) → (1,35) → (0,32) ; Browning (-1,34) → (-2,37) → (-3,40) → (-1,35) → (0,32) | |
| Balancement | `InverseSmooth`, X 0.5–0.6, Y 0.35–0.4 | |
| Côté | main droite à la poignée, main gauche en soutien (FAL) ; Browning à deux mains | |

**W03 et W04 reprennent la convention du FAL** : toile 1536×1024, XScale 6.8, YScale 8.16, Offset -750,-460, flash à part
sur la même toile. Alpha : bords nets, pas de halo (fond transparent, aucune frange claire ou noire). Le bas et les
côtés de la toile doivent couvrir le bras jusqu'au bord en 21:9 et en 4:3 (aucun poignet coupé visible). Le Rapid peut
déborder la toile vers la droite si son canon l'exige : dans ce cas agrandir la toile à droite en gardant l'origine
(décalage inchangé), et le signaler.

Noms réservés (libres dans le dépôt) : sprites `RFRP` (Rapid) et `RFMR` (MR73), flashs `RPFX` et `MRFX`, une lettre
de frame par image (A…Z, puis `[`, `\`, `]` si besoin, comme le moteur le permet), fichiers
`graphics/weapons/rapid/RF2_RAPID_<ETAT>_<NN>.png` et `graphics/weapons/mr73/RF2_MR73_<ETAT>_<NN>.png`, sons
`sounds/rapid/…` et `sounds/mr73/…`.

## 3. Animation : format du moteur

Durées en tics (1/35 s). Un état = une suite de frames, chacune avec sa durée et, au besoin, un événement de code. Le
tir est **un seul** événement (munition, flash, son, trace) sur la première frame de tir ; aucun autre son ou flash ne
redéclenche un tir. Les points où l'on peut changer d'arme pendant une séquence sont des frames `A_WeaponReady(WRF_NOFIRE)`.

Références mesurées :

| Arme | Tir | Recharge |
|---|---|---|
| Browning | B 2 (tir, flash, son) · C 1 · D 2 (son de culasse, étui) · E 2 · F 3 : 10 tics | pas de chargeur modélisé ; vide : G 6 (clic) |
| FAL | B 2 (tir) · C 2 (étui) · D 2 · A 1 : 7 tics | partielle 41 tics (1,17 s), vide 49 tics ; munitions engagées à la frame N (« seat ») ; interruptible à chaque frame |
| Pied-de-biche | armé 5 · frappe 3 · coup 2 · suivi 4 · retour 8 : 22 tics | — |

Sélection et rangement : le moteur fait monter et descendre l'image entière (`A_Raise`/`A_Lower` de 12 unités par tic,
de 128 à 32, soit environ 8 tics) ; des frames propres d'entrée/sortie sont possibles mais pas exigées.

Livrer pour chaque séquence : la liste des frames, leur durée en tics, les événements (nom et frame), et un
`animation.json` qui reprend ces valeurs ; une prévisualisation à 35 i/s réels.

### W03 — Manufrance Rapid (fusil de chasse à pompe)

- États : prêt ; tir → recul → retour ; **cycle de pompe distinct du tir** (fût vers l'arrière : étui éjecté ; fût
  vers l'avant : nouvelle cartouche) ; vide (clic, pas de pompe) ; recharge cartouche par cartouche.
- Enchaînement visé (valeurs de départ, à régler au banc) : tir 2–3 tics, retour 6, fût arrière 5, fût avant 5 ; environ
  20 tics entre deux tirs (0,57 s).
- Recharge : entrée (arme tournée, fût accessible) ~6 tics ; **une cartouche** introduite ~12 tics (événement
  « cartouche entrée » : +1 au magasin à cette frame) ; répétée tant qu'il reste de la place et de la réserve ; sortie
  ~6 tics ; si la chambre était vide, un cycle de pompe à la fin (chambrage). Interruptible entre deux cartouches (tir
  ou changement d'arme) sans perdre ni créer de cartouche.
- Munitions représentées : **À FIXER par Astra avec une source concordante** (capacité du magasin tubulaire de la
  variante retenue, chambre comprise ou non ; ne rien reprendre d'un autre jeu). Le modèle du jeu suivra exactement
  cette représentation : nombre de cartouches dans le tube + une en chambre, affichées « tube | réserve » comme le FAL.
- Cartouches visibles : intactes pendant la recharge ; seul l'étui éjecté au fût arrière est un étui tiré.

### W04 — Manurhin MR73 (revolver)

- Six chambres. États : prêt ; tir (départ double action, sans étui éjecté) → récupération, plus posée que le Browning
  (valeur de départ : 14 tics entre deux tirs, 0,4 s) ; vide (clic du chien) ; recharge.
- Recharge (valeur de départ ~70 tics pour six cartouches, à régler) : ouverture du barillet (à gauche), éjection des
  étuis, introduction des cartouches **une à une** (événement « cartouche entrée » : +1), fermeture, retour. Pas
  d'accessoire de rechargement rapide sans source.
- **Chambres visibles = état du jeu.** Proposition d'Opus pour y arriver sans six versions de chaque frame : livrer le
  barillet ouvert sans cartouches, puis **une couche par chambre** (cartouche en place, même toile et même décalage) ;
  le moteur superpose les couches (calques d'arme supplémentaires) selon le nombre réellement chargé. Même principe pour
  les culots visibles barillet fermé si la vue les montre.
- Recharge partielle : **À FIXER** entre deux lectures, à déclarer et tenir partout : (a) l'éjection vide tout, les
  cartouches intactes retournent à la réserve, puis on recharge à six ; ou (b) seuls les étuis tirés sont remplacés. Opus
  propose (a), plus simple à lire.
- Munition : .357 Magnum représentée ; ressource de jeu distincte du 9 mm (intégration future).

## 4. Munitions : règles communes

Aucune munition ou réserve négative ; clic sur vide sans projectile ; tir impossible pendant les frames de recharge ; les
changements de compte n'arrivent qu'aux frames d'événement ; après sauvegarde et chargement, compte, image et son se
retrouvent d'accord.

## 5. Audio : valeurs réelles

| | Existant |
|---|---|
| Format du jeu | WAV PCM 16 bits, 48 kHz, mono (tous les sons d'armes actuels) |
| Variantes | tir en trois variantes aléatoires (`$random` dans `SNDINFO`), ex. `rf/fal/shot1..3` |
| Canaux | tir : canal arme avec chevauchement (`CHAN_WEAPON`, `CHANF_OVERLAP`) pour ne pas couper la queue du précédent ; mécanique : canal objet (`CHAN_ITEM`, un son y coupe le précédent) |
| Événements FAL | `raise`, `shot`, `shell`, `dry`, `cloth`, `latch`, `mag_out`, `mag_in`, `seat`, `action` |
| Événements Browning | `fire`, `slide`, `dry` |
| Niveaux | crêtes des tirs actuels autour de -2 dBFS ; garder au moins 1 dB de marge ; comparer à `sounds/fal/shot_0?.wav` à écoute constante |

Livrer masters sans perte (24 bits acceptés) **et** exports 16 bits 48 kHz mono ; un fichier par événement, noms en
minuscules. Événements attendus : Rapid `raise`, `shot` (×3), `pump_back`, `pump_fwd`, `shell_in` (×2–3), `dry`,
`cloth` ; MR73 `raise`, `shot` (×3), `dry`, `cyl_open`, `eject`, `round_in` (×2–3), `cyl_close`. Documenter sources,
licences et crédits ; dire ce qui a été écouté, par qui, avec quoi.

## 6. Livraison

Dans ton worktree : `incoming/astra/RF2_ARSENAL/<lot>/` (un lot par arme ou par envoi, jamais réécrit), avec
`manifest.json` : pour chaque fichier `file`, `target_relpath`, `sha256`, taille en px, et pour les images `sprite`,
`frame`, `state`, `tics`, `event` ; pour les sons `event`, durée, crête, format ; plus `animation.json`,
`TEXTURES.<arme>.txt` et `SNDINFO.<arme>.txt` en propositions, les sources (couches, rig, scripts), les aperçus et les
preuves. Ne dépose rien dans les chemins actifs du dépôt.

## 7. Le banc d'essai (Opus)

Opus monte un module séparé, chargé explicitement, dans une scène distincte de RF01/RF02 (stand de tir : cibles à
plusieurs distances, zone sombre et zone claire, mur proche), avec le Browning, le FAL et le pied-de-biche pour
comparer, et des classes d'essai pour W03/W04 construites depuis ta livraison ; lanceur `JOUER_RF2_ARSENAL_ESSAI.cmd`,
configuration, sauvegardes et journaux séparés ; jamais chargé par les lanceurs acceptés. Un script construit le module
depuis le dossier d'une livraison : tu pourras l'utiliser pour tes propres vérifications moteur.
