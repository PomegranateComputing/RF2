# RF2-ART-02 — trois familles RF01, matières et finition

Candidate **OWNER_REVIEW_REQUIRED**, basée sur `5b53d9eaaaf088f49ae98f667fc1d575779dc74e`, conformément au contrat Opus archivé dans `source/contract/`. L'acceptation RF01 du 27 septembre concerne la référence ; elle ne vaut pas acceptation de cette nouvelle passe.

## Périmètre livré

320 sprites : 104 ORDY, 120 BRCD, 96 PREG, tous les états et les huit rotations du contrat. Trois skins de cadavres, sur les OBJ et UV existants. La liasse PRGS reste celle acceptée. Import fichier par fichier depuis `runtime/`, avec contrôle de `base_sha256` dans `manifest.json`.

Tunique gris pierre et veste bleu charbon plus construites ; manches raccordées au tissu du torse ; plis et usure localisés ; peau des membres raccordée au master de visage ; cuir, papier et reliures aux valeurs plus sourdes. Le même rig articulé produit toutes les rotations et poses. Aucun changement d'identité, de géométrie, de pose, d'échelle, de cadre, de pivot, de gameplay, d'arme, de son ou de carte.

Les PNG gardent **exactement** les dimensions, le grAb et le canal alpha de la base. Échelle 0,18, 5 pixels/unité source, précompensation verticale 1,2. Les cadavres gardent les maillages, MODELDEF, emprises et RFBody de la référence. Aucun patch runtime nécessaire pour ce lot.

## Reproduire

Depuis la racine du worktree :

```
python incoming/astra/RF2_ART_02/source/export.py --workers 4
python incoming/astra/RF2_ART_02/source/review.py
python incoming/astra/RF2_ART_02/source/validate_delivery.py
python scripts/validate_astra_batch.py incoming/astra/RF2_ART_02
```

Python 3 et versions dans `source/requirements-lock.txt`. Tous les masters et scripts nécessaires aux images sont joints. `--resume` est réservé à un rendu interrompu dont les sources n'ont pas changé. La génération du master par l'outil intégré image_gen n'est pas déterministe ; le master figé, son prompt exact (`source/IMAGEGEN_PROMPT.txt`) et le réexport contrôlé sont conservés.

## Revue

Ouvrir `evidence/index.html`. Avant/après dans RF01, avec mêmes caméras et réglages, contrôle des corps sur sept supports par famille (quatre côtés et plongée), clip de combat réel muet. Les planches de rotations et les animations WebP sont des contrôles d'exports ; leur cadence de présentation n'est pas celle du gameplay.

`evidence/validation.json` vérifie la couverture, alpha, dimensions, grAb et les fichiers protégés du PK3. `evidence/corpse_comparison.json` compare exactement la télémétrie des 21 placements à celle de la référence. Les captures et la vidéo sont rattachées au hash du paquet réellement lancé.

Limites : pas de nouveau parcours intégral de campagne, pas d'audition (ce lot n'a aucun changement audio), aucune approbation propriétaire. Les limites géométriques/UV des cadavres rigides existants, notamment les plis étirés sur les côtés et les appuis complexes, demeurent ; leur système de pose n'a pas été reconstruit.

## Sources et droits

Rigs et pipeline : sources RF2 acceptées sous `art/rf2_art_01/enemies/`, copiées dans `source/enemies/`. Atlas de matières : édition par l'outil intégré image_gen à partir de l'atlas RF2, sans ressource tierce ajoutée. Crédit projet : Nameless / Pomegranate Interactive. La provenance du rig et de l'atlas de départ demeure celle de RF2-ART-01.

Le build de revue local sous `review/` contient les ressources de base nécessaires au test, dont les cartes existantes. Il est exclu du paquet d'assets à importer. Opus reste l'intégrateur du dépôt actif.

## Complément de canon

Le complément propriétaire du 27 septembre est suivi dans le lot frère `RF2_CANON_01`. Ce lot ne couvre pas CAN-001 à CAN-004 ; les ennemis acceptés ne sont pas réinterprétés comme le couple du roman.
