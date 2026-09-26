"""Strict delivery checks, supplementary to scripts/validate_astra_batch.py.

Run with a batch path. Writes only that batch's evidence/artifact_validation.json.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import struct
import sys
import zlib
import numpy as np
from PIL import Image

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def chunks(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos, result = 8, {}
    while pos < len(data):
        n = struct.unpack('>I', data[pos:pos+4])[0]
        kind, payload = data[pos+4:pos+8], data[pos+8:pos+8+n]
        crc = struct.unpack('>I', data[pos+8+n:pos+12+n])[0]
        assert zlib.crc32(kind + payload) & 0xffffffff == crc, 'PNG CRC mismatch'
        result[kind] = payload
        pos += 12 + n
    return result

def main():
    batch = Path(sys.argv[1]).resolve()
    root = batch.parents[2]
    data = json.loads((batch / 'manifest.json').read_text(encoding='utf-8'))
    errors, details = [], []
    def check(value, msg):
        if not value:
            errors.append(msg)
    check(data['status'] in ('ASTRA_GENERATED', 'OWNER_REVIEW_REQUIRED'), 'status outside ASTRA contract')
    targets, aliases, listed = set(), set(), set()
    required = ('file', 'target_relpath', 'kind', 'sha256', 'bytes', 'format', 'source_method', 'license_or_origin', 'confidence', 'notes')
    groups = {}
    for item in data['files']:
        rel = item['file']
        check(all(k in item and item[k] not in ('', None) for k in required), rel + ': missing required field')
        path = (batch / rel).resolve()
        check(path.is_relative_to(batch), rel + ': escapes batch')
        if not path.is_relative_to(batch) or not path.is_file():
            errors.append(rel + ': missing/invalid file')
            continue
        target = PurePosixPath(item['target_relpath'])
        check(not target.is_absolute() and '..' not in target.parts and ':' not in str(target), rel + ': unsafe target')
        check(str(target).startswith('sprites/'), rel + ': wrong target namespace')
        check(str(target).lower() not in targets, rel + ': duplicate target')
        targets.add(str(target).lower())
        check(rel not in listed, rel + ': duplicate file')
        listed.add(rel)
        check(path.name.startswith('RF2_') and ' ' not in path.name, rel + ': naming')
        check(sha(path) == item['sha256'], rel + ': sha256')
        check(path.stat().st_size == item['bytes'], rel + ': bytes')
        alias = item.get('sprite_alias_proposal')
        check(alias is not None and len(alias) == 6 and alias not in aliases, rel + ': sprite alias')
        aliases.add(alias)
        try:
            metadata = chunks(path)
            grab = list(struct.unpack('>ii', metadata[b'grAb']))
            with Image.open(path) as im:
                im.load()
                check(im.mode == 'RGBA', rel + ': not RGBA')
                check(list(im.size) == [item['width'], item['height']], rel + ': dimensions')
                arr = np.asarray(im)
            check(grab == item['offset_pixels'], rel + ': grAb mismatch')
            alpha = arr[..., 3]
            check(alpha.min() == 0 and alpha.max() == 255, rel + ': real alpha/opaque interior missing')
            check(not np.any(arr[alpha == 0, :3]), rel + ': hidden matte RGB')
            ys, xs = np.nonzero(alpha >= 128)
            metrics = {'file': rel, 'offset': grab, 'bbox_alpha128': [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]}
            if item['kind'] == 'enemy_sprite':
                # Native render ground plane refers to the bottom opaque row.
                floor_delta = int(ys.max()) - grab[1]
                check(abs(floor_delta) <= 2, rel + ': feet not anchored')
                check(xs.min() > 0 and ys.min() > 0 and xs.max() < arr.shape[1]-1 and ys.max() < arr.shape[0]-1, rel + ': clipped canvas')
                family = item['family_id']
                groups.setdefault(family, {'canvases': set(), 'offsets': set(), 'states': {}})
                g = groups[family]
                g['canvases'].add((item['width'], item['height']))
                g['offsets'].add(tuple(grab))
                g['states'].setdefault(item['state'], []).append(item['rotation'])
                metrics['floor_delta_px'] = floor_delta
            details.append(metrics)
        except Exception as exc:
            errors.append(rel + ': ' + repr(exc))
    actual = {p.relative_to(batch).as_posix() for p in (batch / 'runtime').rglob('*') if p.is_file()}
    check(actual == listed, 'runtime inventory differs from manifest')
    for family, group in groups.items():
        check(len(group['canvases']) == 1 and len(group['offsets']) == 1, family + ': unstable canvas/origin')
        for state, rotations in group['states'].items():
            check(sorted(rotations) == list(range(1, 9)), family + '/' + state + ': incomplete rotations')
    provenance = batch / 'source/provenance.json'
    if provenance.exists():
        for record in json.loads(provenance.read_text(encoding='utf-8')):
            check(sha(batch / record['copy']) == record['sha256'], record['copy'] + ': archived source altered')
            original = root / record['original']
            if original.is_file():
                check(sha(original) == record['sha256'], record['original'] + ': legacy changed')
    before_path = batch / 'evidence/protected_before.json'
    protected = {}
    if before_path.exists():
        before = json.loads(before_path.read_text(encoding='utf-8'))
        for name in ('src', 'scripts', 'agent', 'campaign'):
            for path in sorted((root / name).rglob('*')):
                if path.is_file():
                    protected[path.relative_to(root).as_posix()] = sha(path)
        check(before == protected, 'protected files changed; inspect concurrent edits before attributing')
    report = {'status': 'PASS' if not errors else 'FAIL', 'runtime_files': len(listed),
              'checks': ['complete manifest', 'SHA-256 and bytes', 'PNG CRC', 'RGBA and alpha',
                         'unique targets and aliases', 'PNG grAb', 'rotation coverage and baseline where applicable',
                         'source provenance hashes', 'protected-tree hashes'],
              'protected_file_count': len(protected), 'errors': errors, 'frames': details,
              'runtime_engine_validation': 'NOT_RUN; Fable integration required',
              'visual_approval': 'NOT_GRANTED'}
    (batch / 'evidence/artifact_validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('ARTIFACT VALIDATION:', report['status'], f'({len(listed)} runtime files; {len(protected)} protected files)')
    for error in errors:
        print(error)
    return bool(errors)

if __name__ == '__main__':
    raise SystemExit(main())
