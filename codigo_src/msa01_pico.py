#!/usr/bin/env python3
"""MSA-01: semana do pico semanal de casos prováveis em cada temporada (temporada por UF), 2014/15 a 2024/25.
Uso: python3 msa01_pico.py <base.csv.gz> <msa01_desfecho.csv> <saida.csv>
Saída: uf, temporada, alta, k_pico (semanas desde o início da temporada da UF), semana_pico (semana epidemiológica).
"""
import sys, pandas as pd
B, DES, OUT = sys.argv[1:4]
DAY = pd.Timedelta(days=1)
def ew(d):
    w = d + 3 * DAY; j = pd.Timestamp(w.year, 1, 1); f = j - pd.Timedelta(days=(j.dayofweek + 1) % 7)
    if (f + 3 * DAY).year < w.year: f += 7 * DAY
    return (d - f).days // 7 + 1
b = pd.read_csv(B, dtype={'uf': str}, parse_dates=['sem_sin']); b = b[b.grupo == 'provavel']
D = pd.read_csv(DES, dtype={'uf': str}, parse_dates=['inicio']); D = D[D.temporada.between(2014, 2024)]
out = []
for r in D.itertuples():
    g = b[(b.uf == r.uf) & (b.sem_sin >= r.inicio) & (b.sem_sin < r.inicio + pd.Timedelta(weeks=52))].groupby('sem_sin').n.sum()
    d = g.idxmax(); out.append(dict(uf=r.uf, temporada=r.temporada, alta=r.alta, k_pico=(d - r.inicio).days // 7, semana_pico=ew(d)))
P = pd.DataFrame(out); P.to_csv(OUT, index=False)
h = P[P.alta == 1]
print('altas', len(h), 'k_pico mediana', h.k_pico.median(), 'p25', h.k_pico.quantile(.25), 'p75', h.k_pico.quantile(.75))
print(h.groupby('uf').k_pico.median().to_dict())
