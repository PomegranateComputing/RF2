# RF2-ART-02 — ennemis RF01, retouche visuelle (intégration Opus)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Candidate Astra intégrée le 27/09/2026. RF01 reste accepté ;
cette retouche n'est pas approuvée tant que le propriétaire ne l'a pas dit.

## Jouer

- Ennemis seuls sur RF01 accepté : `JOUER_RF2_ART-02.cmd` (branche `candidate/art-02` = tag
  `rf01-owner-accepted-20260927` + ce seul commit d'import). Même carte, mêmes armes, mêmes sons, mêmes menus que le
  build accepté.
- Référence à côté : `JOUER_RF2_ART_REVIEW.cmd` (inchangé).

## Ce qui a été importé

Livraison Astra `C:\PROJECTS\RF2_UZDOOM_ASTRA_20260927\incoming\astra\RF2_ART_02\` (manifeste, base `5b53d9e`).
323 fichiers, copiés fichier par fichier après contrôle : 320 sprites (104 ORDY, 120 BRCD, 96 PREG) et les 3 skins des
modèles de cadavres. Pour chacun : empreinte livrée = manifeste, empreinte de base = fichier de l'arbre courant,
dimensions et grAb identiques à la base, cible dans `sprites/enemies/` ou `models/rf2_art_01/`. 0 écart. Aucun
fichier de code, de carte, de son ni de définition modifié. Sources, manifeste, crédits et preuves sélectionnées :
`art/rf2_art_02/` (le build de revue d'Astra, 1,3 Go, reste dans son worktree).

## Contrôles

| Contrôle | Résultat |
|---|---|
| `RF01.wad` | inchangé (le lot ne touche pas la carte) |
| Comportements (`enemies.zs`, états, durées, hitbox) | inchangés (aucun fichier de code dans le diff) |
| `check_runtime.py` | PASS |
| Compilation | propre |
| Alignement des trois familles dans la cour (rf_dev_weapons) | nouvelles images chargées, pieds au sol, tailles identiques |
| Cadavres, 3 familles × 7 appuis (rf_dev_corpse) | même pose que la référence : Z = 0 sur sol plat, mur, seuil, comptoir, table ; escalier et perron identiques à la base (limite connue du corps rigide) |

## Avis d'intégrateur (à lire avant de juger)

La passe est **surtout une passe de matières et de valeurs** : tunique plus sourde, veste du brancardier bleu charbon
à fines rayures, plis et usure localisés, papier et reliures du porte-registre plus sombres. Le rig articulé, les
volumes, les proportions et les visages sont **les mêmes** qu'en RF2-ART-01. Le lot respecte donc strictement le
contrat (visuel seulement, sans rien casser), mais l'amélioration du dessin demandée — volumes, visages, anatomie
plus aboutis — est limitée. Si le propriétaire attend un saut plus net, la prochaine passe doit reconstruire le master
(silhouettes, têtes, mains) et non seulement l'atlas de matières.

## Retour arrière

`git revert <commit d'import>` sur la branche de production, ou lancer `JOUER_RF2_ART_REVIEW.cmd`. Les 323 empreintes
de base sont dans `art/rf2_art_02/manifest.json` (`base_sha256`).
