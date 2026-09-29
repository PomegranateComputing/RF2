#!/usr/bin/env python3
"""Record which Astra arsenal lot the bench consumes, after checking it file by file (nothing is copied or changed).

    python scripts/arsenal/import_astra_lot.py <lot folder> [--origin <frozen delivery folder>]

Every file listed in the lot's SHA256SUMS.txt is hashed (CRLF lists accepted); with --origin, the two sums lists must
be identical too (the lot is an exact copy of the frozen delivery). Writes art/rf2_arsenal_astra/IMPORT_<lot>.json:
paths, sums hashes, counts, unlisted files, and the files the bench reads (animation files and what they name).
An existing record is never overwritten.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def sums_of(folder):
    out = {}
    for line in (folder / 'SHA256SUMS.txt').read_bytes().decode('utf-8').splitlines():
        line = line.strip()
        if line:
            out[line[64:].strip().lstrip('*').replace('\\', '/')] = line[:64]
    return out


def bench_files(lot):
    """Files named by the lot's per-weapon animation files (what build_bench.py loads)."""
    used = set()
    for p in sorted(lot.glob('animation*.json')):
        a = json.loads(p.read_text(encoding='utf-8'))
        if not isinstance(a.get('sequences'), dict):
            continue
        used.add(p.name)
        used.update(a.get('files', {}).values())
        for variants in a.get('sounds', {}).values():
            used.update(variants)
    return sorted(used)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lot')
    ap.add_argument('--origin')
    a = ap.parse_args()
    lot = Path(a.lot).resolve()
    record_path = ROOT / 'art' / 'rf2_arsenal_astra' / f'IMPORT_{lot.name}.json'
    if record_path.exists():
        print(f'refus : {record_path} existe deja')
        return 1
    sums = sums_of(lot)
    bad = [rel for rel, h in sums.items() if not (lot / rel).is_file() or sha256(lot / rel) != h]
    present = {p.relative_to(lot).as_posix() for p in lot.rglob('*') if p.is_file()}
    unlisted = sorted(present - set(sums) - {'SHA256SUMS.txt'})
    same_as_origin = None
    if a.origin:
        same_as_origin = sums_of(Path(a.origin)) == sums
    used = bench_files(lot)
    missing = [u for u in used if u not in sums]
    ok = not bad and not missing and same_as_origin is not False
    record = dict(lot=lot.name, checked=time.strftime('%Y-%m-%d %H:%M'), folder=str(lot), origin=a.origin,
                  sums_sha256=sha256(lot / 'SHA256SUMS.txt'), files_listed=len(sums), files_mismatched=bad,
                  unlisted=unlisted, same_sums_as_origin=same_as_origin, result='conforme' if ok else 'NON CONFORME',
                  bench_reads=[dict(file=u, sha256=sums.get(u)) for u in used], bench_reads_unlisted=missing)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_bytes(json.dumps(record, indent=2, ensure_ascii=False).encode('utf-8'))
    print(f"{lot.name} : {len(sums)} fichiers listes, {len(bad)} ecart(s), {len(unlisted)} non listes, "
          f"meme liste que l'origine : {same_as_origin} ; le banc lit {len(used)} fichiers -> {record['result']}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
