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
a=load('/root/ana_col/z/56994500_Cotas.csv'); b=a
for n,s in [('56994500',a)]:
    print(n, s.index.min().date(), s.index.max().date(), len(s), 'cm min/max', s.cm.min(), s.cm.max())
    am=s.cm.groupby(s.index.year).agg(['max','count','idxmax'])
    print(am.head(8).to_string()); print(am.tail(15).to_string())
a.to_csv('/root/work/cotas_56994500.csv')
am=a.cm.groupby(a.index.year).max(); c=a.cm.groupby(a.index.year).count(); am=am[c>300]; print('complete years',len(am)); print(am.sort_values(ascending=False).head(10).to_dict())
