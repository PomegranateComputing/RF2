# RF2 — contrat Opus → Codex (production artistique, mandat du 01/10/2026)

Opus, 01/10/2026. Opus est le seul intégrateur (cartes, générateurs, runtime, builds, lanceurs). Codex produit les
ressources artistiques et en répond jusqu'à leur rendu en moteur. Ce contrat fixe ce que le jeu lit réellement ; il
change seulement par une version datée de ce fichier. Copie : `C:\PROJECTS\RF2_UZDOOM_CODEX_ART_20261001\handoff\`.

## 1. Base réelle

| | |
|---|---|
| Projet, branche | `C:\PROJECTS\RF2_UZDOOM`, `prod/rf2-campaign` ; HEAD au départ du mandat `43763fa` (le poste avance : lire `git log`) |
| Version jouée par le propriétaire | `dist\candidates\RF2_CUMUL_20260930_1821\RF2_CUMUL.pk3`, sha256 `6c85e747…ec31`, commit `6134a94` |
| Banc d'armes | `dist\arsenal\RF2_ARSENAL_ESSAI_20260930_1901\` (`48159170…3733`), branche `bench/rf2-arsenal` `a08e4b7`, worktree `C:\PROJECTS\RF2_UZDOOM_BENCH_20260930` |
| Fichiers que le build charge | tout `src/` est empaqueté par `scripts/build.ps1` dans `dist/RF2_DEV.pk3` ; les chemins de ce contrat sont relatifs à `src/` (= `target_relpath`) |
| Ce qui n'est pas chargé | `art/`, `incoming/`, `legacy/`, `docs/` : sources et archives seulement |

## 2. Masters (lire, ne jamais redessiner une autre personne)

| Master | Fichiers lus par le build | Sources |
|---|---|---|
| Visage de Viktor | `graphics/hud/viktor/VIKTOR_H100.png` (et `H080`, `H060`, `H040`, `H020`, `DEAD`), 512 × 512 | planche du propriétaire `art/rf2_hud_viktor_02/source/`, `art/RF2_VIKTOR_HUD_SHEET.png` ; fiche d'identité : dossier maître `legacy/import/RF2_DOSSIER_MAITRE.md` §05 (quarantaine, crâne rasé, peau pâle, yeux bleus, rasé, anneaux noirs aux oreilles, sweat noir) |
| Bras, manche noire | `graphics/weapons/fal/`, `graphics/weapons/browning/`, `graphics/weapons/crowbar/` (acceptés) ; banc : `graphics/weapons/{rapid,mr73,famas,scorpion}` du module 1901 | sources Astra `art/rf2_art_01`, `incoming/astra/RF2_ARSENAL/`, `incoming/astra/RF2_SUITE_20260930/W0*` |
| Tenue de jeu | sweat noir à capuche (cordons), pantalon sombre, Docs, anneaux (roman l. 747 : « le sweat noir, les Docs, les anneaux ») | |

**Constat moteur du 01/10 (à corriger) :** le reflet de RF02 `sprites/rf02_figures/R2F8A1…A8` montre **un autre homme**
(cheveux bruns courts, pull ras du cou, sans anneaux) ; il mesure 68 u des semelles au sommet, pour un joueur de 56 u.
Mesure : `docs/production/handoff/RF2_20261001/mesures/reflet_rf02.md`.

## 3. Conventions lues par le runtime

### Figures non hostiles et reflets (`sprites/rf02_figures/`, `sprites/rf04/`, …)
- Toile 512 × 448 RGBA, 8 rotations réelles `A1…A8`, `grAb` 256, 424 (milieu des semelles), `Scale 0.18` uniforme.
- **Hauteur monde = hauteur en pixels × 0,18**, sans précompensation verticale dans l'image : le moteur étire tout
  (murs, figures, ennemis) de 1,2 en hauteur de la même façon ; l'infirmier (53 u) suit déjà cette règle.
- Cibles : Viktor **56 u = 311 px** (taille du joueur) ; adultes 52–58 u ; enfant d'après la fiche.
- Les yeux du joueur sont à 41 u (`Player.ViewHeight`, règle du jeu, inchangée) : face à un miroir, les yeux d'un
  reflet de 56 u sont ~11 u au-dessus de l'horizon de l'écran. C'est connu et accepté ; ne pas le corriger par l'image.
- Pas de dérive d'une image à l'autre : même hauteur de tête, mêmes semelles sur la ligne 424.

### Ennemis (`sprites/enemies/`, `models/rf2_art_01/`)
| Famille | Préfixe | États lus (lettre : durée en tics) | Acteur |
|---|---|---|---|
| Infirmier `RFOrderly` | `ORDY` | A repos 10 ; B–E marche 4 chacune ; F armé 10, G frappe 4, H retour 14 ; I douleur 3 + 4 ; J 6, K 7, L 8 chute ; M corps (modèle) | Height 54, Radius 18, Scale 0.18 |
| Brancardier `RFBrancardier` | `BRCD` | A 10 ; B–E 5 ; F tension 24, G 1 puis G/N 2+2 charge ; O impact 8 ; H récupération 28 ; I douleur 8 ; J 7, K 8, L 10 ; M corps | Height 56, Radius 40 |
| Porte-registre `RFPorteRegistre` | `PREG` (+ liasse `PRGS`) | A 8 ; B–E 5 ; F prépare 26, G lance 2, N 12 ; H douleur 5 ; I 7, J 7 ; K corps | Height 60, Radius 22 |
- Toile actuelle d'ORDY : 180 × 301 (debout), `grAb` aux semelles (90, 299) ; modèles de corps OBJ + peau dans
  `models/rf2_art_01/`, `MODELDEF` d'Opus (`Scale 5 5 5`, ne pas revenir à 5 5 6), corps posé au sol.
- Corrections runtime du 30/09 conservées par Opus (collision, coups à travers obstacle, chute, corps).

### Textures et sols
- 4 px/u pour ce qui se voit de loin (façades, charpentes), 8 px/u pour ce qui se voit de près (objets de scène,
  plaques) ; Codex donne la taille monde et un bloc `TEXTURES` proposé ; Opus l'écrit dans `src/TEXTURES.*`.
- Masqués (panneaux, vitres, grilles) : RGBA ; inscriptions composées avec une vraie police sur une couche séparée.

### Armes (vue à la première personne)
- Toile 1536 × 1024 RGBA, `XScale 6.8`, `YScale 8.16`, `Offset -750, -460` ; offsets d'image explicites `[0, 32]`.
- Animation : schéma `rf2-bench-animation/1` (contrat arsenal v2, `docs/production/handoff/RF2-ARSENAL/CONTRAT.md`) ;
  Rapid 4+1, MR73 six chambres règle (a), Scorpion à cadence réparée : **ne pas changer leur fonctionnement**.

### Sons
- WAV PCM mono 48 kHz 16 bits (master plus profond en source) ; noms : ceux des tableaux de routage
  (`ROUTAGE_SON_ARMES.md`, livré par Opus avec un film de référence au son natif) ; le campagne lit
  `rf/fal/*`, `rf/browning/*`, `rf/crowbar/*` (`src/SNDINFO`), le banc `rf/bench/{rapid,mr73,w05,w09}/*`.

### Planches de transition (nouveau, structure fixée par Opus)
| Élément | Format |
|---|---|
| Identifiants | `RF01_RF02`, `RF02_RF04`, `RF04_RF05`, `RF05_RF06`, `RF06_RF07` (ce dernier seulement quand RF07 existe) |
| Image lue par le jeu | `graphics/comics/<ID>.png`, 1920 × 1080, sRGB, **sans texte**, une page composée de 3 à 5 cases |
| Master | 3200 × 1800 en source, calques ; même composition |
| Données | `planche.json` dans le lot : cases `[{"id", "rect": [x, y, w, h]}]` en pixels de l'image 1920 × 1080, dans l'ordre de lecture ; légendes `[{"id", "texte", "zone": [x, y, w, h], "apres_case"}]` (UTF-8) |
| Texte | composé par le jeu (police du jeu) dans les zones ; aucune lettre dans l'image |
| Ratio | le jeu garde l'image entière en 4:3 et 21:9 (bandes) : rien d'essentiel à moins de 5 % des bords |

## 4. Noms réservés (états lus par les scripts d'Opus)

- RF04 / RF05 : la liste de `docs/production/handoff/DEMANDES_20260930/RF04_RF05_LUNA_PARK.md` (`RF4_*`, `RF5_*`,
  `R4G1`, `R4JB`, `R4SH`, `R5EN`, `R5TR`…) et les définitions en place dans `src/TEXTURES.rf04` (59 entrées). Reflets
  alternatifs de la salle de danse : **`R4V2`** (blouse grise d'ouvrier) et **`R4V3`** (chemise claire, badge à la
  ceinture), convention « figures » ci-dessus, visibles seulement dans les miroirs. Mêmes masters RF04 fermé / RF05
  rallumé : un nom par objet, un état par variante (`…0` éteint, `…1` allumé).
- RF06 : `src/TEXTURES.rf06` (`RF6_*` : pochoirs `RF6_N117`, `RF6_N404`, `RF6_N017`, `RF6_ER1…5`) ; nouveaux noms à
  demander à Opus quand la carte recomposée les fixe.
- RF07 : `docs/production/handoff/DEMANDES_20260930/RF07_JERMA.md` (`RF7_*`, `R7*`).
- Un nom absent de ces listes se demande à Opus avant export.

## 5. Lots : qui produit quoi

| Lot / asset | Producteur unique | Statut au 01/10 |
|---|---|---|
| RF01 sang-de-bœuf V03, crasse, coulure, frottement V03 | Astra | intégrés (1821) |
| RF01 humidité `RFDSTN1` (V03 retenue) ; frottement `RFDSTN4` à reprendre | **Codex** (`LOT_CORRECTIONS_01` reçu, en revue) | réattribués |
| Infirmier ORDY V03 | Astra | intégré (1821) ; **image E de profil → Codex** |
| Luna tranche 01 (pointeuse, clefs, compteurs, 8 sons) | Astra | intégrée ; **NIAG et marges CHAMBRE FROIDE → Codex** (`LOT_CORRECTIONS_01`) |
| Reste de LUNA-V01, RF05, recomposition Luna | **Codex** (`LUNA_PILOTE_01` reçu : `RF4_BROO`) | réattribué |
| Brancardier, porte-registre, roster suivant, premier boss | **Codex** | réattribué / nouveau |
| Viktor : fiche de continuité, `R2F8`, `R4V2`, `R4V3`, tout reflet futur | **Codex** | nouveau |
| Objets RF02 relevés par l'audit d'Opus (tram, landau, Astra : reprise ciblée seulement) | **Codex** | après le relevé d'Opus |
| RF06 matières ; Jerma (JERMA-V01) | **Codex** | réattribué / nouveau |
| Planches de transition | **Codex** | nouveau |
| Sons des armes (campagne et banc), ambiances Luna restantes | **Codex** | nouveau |
| Armes suivantes (après contrat par arme d'Opus) | **Codex** | à venir |
| Lots d'Astra livrés (RF02 figures F02-01…07, tram, landau, armes W03/W04/W05/W09, menus, portrait) | Astra | conservés tels quels ; Codex ne les refait pas, il retouche seulement ce qu'Opus relève |

Astra est prévenue dans son espace (`incoming/astra/DEMANDES_OPUS_20260930/REATTRIBUTION_20261001.md`) : ses
demandes encore ouvertes passent à Codex ; elle ne les poursuit pas.

## 6. Vues de contrôle (sur 1821, par la bande de tic)

`dist\candidates\RF2_CUMUL_20260930_1821\preuves\controle_20261001\{rf01,rf02,rf04,rf05,rf06}\` — `NN_<vue>.png`
1920 × 1080 et `vues.json` ; caméras dans `docs/production/handoff/RF2_20261001/vues/`. RF01 (10 vues) et RF02 (48 :
scènes du propriétaire V01–V10, tram, landau, valise, figures F02) = **rendu cible** ; RF04 (14), RF05 (12), RF06 (7) =
état de départ à dépasser. Monstres masqués pendant ces vues. Outil : `scripts/production/capture_views.py`.

## 7. Séparation des écritures

| Nature | Qui écrit | Où |
|---|---|---|
| Image, modèle, son | Codex | son espace `C:\PROJECTS\RF2_UZDOOM_CODEX_ART_20261001\<LOT>\runtime\…` |
| Proposition de définition (`TEXTURES`, `MODELDEF`, `SNDINFO`, échelle, routage) | Codex propose (texte dans le lot) | Opus l'écrit dans `src/` |
| Carte, générateur, ZScript, `MAPINFO`, `LANGUAGE`, build, lanceur | Opus seul | `C:\PROJECTS\RF2_UZDOOM` |
| Retours | Opus | `docs/production/handoff/RF2_20261001/RETOURS_CODEX/` |

Codex n'écrit pas dans `src/`, les générateurs, `user/`, `dist/`, `incoming/astra/`. Opus ne modifie pas les sources
de Codex ; il importe des lots figés (`scripts/import_astra_lot.py`, contrôles de base et de destination ; une
destination changée depuis la base du lot n'est pas écrasée et cet asset seul revient).

**Lot figé** = dossier contenant `manifest.json` (schéma 1 : `file`, `target_relpath`, `sha256`, `base_sha256` pour
un remplacement, dimensions/états), `SHA256SUMS.txt` en **LF**, `POUR_OPUS.md` et une planche de contrôle. Un dossier
sans ces fichiers est un travail en cours : Opus ne l'importe pas.

**Moteur :** une seule session UZDoom à la fois sur le poste. Verrou commun `C:\PROJECTS\RF2_MOTEUR.lock` :
`python C:\PROJECTS\RF2_UZDOOM\scripts\engine_lock.py --agent codex --task "<quoi>" -- <commande>` attend, lance,
libère. Profil et sauvegardes de Codex distincts (`-config`/`-savedir` dans son espace) ; jamais `user\`.

## 8. Ordre utile pour Codex

1. Fiche de continuité de Viktor ; `R2F8` refait (56 u, visage du master, tenue de jeu) ; image E de l'infirmier.
2. Pilote Luna (zone : ouverture sur le bassin, charpente visible, façade d'attraction, marquise, sol) — les noms et
   tailles de la zone pilote sont dans `ZONE_PILOTE_RF04.md` qu'Opus dépose avec le relevé du plan.
3. Planche `RF01_RF02` (pilote des transitions).
4. Reste de RF04, RF05, RF06 ; `R4V2`, `R4V3` ; autres planches ; sons des armes.
5. Brancardier, porte-registre, roster suivant ; premier boss ; armes suivantes (contrats par arme d'Opus) ; Jerma.
