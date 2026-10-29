import json, io, base64, math, re
import numpy as np, pandas as pd
from scipy import ndimage
from PIL import Image, ImageDraw

W = '/root/col/'
dem = np.load(W + 'dem.npy'); spill = np.load(W + 'spill.npy'); river = np.load(W + 'river.npy')
v = json.load(open(W + 'col_vec.json')); ov = json.load(open(W + 'ov.json'))
GH, GW = dem.shape; mpp = v['mpp']
X0, Y0 = 6339, 9096


def b64png(arr, mode):
    b = io.BytesIO(); Image.fromarray(arr, mode).save(b, 'PNG', optimize=True); return base64.b64encode(b.getvalue()).decode()


gy, gx = np.gradient(dem)
sl = np.arctan(np.hypot(gx, gy) / mpp * 1.3); asp = np.arctan2(-gx, gy)
hs = np.clip(np.sin(np.radians(48)) * np.cos(sl) + np.cos(np.radians(48)) * np.sin(sl) * np.cos(np.radians(315) - asp), 0, 1)
hs = (hs - hs.min()) / (hs.max() - hs.min())
b = io.BytesIO(); Image.fromarray((hs * 255).astype(np.uint8), 'L').save(b, 'JPEG', quality=80); hill = base64.b64encode(b.getvalue()).decode()
enc = np.clip(np.round(spill * 10), 0, 254).astype(np.uint8); enc[spill > 25] = 255; enc[river] = 0

# roads
keep = {'residential', 'tertiary', 'service', 'unclassified', 'primary', 'secondary', 'trunk', 'living_street'}
roads = []
for s in ov['seg']:
    if s['c'] in keep:
        for part in s['g']:
            if len(part) > 1:
                roads.append(dict(k='primary' if s['c'] in ('trunk', 'secondary') else s['c'], p=part))

# pois: schools and main hospitals, de-duplicated
def norm(n):
    k = re.sub(r'[^a-z]', '', (n or '').lower().replace('í', 'i').replace("'", ''))
    return 'silvioavidoscomplexo' if 'avidos' in k else k
pois = []
for p in ov['pl']:
    c = p['c']; n = p.get('n') or ''; cf = p.get('cf') or 0
    x, y = p['g'][0][0]
    if not (0 <= x < GW and 0 <= y < GH):
        continue
    if c in ('elementary_school', 'middle_school', 'high_school', 'preschool', 'school', 'specialty_school') and cf >= 0.6:
        a = 'school'
    elif c == 'hospital' and cf >= 0.9 and re.search(r'^hospital|santa casa|pronto socorro|apart hospital', n, re.I):
        a = 'hospital'
    else:
        continue
    if any(q['a'] == a and (norm(q['n'])[:12] == norm(n)[:12] or math.hypot(q['x'] - x, q['y'] - y) < 8) for q in pois):
        continue
    if 'avidos' in norm(n): n = 'Hospital Estadual Sílvio Avidos'
    pois.append(dict(n=n, a=a, x=round(x, 1), y=round(y, 1), s=round(min(float(spill[int(y), int(x)]), 30), 1)))
print('pois', sum(p['a'] == 'school' for p in pois), 'schools', [p['n'] for p in pois if p['a'] == 'hospital'])

# urban footprint and curves
urb = Image.new('L', (GW, GH), 0); d = ImageDraw.Draw(urb)
for r in roads:
    if r['k'] in ('residential', 'living_street', 'tertiary', 'unclassified', 'service', 'primary'):
        d.line([tuple(p) for p in r['p']], fill=255, width=1)
urb = np.array(urb) > 0
dens = ndimage.uniform_filter(urb.astype(float), 21)
urban = ndimage.binary_dilation(urb, iterations=5) & (dens > 0.04) & ~river
seg = []
for r in roads:
    for (a, b2), (c, e) in zip(r['p'][:-1], r['p'][1:]):
        mx, my = (a + c) / 2, (b2 + e) / 2
        if 0 <= mx < GW and 0 <= my < GH:
            seg.append((float(spill[int(my), int(mx)]), math.hypot(c - a, e - b2) * mpp / 1000))
seg = np.array(seg); levels = np.round(np.arange(0, 15.01, 0.1), 1); us = spill[urban]
curve = dict(lv=levels.tolist(), urb=[round(float((us <= L).sum() * mpp * mpp / 1e6), 3) for L in levels],
             road=[round(float(seg[seg[:, 0] <= L, 1].sum()), 2) for L in levels],
             urban_total=round(float(urban.sum() * mpp * mpp / 1e6), 2), road_total=round(float(seg[:, 1].sum()), 1))

# buildings: thresholds and areas
polys = np.load(W + 'bld.npy', allow_pickle=True)
thr, area = [], []
for p in polys:
    x, y = p[:, 0], p[:, 1]; cx, cy = x.mean(), y.mean()
    xs = np.clip(np.r_[x, cx].astype(int), 0, GW - 1); ys = np.clip(np.r_[y, cy].astype(int), 0, GH - 1)
    t = float(spill[ys, xs].min())
    thr.append(255 if t > 25 else min(254, int(round(t * 10))))
    area.append(min(65535, int(round(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) * mpp * mpp))))
thr = np.array(thr, np.uint8); area = np.array(area, np.uint16)

# gauge
s = pd.read_csv('/root/work/cotas_56994500.csv', parse_dates=['d']).set_index('d').cm / 100
cnt = s.groupby(s.index.year).count(); am = s.groupby(s.index.year).max()[cnt > 300]
am = am[am.index <= 2025]
R0 = round(7.99 - v['fit']['1997'][0], 1)
print('R0', R0, 'years', len(am), 'first', am.index.min())

d = dict(id='colatina', GW=GW, GH=GH, X0=X0, Y0=Y0, hill=hill, enc=b64png(enc, 'L'), riv=b64png((river * 255).astype(np.uint8), 'L'),
         curve=curve, sect=v['sect'], obs=v['obs'], roads=roads, pois=pois, mpp=mpp, bounds=v['bounds'],
         bld=open(W + 'bld_b64.txt').read(), bthr=base64.b64encode(thr.tobytes()).decode(), barea=base64.b64encode(area.tobytes()).decode(),
         nb=int(len(thr)), R0=R0, annmax={int(k): round(float(x), 2) for k, x in am.items()},
         fit={k: dict(L=f[0], iou=round(f[1], 3), recall=round(f[2], 3), precision=round(f[3], 3)) for k, f in v['fit'].items()})
json.dump(d, open('/home/claude/work/city_colatina.json', 'w'), ensure_ascii=False, separators=(',', ':'))
o = thr.astype(float) / 10; o[thr == 255] = 99
for H in [7.5, 7.99, 8.9]:
    L = H - R0; i = int(round(L * 10))
    print(H, 'bld', int((o <= L + 1e-6).sum()), 'of', len(o), 'years', int((am >= H).sum()), 'urb', curve['urb'][i], 'schools', sum(p['s'] <= L for p in pois if p['a'] == 'school'), 'hosp', sum(p['s'] <= L for p in pois if p['a'] == 'hospital'))
fl = [x for x in v['sect'] if 'nunda' in x['tipo']]
print('flood sectors cov at 1997:', round(np.mean([x['cov'][int(round((7.99 - R0) * 10))] for x in fl]), 2))
