#!/usr/bin/env python3
"""MSA-01, emenda 2: início, antecedência e acerto de cada um dos 21 modelos da triagem (e de A e M), a partir das previsões publicadas.
Mesmas regras da avaliação principal: início = primeira semana com acerto >= 75% nela e em todas as seguintes até 42;
regra estrita = o mesmo com o limite inferior do IC 95%; evidência = primeira semana com metade das temporadas altas evidentes;
antecedência = evidência - início (zero se não houver janela). IC por 4.000 reamostragens das temporadas.
Uso: python3 msa01_antecedencia_modelos.py <msa01_previsoes.csv.gz> <saida.csv>
"""
import sys, numpy as np, pandas as pd
P = pd.read_csv(sys.argv[1]); OUT = sys.argv[2]
rng = np.random.default_rng(20261107); B = 4000; KS = list(range(43))
seas = sorted(P.temporada.unique()); boots = [list(rng.choice(seas, len(seas))) for _ in range(B)]
cols = [c for c in P.columns if c.startswith('p_')] + ['pA', 'pM']
N = P.pivot_table(index='temporada', columns='k', values='alta', aggfunc='count')[KS]
NP = P[P.alta == 1].pivot_table(index='temporada', columns='k', values='alta', aggfunc='count').reindex(index=seas, columns=KS).fillna(0)
NN = P[P.alta == 0].pivot_table(index='temporada', columns='k', values='alta', aggfunc='count').reindex(index=seas, columns=KS).fillna(0)
DEC = P[P.alta == 1].pivot_table(index='temporada', columns='k', values='decidido', aggfunc='sum').reindex(index=seas, columns=KS).fillna(0)
def inicio(a):
    w = None
    for i in range(len(KS) - 1, -1, -1):
        if a[i] >= 0.75: w = i
        else: break
    return w
def evid(ix):
    d = DEC.loc[ix].sum().values / NP.loc[ix].sum().values; e = [i for i in KS if d[i] >= 0.5]
    return min(e) if e else len(KS)
EV = evid(seas); EVB = [evid(ix) for ix in boots]
q = lambda v: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
rows = []
for c in cols:
    yes = (P[c] >= 0.5).astype(int)
    K = P.assign(o=(yes == P.alta).astype(int)).pivot_table(index='temporada', columns='k', values='o', aggfunc='sum')[KS]
    TP = P.assign(o=((yes == 1) & (P.alta == 1)).astype(int)).pivot_table(index='temporada', columns='k', values='o', aggfunc='sum')[KS]
    TN = P.assign(o=((yes == 0) & (P.alta == 0)).astype(int)).pivot_table(index='temporada', columns='k', values='o', aggfunc='sum')[KS]
    acc = K.sum().values / N.sum().values
    accb = np.array([K.loc[ix].sum().values / N.loc[ix].sum().values for ix in boots])
    lo = np.percentile(accb, 2.5, axis=0)
    i0, i0s = inicio(acc), inicio(lo)
    ant = (EV - i0) if (i0 is not None and i0 < EV) else 0
    ants = (EV - i0s) if (i0s is not None and i0s < EV) else 0
    ab = []
    for b, ix in enumerate(boots):
        ib = inicio(accb[b]); ab.append((EVB[b] - ib) if (ib is not None and ib < EVB[b]) else 0)
    ab = np.array(ab)
    rows.append(dict(modelo=c.replace('p_', ''), inicio=i0, inicio_estrito=i0s, evidencia=EV, antecedencia=ant, antecedencia_ic=q(ab),
                     frac_boot_sem_janela=float(np.mean(ab == 0)), antecedencia_estrita=ants, acerto_max=float(acc.max()),
                     acerto_inicio=float(acc[i0]) if i0 is not None else None,
                     sens_inicio=float(TP[i0].sum() / NP[i0].sum()) if i0 is not None else None,
                     espec_inicio=float(TN[i0].sum() / NN[i0].sum()) if i0 is not None else None))
R = pd.DataFrame(rows).sort_values(['antecedencia', 'acerto_max'], ascending=False)
R.to_csv(OUT, index=False); print(R.round(3).to_string())
