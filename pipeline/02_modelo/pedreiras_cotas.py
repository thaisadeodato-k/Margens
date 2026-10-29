import pandas as pd, numpy as np, io, sys
def load(path):
    txt=open(path,encoding='latin1').read().splitlines()
    i=next(k for k,l in enumerate(txt) if l.startswith('EstacaoCodigo'))
    df=pd.read_csv(io.StringIO('\n'.join(txt[i:])),sep=';',decimal=',',dtype=str)
    rows=[]
    for _,r in df.iterrows():
        d=pd.to_datetime(r['Data'],dayfirst=True)
        for k in range(1,32):
            v=r.get(f'Cota{k:02d}')
            if v is None or pd.isna(v) or v=='': continue
            try: day=d.replace(day=k)
            except ValueError: continue
            rows.append((day,int(r['NivelConsistencia']),float(str(v).replace(',','.'))))
    s=pd.DataFrame(rows,columns=['d','nc','cm'])
    # prefer consistido (2) over bruto (1) on same day
    s=s.sort_values(['d','nc']).drop_duplicates('d',keep='last').set_index('d')
    return s
a=load('/root/ana_dl/z0/33280000_Cotas.csv'); b=load('/root/ana_dl/z1/33281000_Cotas.csv')
for n,s in [('33280000',a),('33281000',b)]:
    print(n, s.index.min().date(), s.index.max().date(), len(s), 'cm min/max', s.cm.min(), s.cm.max())
    am=s.cm.groupby(s.index.year).agg(['max','count','idxmax'])
    print(am.tail(25).to_string())
b.to_csv('/root/work/cotas_33281000.csv'); a.to_csv('/root/work/cotas_33280000.csv')
ov=a.join(b,lsuffix='_a',rsuffix='_b',how='inner'); print('overlap days',len(ov), (ov.cm_b-ov.cm_a).describe() if len(ov) else '')
