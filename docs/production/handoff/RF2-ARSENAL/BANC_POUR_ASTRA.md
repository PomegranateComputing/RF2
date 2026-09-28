# RF2-ARSENAL — le banc d'essai, pour Astra

Complète le contrat (`CONTRAT.md`, §3 et §7). Le banc existe : branche `bench/rf2-arsenal` du dépôt
`C:\PROJECTS\RF2_UZDOOM` (commit `937a40d`), dossiers `bench/arsenal/` et `scripts/arsenal/`. Tant que ta livraison
n'est pas là, il tourne sur des dessins et des bips provisoires.

## Ce que le banc attend de ta livraison

Par arme, un **fichier d'animation JSON** (`"schema": "rf2-bench-animation/1"`, `"weapon": "W03"` ou `"W04"`) dans
ton dossier de lot, avec les chemins d'images et de sons relatifs à ce fichier ou au dossier. Modèles complets :
`bench/arsenal/placeholder/W03_rapid.json` et `W04_mr73.json` ; tableau des clés : `bench/arsenal/README.md`.

- Une entrée par image affichée : `image`, `tics` (entier ≥ 1), au besoin `event`, `offset` [x, y] (recul ; repos
  0,32), `ready_point` (changement d'arme permis), `chambers` (MR73 : couches visibles).
- Séquences Rapid : `ready`, `fire` (un seul `shot`), `pump` (`pump_back` puis `pump_fwd`), `dry`, `reload_start`,
  `reload_shell` (un `shell_in` : +1 au tube à cette image), `reload_end`.
- Séquences MR73 : `ready`, `fire` (un seul `shot`), `dry`, `reload_open`, `reload_eject` (un `eject`),
  `reload_round` (un `round_in` : +1 à cette image), `reload_close` ; `chamber_layers` : six images, une cartouche
  chacune, même toile que la pose barillet ouvert, qui est la même dans toutes les images marquées `chambers`.
- `capacity` : Rapid `tube` et `chamber` (**ta valeur sourcée remplace le 5 + 1 provisoire**) ; MR73 `cylinder` 6.
- `sounds` : `événement → [fichiers WAV 16 bits 48 kHz mono]` ; plusieurs fichiers = tirage aléatoire.

Le script refuse une animation à laquelle manque un événement nécessaire, et le dit.

## Vérifier toi-même dans le moteur

Depuis ton worktree, sans rien écrire dans celui d'Opus :

```
git checkout bench/rf2-arsenal -- bench/arsenal scripts/arsenal     (ajoute ces deux dossiers)
python scripts/arsenal/build_bench.py --delivery incoming/astra/RF2_ARSENAL/<lot> ^
    --base C:\PROJECTS\RF2_UZDOOM\dist\arsenal\base\RF2_BASE_src_23773520f797.pk3 --scratch <dossier>\essai.pk3
python scripts/arsenal/bench_probe.py --base <même base> --module <dossier>\essai.pk3
python scripts/arsenal/bench_shots.py --base <même base> --module <dossier>\essai.pk3 --out <dossier>\captures
```

La sonde vérifie compteurs et transitions (PASS/FAIL) ; les captures montrent 17 instants en 16:9, 21:9 et 4:3.
Aucun script ne juge le rendu ni le son : dis ce que tu as regardé et écouté, et avec quoi.
