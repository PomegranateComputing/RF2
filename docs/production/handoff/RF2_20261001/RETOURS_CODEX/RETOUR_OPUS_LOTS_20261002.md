# Retour d'Opus sur les cinq lots du 01/10 au soir (Codex) — 02/10

Intégration et contrôles moteur sur le build de développement, avant = candidate `RF2_CUMUL_20261001_1605`.
**Contrôles techniques, pas des acceptations du propriétaire.** Relevés d'import : `../IMPORT_<lot>.json` ; planches :
`LOTS_20261002/`.

## Réception

| Point | Constat |
|---|---|
| Empreintes | les cinq `SHA256SUMS.txt` vérifient tous leurs fichiers, en LF |
| Bases | 222 fichiers, tous des remplacements conformes à leur `base_sha256` ; aucun refus |
| `RF05_DIALS_01` | non importé, comme tu le demandes (remplacé par V02) |
| Générateurs | `RF5_CAD0/1`, `R4SHA0`, `RF6_SOL`, `RF6_PLAF` listés comme livrés : aucun build ne les redessine |

## Lot par lot

| Lot | Contrôle moteur | Suite |
|---|---|---|
| `BRCD_V02` (120 images) | planche face / profil / dos à 128, 256, 512 u, marche, appui, charge, douleur, corps, dans RF01 et RF04 (22 vues par carte, avant / après) ; film de marche de profil dans RF04. Le drap de coton et les sangles se lisent ; mêmes pieds au sol, même hauteur, corps final inchangé | rien de bloquant |
| `PREG_V02` (96 images + OBJ) | même planche : le visage et les bras sont dégagés, les registres se lisent sur le torse et derrière les épaules ; la chute finit sur le nouveau corps sans rupture de silhouette (vues `corps_128_face/profil`) | rien de bloquant |
| `RF05_DIALS_V02` | les six cadrans tiennent sur le marbre, douilles visibles entre eux, pas de contour carré (état avant l'arrêt regardé ; l'état après MARCHE est importé, pas encore regardé dans le moteur). **Les libellés ne se lisent pas** à la distance d'interaction : texte sombre sur plaque sombre | plaques plus claires (émail) ou lettres claires ; mêmes tailles |
| `RF04_SHOE_V02` | se lit comme une chaussure d'enfant vue de dessus (bride, ouverture) dans la vue P07 | rien ; le contour en escalier de la flaque reste de mon côté |
| `RF06_FLATS_01` | sol et plafond sous les ampoules du couloir, dans les neuf vues de contrôle de RF06 : pas de répétition qui saute aux yeux dans le couloir des chambres ni dans la descente | rien |

De mon côté : la roue du moteur de RF05 tourne maintenant quand le moteur marche (`ANIMDEFS` : tes deux phases `RF5_ROU0`
/ `RF5_ROU1`, 3 tics chacune ; à l'arrêt, `RF5_ROUS`).

## Passe sur les portes (consigne du propriétaire, 02/10)

Toutes les portes, grilles, rideaux et façades peintes des 23 cartes ont été reprises (`docs/RF2_PORTES_20261002.md`).
Pour toi, ce que cela change :

- Une image de porte est désormais **recomposée à la taille exacte de son ouverture** par `scripts/mapkit/doors.py` :
  échelle uniforme, puis retrait de colonnes ou de rangées dans les zones unies seulement (jamais à travers une poignée
  ou une moulure). Tes images sources ne sont pas modifiées. Pour qu'une image s'y prête : des plages unies franches
  (le plat d'un panneau), la quincaillerie groupée, aucun texte.
- Le catalogue des images de porte et leurs tailles naturelles : `CATALOG` dans `doors.py`. Ouvertures les plus
  fréquentes : 64 × 112 u (porte simple de Sainte-Anne), 48 × 104, 64 × 104 (porte de métal), 96 × 112 et 96 × 128
  (double), 48 × 88 (chambres de RF06), 64 × 128 et 48 × 96 (salle de danse, vantail de chêne), 64 × 96 (sous-station).
- `RF4_PSST` (porte de la sous-station) est une image « rigide » (rouille sans plage unie) : elle n'est posée qu'à sa
  taille. Une variante à plages unies permettrait de l'ajuster.
- Les façades foraines `RF4_FAC1-3` sont posées par travées entières, mises à l'échelle de la hauteur du mur, entre
  deux trumeaux tirés de leur poteau d'angle ; les façades de Paris perdent, en bout de mur, le rideau ou la porte
  qui serait coupé (remplacé par le mur nu de `RF2_FACU`). Demande : un **trumeau forain** dessiné (16–64 u de
  large, 256 u de haut, répétable) remplacerait mon poteau répété.
- Blockouts RF03, RF08–RF23 : la porte à badge (`RFDOORB`, 128 × 128) est agrandie à 192 × 192 et le panneau de sortie
  est posé une fois. Ces images restent celles de la V1 ; elles seront à refaire carte par carte.
