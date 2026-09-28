# RF2-HUD-02 — portrait de Viktor, six états de santé

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Commande du propriétaire `RF2_VIKTOR_HUD_OPUS.md` (27/09/2026).
La ressemblance reste à accepter par le propriétaire.

## Jouer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_HUD-02.cmd` | écran titre ; « Nouvelle partie » : RF01 puis RF02 |
| `JOUER_RF2_HUD-02_RF02.cmd` | RF02 directement (difficulté Service, équipement de sortie de Sainte-Anne) |

Build `dist\candidates\RF2_HUD-02_20260927_2230\RF2_HUD-02.pk3`, sha256
`447f911efc594810f5e777987847b9690159dd6ef90b2b8c15f3cad55ad826d9`, commit `a5ae6d3` (branche `prod/rf2-campaign`).
Build cumulatif : RF01 accepté + ennemis retouchés (ART-02) + menus (UI-01) + RF02 (MAP-02) + ce portrait. Profil et
sauvegardes séparés (`user\uzdoom_hud02.ini`, `user\savegames_hud02`). Le build accepté de RF01 et son lanceur
`JOUER_RF2_ART_REVIEW.cmd` sont inchangés et gardent l'ancien visage.

Niveaux concernés : RF01 (Sainte-Anne) et RF02 (Paris) ; tous les suivants héritent du HUD commun (`RFStatusBar`,
déclaré dans `MAPINFO` pour tout le jeu) : aucune logique propre à une carte, aucun second HUD.

## États

| Santé (part de la santé maximale normale : 100) | Fichier | État |
|---|---|---|
| plus de 80 % (et toute sur-vie) | `graphics/hud/viktor/VIKTOR_H100.png` | intact |
| plus de 60 %, jusqu'à 80 % | `VIKTOR_H080.png` | légèrement blessé |
| plus de 40 %, jusqu'à 60 % | `VIKTOR_H060.png` | blessé |
| plus de 20 %, jusqu'à 40 % | `VIKTOR_H040.png` | grièvement blessé |
| vivant, 20 % ou moins | `VIKTOR_H020.png` | critique |
| joueur mort (prioritaire) | `VIKTOR_DEAD.png` | mort |

Calcul : `RFPortrait.StateOf()` (`src/zscript/rf/hud.zs`) à partir du joueur affiché et de sa santé courante ;
référence = `GetMaxHealth(false)` (la santé maximale normale, sans bonus) ; part bornée entre 0 et 100 ; l'armure
n'intervient pas. Les six textures sont cherchées une fois puis gardées (aucun accès disque en jeu). Le portrait
occupe le même logement que l'ancien (512×512 dessiné à 15 % de l'échelle du HUD).

## Assets

Planche du propriétaire (1536×1024, six portraits détourés) conservée dans `art/rf2_hud_viktor_02/source/` ;
découpage reproductible `scripts/ui/viktor_portraits.py` ; correspondance état → fichier, positions et empreintes
dans `art/rf2_hud_viktor_02/manifest.json` ; méthode dans `art/rf2_hud_viktor_02/README.md`. Chaque tête est
cadrée depuis sa silhouette (sommet du crâne, axe) : la planche n'était pas sur une grille exacte. Les six anciens
portraits sont conservés à l'identique dans `art/rf2_hud_viktor_01/` et ne sont plus empaquetés ; plus aucune
référence active (vérifié dans le pk3 : seuls les six nouveaux fichiers).

## Preuves (dossier `evidence\` de la candidate)

- `RF01\` et `RF02\` : 14 captures 1920×1080 chacune, nommées par santé et état ; planches `RF0x_six_etats_planche.png`.
- `controles_portrait.txt` : les relevés `RF_DEV_PORTRAIT` (santé, état, fichier) de tous les contrôles.
- Seuils 100, 81, 80, 61, 60, 41, 40, 21, 20, 1 : états 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, dans RF01 et RF02 ; sur-vie 150 :
  intact ; soin de 15 à 90 (trois paliers d'un coup) : intact ; sauvegarde à 15, mort : portrait mort ; reprise par la
  touche d'usage : chargement de la sauvegarde, 15, critique.
- `transition\` : santé 35 à la fin de RF01, 35 et le même portrait à l'arrivée dans RF02.
- `resolutions\` : 1440×1080, 2560×1080, 2560×1440, 3840×2160, et échelle du HUD 0.75 et 1.5.
- `film\sequence_degats_soin_mort_reprise.mp4` : 100 → 78 → 56 → 34 → soin à 94 → 64 → 34 → mort → reprise ; image et
  son du jeu, séquence pilotée par le mode de test (pas une partie humaine).

- `RF01_E2E.json`, `RF02_E2E.json` : RF01 et RF02 rejoués de bout en bout avec ce build (passes A et B PASS,
  objectifs inchangés) : le portrait ne casse ni la progression, ni la mort, ni la reprise, ni les sauvegardes.
- Lanceurs essayés depuis `C:\` : départ direct (RF02 chargé en 3,7 s) et écran titre (pk3 chargé).

Toutes ces vérifications sont faites avec le profil de développement isolé (`build\dev`), jamais avec la
configuration ou les sauvegardes du propriétaire.

## Fichiers modifiés

| Fichier | Changement |
|---|---|
| `src/zscript/rf/hud.zs` | classe `RFPortrait` (état, fichier), sélection du portrait et cache des textures |
| `src/graphics/hud/viktor/VIKTOR_H100/H080/H060/H040/H020/DEAD.png` | nouveaux portraits |
| `art/rf2_hud_viktor_01/` | anciens portraits déplacés (hors pk3) |
| `art/rf2_hud_viktor_02/` | planche source, manifeste, méthode |
| `scripts/ui/viktor_portraits.py` | découpage |
| `src/zscript/rf/dev.zs`, `src/zscript/rf/player.zs`, `src/CVARINFO` | mode de contrôle `rf_dev_portrait` (développement seulement) |
| `scripts/film.py` | option `--no-autopilot` pour filmer une scène de test |

## Limites

- La ressemblance n'est pas jugeable par Opus : les photographies de référence (11975 à 11978) n'ont pas été
  transmises au dépôt ; seule la planche l'a été.
- Sur la planche, les iris tirent vers le bleu-vert (la commande dit « yeux bleus ») : non retouché.
- Le nombre de santé passe au rouge à 25 (règle antérieure du HUD), le portrait critique à 20 : écart laissé tel quel.
- Pas d'animation secondaire (hors périmètre de cette passe) ; le HUD n'avait pas de réaction d'impact propre au
  portrait.
