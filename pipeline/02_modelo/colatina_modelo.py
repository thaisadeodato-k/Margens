import json, math
import numpy as np
from scipy import ndimage
from skimage.morphology import reconstruction
from skimage.draw import line as skline, polygon as skpoly
import geopandas as gpd

W = '/root/col/'
dem = np.load(W + 'dem.npy')
H, Wd = dem.shape
z, x0, y0 = 14, 6339, 9096
N = 256 * 2 ** z
mpp = 40075016.686 * math.cos(math.radians(-19.53)) / N


def ll2px(lon, lat):
    px = (lon + 180) / 360 * N - x0 * 256
    r = math.radians(lat)
    py = (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * N - y0 * 256
    return px, py


def px2ll(px, py):
    lon = (px + x0 * 256) / N * 360 - 180
    n = math.pi - 2 * math.pi * (py + y0 * 256) / N
    return lon, math.degrees(math.atan(math.sinh(n)))


ov = json.load(open(W + 'ov.json'))


def raster_poly(rings, shape):
    m = np.zeros(shape, bool)
    for ring in rings:
        a = np.array(ring)
        if len(a) < 3:
            continue
        rr, cc = skpoly(a[:, 1], a[:, 0], shape)
        m[rr, cc] = True
    return m


# ---- river mask: Rio Doce lines + river polygons touching them
line = np.zeros((H, Wd), bool)
for w in ov['wat']:
    if w['s'] == 'river' and w['ty'] == 2 and (w.get('n') or '') == 'Rio Doce':
        for part in w['g']:
            for (a, b), (c, d) in zip(part[:-1], part[1:]):
                rr, cc = skline(int(round(b)), int(round(a)), int(round(d)), int(round(c)))
                ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < Wd)
                line[rr[ok], cc[ok]] = True
polys = np.zeros((H, Wd), bool)
for w in ov['wat']:
    # só os polígonos do próprio Rio Doce: os afluentes (Pancas, Santa Maria do Doce) ficam fora da máscara, para que a
    # água entre neles pelo nível do Doce (remanso) e não pelo leito do afluente
    if w['s'] == 'river' and w['ty'] == 3 and (w.get('n') or '') == 'Rio Doce':
        polys |= raster_poly(w['g'], (H, Wd))
lab, n = ndimage.label(polys)
touch = np.unique(lab[ndimage.binary_dilation(line, iterations=3) & polys])
river = np.isin(lab, touch[touch > 0]) | ndimage.binary_dilation(line, iterations=3)
river = ndimage.binary_closing(river, iterations=2)
print('river cells', river.sum(), 'km2', river.sum() * mpp * mpp / 1e6)

lowf = ndimage.percentile_filter(np.where(river, dem, 999), 10, size=41)
lowf = np.where(river, np.minimum(lowf, dem), np.nan)
idx = ndimage.distance_transform_edt(~river, return_distances=False, return_indices=True)
ref = ndimage.gaussian_filter(lowf[idx[0], idx[1]], 25)
rel = dem - ref
mask = np.where(river, np.minimum(rel, 0), rel)
seed = np.where(river, mask, rel.max() + 1)
spill = np.maximum(reconstruction(seed, mask, method='erosion'), 0)
spill[river] = 0
np.save(W + 'spill.npy', spill); np.save(W + 'river.npy', river); np.save(W + 'ref.npy', ref)

# ---- SGB observed floods (2016 package) and 2019 sectors
def gdf_rings(g):
    out = []
    for geom in g.geometry:
        ps = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
        for p in ps:
            out.append([list(ll2px(x, y)) for x, y, *_ in p.exterior.coords])
    return out

obs = {}
for yr in ['1979', '1997']:
    g = gpd.read_file(f'/root/sgb_col/plan/EVENTOS/cheia_{yr}.shp').to_crs(4326)
    rings = gdf_rings(g)
    obs[yr] = dict(rings=rings, mask=raster_poly(rings, (H, Wd)) & ~river)
    print('obs', yr, 'km2', obs[yr]['mask'].sum() * mpp * mpp / 1e6)

# fit: model level L that best matches each observed extent (IoU)
fit = {}
both = obs['1979']['mask'] | obs['1997']['mask']
ys_, xs_ = np.where(both)
win = np.zeros_like(river); win[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1] = True
near = ndimage.binary_dilation(both, iterations=60) & win & ~river  # corridor the SGB mapped
for yr, o in obs.items():
    best = None
    for L in np.arange(0, 20.01, 0.1):
        m = (spill <= L) & near
        inter = (m & o['mask']).sum(); uni = (m | o['mask']).sum()
        iou = inter / uni
        if best is None or iou > best[1]:
            best = (round(float(L), 1), float(iou), float(inter / o['mask'].sum()), float(inter / max(m.sum(), 1)))
    fit[yr] = best
    print('fit', yr, 'L', best[0], 'IoU', round(best[1], 3), 'recall', round(best[2], 3), 'precision', round(best[3], 3))

sg = gpd.read_file('/root/sgb_col/set19/GDB/ES_COLATIN_SR_CPRM.gdb').to_crs(4326)
sect = []
levels = np.round(np.arange(0, 15.01, 0.1), 1)
for _, r in sg.iterrows():
    rings = gdf_rings(gpd.GeoDataFrame(geometry=[r.geometry], crs=4326))
    m = raster_poly(rings, (H, Wd))
    if m.sum() == 0:
        continue
    vals = spill[m]
    tip = r['TIPOLO_G1']
    sect.append(dict(mun='Colatina', id=r['NUM_SETOR'], local=r['LOCAL'], tipo=tip, risco=r['GRAU_RISCO'],
                     morad=int(r['NUM_EDIF'] or 0), pess=int(r['NUM_PESS'] or 0), desc=r['DESCRICAO'], interv=r['SUG_INTERV'],
                     area_km2=float(m.sum() * mpp * mpp / 1e6), rings=[[[round(a, 1), round(b, 1)] for a, b in ring] for ring in rings],
                     cov=[round(float((vals <= L).mean()), 3) for L in levels]))
print('sectors in map', len(sect), sum(1 for s in sect if 'nunda' in s['tipo']))
json.dump(dict(fit=fit, sect=sect, obs={k: [[[round(a, 1), round(b, 1)] for a, b in ring] for ring in v['rings']] for k, v in obs.items()},
               mpp=mpp, bounds=[*px2ll(0, 0), *px2ll(Wd, H)]), open(W + 'col_vec.json', 'w'), ensure_ascii=False)
np.save(W + 'obs1997.npy', obs['1997']['mask']); np.save(W + 'obs1979.npy', obs['1979']['mask'])
