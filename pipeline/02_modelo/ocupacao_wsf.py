"""Ano de ocupação de cada construção, pelo WSF Evolution (DLR). Uma cidade por vez: python3 pipeline/02_modelo/ocupacao_wsf.py colatina

Entrada
  dados/intermediarios/<cidade>_wsf_evolution.b64  recorte do bloco do WSF Evolution (pipeline/01_obter/wsf_evolution_recorte.js):
                                                    uint8, valor = ano − 1984 (1 = já ocupado em 1985), 0 = não detectado
  site/data/<cidade>.json                           contornos das construções (bld) e limiar de água de cada uma (bthr)
Saída
  dados/intermediarios/<cidade>_ocupacao_wsf.npz    para cada construção (ordem do site): ano (0 = não detectado até 2015) e
                                                    origem (1 = pixel do centro, 2 = vizinhança de 3 × 3 pixels, 0 = nenhum)
  e o resumo impresso abaixo, usado em docs/METODO.md

Regra: o WSF tem pixels de ~30 m, maiores que a maioria das construções. Vale o pixel do centro da construção; se ele não
tem ocupação detectada, vale o menor ano entre os 8 vizinhos (uma casa na borda de uma área ocupada). O ano é o da
primeira detecção de área construída naquele pixel, não o ano da construção em si.

Rodar a partir da raiz do repositório.
"""
import base64, gzip, json, math, sys
import numpy as np

ROOT = ''
CID = sys.argv[1] if len(sys.argv) > 1 else 'colatina'
RES = 0.00026949458523585647
# recorte do WSF de cada cidade (parâmetros devolvidos pelo script do navegador) e cheias de referência para o resumo
CFG = {
    'colatina': dict(tile='WSFevolution_v1_-42_-20', C0=4802, R0W=5516, WW=576, HW=389, LON0=-42.010163419491484, LAT0=-17.989841542834363,
                     nz=16797, cheias=[(7.99, 'cheia de 1997'), (8.90, 'cheia de 2013')]),
    'pedreiras': dict(tile='WSFevolution_v1_-46_-6', C0=5050, R0W=1971, WW=331, HW=330, LON0=-46.01000205356207, LAT0=-3.989867334416855,
                      nz=9678, cheias=[(7.45, 'cheias de 2024 e 2026'), (9.81, 'cheia de 2009')]),
}[CID]
C0, R0W, WW, HW, LON0, LAT0 = (CFG[k] for k in ('C0', 'R0W', 'WW', 'HW', 'LON0', 'LAT0'))

wsf = np.frombuffer(gzip.decompress(base64.b64decode(open(ROOT + f'dados/intermediarios/{CID}_wsf_evolution.b64').read().strip())),
                    np.uint8).reshape(HW, WW).astype(int)
assert (wsf > 0).sum() == CFG['nz']

D = json.load(open(ROOT + f'site/data/{CID}.json'))
X0, Y0, NT = D['X0'], D['Y0'], 256 * 2 ** 14
R0 = D['R0']


def ll(px, py):
    lon = (px + X0 * 256) / NT * 360 - 180
    n = math.pi - 2 * math.pi * (py + Y0 * 256) / NT
    return lon, math.degrees(math.atan(math.sinh(n)))


# contornos das construções: cabeçalho (nb, nv), depois por construção n e n pares (x, y) em 1/16 de pixel da grade
buf = gzip.decompress(base64.b64decode(D['bld']))
nb, nv = np.frombuffer(buf[:8], np.uint32)
v = np.frombuffer(buf[8 + nb: 8 + nb + nv * 2], np.uint16)
cent = []
i = 0
while i < len(v):
    n = int(v[i]); xy = v[i + 1: i + 1 + 2 * n].reshape(n, 2) / 16
    cent.append(xy.mean(axis=0)); i += 1 + 2 * n
cent = np.array(cent)
assert len(cent) == nb == D['nb']

ano = np.zeros(nb, np.uint16); origem = np.zeros(nb, np.uint8)
for k, (px, py) in enumerate(cent):
    lon, lat = ll(px, py)
    c = int(math.floor((lon - LON0) / RES)) - C0; r = int(math.floor((LAT0 - lat) / RES)) - R0W
    if not (0 <= c < WW and 0 <= r < HW):
        continue
    if wsf[r, c]:
        ano[k] = wsf[r, c] + 1984; origem[k] = 1
        continue
    win = wsf[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2]
    if (win > 0).any():
        ano[k] = win[win > 0].min() + 1984; origem[k] = 2

np.savez_compressed(ROOT + f'dados/intermediarios/{CID}_ocupacao_wsf.npz', ano=ano, origem=origem)

# ---- resumo
thr = np.frombuffer(base64.b64decode(D['bthr']), np.uint8).astype(float) / 10
thr[thr >= 25.5] = 99
FAIXAS = [('já ocupado em 1985', 1985, 1985), ('1986–1997', 1986, 1997), ('1998–2015', 1998, 2015), ('não detectado até 2015', 0, 0)]


def faixa(a):
    return [((a >= lo) & (a <= hi)).sum() for _, lo, hi in FAIXAS]


print('construções', nb, '| centro', int((origem == 1).sum()), '| vizinhança', int((origem == 2).sum()), '| nenhum', int((origem == 0).sum()))
for H, nome in CFG['cheias'] + [(99, 'cidade toda')]:
    sel = thr <= H - R0 + 1e-6 if H < 99 else np.ones(nb, bool)
    f = faixa(ano[sel]); tot = sel.sum()
    print(f'{nome:22s} {tot:6d} construções: ' + ' | '.join(f'{FAIXAS[j][0]} {f[j]} ({f[j] / tot:.0%})' for j in range(4)))
