"""Pedreiras: calibra a régua da estação Pedreiras II (33281000) e completa os dados da página.

Reconstituído a partir dos passos feitos durante o desenvolvimento (out/2026).
Calibração: as famílias começam a ser afetadas quando a régua passa de 6 m (Agência Brasil, abr/2023).
No modelo, isso corresponde ao nível L1 em que 1% das construções é alcançado. R0 = 6,0 − L1 (≈ 3,8 m).
"""
import json, base64
import numpy as np, pandas as pd

W = '/root/work/'  # pasta de trabalho com os intermediários (ver pipeline/README.md)
o = np.load(W + 'bld_attr_anadem.npy')  # por construção: cx, cy, área m², nível em que a água toca o contorno, nível no centroide
d = json.loads(open(W + 'data_anadem.js').read()[len('window.MEARIM='):-1])  # saída de pedreiras_dados_pagina.py

thr = np.where(o[:, 3] > 25, 255, np.clip(np.round(o[:, 3] * 10), 0, 254)).astype(np.uint8)
d['bthr'] = base64.b64encode(thr.tobytes()).decode()
d['nb'] = int(len(o))

s = pd.read_csv('dados/estacoes/cotas_33281000.csv', parse_dates=['d']).set_index('d').cm / 100
cnt = s.groupby(s.index.year).count()
am = s.groupby(s.index.year).max()[cnt > 300]          # só anos com série quase completa
d['annmax'] = {int(k): round(float(v), 2) for k, v in am.items()}

lv = np.arange(0, 15.01, 0.01)
cnts = np.array([(o[:, 3] <= L).sum() for L in lv])
L1 = float(lv[np.argmax(cnts >= 0.01 * len(o))])
d['R0'] = round(6.0 - L1, 1)
print('L1', L1, 'R0', d['R0'])
for H in [6, 7.45, 9.81, 10.1]:
    L = H - d['R0']
    print(f'régua {H} m → nível {L:.2f} m · {int((o[:, 3] <= L).sum())} construções · {int((am >= H).sum())} de {len(am)} anos')
d.update(id='pedreiras', GW=1024, GH=1024, X0=6160, Y0=8398)
json.dump(d, open(W + 'city_pedreiras.json', 'w'), ensure_ascii=False, separators=(',', ':'))
# Depois: acrescentar `cfg` (textos, eventos, régua) e `labels`/`view`, e salvar em site/data/pedreiras.json.
