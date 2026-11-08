#!/usr/bin/env python3
"""MSA-01, emenda 6: regra de três estados com faixa da projeção.
Erro da projeção de um par (UF, temporada) na semana k: e = log(incidência final + 1) - log(projeção na data + 1).
Faixa da previsão (UF, Y, k) com data D: quantis q e 1 - q de e em todos os pares na mesma semana k com desfecho
conhecido em D e projeção disponível (mínimo 30); os dois limites nunca abaixo da incidência já disponível (emenda 7:
antes só o inferior, o que podia inverter a faixa); com --sem-piso, sem esse piso (usado na S5 com todas as notificações,
porque a incidência disponível de casos prováveis depende da classificação final).
Estado: "alta" se inferior >= 300 por 100 mil; "baixa" se superior < 300; "indefinida" nos demais casos.
Alerta: primeira semana (1 a 42) com "alta" nela e na anterior; medidas como na regra de alerta da emenda 5.
Uso: python3 msa01_faixa.py <apuracao.csv.gz> <desfecho.csv> <pico.csv> <saida_prefixo> [--q 0.10] [--excluir 2013,2014] [--sem-piso]
"""
import sys, json, numpy as np, pandas as pd
AP, DES, PICO, OUT = sys.argv[1:5]
QL = float(sys.argv[sys.argv.index('--q') + 1]) if '--q' in sys.argv else 0.10
EXC = [int(x) for x in sys.argv[sys.argv.index('--excluir') + 1].split(',')] if '--excluir' in sys.argv else []
PISO = '--sem-piso' not in sys.argv
LIM, KS, B = 300.0, list(range(43)), 4000
A = pd.read_csv(AP, dtype={'uf': str}, parse_dates=['D']); Dd = pd.read_csv(DES, dtype={'uf': str}, parse_dates=['conhecido'])
A = A.merge(Dd[['uf', 'temporada', 'alta', 'incidencia', 'conhecido']], on=['uf', 'temporada'], how='left')
A = A[~A.temporada.isin(EXC)].copy()
A['disp_inc'] = A.disp_prov / A['pop'] * 1e5
A['e'] = np.log(A.incidencia + 1) - np.log(A.proj_inc + 1)
AVAL = [t for t in range(2014, 2025) if t not in EXC]
PK = {(r.uf, r.temporada): r.k_pico for r in pd.read_csv(PICO, dtype={'uf': str}).itertuples()}
saida = []
for k in KS:
    pool = A[(A.k == k) & A.proj_inc.notna() & A.incidencia.notna()][['conhecido', 'e']].sort_values('conhecido')
    pc, pe = pool.conhecido.values, pool.e.values
    te = A[(A.k == k) & (A.temporada.isin(AVAL) | (A.D == pd.Timestamp('2026-11-01')))].copy()
    lo, hi, npar = [], [], []
    for r in te.itertuples():
        n = np.searchsorted(pc, np.datetime64(r.D), side='right'); x = pe[:n]; npar.append(n)
        if n < 30 or np.isnan(r.proj_inc): lo.append(np.nan); hi.append(np.nan); continue
        a, b = np.quantile(x, [QL, 1 - QL])
        piso = r.disp_inc if PISO else 0.0
        lo.append(max((r.proj_inc + 1) * np.exp(a) - 1, piso)); hi.append(max((r.proj_inc + 1) * np.exp(b) - 1, piso))
    te['inf'], te['sup'], te['n_pares'] = lo, hi, npar
    saida.append(te)
T = pd.concat(saida)
T['estado'] = np.where(T.inf >= LIM, 'alta', np.where(T.sup < LIM, 'baixa', 'indefinida'))
T.loc[T.inf.isna(), 'estado'] = 'indefinida'
PR = T[T.D == pd.Timestamp('2026-11-01')]
T = T[T.temporada.isin(AVAL)].copy()
T[['uf', 'temporada', 'k', 'D', 'proj_inc', 'disp_inc', 'inf', 'sup', 'n_pares', 'estado', 'incidencia', 'alta', 'decidido']].to_csv(OUT + '_estados.csv.gz', index=False)
# por semana
T['dentro'] = np.where(T.inf.notna(), ((T.incidencia >= T.inf) & (T.incidencia <= T.sup)).astype(float), np.nan)
T['dec'] = T.estado != 'indefinida'
T['certo'] = np.where(T.dec, ((T.estado == 'alta') == (T.alta == 1)).astype(float), np.nan)
S = T.groupby('k').agg(cobertura=('dentro', 'mean'), frac_indefinida=('dec', lambda v: 1 - v.mean()), acerto_decididos=('certo', 'mean'),
                       frac_alta=('estado', lambda v: (v == 'alta').mean()), frac_baixa=('estado', lambda v: (v == 'baixa').mean())).reset_index()
S.to_csv(OUT + '_por_semana.csv', index=False)
# alerta por temporada
lin = []
for (uf, t), g in T.groupby(['uf', 'temporada']):
    g = g.set_index('k').sort_index(); alta = int(g.alta.iloc[0]); ev = g.index[g.decidido == 1]
    kc = int(ev.min()) if len(ev) else 43
    y = (g.estado == 'alta').reindex(KS).fillna(False).values
    ka = next((k for k in range(1, 43) if y[k] and y[k - 1]), None)
    bx = (g.estado == 'baixa').reindex(KS).fillna(False).values
    d = dict(uf=uf, temporada=t, alta=alta, k_alerta=ka, k_evidencia=kc, censurada=int(kc >= 43), declarou_baixa=int(bx.any()))
    if alta:
        kp = PK.get((uf, t)); d['k_pico'] = kp
        d['antecedencia'] = (kc - ka) if (ka is not None and ka < kc) else 0
        d['antecipada'] = int(ka is not None and ka < kc); d['antes_do_pico'] = int(ka is not None and kp is not None and ka < kp)
    else:
        d['alarme_falso'] = int(ka is not None)
    lin.append(d)
L = pd.DataFrame(lin); L.to_csv(OUT + '_por_temporada.csv', index=False)
rng = np.random.default_rng(20261107); seas = sorted(L.temporada.unique()); boots = [list(rng.choice(seas, len(seas))) for _ in range(B)]
q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
def resumo(x):
    h, n = x[x.alta == 1], x[x.alta == 0]
    return dict(antecedencia_mediana=float(np.median(h.antecedencia)), frac_antecipada=float(h.antecipada.mean()),
                frac_antes_do_pico=float(h.antes_do_pico.mean()), alarme_falso=float(n.alarme_falso.mean()) if len(n) else np.nan,
                altas_declaradas_baixa=float(h.declarou_baixa.mean()), nao_altas_declaradas_baixa=float(n.declarou_baixa.mean()) if len(n) else np.nan,
                n_altas=int(len(h)), n_nao_altas=int(len(n)), n_alarme_falso=int(n.alarme_falso.sum()) if len(n) else 0,
                n_altas_declaradas_baixa=int(h.declarou_baixa.sum()))
G = {s: L[L.temporada == s] for s in seas}; r = resumo(L); bt = [resumo(pd.concat([G[s] for s in ix])) for ix in boots]
for kk in ['antecedencia_mediana', 'frac_antecipada', 'frac_antes_do_pico', 'alarme_falso']:
    r[kk + '_ic'] = q([b[kk] for b in bt if not np.isnan(b[kk])])
# acerto entre decididos e fração indefinida, no total
r.update(q_inferior=QL, piso=PISO, n_invertidas=int((T.inf > T.sup).sum()), acerto_decididos=float(T.certo.mean()), frac_indefinida=float(1 - T.dec.mean()), cobertura=float(T.dentro.mean()),
         temporadas=[int(s) for s in seas])
r['prospectivo_2026_11_01'] = PR[['uf', 'k', 'proj_inc', 'disp_inc', 'inf', 'sup', 'estado']].to_dict('records')
json.dump(r, open(OUT + '_resumo.json', 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: v for k, v in r.items() if k != 'prospectivo_2026_11_01'}, indent=1, default=float))
print(S.round(3).to_string()); print(PR[['uf', 'k', 'proj_inc', 'disp_inc', 'inf', 'sup', 'estado']].round(0).to_string())
