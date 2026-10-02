#!/usr/bin/env python3
"""Plans, sections and dimension tables of the kit maps, drawn from the map sources themselves (scripts/mapkit): what
the art producer needs before drawing large surfaces (order of 02/10: plan, coupes, dimensions avant les façades).

A plan: every 16-unit cell coloured by what it is (open ground by its floor height, closed mass by its top, roofed
room, water/basin), a 256-unit grid with coordinates, the named areas of the map and a scale bar; north is up.
A section: the floor and ceiling of the cells along a straight line (east-west or north-south), masses filled, sky
left open, slabs (decks, lintels) drawn, heights written at each change.
The dimension table: the named areas with their footprint, floor and clear height.

Usage: python scripts/production/map_plans.py <out dir>
Maps and section lines are listed in MAPS below. 1 unit = about 2.5 cm (a 56-unit player is 1.75 m tall here: 32 u/m).
"""
import contextlib, io, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'mapkit'))
U = 16
UPM = 32.0          # units per metre (player 56 u = 1.75 m)


def font(size):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)
    except OSError:
        return ImageFont.load_default()


def load(name):
    argv = sys.argv
    sys.argv = [name + '.py']
    with contextlib.redirect_stdout(io.StringIO()):
        mod = __import__(name)
    sys.argv = argv
    return mod


def cell_colour(c):
    if c.ceil <= c.floor:                                   # a closed mass: brown, lighter when higher
        v = max(0, min(255, 70 + c.ceil // 3))
        return (v, int(v * 0.72), int(v * 0.55))
    if c.ctex == 'F_SKY1':                                  # open ground: green-grey by floor height
        v = max(0, min(120, (c.floor + 96) // 3))
        if 'EAU' in c.ftex or 'FLAQ' in c.ftex or 'MER' in c.ftex:
            return (60, 90, 130)
        return (150 + v // 2, 168 + v // 3, 140 + v // 2)
    v = max(0, min(100, (c.floor + 256) // 5))              # a roofed room: blue-grey
    return (120 + v, 140 + v, 190 + v // 2)


def plan(m, areas, title, out, scale=0.5, labels=()):
    xs = [p[0] for p in m.cells]
    ys = [p[1] for p in m.cells]
    x0, x1, y0, y1 = min(xs) * U - 64, (max(xs) + 1) * U + 64, min(ys) * U - 64, (max(ys) + 1) * U + 64
    W, H = int((x1 - x0) * scale), int((y1 - y0) * scale)
    img = Image.new('RGB', (W + 20, H + 90), (22, 22, 24))
    d = ImageDraw.Draw(img)
    px = lambda x: 10 + (x - x0) * scale
    py = lambda y: 50 + (y1 - y) * scale
    for (cx, cy), c in m.cells.items():
        d.rectangle([px(cx * U), py(cy * U + U), px(cx * U + U) - 1, py(cy * U) - 1], fill=cell_colour(c))
        if c.slabs:
            d.rectangle([px(cx * U) + 2, py(cy * U + U) + 2, px(cx * U + U) - 3, py(cy * U) - 3], outline=(240, 220, 120))
        if c.role == 'door':
            d.rectangle([px(cx * U), py(cy * U + U), px(cx * U + U) - 1, py(cy * U) - 1], fill=(220, 60, 50))
    f, fs = font(15), font(12)
    for gx in range((x0 // 256) * 256, x1, 256):
        d.line([(px(gx), 50), (px(gx), 50 + H)], fill=(0, 0, 0), width=1)
        d.text((px(gx) + 2, 52), str(gx), font=fs, fill=(255, 255, 255))
    for gy in range((y0 // 256) * 256, y1, 256):
        d.line([(10, py(gy)), (10 + W, py(gy))], fill=(0, 0, 0), width=1)
        d.text((12, py(gy) - 14), str(gy), font=fs, fill=(255, 255, 255))
    for name, (ax0, ay0, ax1, ay1) in areas.items():
        d.rectangle([px(ax0), py(ay1), px(ax1), py(ay0)], outline=(255, 255, 255), width=2)
        d.text((px(ax0) + 4, py(ay1) + 3), name, font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    for (lx, ly, text) in labels:
        d.text((px(lx), py(ly)), text, font=f, fill=(255, 240, 150), stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((10, 10), title, font=font(22), fill=(240, 240, 240))
    bar = 320 * scale                                       # 320 u = 10 m
    d.line([(10, H + 70), (10 + bar, H + 70)], fill=(255, 255, 255), width=4)
    d.text((16 + bar, H + 60), '320 u = 10 m ; grille 256 u = 8 m ; nord en haut ; rouge = porte, cadre jaune = dalle (pont, linteau, toit)',
           font=fs, fill=(230, 230, 230))
    img.save(out, quality=90)


def section(m, axis, coord, lo, hi, title, out, zmin=None, zmax=None, scale=0.75):
    """axis 'x': the line y = coord from x = lo to hi (seen from the south); axis 'y': the line x = coord (seen from the east)."""
    cols = []
    for k in range(lo // U, hi // U):
        p = (k, coord // U) if axis == 'x' else (coord // U, k)
        cols.append(m.cells.get(p))
    zs = [z for c in cols if c for z in (c.floor, c.ceil if c.ctex != 'F_SKY1' or c.ceil <= c.floor else c.floor)]
    zmin = min(zs) - 48 if zmin is None else zmin
    zmax = max(zs) + 96 if zmax is None else zmax
    W, H = int((hi - lo) * scale), int((zmax - zmin) * scale)
    img = Image.new('RGB', (W + 80, H + 110), (236, 234, 226))
    d = ImageDraw.Draw(img)
    px = lambda x: 60 + (x - lo) * scale
    pz = lambda z: 50 + (zmax - z) * scale
    f, fs = font(14), font(12)
    for z in range((zmin // 64) * 64, zmax, 64):
        d.line([(60, pz(z)), (60 + W, pz(z))], fill=(205, 203, 196))
        d.text((8, pz(z) - 7), f'{z:+d}', font=fs, fill=(90, 90, 90))
    last = None
    for i, c in enumerate(cols):
        xa, xb = px(lo // U * U + i * U), px(lo // U * U + (i + 1) * U)
        if c is None:
            d.rectangle([xa, 50, xb, 50 + H], fill=(60, 58, 54))
            last = None
            continue
        d.rectangle([xa, pz(c.floor), xb, 50 + H], fill=(96, 84, 70))                     # the ground under the floor
        if c.ceil <= c.floor:
            d.rectangle([xa, pz(c.ceil), xb, 50 + H], fill=(96, 84, 70))                  # a closed mass
        elif c.ctex != 'F_SKY1':
            d.rectangle([xa, 50, xb, pz(c.ceil)], fill=(96, 84, 70))                      # the mass above a roofed room
            d.rectangle([xa, pz(c.ceil), xb, pz(c.floor)], fill=(250, 248, 240))
        for (z0, z1, *_) in c.slabs:
            d.rectangle([xa, pz(z1), xb, pz(z0)], fill=(150, 120, 60))
        key = (c.floor, c.ceil if c.ctex != 'F_SKY1' else 'ciel')
        if key != last:
            top = c.ceil if c.ceil <= c.floor else c.floor
            d.text((xa + 1, pz(top) - 15), f'{top}', font=fs, fill=(170, 30, 20))
            if c.ceil > c.floor and c.ctex != 'F_SKY1':
                d.text((xa + 1, pz(c.ceil) + 1), f'{c.ceil}', font=fs, fill=(20, 60, 170))
            last = key
    for x in range((lo // 256) * 256, hi + 1, 256):
        if lo <= x <= hi:
            d.line([(px(x), 50 + H), (px(x), 58 + H)], fill=(0, 0, 0))
            d.text((px(x) - 12, 60 + H), str(x), font=fs, fill=(0, 0, 0))
    d.text((10, 8), title, font=font(18), fill=(20, 20, 20))
    d.text((10, 84 + H), ("coupe d'ouest en est" if axis == 'x' else 'coupe du sud au nord') + ' ; hauteurs en unites (rouge : sol ou sommet de masse ; bleu : plafond) ; '
           '32 u = 1 m ; brun clair = dalle', font=fs, fill=(40, 40, 40))
    img.save(out, quality=90)


def table(m, areas, out):
    """Named areas: footprint, the floor most of the area stands at, its clear height, the other floors found there."""
    import collections
    lines = ['| Zone | x0, y0 → x1, y1 (u) | Emprise (u) | Emprise (m) | Sol principal (u) | Hauteur libre | Autres niveaux (u) |', '|---|---|---|---|---|---|---|']
    for name, (x0, y0, x1, y1) in areas.items():
        cs = [c for (cx, cy), c in m.cells.items() if x0 <= cx * U < x1 and y0 <= cy * U < y1]
        open_ = [c for c in cs if c.ceil > c.floor]
        if open_:
            floor = collections.Counter(c.floor for c in open_).most_common(1)[0][0]
            hs = collections.Counter('ciel' if c.ctex == 'F_SKY1' else str(c.ceil - c.floor) for c in open_ if c.floor == floor)
            height = hs.most_common(1)[0][0]
            others = sorted({c.floor for c in open_} - {floor})
        else:
            floor, height, others = sorted({c.ceil for c in cs})[-1], 'masse fermée', []
        lines.append(f"| {name} | {x0}, {y0} → {x1}, {y1} | {x1 - x0} × {y1 - y0} | {(x1 - x0) / UPM:.1f} × {(y1 - y0) / UPM:.1f} | "
                     f"{floor} | {height} | {', '.join(str(f) for f in others[:8])} |")
    Path(out).write_text('\n'.join(lines) + '\n', encoding='utf-8')


def luna_areas():
    import luna_park as lp
    a = dict(ESPLANADE=lp.ESP, BASSIN=lp.BAS, RAMPE=lp.CHUTE, TOUR=lp.TOWER, QUAI=lp.QUAI, SALLE=lp.HALLB, MARQUISE=lp.MARQ,
             RUELLE=lp.LANE_BOX, AVANT_COUR=lp.FORE_BOX, GUERITE=lp.HUT, KIOSQUE=lp.BANDSTAND, MANEGE=lp.CAROUSEL, LOGE=lp.ORCH,
             SERVICE=lp.SERVICE)
    a['CHEMIN DE SERVICE'] = (lp.SVC_X0, 0, lp.SVC_X1, 2336)
    a['COULISSE BROOKLYN'] = (lp.CORR_X0, lp.BROOKLYN[0] - 320, lp.CORR_X1, lp.BROOKLYN[1])
    return a


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    import luna_park as lp
    rf04, rf05, rf06 = load('rf04'), load('rf05'), load('rf06')
    areas = luna_areas()
    plan(rf04.m, areas, 'RF04 - Luna Park, plan (reconstruction jouable, pas un releve) - etat du 02/10/2026', out / 'RF04_plan.png')
    plan(rf05.m, areas, 'RF05 - le meme parc et la sous-station au nord (sous-sol a -192) - etat du 02/10/2026', out / 'RF05_plan.png')
    plan(rf06.m, {}, 'RF06 - le couloir - etat du 02/10/2026', out / 'RF06_plan.png', scale=0.6)
    table(rf04.m, areas, out / 'RF04_RF05_DIMENSIONS.md')
    by = (lp.BAS[1] + lp.BAS[3]) // 2
    section(rf04.m, 'x', by // U * U + 8, 0, 1936, f'RF04 coupe A : bassin et quai, ligne y = {by}', out / 'RF04_coupe_A_bassin_quai.png', zmin=-160, zmax=560)
    section(rf04.m, 'y', (lp.BAS[0] + lp.BAS[2]) // 2 // U * U + 8, 0, 2400, f'RF04 coupe B : portes, bassin, rampe, tour, ruelle, ligne x = {(lp.BAS[0] + lp.BAS[2]) // 2}',
            out / 'RF04_coupe_B_sud_nord.png', zmin=-160, zmax=560)
    section(rf04.m, 'y', (lp.TRESTLE_XS[0] + lp.TRESTLE_XS[1]) // 2 // U * U + 8, 0, 2400, f'RF04 coupe C : grand huit (treteaux, quai, rampe de levage), ligne x = {(lp.TRESTLE_XS[0] + lp.TRESTLE_XS[1]) // 2}',
            out / 'RF04_coupe_C_grand_huit.png', zmin=-64, zmax=560)
    section(rf04.m, 'x', (lp.HALL_IN[1] + lp.HALL_IN[3]) // 2 // U * U + 8, 256, 1700, f'RF04 coupe D : salle de danse et aile est, ligne y = {(lp.HALL_IN[1] + lp.HALL_IN[3]) // 2}',
            out / 'RF04_coupe_D_salle.png', zmin=-64, zmax=560)
    section(rf05.m, 'y', 1568, 2200, 3100, 'RF05 coupe E : ruelle, escalier, palier, sous-station, ligne x = 1568', out / 'RF05_coupe_E_escalier_sous_station.png')
    section(rf05.m, 'x', 2848, 700, 2050, 'RF05 coupe F : galeries, sous-station, atelier, ligne y = 2848', out / 'RF05_coupe_F_sous_sol.png')
    # the volumes added on 02/10 (RF05: the feeders' gallery and its bay, the culvert; RF06: the valve chamber, the side loop)
    section(rf05.m, 'x', 3080, 1280, 2040, 'RF05 coupe G : transformateurs, escalier, galerie des departs (+96), ligne y = 3080',
            out / 'RF05_coupe_G_galerie_des_departs.png', scale=1.25)
    section(rf05.m, 'x', 2960, 1480, 1920, 'RF05 coupe H : la nef, la baie de la galerie sur la roue, ligne y = 2960', out / 'RF05_coupe_H_baie.png', scale=2.0)
    section(rf05.m, 'y', 1976, 2740, 3120, "RF05 coupe I : l'atelier et l'escalier qui y redescend, ligne x = 1976", out / 'RF05_coupe_I_atelier.png', scale=2.2)
    section(rf05.m, 'y', 1264, 2780, 3250, 'RF05 coupe J : le caniveau entre les deux galeries, ligne x = 1264', out / 'RF05_coupe_J_caniveau.png', scale=2.0)
    section(rf06.m, 'x', 1528, -16, 320, 'RF06 coupe K : la descente, la passerelle haute et la fosse des vannes, ligne y = 1528',
            out / 'RF06_coupe_K_chambre_des_vannes.png', zmin=-260, zmax=110, scale=2.5)
    section(rf06.m, 'y', 168, 1420, 1880, 'RF06 coupe L : passerelle haute, marches, passerelle basse, ligne x = 168',
            out / 'RF06_coupe_L_passerelles.png', zmin=-260, zmax=110, scale=2.0)
    section(rf06.m, 'y', 192, 1060, 1300, "RF06 coupe M : la boucle d'inspection de la salle des peaux, ligne x = 192",
            out / 'RF06_coupe_M_boucle.png', zmin=-140, zmax=110, scale=3.0)
    print('plans et coupes ->', out)


if __name__ == '__main__':
    main()
