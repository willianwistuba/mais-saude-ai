#!/usr/bin/env python3
"""MSA-01, emenda 5: regra de alerta fixa e teste em temporadas reservadas.
Alerta: primeira semana k (1 a 42) com probabilidade >= 0,5 em k e em k - 1; só o primeiro alerta.
Temporada alta: antecedência = semana de evidência (casos prováveis disponíveis >= 300/100 mil; 43 se não ocorrer, censura)
menos a semana do alerta, ou zero se não houve alerta antes da evidência; antes do pico se o alerta veio antes da semana do pico.
Temporada não alta: alarme falso se houve alerta. IC 95% por 4.000 reamostragens das temporadas.
Reserva: escolhe-se entre os modelos da triagem (21; 36 com a emenda 6) o de menor Brier nas temporadas 2011/12 a 2018/19 (cache da avaliação);
ele, A e R0 são avaliados só em 2020/21 a 2024/25.
Uso: python3 msa01_alerta.py <dir_avaliacao> <pico.csv> <saida_prefixo> [--reserva --desfecho <msa01_desfecho.csv>]
"""
import sys, json, numpy as np, pandas as pd
D, PICO, OUT = sys.argv[1:4]; RES = '--reserva' in sys.argv
P = pd.read_csv(f'{D}/msa01_previsoes.csv.gz')
PK = {(r.uf, r.temporada): r.k_pico for r in pd.read_csv(PICO).itertuples()}
rng = np.random.default_rng(20261107); B = 4000
q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
MODELOS = {'R0': 'p0', 'A': 'pA', 'M': 'pM', 'dupla': 'p_lproj+fora'}
for nm in ['lproj+cap', 'lproj+int']:  # emenda 6
    if 'p_' + nm in P.columns: MODELOS[nm.replace('lproj', 'proj')] = 'p_' + nm
info = {}
if RES:
    C = pd.read_pickle(f'{D}/cache_conjuntos.pkl')
    des = pd.read_csv(sys.argv[sys.argv.index('--desfecho') + 1], dtype={'uf': str}).set_index(['uf', 'temporada']).alta
    br = {}
    for n, r in C.items():
        x = r[r.temporada <= 2018].copy(); x['alta'] = [des.get((str(u), t)) for u, t in zip(x.uf, x.temporada)]
        br[n] = float(np.mean((x.p - x.alta.astype(float)) ** 2))
    sel = min(br, key=br.get); MODELOS = {'R0': 'p0', 'A': 'pA', 'escolhido': 'p_' + sel}
    P = P[P.temporada >= 2020].copy(); info = dict(escolhido=sel, brier_2011_2018=br)
seas = sorted(P.temporada.unique()); boots = [list(rng.choice(seas, len(seas))) for _ in range(B)]
linhas = []
for (uf, t), g in P.groupby(['uf', 'temporada']):
    g = g.set_index('k').sort_index(); alta = int(g.alta.iloc[0]); ev = g.index[g.decidido == 1]
    kc = int(ev.min()) if len(ev) else 43
    for nome, c in MODELOS.items():
        y = (g[c] >= 0.5).reindex(range(43)).fillna(False).values
        ka = next((k for k in range(1, 43) if y[k] and y[k - 1]), None)
        d = dict(uf=uf, temporada=t, alta=alta, modelo=nome, k_alerta=ka, k_evidencia=kc, censurada=int(kc >= 43))
        if alta:
            kp = PK.get((uf, t)); d['k_pico'] = kp
            d['antecedencia'] = (kc - ka) if (ka is not None and ka < kc) else 0
            d['antecipada'] = int(ka is not None and ka < kc); d['antes_do_pico'] = int(ka is not None and kp is not None and ka < kp)
        else:
            d['alarme_falso'] = int(ka is not None)
        linhas.append(d)
L = pd.DataFrame(linhas); L.to_csv(OUT + '_por_temporada.csv', index=False)
def resumo(x):
    h, n = x[x.alta == 1], x[x.alta == 0]
    return dict(antecedencia_mediana=float(np.median(h.antecedencia)) if len(h) else np.nan, frac_antecipada=float(h.antecipada.mean()) if len(h) else np.nan,
                frac_antes_do_pico=float(h.antes_do_pico.mean()) if len(h) else np.nan, alarme_falso=float(n.alarme_falso.mean()) if len(n) else np.nan,
                n_altas=int(len(h)), n_nao_altas=int(len(n)), altas_censuradas=int(h.censurada.sum()))
out = {}
for nome in MODELOS:
    x = L[L.modelo == nome]; G = {s: x[x.temporada == s] for s in seas}
    r = resumo(x); bt = [resumo(pd.concat([G[s] for s in ix])) for ix in boots]
    for kk in ['antecedencia_mediana', 'frac_antecipada', 'frac_antes_do_pico', 'alarme_falso']:
        r[kk + '_ic'] = q([b[kk] for b in bt if not np.isnan(b[kk])])
    out[nome] = r
# acerto e antecedência da janela (regra principal e estrita) nas temporadas avaliadas, para comparação na reserva
KS = list(range(43))
def janela(c):
    acc = P.assign(o=((P[c] >= .5).astype(int) == P.alta)).pivot_table(index='temporada', columns='k', values='o', aggfunc='mean')[KS]
    nh = P[P.alta == 1].groupby('temporada').uf.nunique()
    dec = P[P.alta == 1].groupby('k').decidido.mean().reindex(KS)
    ev = next((k for k in KS if dec[k] >= .5), 43)
    a = acc.mean().values  # média por temporada (todas com 27 pares)
    ab = np.array([acc.loc[ix].mean().values for ix in boots]); lo = np.percentile(ab, 2.5, axis=0)
    def ini(v):
        w = None
        for i in range(42, -1, -1):
            if v[i] >= .75: w = i
            else: break
        return w
    i0, i0s = ini(a), ini(lo)
    return dict(inicio=i0, inicio_estrito=i0s, evidencia=ev, antecedencia=(ev - i0) if (i0 is not None and i0 < ev) else 0,
                antecedencia_estrita=(ev - i0s) if (i0s is not None and i0s < ev) else 0, acerto_max=float(a.max()),
                brier=float(np.mean((P[c] - P.alta) ** 2)))
for nome, c in MODELOS.items(): out[nome]['janela'] = janela(c)
out['_info'] = info; out['_temporadas'] = [int(s) for s in seas]
json.dump(out, open(OUT + '_resumo.json', 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, indent=1, default=float, ensure_ascii=False))
