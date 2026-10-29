"""Altura de cada construção de Colatina: mediana de (MDE - MDT) do IEMA dentro do contorno, na grade z16 (~2,4 m)."""
import numpy as np
from skimage.draw import polygon as skpoly
O = '/root/col_iema/'
mdt = np.load(O + 'mdt_z16.npy'); mde = np.load(O + 'mde_z16.npy')
nd = mde - mdt
H, W = nd.shape
polys = np.load('/root/col/bld.npy', allow_pickle=True)
F = 4
hm, hp, npx = [], [], []
for p in polys:
    rr, cc = skpoly(p[:, 1] * F, p[:, 0] * F, (H, W))
    if rr.size < 2:  # muito pequena: usa o centroide
        rr = np.array([int(p[:, 1].mean() * F)]).clip(0, H - 1); cc = np.array([int(p[:, 0].mean() * F)]).clip(0, W - 1)
    v = nd[rr, cc]; v = v[np.isfinite(v)]
    npx.append(rr.size)
    if v.size == 0:
        hm.append(np.nan); hp.append(np.nan); continue
    hm.append(np.median(v)); hp.append(np.percentile(v, 75))
hm = np.array(hm); hp = np.array(hp); npx = np.array(npx)
np.savez(O + 'alturas.npz', med=hm, p75=hp, npx=npx)
print('n', len(hm), 'nan', int(np.isnan(hm).sum()))
print('median pct', np.nanpercentile(hm, [5, 10, 25, 50, 75, 90, 95, 99]).round(1))
print('p75 pct', np.nanpercentile(hp, [5, 10, 25, 50, 75, 90, 95, 99]).round(1))
print('share med>=2.5', np.nanmean(hm >= 2.5).round(3), 'p75>=2.5', np.nanmean(hp >= 2.5).round(3))
