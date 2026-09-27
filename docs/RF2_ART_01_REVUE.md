# RF2-ART-01 — revue de la passe artistique (armes, ennemis, cadavres, son, HUD)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Le comportement en jeu a été vérifié dans UZDoom par les outils
du projet ; le jugement visuel et sonore reste au propriétaire. Aucune écoute n'a eu lieu, ni par l'agent ni par une
personne.

## Jouer la revue

- Lanceur : `C:\PROJECTS\RF2_UZDOOM\JOUER_RF2_ART_REVIEW.cmd` (double-clic ; fonctionne depuis n'importe quel dossier).
  Il lance le build figé indiqué par `dist\review\LATEST.txt`, sans recompiler.
- Build : `dist\review\RF2_ART_REVIEW_20260926_1451\RF2_ART_REVIEW.pk3`, commit `e1d007c` (branche
  `art/rf2-art-01-integration`), SHA-256 dans `BUILD_INFO.json`. Configuration et sauvegardes de revue séparées
  (`user\uzdoom_art_review.ini`, copie de ta configuration au premier lancement ; `user\savegames_art_review`) : ta
  configuration n'est pas modifiée.
- Preuves : `dist\review\RF2_ART_REVIEW_20260926_1451\evidence\` (`index.html`). Livraison Codex et ses propres
  preuves : `C:\PROJECTS\RF2_ART_HANDOFF_20260925\CODEX_LIVRAISON\` — **dossier externe disparu (constat du
  27/09/2026) / preuve originale indisponible.** Ce qui en survit est versionné : rapport d'import
  ([import_codex_report_20260926_1349.json](production/recovery/import_codex_report_20260926_1349.json)), sources et
  crédits (`art/rf2_art_01/`) ; voir [RECUPERATION_RF2_ART_01.md](production/recovery/RECUPERATION_RF2_ART_01.md).

## Ce qui a changé

- **Pistolet** (Codex) : Browning vu depuis l'arrière, canon qui s'éloigne, deux mains continues, culasse rigide,
  flash sur un calque séparé. **FAL** : même matière, cadrage moins envahissant.
- **Ennemis** (Codex) : les trois familles refaites sur 8 rotations (infirmier, brancardier, porte-registre), matières
  lisibles, marge dans les tons clairs : la blouse qui brûlait au blanc sous les lampes du couloir garde son détail
  (pixels ≥ 240 dans la silhouette : 3 355 avant, 4 après, même position, mêmes lumières).
- **Cadavres** : la pose finale est un modèle 3D couché (Codex) au lieu d'une silhouette debout tournée dans l'image.
  Ajout Opus : le corps se pose une fois à l'arrivée au sol. Il reste où il est tombé si rien ne gêne ; sinon il se
  tourne ou glisse de 12 à 24 unités (jamais à travers un mur) : à plat à côté d'une table ou d'un comptoir, à plat
  sur une marche ou incliné le long des marches (sinon le modèle rigide s'enfonçait dans les marches et les murs).
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
| Tir | Un tir = une balle, un son, un flash ; dégâts, cadence, consommation inchangés ; impacts sous le point central horizontalement (0,00°) | parcours A/B ; `11_visee_point_central`, `impacts_visee.txt` | Impacts 5 unités sous le point (hauteur de tir du moteur, inchangée) : moins de 1,5° aux distances de combat |
| Ennemis | 3 classes, 8 rotations de chaque frame utilisée, états complets ; pieds sur la ligne de sol, taille stable | `sprites_controle.txt` (322 sprites), `05_ennemis_alignement` | Anatomie et vêtements : jugement artistique |
| Éclairage | Plus de blanc brûlé ; éclairage de la carte inchangé | `04_blanc_brule_lampes` | — |
| Mort | Chute en sprites puis corps couché au sol, tenu | `06_cadavre_*`, `10_cadavre_*` (côté, plongée) ; film après | Chute sur peu de poses (budget existant) |
| Contact au sol | Sol plat, mur, seuil, bord de comptoir et de table : au sol ; escaliers : à plat sur une marche ou le long des marches ; en fin de parcours A, tous les corps sont au repos | `corpse_art5.txt` (3 classes × 7 placements), `e2e_A.txt` (`RF_DEV_BODY`) | Corps rigide : sur le perron de la cour (marches à 45°) le corps roule sur les marches ; le brancardier et son brancard ne tiennent pas dans l'escalier étroit de la lingerie |
| Progression | Parcours A et B, 104 lignes de porte : réussis | `mesures/RF01_E2E_*.json`, `doortest.txt` | Autopilote : pas un joueur humain |
| Sources audio | Tirs travaillés, variantes, voix, chutes de corps, portes | livraison Codex (masters, crédits) | Aucune écoute |
| Mixage | Pas d'écrêtage : crête −10,9 (ouverture) et −6,7 dBFS (combat dense) ; lit de fond 12 dB plus bas (médiane −33,6 contre −21,6 dBFS) | `films/*.json` | Mesures ≠ écoute ; à juger au casque et aux enceintes |
| Acoustique | Voix ennemie −8 dB de 64 à 700 unités, localisée à gauche (+6,9 dB) quand elle vient de gauche ; tirs du joueur centrés, sans atténuation ; réverbération des pièces par le moteur | `son_distance_centre.txt`, `docs/RF01_AUDIO.md` | Non écouté |
| HUD | Messages du moteur intégrés, marges propres, rien de supprimé | `08_hud_messages` | — |
| FX | Sang RF ; flash du Browning à la bouche | films, captures | Décalques de sang sur les murs : ceux du moteur |
| Map | Géométrie et parcours inchangés : `RF01.wad` identique à la base | SHA-256 `b643321…` | — |
| Packaging | Build depuis `src/` seul ; 616 fichiers importés vérifiés par empreinte ; aucun avertissement au chargement | `import_codex_report.json`, journaux | — |
| Performance | Pas de régression notable : 0,44–0,59 ms par image ; avec 28 corps accumulés 0,6–1,0 ms ; 6,3 ms au pire à l'instant où 8 ennemis meurent ensemble (pose des corps) | `mesures/perf_*.txt` | Mesuré sur RTX 5070 Ti, bureau invisible, GPU partagé |
| Livraison | Lanceur testé depuis un autre dossier ; build distinct et daté ; base à côté | `BUILD_INFO.json` | — |

## À juger à l'œil et à l'oreille

Le Browning (forme, mains), l'allure des trois ennemis de près et de loin, les chutes, le mix en combat (hiérarchie
armes / voix / ambiance), le confort des voix et des tirs, le sang.

## Retour arrière

- La base est intacte : branche `main` (`6e1a31b`) ; `dist\review\RF2_BASELINE_6e1a31b.pk3` pour comparer (même
  commande que le lanceur, avec ce fichier).
- Retour ciblé : `git revert` des commits `43ce8e1` (import Codex), `54f33b9` et `e1d007c` (pose des corps), `405df6a`
  (mix), ou retour d'une famille de chemins. La liste de `CODEX_LIVRAISON\MANIFEST.json` n'est plus disponible
  (**dossier externe disparu / preuve originale indisponible**) ; elle est remplacée par une reconstruction datée de
  l'import observé dans Git :
  [RF2_ART_01_IMPORT_43ce8e1_RECONSTRUCTION.json](production/recovery/RF2_ART_01_IMPORT_43ce8e1_RECONSTRUCTION.json),
  procédure dans [RECUPERATION_RF2_ART_01.md](production/recovery/RECUPERATION_RF2_ART_01.md).
