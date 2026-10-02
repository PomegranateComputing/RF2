# Le manifeste que l'importateur lit — schéma 1

Le gabarit du pack (`gabarits/LOT_ARTISTIQUE_TEMPLATE.json`, clés `assets`, `source_relpath`, `delivered_sha256`) **n'est
pas lu par l'importateur** : c'est une fiche de spécification. L'importateur (`scripts/import_astra_lot.py`) lit ceci :

```json
{
  "schema": 1,
  "batch_id": "E01_ORDY_V05",
  "status": "candidate_pour_revue_moteur",
  "files": [
    {
      "file": "runtime/sprites/enemies/ORDYE3.png",
      "sha256": "<empreinte du fichier livré>",
      "target_relpath": "sprites/enemies/ORDYE3.png",
      "base_sha256": "<empreinte du fichier en place quand tu as commencé>"
    }
  ]
}
```

| Clé | Règle |
|---|---|
| `schema` | `1` (un lot d'armes pour le banc a un autre schéma et ne passe pas par ici) |
| `batch_id` | lot et version, unique ; sert de nom au relevé d'import |
| `files[].file` | chemin du fichier livré, relatif à la racine du lot |
| `files[].sha256` | empreinte du fichier livré : l'import est refusé si elle ne correspond pas |
| `files[].target_relpath` | destination sous `src/` ; jamais une carte (`maps/`), du code (`zscript/`) ni une définition à la racine de `src/` (`TEXTURES.*`, `MAPINFO`…) : ces fichiers-là se proposent en texte dans `POUR_OPUS.md` |
| `files[].base_sha256` | empreinte de la destination au moment où tu l'as prise comme base ; **si la destination a changé depuis, l'import est refusé** et nous rapprochons les versions. Absent pour un fichier neuf |
| autres clés | libres (`kind`, `notes`, dimensions…) : conservées dans le relevé, ignorées par l'import |

## Partir des manifestes de base

`CONTRATS/<LOT>_MANIFESTE_BASE.json` contient, pour chaque fichier du lot en jeu, `target_relpath` et `base_sha256` déjà
remplis (relevés au commit indiqué dans `base_commit`). Garder les entrées des fichiers livrés, supprimer les autres,
renseigner `batch_id`, puis :

```
python C:\PROJECTS\RF2_UZDOOM\scripts\production\astra_lot_check.py <dossier du lot> --write
```

`--write` calcule les `sha256` laissés à `A_CALCULER…` et écrit `SHA256SUMS.txt` en LF. Sans `--write`, l'outil ne fait
que contrôler : fichiers présents et conformes, destination permise, base inchangée, **même taille en pixels que la
base** (ou `"resize": true` dans l'entrée, convenu avec moi), chunk `grAb` présent quand la base en a un, transparence
conservée. Il ne copie rien et n'écrit pas hors du lot. Copie de l'outil : `outils/astra_lot_check.py` (elle lit
`src/` du dépôt : la lancer depuis le dépôt).

## Ce qui se passe à l'import

`python scripts/import_astra_lot.py <lot> --record-dir <dossier de relevés> [--dry-run]` : copie fichier par fichier,
écrit `docs/production/handoff/<dossier>/IMPORT_<batch_id>.json` (empreintes avant / après, état de chaque fichier).
Les fichiers importés sont ensuite listés comme « livrés » dans les générateurs procéduraux : aucun build ne les
redessine. Puis revue dans le moteur, avant / après aux mêmes caméras, et retour écrit.
