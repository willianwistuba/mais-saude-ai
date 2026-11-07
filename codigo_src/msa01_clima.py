#!/usr/bin/env python3
"""MSA-01: temperatura média diária por UF (NASA POWER, reanálise MERRA-2), média ponderada pela população
da capital e dos 5 maiores municípios de cada UF (Censo 2022, IBGE/SIDRA tabela 4709).
Uso: python3 msa01_clima.py <municipios_coordenadas.csv> <saida_dir> <data_fim AAAAMMDD>
municipios_coordenadas.csv: codigo_ibge, latitude, longitude, capital, codigo_uf (base pública kelvins/municipios-brasileiros).
"""
import sys, os, json, subprocess, time, pandas as pd
MUN, OUT, FIM = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
pop = json.loads(subprocess.run(['curl', '-sS', 'https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022'], capture_output=True, text=True).stdout)[1:]
pop = pd.DataFrame({'codigo_ibge': [int(r['D1C']) for r in pop], 'pop2022': [int(r['V']) for r in pop]})
m = pd.read_csv(MUN).merge(pop, on='codigo_ibge')
pts = pd.concat([g.sort_values('pop2022', ascending=False).pipe(lambda x: pd.concat([x[x.capital == 1], x[x.capital == 0].head(5)])) for _, g in m.groupby('codigo_uf')])
pts[['codigo_ibge', 'codigo_uf', 'latitude', 'longitude', 'capital', 'pop2022']].to_csv(os.path.join(OUT, 'pontos.csv'), index=False)
rows = []
for r in pts.itertuples():
    u = (f'https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M&community=AG&longitude={r.longitude}'
         f'&latitude={r.latitude}&start=20060101&end={FIM}&format=JSON')
    for k in range(4):
        try:
            d = json.loads(subprocess.run(['curl', '-sS', '--max-time', '120', u], capture_output=True, text=True).stdout)['properties']['parameter']['T2M']; break
        except Exception: time.sleep(5)
    rows += [(r.codigo_ibge, r.codigo_uf, r.pop2022, k_, v) for k_, v in d.items() if v > -900]
    print(r.codigo_ibge, len(d), flush=True)
c = pd.DataFrame(rows, columns=['codigo_ibge', 'uf', 'pop', 'dia', 't2m'])
c['dia'] = pd.to_datetime(c.dia, format='%Y%m%d')
c.to_csv(os.path.join(OUT, 'clima_ponto_dia.csv.gz'), index=False)
c['w'] = c['pop'] * c.t2m
g = c.groupby(['uf', 'dia']).agg(w=('w', 'sum'), p=('pop', 'sum')).reset_index(); g['t2m'] = g.w / g.p
g[['uf', 'dia', 't2m']].to_csv(os.path.join(OUT, 'clima_uf_dia.csv.gz'), index=False); print('ok', g.uf.nunique(), len(g))
