"""Colatina: modelo de água conectada com o MDT de 2 m do IEMA (reamostrado para a grade z15, ~4,8 m).

Diferenças em relação ao modelo ANADEM (col_model.py):
- relevo: MDT IEMA/GEOBASES 2012-2015 (metros inteiros), média dos pixels de 2 m em cada célula z15;
- referência do rio: vem do ANADEM (ref.npy), porque o MDT do IEMA tem valores ruidosos sobre a água
  (a restituição estereoscópica não funciona bem em superfícies de água). Desvio constante é absorvido por R0;
- grade 2x mais fina: tudo que estava em pixels z14 é multiplicado por 2.
"""
import json, math
import numpy as np
from scipy import ndimage
from skimage.morphology import reconstruction
from skimage.draw import polygon as skpoly
import geopandas as gpd

W = '/root/col/'; O = '/root/col_iema/'
F = 2
dem = np.load(O + 'mdt_z15.npy').astype(np.float64)
ana = np.load(W + 'dem.npy')
H, Wd = dem.shape
# células sem dado: preencher com ANADEM
nan = ~np.isfinite(dem)
dem[nan] = ndimage.zoom(ana, F, order=1)[nan]
# picos isolados (|z - mediana 9x9| > 8 m): trocar pela mediana
med = ndimage.median_filter(dem, size=9)
spk = np.abs(dem - med) > 8
dem[spk] = med[spk]
print('cells', dem.size, 'filled', int(nan.sum()), 'spikes', int(spk.sum()))

z, x0, y0 = 15, 6339 * F, 9096 * F
N = 256 * 2 ** z
mpp = 40075016.686 * math.cos(math.radians(-19.53)) / N


def ll2px(lon, lat):
    px = (lon + 180) / 360 * N - x0 * 256  # x0, y0 em blocos z15
    r = math.radians(lat)
    py = (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * N - y0 * 256
    return px, py


def raster_poly(rings, shape):
    m = np.zeros(shape, bool)
    for ring in rings:
        a = np.array(ring)
        if len(a) < 3:
            continue
        rr, cc = skpoly(a[:, 1], a[:, 0], shape)
        m[rr, cc] = True
    return m


river = np.kron(np.load(W + 'river.npy'), np.ones((F, F), bool))
ref = ndimage.zoom(np.load(W + 'ref.npy'), F, order=1)
rel = dem - ref
mask = np.where(river, np.minimum(rel, 0), rel)
seed = np.where(river, mask, rel.max() + 1)
spill = np.maximum(reconstruction(seed, mask, method='erosion'), 0)
spill[river] = 0
np.save(O + 'spill.npy', spill.astype(np.float32)); np.save(O + 'river.npy', river); np.save(O + 'dem_clean.npy', dem.astype(np.float32))


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
    obs[yr] = raster_poly(gdf_rings(g), (H, Wd)) & ~river

both = obs['1979'] | obs['1997']
ys_, xs_ = np.where(both)
win = np.zeros_like(river); win[ys_.min():ys_.max() + 1, xs_.min():xs_.max() + 1] = True
near = (ndimage.distance_transform_edt(~both) <= 60 * F) & win & ~river  # mesmo corredor do modelo ANADEM
fit = {}
for yr, o in obs.items():
    best = None
    for L in np.arange(0, 20.01, 0.1):
        m = (spill <= L) & near
        inter = (m & o).sum(); uni = (m | o).sum()
        iou = inter / uni
        if best is None or iou > best[1]:
            best = (round(float(L), 1), float(iou), float(inter / o.sum()), float(inter / max(m.sum(), 1)))
    fit[yr] = best
    print('fit', yr, 'L', best[0], 'IoU', round(best[1], 3), 'recall', round(best[2], 3), 'precision', round(best[3], 3))

# setores SGB 2019
sg = gpd.read_file('/root/sgb_col/set19/GDB/ES_COLATIN_SR_CPRM.gdb').to_crs(4326)
levels = np.round(np.arange(0, 15.01, 0.1), 1)
cov = {}
for _, r in sg.iterrows():
    m = raster_poly(gdf_rings(gpd.GeoDataFrame(geometry=[r.geometry], crs=4326)), (H, Wd))
    if m.sum():
        cov[r['NUM_SETOR']] = [round(float((spill[m] <= L).mean()), 3) for L in levels]
json.dump(dict(fit=fit, cov=cov, mpp=mpp), open(O + 'col_iema_vec.json', 'w'))
np.save(O + 'obs1997.npy', obs['1997']); np.save(O + 'near.npy', near)
