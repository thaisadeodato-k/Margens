"""Junta os 4 blocos do MDT e do MDE do IEMA (2 m, EPSG:31984) e reamostra para as grades da página de Colatina.

Entrada: 32_784.img, 33_784.img, 32_785.img, 33_785.img (MDT) e os mesmos com "(1)" no nome (MDE), baixados do
GEOBASES (MAP_ES_2012_2015/MDT e /MDE). Valores em metros inteiros; 0 = sem dado.
Saída: mdt_z15/mde_z15 (média, ~4,8 m) e mdt_z16/mde_z16 (bilinear, ~2,4 m), alinhadas à grade z14 do modelo
(blocos x 6339, y 9096; z15 = 2x, z16 = 4x).
"""
import sys, glob
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin

ENT = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads'
SAI = sys.argv[2] if len(sys.argv) > 2 else '/root/col_iema'
O = 20037508.342789244
GW14, GH14, X14, Y14 = 1792, 1280, 6339, 9096


def grade(z):
    f = 2 ** (z - 14)
    T = 2 * O / 2 ** z / 256  # metros (Mercator) por pixel
    return from_origin(-O + X14 * f * 256 * T, O - Y14 * f * 256 * T, T, T), (GH14 * f, GW14 * f)


for nome, padrao in [('mdt', '[0-9][0-9]_[0-9][0-9][0-9].img'), ('mde', '*_1_.img')]:
    arqs = sorted(glob.glob(f'{ENT}/{padrao}'))
    print(nome, arqs)
    srcs = [rasterio.open(a) for a in arqs]
    mos, tr = merge(srcs, nodata=0)
    a = mos[0].astype(np.float32); a[a == 0] = np.nan
    for z, metodo in [(15, Resampling.average), (16, Resampling.bilinear)]:
        dst_tr, shape = grade(z)
        out = np.full(shape, np.nan, np.float32)
        reproject(a, out, src_transform=tr, src_crs=srcs[0].crs, src_nodata=np.nan,
                  dst_transform=dst_tr, dst_crs='EPSG:3857', dst_nodata=np.nan, resampling=metodo)
        np.save(f'{SAI}/{nome}_z{z}.npy', out)
        print(nome, z, out.shape, np.nanpercentile(out, [1, 50, 99]))
