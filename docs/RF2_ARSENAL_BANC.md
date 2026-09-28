# RF2-ARSENAL — banc d'essai (W03 Manufrance Rapid, W04 Manurhin MR73)

**Statut : banc d'essai prêt, images et sons PROVISOIRES.** Astra produit les armes (contrat
`docs/production/handoff/RF2-ARSENAL/CONTRAT.md`) ; ce banc les recevra. Aucune arme n'entre dans la campagne, les
cartes, les inventaires ou les lanceurs acceptés. Rien ici ne vaut accord du propriétaire.

## Lancer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_ARSENAL_ESSAI.cmd` | stand de tir `ARSENAL` directement ; **4** Rapid, **5** MR73, **1–3** Browning, FAL, pied-de-biche ; **R** recharger |

Build `dist\arsenal\RF2_ARSENAL_ESSAI_20260928_1822\` : module `RF2_ARSENAL_ESSAI.pk3` (sha256 `ebca717d…`, 65
fichiers), chargé par-dessus la base figée `dist\arsenal\base\RF2_BASE_src_23773520f797.pk3` (sha256 `a03fad5f…`,
jeu construit depuis `src/` de `prod/rf2-campaign` `bf66019` ; Browning et FAL identiques au build accepté, contrat
§0). Branche `bench/rf2-arsenal` (`937a40d`). Configuration `user\uzdoom_arsenal_essai.ini`, sauvegardes
`user\savegames_arsenal_essai`, journal `user\logs_arsenal_essai\` : la partie normale et ses sauvegardes ne sont pas
touchées. Mode d'emploi et format des fichiers : `bench/arsenal/README.md`.

## Produit

- **Stand** : couloir clair et couloir sombre, cibles à 128, 256, 512, 896 unités (elles rapportent touches et dégâts,
  ne tombent jamais), mur proche ; les armes de référence pour comparer à réglages constants.
- **Mécaniques** (code du banc, pas de la campagne) : Rapid — tube + chambre, étui laissé par le tir, course de pompe
  distincte du tir (arrière : étui éjecté ; avant : cartouche chambrée), recharge cartouche par cartouche interrompue
  par la détente ou un changement d'arme, clic à vide ; MR73 — six chambres, recharge partielle règle (a), une
  cartouche à la fois, six couches de chambre qui montrent le nombre réellement chargé, clic du chien.
- **Construction depuis une livraison** : `scripts/arsenal/build_bench.py --delivery <dossier>` lit un fichier
  d'animation par arme (images, durées en tics, événements, sons) et génère les classes, `TEXTURES` et `SNDINFO` ; il
  refuse une animation sans les événements dont la mécanique a besoin. Sans livraison : dessins étiquetés (nom
  d'image, séquence, durée, événement) et bips, aux valeurs de départ du contrat (Rapid : tir 8 tics + pompe 10 ;
  MR73 : 14 tics entre deux tirs, recharge de six 71 tics).
- **HUD d'essai** (en haut à droite) : source (livraison / PROVISOIRE), compteur, séquence, image et durée en cours,
  tirs, contrôle du compte, dernier impact.

## Vu, entendu, vérifié

| | |
|---|---|
| Vu (Opus, sur images fixes) | 17 instants × 3 formats (1920×1080, 2560×1080, 1440×1080) : prêt, tir avec flash, pompe arrière/avant, cartouche introduite, couloir sombre, barillet ouvert avec 1 puis 3 cartouches, éjection, tir contre le mur proche, FAL et Browning de référence. Les couches de chambre tombent dans les trous du barillet ; manches jusqu'aux bords en 4:3 et 21:9 ; flash à la bouche. Les dessins provisoires ne se jugent pas comme des armes. |
| Entendu | **rien** : les sons provisoires sont des bips synthétiques ; aucune écoute. |
| Vérifié par script (`bench_probe.py`, PASS) | compte conservé à chaque événement ; rien de négatif ni au-dessus de la capacité ; impacts = plombs × tirs (88 pour 9 tirs de Rapid et 16 de MR73) ; clic à vide sans tir ni impact ; détente pendant la recharge : tir après la cartouche en cours ; changement d'arme pendant la recharge : plus rien n'entre ; réserve courte (2) puis vide ; sauvegarde et chargement : mêmes compteurs, l'arme tire ; mort pendant la recharge : plus rien n'entre ni ne tire. |

## Choix déclarés (identiques dans l'image, le code et le HUD d'essai)

- **Rapid, capacité 5 + 1 : provisoire, à fixer par Astra** avec une source concordante (contrat §3).
- Chambre vide, tube non vide : la détente fait une course de pompe sans tir. Après une recharge avec chambre vide,
  la pompe prend une cartouche du tube : une deuxième recharge complète le tube.
- MR73, recharge partielle **(a)** : tout est éjecté, les cartouches intactes retournent à la réserve.
- Munitions du banc (`RFBenchShells`, `RFBenchMagnum`) distinctes de celles du jeu ; dégâts et dispersion de banc
  (Rapid 8 plombs × 8, MR73 40) : **pas un équilibrage**.
- Le panneau d'arme du HUD RF ne connaît que le FAL : pour les armes d'essai il affiche la réserve seule ; le compteur
  complet est dans le HUD d'essai. Le HUD appartient à un autre lot : non modifié.

## Restes et limites

- Images et sons définitifs : attendus d'Astra. Les dessins provisoires sont plus fins que le FAL ; le cadrage réel se
  jugera sur ses exports.
- Non testé par script : la pause (menu) ; l'écoute du mix.
- Au chargement d'une sauvegarde, la ligne de journal « banc=ARSENAL » n'apparaît pas ; sans effet sur les compteurs.
- UZDoom 5.0.1 ignore `+logfile` en ligne de commande : le lanceur écrit le journal depuis la sortie standard.
- Builds conservés et remplacés : `RF2_ARSENAL_ESSAI_20260928_1807` (défaut : une cartouche perdue à chaque
  introduction, `TakeInventory` sans `fromdecorate` — trouvé par la sonde), `_1818` (journal vide) ; `_1822` a le
  même module que `_1818`.
- Restent pour l'intégration : emplacements, classes et munitions de campagne, équilibrage, apparitions, ramassages,
  progression ; Rapid et MR73 sont postérieurs à 1940 (placement selon le parcours temporel, contrat).

## Preuves

`dist\arsenal\RF2_ARSENAL_ESSAI_20260928_1822\` : `BUILD_INFO.json` (empreintes, séquences, durées), `genere\` (code,
`TEXTURES`, `SNDINFO` générés), `preuves\sonde.json` (journal complet de la sonde), `preuves\captures\` (planches et
captures par format).
