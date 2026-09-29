# RF2-ARSENAL — le banc d'essai, pour Astra

Complète le contrat (`CONTRAT.md` v2, §3, §8 et §9). Le banc : branche `bench/rf2-arsenal` du dépôt
`C:\PROJECTS\RF2_UZDOOM`, dossiers `bench/arsenal/` et `scripts/arsenal/`. Il lit ta livraison W03/W04 V01 telle
quelle ; les armes que tu n'as pas encore livrées y tournent sur des dessins et des bips provisoires.

## Ce que le banc attend de ta livraison

Par arme, un **fichier d'animation JSON** (`"schema": "rf2-bench-animation/1"`) dans ton dossier de lot, comme
`animation.rapid.json` et `animation.mr73.json` de V01. Format complet et tableau des `kind` (`pump`, `revolver`,
`magazine`, `saw`, `melee`) : `bench/arsenal/README.md` ; modèles : `bench/arsenal/placeholder/*.json`.

- Une entrée par image affichée : `image`, `tics` (entier ≥ 1), au besoin `event`, `offset` [x, y] (recul ; repos
  0,32), `ready_point` (changement d'arme permis), et pour le revolver `chamber_pose`, `hand_stage`.
- `files` : image → chemin dans ta livraison ; le manifeste donne le `target_relpath` où le banc range chaque fichier.
- `sounds` : `événement → [fichiers WAV 16 bits 48 kHz mono]` ; plusieurs fichiers = tirage aléatoire.
- Répliques : un JSON avec une clé `voices` (format dans le README).

Le constructeur refuse une animation à laquelle manque un événement nécessaire, ou dont un nom de sprite ou un chemin
entre en collision avec la base, le moteur ou l'IWAD, et il dit pourquoi.

## Vérifier toi-même dans le moteur

Depuis ton worktree, sans rien écrire dans celui d'Opus :

```
git checkout bench/rf2-arsenal -- bench/arsenal scripts/arsenal     (ajoute ces deux dossiers)
python scripts/arsenal/build_bench.py --delivery incoming/astra/RF2_ARSENAL/<lot> ^
    --base C:\PROJECTS\RF2_UZDOOM\dist\arsenal\base\RF2_BASE_src_23773520f797.pk3 --scratch <dossier>\essai.pk3
python scripts/arsenal/bench_probe.py --base <même base> --module <dossier>\essai.pk3
python scripts/arsenal/next_probe.py  --base <même base> --module <dossier>\essai.pk3
python scripts/arsenal/bench_shots.py --base <même base> --module <dossier>\essai.pk3 --out <dossier>\captures
```

Les sondes vérifient compteurs, transitions, contacts et sons de boucle (PASS/FAIL). Les captures portent le tic de
jeu qu'elles montrent (bande en haut à gauche, `scripts/arsenal/ticcode.py`) : classe-les par ce tic, pas par
l'ordre des fichiers. Aucun script ne juge le rendu ni le son : dis ce que tu as regardé et écouté, et avec quoi.
