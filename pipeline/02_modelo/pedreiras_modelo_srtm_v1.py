import json, math
import numpy as np
from scipy import ndimage
from skimage.morphology import reconstruction
from skimage.draw import line as skline, polygon as skpoly
import geopandas as gpd

W = '/root/work/'
dem = np.load(W + 'dem.npy')  # 1024x1024 metres
H, Wd = dem.shape
z, x0, y0 = 14, 6160, 8398
N = 256 * 2 ** z


def ll2px(lon, lat):
    px = (lon + 180) / 360 * N - x0 * 256
    r = math.radians(lat)
    py = (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * N - y0 * 256
    return px, py


def px2ll(px, py):
    lon = (px + x0 * 256) / N * 360 - 180
    n = math.pi - 2 * math.pi * (py + y0 * 256) / N
    lat = math.degrees(math.atan(math.sinh(n)))
    return lon, lat


lon_a, lat_a = px2ll(0, 0)
lon_b, lat_b = px2ll(Wd, H)
print('bounds', lon_a, lat_a, lon_b, lat_b)
# metres per pixel at this latitude
mpp = 40075016.686 * math.cos(math.radians(-4.57)) / N
print('m/px', mpp)

osm = json.load(open(W + 'osm.json'))

# --- river mask (Rio Mearim lines + water polygons touching them)
river = np.zeros((H, Wd), bool)
for e in osm:
    if e['g'].get('waterway') == 'river' and isinstance(e.get('c'), list) and isinstance(e['c'][0], list):
        pts = [ll2px(*p) for p in e['c']]
        for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
            rr, cc = skline(int(round(b)), int(round(a)), int(round(d)), int(round(c)))
            ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < Wd)
            river[rr[ok], cc[ok]] = True
river_line = river.copy()
water = np.zeros((H, Wd), bool)
for e in osm:
    if e['g'].get('natural') == 'water':
        rings = []
        if e['t'] == 'w' and e.get('c'):
            rings = [e['c']]
        elif e.get('m'):
            rings = [m['c'] for m in e['m'] if m['r'] == 'outer']
        for ring in rings:
            pts = np.array([ll2px(*p) for p in ring])
            rr, cc = skpoly(pts[:, 1], pts[:, 0], (H, Wd))
            water[rr, cc] = True
lab, n = ndimage.label(water)
touch = np.unique(lab[ndimage.binary_dilation(river_line, iterations=2) & water])
touch = touch[touch > 0]
# OSM water polygons here include a malformed riverbank multipolygon, so use the river line only
river = ndimage.binary_dilation(river, iterations=3)
print('river cells', river.sum())

# --- reference water surface: low percentile of DEM over river cells, propagated & smoothed
rz = np.where(river, dem, np.nan)
# local low value along the channel (SRTM is noisy over water)
lowf = ndimage.percentile_filter(np.where(river, dem, 999), 10, size=41)
lowf = np.where(river, np.minimum(lowf, dem), np.nan)
idx = ndimage.distance_transform_edt(~river, return_distances=False, return_indices=True)
ref = lowf[idx[0], idx[1]]
ref = ndimage.gaussian_filter(ref, 25)
rel = dem - ref  # height above the nearby river surface

# --- connected flooding: minimal water height needed to reach each cell from the river
mask = np.where(river, np.minimum(rel, 0), rel)
seed = np.where(river, mask, rel.max() + 1)
spill = reconstruction(seed, mask, method='erosion')
spill = np.maximum(spill, 0)
spill[river] = 0
print('spill pct', np.percentile(spill, [5, 25, 50, 75, 95]))

# encode: decimetres, 0..250, 255 = never within 25 m
enc = np.clip(np.round(spill * 10), 0, 254).astype(np.uint8)
enc[spill > 25] = 255
enc[river] = 0
np.save(W + 'spill.npy', spill)
np.save(W + 'river.npy', river)

# --- SGB sectors to pixel space
sect = []
files = [
    ('/root/sgb_data/sig_pedreiras_ma_risco_2012/Shape/MA_PD_SR_CPRM_atualizado.shp', 'Pedreiras'),
    ('/root/sgb_data/sig_trizideladovale_ma_risco_2012/Shapes/MA_TRIZ_SR_CPRM_atualizado.shp', 'Trizidela do Vale'),
]
orig = {
    'Pedreiras': gpd.read_file('/root/sgb_data/sig_pedreiras_ma_risco_2012/Shape/MA_PD_SR_CPRM.shp').to_crs(4326),
}
for f, mun in files:
    g = gpd.read_file(f).to_crs(4326)
    for _, r in g.iterrows():
        geom = r.geometry
        polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        rings = []
        for p in polys:
            rings.append([[round(v, 1) for v in ll2px(x, y)] for x, y in p.exterior.coords])
        m = np.zeros((H, Wd), bool)
        for ring in rings:
            a = np.array(ring)
            rr, cc = skpoly(a[:, 1], a[:, 0], (H, Wd))
            m[rr, cc] = True
        cov = {lv: float((spill[m] <= lv).mean()) for lv in [2, 4, 6, 8, 10, 12]}
        tip = r['TIPOLOGIA'].strip()
        sect.append(dict(mun=mun, id=r['NUM_SETOR'], local=r['LOCAL'], tipo=tip,
                         risco=r['GRAU_RISCO'], morad=r['NUM_MORAD'], pess=r['NUM_PESS'],
                         desc=r['DESCRICAO'], interv=r['SUG_INTERV'], area_km2=float(m.sum() * mpp * mpp / 1e6),
                         rings=rings, cov=cov))
        print(mun, r['NUM_SETOR'], tip, 'area', m.sum() * mpp * mpp / 1e6, cov)

# --- roads, schools
roads = []
for e in osm:
    hw = e['g'].get('highway')
    if hw and isinstance(e.get('c'), list) and isinstance(e['c'][0], list):
        pts = [[round(v, 1) for v in ll2px(*p)] for p in e['c']]
        roads.append(dict(k=hw, p=pts))
pois = []
for e in osm:
    am = e['g'].get('amenity')
    if am in ('school', 'hospital', 'clinic'):
        c = e['c']
        if isinstance(c[0], list):
            c = list(np.mean(np.array(c), axis=0))
        px, py = ll2px(*c)
        if 0 <= px < Wd and 0 <= py < H:
            s = float(spill[int(py), int(px)])
            pois.append(dict(n=e['g'].get('name') or ('Clínica' if am == 'clinic' else 'Escola sem nome'), a=am,
                             x=round(px, 1), y=round(py, 1), s=round(min(s, 30), 1)))
print('pois', len(pois), sorted(p['s'] for p in pois))

# road length flooded by level (sample along segments)
seglen = []
for r in roads:
    for (a, b), (c, d) in zip(r['p'][:-1], r['p'][1:]):
        L = math.hypot(c - a, d - b)
        mx, my = (a + c) / 2, (b + d) / 2
        if 0 <= mx < Wd and 0 <= my < H:
            seglen.append((float(spill[int(my), int(mx)]), L * mpp / 1000))
seg = np.array(seglen)
print('total road km', seg[:, 1].sum())

json.dump(dict(sect=sect, roads=roads, pois=pois, mpp=mpp,
               seg_s=[round(v, 1) for v in seg[:, 0]], seg_km=[round(v, 4) for v in seg[:, 1]],
               bounds=[lon_a, lat_a, lon_b, lat_b]),
          open(W + 'vec.json', 'w'), ensure_ascii=False)
np.save(W + 'enc.npy', enc)
