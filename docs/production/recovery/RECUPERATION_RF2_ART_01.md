# RF2-ART-01 — dossiers externes disparus, reconstruction et retour arrière

Constat du 27 septembre 2026 (Opus 5.5, lecture seule).

## 1. Dossiers externes

| Dossier | Constat 27/09 | Remarque |
|---|---|---|
| `C:\PROJECTS\RF2_ART_HANDOFF_20260925` (dont `CODEX_LIVRAISON\`, `MANIFEST.json`, `BASE_6e1a31b.sha256`, preuves Codex) | absent | ni dans `C:\PROJECTS`, ni dans la corbeille Windows, ni dans Documents / Téléchargements / Bureau (recherche par nom, profondeur 6) |
| `C:\PROJECTS\RF2_ART_PASS_20260925` (pack de prompts du 25/09) | absent | archive `RF2_PASSE_ARTISTIQUE_CODEX_OPUS_2026-09-25.zip` non trouvée sur ce poste ; elle existe hors poste selon le pack du 27/09 (SHA-256 `304d6601…fd926`) |
| `C:\PROJECTS\RF2_UZDOOM_ART` | présent (modifié le 26/09 à 12:16) | copie de travail Codex, **non** versionnée ; contient `art_pass\POUR_OPUS.md`, `RAPPORT.md`, `evidence\index.html`. Rien ne prouve qu'elle soit identique à `CODEX_LIVRAISON` |

Aucune cause ni aucun auteur de la disparition n'est établi. Git ne suit pas les dossiers externes ; l'arbre propre
et l'heure annoncée (vers 20:46) ne désignent personne. L'enquête reste un chantier distinct et non bloquant.

Le jeu ne dépend d'aucun de ces dossiers : le build accepté a le contenu exact de `src/` à `5b53d9e` (vérifié fichier par
fichier), et les sources, crédits et scripts de reproduction de la passe sont versionnés dans `art/rf2_art_01/`.

## 2. Ce qui survit dans le dépôt

- `docs/production/recovery/import_codex_report_20260926_1349.json` : copie du rapport écrit par
  `scripts/import_codex_delivery.py` au moment de l'import (26/09 13:49) — 616 fichiers copiés, empreintes vérifiées,
  0 conflit, 0 refus. Original dans `build/dev/` (non versionné).
- `docs/production/recovery/RF2_ART_01_IMPORT_43ce8e1_RECONSTRUCTION.json` : **reconstruction datée du 27/09** de
  l'import observé dans Git. Ce n'est pas le `MANIFEST.json` de Codex.
- `art/rf2_art_01/` : sources, masters audio, prompts d'image archivés, crédits CC0, scripts de réexport.

## 3. Reconstruction de l'import observé (`43ce8e1`, parent `844b50f`)

606 chemins modifiés par le commit : 221 ajouts, 385 remplacements, aucune suppression ni renommage.

| Voie | Fichiers |
|---|---|
| Copie vérifiée par l'importeur | 593 (le rapport compte 616 : 23 fichiers livrés étaient identiques à l'arbre et n'apparaissent pas dans le diff) |
| `art/rf2_art_01/install_models.py` (modèles des corps) | 6 (`src/models/rf2_art_01/`) |
| Patch partagé fusionné à la main | 7 (`CVARINFO`, `MODELDEF`, `SNDINFO`, `TEXTURES.weapons`, `dev.zs`, `enemies.zs`, `weapons.zs`) |

Changés ensuite jusqu'à `5b53d9e` : `CVARINFO`, `MODELDEF`, `SNDINFO`, `dev.zs`, `enemies.zs` (pose des corps,
niveaux des voix, sondes). Chaque ligne du JSON donne l'empreinte à `43ce8e1`, l'empreinte de base à `844b50f` pour
un remplacement, la voie d'import et le consommateur runtime.

Commande de reconstruction : `python scripts/production/reconstruct_import_manifest.py` (lecture `git show` des deux
révisions, SHA-256 des blobs ; rien d'autre n'est lu que Git et la copie du rapport d'import).

## 4. Retour arrière ciblé (décrit, non exécuté)

Le dossier de livraison disparu n'est pas nécessaire. Sur une branche dédiée issue du HEAD à corriger :

1. **Tout RF2-ART-01** : `git revert 405df6a e1d007c 54f33b9 43ce8e1` (mix, pose des corps, import), dans cet ordre,
   puis reconstruire. Les commits documentaires (`aee054b`, `80c7e32`, `5b53d9e`) peuvent rester.
2. **Une famille de ressources seulement** (par exemple les sprites ennemis) : prendre la liste des chemins de la
   reconstruction filtrée sur le consommateur, puis `git checkout 844b50f -- <chemins>` pour les remplacements et
   `git rm` des ajouts de cette famille. Vérifier ensuite les fichiers partagés qui les référencent (`MODELDEF` pour
   ORDY M / BRCD M / PREG K, `enemies.zs` pour `RFBody.Settle`, `SNDINFO`) : ils ont évolué après l'import et ne
   doivent pas être restaurés aveuglément.
3. Reconstruire, `python scripts/check_runtime.py`, compilation (`devrun.py --norun`), parcours A/B.

Ne jamais restaurer l'état complet d'un ancien commit sur le HEAD courant : RF01 accepté, les lots postérieurs et les
consommateurs partagés seraient perdus. Le build accepté reste la référence immédiate quoi qu'il arrive.
