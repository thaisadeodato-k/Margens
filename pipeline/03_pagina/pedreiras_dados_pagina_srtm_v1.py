import json, io, base64, math
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

W = '/root/work/'
dem = np.load(W + 'dem.npy')
spill = np.load(W + 'spill.npy')
river = np.load(W + 'river.npy')
v = json.load(open(W + 'vec.json'))
mpp = v['mpp']
H = dem.shape[0]


def b64png(arr, mode):
    b = io.BytesIO()
    Image.fromarray(arr, mode).save(b, 'PNG', optimize=True)
    return base64.b64encode(b.getvalue()).decode()


# hillshade (grayscale), recoloured in the page per theme
gy, gx = np.gradient(dem)
az, alt = np.radians(315), np.radians(48)
sl = np.arctan(np.hypot(gx, gy) / 9.5 * 1.6)
asp = np.arctan2(-gx, gy)
hs = np.sin(alt) * np.cos(sl) + np.cos(alt) * np.sin(sl) * np.cos(az - asp)
hs = np.clip(hs, 0, 1)
hs = (hs - hs.min()) / (hs.max() - hs.min())
b = io.BytesIO()
Image.fromarray((hs * 255).astype(np.uint8), 'L').save(b, 'JPEG', quality=82)
hill = base64.b64encode(b.getvalue()).decode()

# flood threshold grid (decimetres; 255 = above 25 m)
enc = np.clip(np.round(spill * 10), 0, 254).astype(np.uint8)
enc[spill > 25] = 255
enc[river] = 0
encp = b64png(enc, 'L')

# river mask
rivp = b64png((river * 255).astype(np.uint8), 'L')

# 16-bit grids for the 3D mesh (257 x 257 samples)
idx = np.linspace(0, H - 1, 257).round().astype(int)
dem_s = ndimage.gaussian_filter(dem, 1.5)[np.ix_(idx, idx)]
ref = dem - (dem - dem)  # placeholder overwritten below
# recompute reference water surface the same way as the model
lowf = ndimage.percentile_filter(np.where(river, dem, 999), 10, size=41)
lowf = np.where(river, np.minimum(lowf, dem), np.nan)
ii = ndimage.distance_transform_edt(~river, return_distances=False, return_indices=True)
ref = ndimage.gaussian_filter(lowf[ii[0], ii[1]], 25)[np.ix_(idx, idx)]


def enc16(a):
    q = np.clip(np.round(a * 100), 0, 65535).astype(np.uint32)
    rgb = np.stack([(q >> 8).astype(np.uint8), (q & 255).astype(np.uint8), np.zeros_like(q, np.uint8)], -1)
    return b64png(rgb, 'RGB')


demp = enc16(dem_s)
refp = enc16(ref)

# urban footprint: cells within ~50 m of local streets
urb = Image.new('L', (H, H), 0)
d = ImageDraw.Draw(urb)
for r in v['roads']:
    if r['k'] in ('residential', 'living_street', 'tertiary', 'unclassified', 'service', 'primary'):
        d.line([tuple(p) for p in r['p']], fill=255, width=1)
urb = np.array(urb) > 0
dens = ndimage.uniform_filter(urb.astype(float), 21)
urban = ndimage.binary_dilation(urb, iterations=5) & (dens > 0.04) & ~river
print('urban km2', urban.sum() * mpp * mpp / 1e6)

levels = np.round(np.arange(0, 15.01, 0.1), 1)
seg_s = np.array(v['seg_s'])
seg_km = np.array(v['seg_km'])
us = spill[urban]
curve = dict(
    lv=levels.tolist(),
    urb=[round(float((us <= L).sum() * mpp * mpp / 1e6), 3) for L in levels],
    road=[round(float(seg_km[seg_s <= L].sum()), 2) for L in levels],
    urban_total=round(float(urban.sum() * mpp * mpp / 1e6), 2),
    road_total=round(float(seg_km.sum()), 1),
)
# coverage of official flood sectors by level
for s in v['sect']:
    pass

sect_cov = {}
from skimage.draw import polygon as skpoly
for s in v['sect']:
    m = np.zeros((H, H), bool)
    for ring in s['rings']:
        a = np.array(ring)
        rr, cc = skpoly(a[:, 1], a[:, 0], (H, H))
        m[rr, cc] = True
    vals = spill[m]
    s['cov'] = [round(float((vals <= L).mean()), 3) for L in levels]

data = dict(hill=hill, enc=encp, riv=rivp, dem=demp, ref=refp, curve=curve,
            sect=v['sect'], roads=[r for r in v['roads'] if r['k'] not in ('path',)],
            pois=v['pois'], mpp=mpp, bounds=v['bounds'])
s = 'window.MEARIM=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';'
open('/home/claude/work/data.js', 'w').write(s)
print('data.js', len(s) / 1e6, 'MB')
for L in [2, 4, 6, 8, 10]:
    i = int(L * 10)
    print(L, curve['urb'][i], curve['road'][i], sum(p['s'] <= L for p in v['pois']))
