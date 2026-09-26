# RF2-ART-01 — revue de la passe artistique (armes, ennemis, cadavres, son, HUD)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Le comportement en jeu a été vérifié dans UZDoom par les outils
du projet ; le jugement visuel et sonore reste au propriétaire. Aucune écoute n'a eu lieu, ni par l'agent ni par une
personne.

## Jouer la revue

- Lanceur : `C:\PROJECTS\RF2_UZDOOM\JOUER_RF2_ART_REVIEW.cmd` (double-clic ; fonctionne depuis n'importe quel dossier).
  Il lance le build figé indiqué par `dist\review\LATEST.txt`, sans recompiler.
- Build : `dist\review\RF2_ART_REVIEW_20260926_1418\RF2_ART_REVIEW.pk3`, commit `405df6a` (branche
  `art/rf2-art-01-integration`), SHA-256 dans `BUILD_INFO.json`. Configuration et sauvegardes de revue séparées
  (`user\uzdoom_art_review.ini`, copie de ta configuration au premier lancement ; `user\savegames_art_review`) : ta
  configuration n'est pas modifiée.
- Preuves : `dist\review\RF2_ART_REVIEW_20260926_1418\evidence\` (`index.html`). Livraison Codex et ses propres
  preuves : `C:\PROJECTS\RF2_ART_HANDOFF_20260925\CODEX_LIVRAISON\` (`evidence\index.html`, `RAPPORT.md`).

## Ce qui a changé

- **Pistolet** (Codex) : Browning vu depuis l'arrière, canon qui s'éloigne, deux mains continues, culasse rigide,
  flash sur un calque séparé. **FAL** : même matière, cadrage moins envahissant.
- **Ennemis** (Codex) : les trois familles refaites sur 8 rotations (infirmier, brancardier, porte-registre), matières
  lisibles, marge dans les tons clairs : la blouse qui brûlait au blanc sous les lampes du couloir garde son détail
  (pixels ≥ 240 dans la silhouette : 3 355 avant, 4 après, même position, mêmes lumières).
- **Cadavres** : la pose finale est un modèle 3D couché (Codex) au lieu d'une silhouette debout tournée dans l'image.
  Ajout Opus : le corps se pose une fois à l'arrivée au sol, incliné le long d'un escalier et tourné s'il traverserait
  un mur (sinon le modèle rigide s'enfonçait dans les marches).
- **Sang** (Codex) : sprites RF au lieu du sang pixelisé de l'IWAD.
- **Son** : 66 sons (Codex, sources CC0 et crédits) ; tirs avec variantes, voix de Viktor. Mix (Opus) : le lit
  `RFAMB01` qui masquait tout est 12 dB plus bas, les voix ennemies recalées sur les nouveaux fichiers, les tirs ne se
  coupent plus entre eux.
- **HUD** (Opus) : le texte rouge du moteur en haut à gauche (messages de ramassage) est dessiné par le HUD sous
  l'objectif ; notes et verrous dans la police RF, sur fond lisible ; « Partie sauvegardée. » en français.
- **Combat** (Opus) : la liasse du porte-registre faisait 9 à 72 dégâts (règle du moteur pour les projectiles), elle
  fait les 9 déclarés.

## Grille de revue

| Domaine | Résultat | Preuve | Limite |
|---|---|---|---|
| Perspective du pistolet | Vue arrière, canon vers l'avant au repos et au tir | `avant_apres/01`, `02`, `03` | Master généré, pas une CAO : forme du chien et prise à juger |
| Mains et animation | Prise stable, manches continues, sélection, tir, vide, recharges FAL exercés | captures `09_cadrage_*` ; recharge vide et partielle : chargeur et réserve corrects | Timing identique à la base (aucune frame ajoutée) |
| Cadrage | Mêmes proportions en 1920×1080, 2560×1440 et 3840×2160 plein écran | `09_cadrage_*` | 21:9 non vérifié |
| Tir | Un tir = une balle, un son, un flash ; dégâts, cadence, consommation inchangés | parcours A/B ; code | — |
| Ennemis | 3 classes, 8 rotations de chaque frame utilisée, états complets | contrôle statique (0 rotation manquante), `05_ennemis_alignement` | Anatomie et vêtements : jugement artistique |
| Éclairage | Plus de blanc brûlé ; éclairage de la carte inchangé | `04_blanc_brule_lampes` | — |
| Mort | Chute en sprites puis corps couché au sol, tenu | `06_cadavre_*` (côté, plongée) ; film après | Chute sur peu de poses (budget existant) |
| Contact au sol | Plat, mur, seuil : au sol ; escalier : incliné sur les marches | journal `corpse_art2.txt` (z, inclinaison) | Corps rigide : un grand corps (brancardier et brancard) ne tient pas dans un escalier de 64 unités |
| Progression | Parcours A et B, 104 lignes de porte : réussis | `mesures/RF01_E2E_*.json`, `doortest.txt` | Autopilote : pas un joueur humain |
| Sources audio | Tirs travaillés, variantes, voix, chutes de corps, portes | livraison Codex (masters, crédits) | Aucune écoute |
| Mixage | Pas d'écrêtage : crête −10,9 (ouverture) et −6,7 dBFS (combat dense) ; lit de fond 12 dB plus bas (médiane −33,6 contre −21,6 dBFS) | `films/*.json` | Mesures ≠ écoute ; à juger au casque et aux enceintes |
| Acoustique | Fichiers secs, réverbération des pièces par le moteur | `docs/RF01_AUDIO.md` | Non écouté |
| HUD | Messages du moteur intégrés, marges propres, rien de supprimé | `08_hud_messages` | — |
| FX | Sang RF ; flash du Browning à la bouche | films, captures | Décalques de sang sur les murs : ceux du moteur |
| Map | Géométrie et parcours inchangés : `RF01.wad` identique à la base | SHA-256 `b643321…` | — |
| Packaging | Build depuis `src/` seul ; 616 fichiers importés vérifiés par empreinte ; aucun avertissement au chargement | `import_codex_report.json`, journaux | — |
| Performance | Pas de régression notable : 0,44–0,59 ms par image ; avec 28 corps accumulés 0,6–1,0 ms (pire 1,66 ms) | `mesures/perf_*.txt` | Mesuré sur RTX 5070 Ti, bureau invisible, GPU partagé |
| Livraison | Lanceur testé depuis un autre dossier ; build distinct et daté ; base à côté | `BUILD_INFO.json` | — |

## À juger à l'œil et à l'oreille

Le Browning (forme, mains), l'allure des trois ennemis de près et de loin, les chutes, le mix en combat (hiérarchie
armes / voix / ambiance), le confort des voix et des tirs, le sang.

## Retour arrière

- La base est intacte : branche `main` (`6e1a31b`) ; `dist\review\RF2_BASELINE_6e1a31b.pk3` pour comparer (même
  commande que le lanceur, avec ce fichier).
- Retour ciblé : `git checkout 6e1a31b -- <chemins>` (liste dans `CODEX_LIVRAISON\MANIFEST.json`) ou `git revert` des
  commits `43ce8e1` (import Codex), `54f33b9` (pose des corps), `405df6a` (mix).
