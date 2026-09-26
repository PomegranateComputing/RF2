"""Rebuild the candidate FAL from its native editable layers, inside this batch only.

    python -B incoming/astra/RF01_P0_FAL/source/build_batch.py
Dependencies: Pillow, numpy. No image-generation calls or external input required.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin, ImageFilter
import rigcomp as rc
import fal_native as fal

BATCH = Path(__file__).resolve().parent
SOURCE = BATCH
OUT = BATCH / 'reexport'
EVIDENCE = BATCH / 'evidence'

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def font(size):
    try:
        return ImageFont.truetype('arial.ttf', size)
    except OSError:
        return ImageFont.load_default(size=size)

def png(image, path, offset):
    meta = PngImagePlugin.PngInfo()
    meta.add(b'grAb', struct.pack('>ii', *offset))
    image.save(path, pnginfo=meta)

def sheet(files, background, name):
    cols, tw, th = 4, 384, 286
    out = Image.new('RGB', (cols * tw, 52 + math.ceil(len(files) / cols) * th), background)
    d = ImageDraw.Draw(out)
    fg = '#ece9df' if sum(background) < 400 else '#222b30'
    d.text((14, 12), 'RF01 / FAL - candidats / alpha droit - ' + name, font=font(20), fill=fg)
    for i, (path, label) in enumerate(files):
        with Image.open(path) as im:
            thumb = im.convert('RGBA').resize((tw, 256), Image.Resampling.LANCZOS)
        x, y = (i % cols) * tw, 52 + (i // cols) * th
        tile = Image.new('RGBA', thumb.size, background + (255,))
        tile.alpha_composite(thumb)
        out.paste(tile.convert('RGB'), (x, y))
        d.text((x + 8, y + 260), label, font=font(14), fill=fg)
    out.save(EVIDENCE / f'RF2_FAL_ALL_{name.upper()}.png')

def repair_grasp(layers):
    # Both inputs are native editable layers. A single donor sleeve replaces the
    # repeated cuff/skin strips in the legacy grasp layer. The hand stays intact.
    donor = rc.transform_layer(layers['arm_l'], scale=0.80,
                               tx=150, ty=187, pivot=(1060, 807))
    yy, xx = np.mgrid[:donor.shape[0], :donor.shape[1]]
    axis = (-0.515, 0.857)
    along = (xx - 1210) * axis[0] + (yy - 994) * axis[1]
    blend = np.clip((along - 20) / 35, 0, 1).astype(np.float32)[..., None]
    repaired = layers['arm_l2'] * (1 - blend) + donor * blend
    layers['arm_l2'] = repaired
    rc.save_rgba(rc.unpremul(repaired), SOURCE / 'arm_l2_continuous.png')
    return {'donor': 'layers/arm_l.png', 'recipient': 'layers/arm_l2.png',
            'donor_scale': 0.8, 'donor_pivot': [1060, 807], 'translation': [150, 187],
            'seam_axis_origin': [1210, 994], 'seam_axis': list(axis),
            'seam_blend_interval': [20, 55], 'hand_pose': 'legacy grasp, unchanged above seam'}

def seal_layer(layer, overlap=False):
    """Seal narrow native mask seams using neighboring foreground color only.

    This changes layer masks, not camera or animation poses. Filling uses a
    premultiplied neighborhood so no black matte is introduced at transparent edges.
    """
    a = layer[..., 3]
    mask = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    closed = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    if overlap:
        closed = closed.filter(ImageFilter.MaxFilter(3))
    target = np.maximum(a, np.asarray(closed, dtype=np.float32) / 255)
    delta = target - a
    summed = np.zeros_like(layer)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            summed += np.roll(np.roll(layer, dy, axis=0), dx, axis=1)
    color = summed[..., :3] / np.maximum(summed[..., 3:4], 1e-6)
    result = layer.copy()
    result[..., :3] += color * delta[..., None]
    result[..., 3] = target
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    layers = {p.stem: rc.premul(rc.load_rgba(p)) for p in sorted((SOURCE / 'layers').glob('*.png'))
              if not p.stem.startswith('_')}
    for name in ('arm_l', 'arm_r', 'body', 'housing'):
        layers[name] = seal_layer(layers[name], overlap=name in ('body', 'housing'))
    repair = repair_grasp(layers)
    manifest = {'schema': 1, 'batch_id': BATCH.name, 'created_by': 'Codex Astra',
                'status': 'OWNER_REVIEW_REQUIRED', 'level': 'RF01',
                'summary': 'FAL legacy stable master; continuous reload sleeve; separate flash; editable native source.',
                'uncertainties': ['No owner approval inferred from legacy filenames.',
                    'Legacy brief says classic 50.00; exact hardware variant unverified; no new markings.',
                    'Two rigid hand poses; finger articulation and charging contact need review.',
                    'Rebuilt occluded surfaces from legacy, not mechanically certified.',
                    'Offsets, timing and aliases proposed only; not tested in RF01.'],
                'files': []}
    sequence, files, qa = [], [], []
    specs = fal.frame_specs()
    for i, (state, spec, tics, event) in enumerate(specs):
        # The fire body is deliberately flash-free. The flash uses the exact
        # same native group transform and canvas as the fire pose.
        spec = {**spec, 'flash': None}
        canvas = fal.compose(layers, spec)
        rgba = rc.unpremul(canvas)[fal.PAD_T:fal.PAD_T + fal.H0, fal.PAD_L:fal.PAD_L + fal.W0]
        array = (np.clip(rgba, 0, 1) * 255 + 0.5).astype(np.uint8)
        array[array[..., 3] == 0, :3] = 0
        name = f'RF2_{state}_A0.png'
        path = OUT / name
        png(Image.fromarray(array), path, (-700, -300))
        alias = f'RFLV{chr(65 + i)}0'
        sequence.append({'state': state, 'file': name, 'sprite_alias_proposal': alias,
                         'duration_tics_proposal': tics, 'legacy_event_reference': event,
                         'transforms': spec})
        files.append((path, f'{chr(65+i)} / ' + state.replace('FAL_', '')))
        qa.append({'file': name, 'alpha_bbox': list(Image.fromarray(array[..., 3]).getbbox()),
                   'transparent_pixels': int((array[..., 3] == 0).sum()),
                   'opaque_pixels': int((array[..., 3] == 255).sum())})
        manifest['files'].append(entry(path, alias, 'weapon_sprite', tics))
        print(name, flush=True)
    flash = rc.transform_layer(layers['flash'], **specs[1][1]['group'])
    arr = (np.clip(rc.unpremul(flash)[fal.PAD_T:fal.PAD_T+fal.H0, fal.PAD_L:fal.PAD_L+fal.W0], 0, 1)*255+0.5).astype(np.uint8)
    arr[arr[..., 3] == 0, :3] = 0
    flash_path = OUT / 'RF2_FAL_MUZZLE_FLASH_A0.png'
    png(Image.fromarray(arr), flash_path, (-700, -300))
    files.append((flash_path, 'FLASH / overlay sur FIRE uniquement'))
    manifest['files'].append(entry(flash_path, 'RFMZA0', 'weapon_flash', 2))
    ready = np.asarray(Image.open(files[0][0]))
    end = np.asarray(Image.open(files[19][0]))
    assert np.array_equal(ready, end), 'Reload must return exactly to the same ready pose'
    write_json(SOURCE / 'animation.json', {
        'canvas': [1536, 1024], 'alpha': 'straight RGBA', 'png_grAb': [-700, -300],
        'texture_scale_proposal': [6, 7.2], 'logical_dimensions': [256, 142.222222],
        'sprite_aliases_require_explicit_engine_mapping': True,
        'states': sequence, 'flash': {'file': flash_path.name, 'alias': 'RFMZA0', 'overlay_state': 'FAL_FIRE'},
        'empty_reload_tics': sum(s[2] for s in specs[4:]),
        'tactical_reload': 'Use reload 01..11 then 15..16, skip charging 12..14; Fable owns logic.',
        'sleeve_repair': repair, 'select_deselect': 'Use READY with engine vertical offset; no extra frames.',
        'sound_events': 'Legacy references only. No audio supplied or assumed to exist in baseline.'})
    write_json(BATCH / 'manifest.json', manifest)
    write_json(EVIDENCE / 'alpha_metrics.json', {'ready_equals_reload_end': True, 'frames': qa})
    sheet(files, (231, 230, 222), 'light')
    sheet(files, (24, 30, 35), 'dark')
    write_review(files)

def entry(path, alias, kind, tics):
    return {'file': path.relative_to(BATCH).as_posix(),
            'target_relpath': 'sprites/weapons/fal/' + path.name,
            'kind': kind, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size, 'width': 1536, 'height': 1024, 'format': 'PNG RGBA8',
            'source_method': 'Native layered legacy master, premultiplied transforms; reproducible source/build_batch.py',
            'license_or_origin': 'Original RF2 project assets. Pomegranate Interactive reserved rights; source/reference/LEGACY_LICENSE.md. Master generated by imagegen in legacy, no third-party game input recorded.',
            'confidence': 'medium', 'sprite_alias_proposal': alias, 'offset_pixels': [-700, -300],
            'duration_tics_proposal': tics,
            'notes': 'Candidate. Fixed camera/canvas; explicit sprite alias mapping required. Fable must validate scale, hands and animation in RF01.'}

def write_review(files):
    im = Image.open(files[6][0]).convert('RGBA')
    before = Image.open(SOURCE / 'reference/reload_before.png').convert('RGBA')
    board = Image.new('RGB', (1536, 1080), '#e7e6de')
    d = ImageDraw.Draw(board)
    for i, (picture, label) in enumerate(((before, 'LEGACY / manche repetee'), (im, 'CANDIDAT / manche continue'))):
        tile = Image.new('RGBA', (768, 512), '#e7e6de')
        tile.alpha_composite(picture.resize((768, 512), Image.Resampling.LANCZOS))
        board.paste(tile.convert('RGB'), (768*i, 32))
        d.text((768*i+10, 8), label, fill='#202930', font=font(18))
    d.text((10, 558), 'Gros plan candidat / alpha sur fond clair et sombre', fill='#202930', font=font(18))
    crop = im.crop((100, 580, 850, 1024))
    for i, bg in enumerate(('#e7e6de', '#181e23')):
        tile = Image.new('RGBA', crop.size, bg)
        tile.alpha_composite(crop)
        board.paste(tile.convert('RGB'), (i*768+8, 600))
    board.save(EVIDENCE / 'RF2_FAL_SLEEVE_REPAIR.png')

if __name__ == '__main__':
    main()
