#!/usr/bin/env python3
"""MSA-01: triagem dos previsores (sozinhos e em duplas), critério M com escolha aninhada, acerto semanal,
antecedência em relação à contagem e ao pico, e previsão prospectiva 2026/27.
O treino de cada temporada Y na semana k usa só pares com desfecho conhecido (coluna 'conhecido' do desfecho)
na data mais cedo entre as datas de previsão de Y nessa semana. M para a temporada t é escolhido com as temporadas até t - 2.
Uso: python3 msa01_avaliacao.py <apuracao.csv.gz> <desfecho.csv> <pico.csv> <saida_dir> [--excluir 2015,2016] [--decidido 0.5] [--B 4000]
"""
import os, json, argparse, itertools, numpy as np, pandas as pd
from multiprocessing import Pool
from scipy.optimize import minimize
from scipy.special import expit, logit
ap = argparse.ArgumentParser(); ap.add_argument('apur'); ap.add_argument('des'); ap.add_argument('pico'); ap.add_argument('out')
ap.add_argument('--excluir', default=''); ap.add_argument('--decidido', type=float, default=0.5)
ap.add_argument('--semente', type=int, default=20261107); ap.add_argument('--B', type=int, default=4000); ap.add_argument('--comparar', action='store_true')
o = ap.parse_args(); os.makedirs(o.out, exist_ok=True); rng = np.random.default_rng(o.semente)
EXC = [int(x) for x in o.excluir.split(',') if x]
KS = list(range(43)); AVAL = [t for t in range(2014, 2025) if t not in EXC]; PREV = [t for t in range(2011, 2025) if t not in EXC]
LAMS = [0.01, 0.1, 1, 10, 100]; PRED = ['lproj', 'cresc', 'fora', 'inverno', 'apt', 'oni']
CONJ = [(p,) for p in PRED] + list(itertools.combinations(PRED, 2))
A = pd.read_csv(o.apur, dtype={'uf': str}, parse_dates=['D']); D = pd.read_csv(o.des, dtype={'uf': str}, parse_dates=['conhecido'])
A = A.merge(D[['uf', 'temporada', 'alta', 'incidencia', 'conhecido']], on=['uf', 'temporada'], how='left')
A['lproj'] = np.log(A.proj_inc.clip(lower=1)); A['off'] = logit(A.p0)
A = A[~A.temporada.isin(EXC)]

def fit(X, y, off, lam):
    def f(w):
        p = expit(off + w[0] + X @ w[1:]); g = p - y
        return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + lam * np.sum(w[1:] ** 2), np.concatenate([[g.sum()], X.T @ g + 2 * lam * w[1:]])
    return minimize(f, np.zeros(X.shape[1] + 1), jac=True, method='L-BFGS-B').x
def std(tr, te, cols):
    mu = tr[cols].mean().fillna(0); sd = tr[cols].std().replace(0, 1).fillna(1)
    return ((tr[cols] - mu) / sd).fillna(0).values, ((te[cols] - mu) / sd).fillna(0).values
def escolhe_lam(tr, cols, filtro):
    ts = sorted(tr.temporada.unique()); best, bl = 1, 1e9
    for lam in LAMS:
        e = []
        for v in ts[-3:]:
            b = tr[tr.temporada == v]
            a = tr[(tr.temporada < v) & (tr.conhecido <= b.D.min())] if filtro else tr[tr.temporada < v]  # validação interna com desfecho conhecido
            if a.temporada.nunique() < 2: continue
            X, Z = std(a, b, cols); w = fit(X, a.alta.values, a.off.values, lam)
            e.append(np.mean((expit(b.off.values + w[0] + Z @ w[1:]) - b.alta.values) ** 2))
        if e and np.mean(e) < bl: bl, best = np.mean(e), lam
    return best
LAMLOG = []
def modelo(tr, te, cols, log=None):
    best = escolhe_lam(tr, cols, True)
    if log is not None and o.comparar: log.append((best, escolhe_lam(tr, cols, False)))
    X, Z = std(tr, te, cols); w = fit(X, tr.alta.values, tr.off.values, best)
    return expit(te.off.values + w[0] + Z @ w[1:])
def modelo_A(tr, te):
    X, Z = std(tr, te, ['lproj']); w = fit(X, tr.alta.values, np.zeros(len(tr)), 0.01)
    return expit(w[0] + Z @ w[1:])
def treino(sk, te):  # só pares com desfecho conhecido na data mais cedo das previsões de te
    return sk[(sk.temporada >= 2008) & sk.alta.notna() & (sk.conhecido <= te.D.min())]

def roda(cols):
    out = []; lg = []
    for k in KS:
        sk = A[A.k == k]
        for Y in PREV:
            te = sk[sk.temporada == Y]
            if len(te) == 0: continue
            tr = treino(sk, te)
            if tr.temporada.nunique() < 3: continue
            out.append(pd.DataFrame(dict(uf=te.uf.values, temporada=Y, k=k, p=modelo(tr, te, list(cols), lg))))
    if o.comparar: pd.DataFrame(lg, columns=['lam_novo', 'lam_antigo']).to_csv(os.path.join(o.out, 'lam_' + '+'.join(cols) + '.csv'), index=False)
    return '+'.join(cols), pd.concat(out)
CACHE = os.path.join(o.out, 'cache_conjuntos.pkl')
if os.path.exists(CACHE): RES = pd.read_pickle(CACHE)
else:
    with Pool(min(8, os.cpu_count())) as pool: RES = dict(pool.map(roda, CONJ))
    pd.to_pickle(RES, CACHE)
base = []
for k in KS:
    sk = A[A.k == k]
    for Y in PREV:
        te = sk[sk.temporada == Y].copy()
        if len(te) == 0: continue
        tr = treino(sk, te)
        if tr.temporada.nunique() < 3: continue
        te['pA'] = modelo_A(tr, te); base.append(te)
P = pd.concat(base)
for nome, r in RES.items(): P = P.merge(r.rename(columns={'p': 'p_' + nome}), on=['uf', 'temporada', 'k'], how='left')
NOMES = list(RES)
brier = lambda d, c: np.mean((d[c] - d.alta) ** 2)
esc = {}
for Y in AVAL:
    h = P[P.temporada <= Y - 2]; esc[Y] = min(NOMES, key=lambda n: brier(h, 'p_' + n))
esc_final = min(NOMES, key=lambda n: brier(P[P.temporada <= 2024], 'p_' + n))
P['pM'] = [r['p_' + esc[r.temporada]] if r.temporada in esc else np.nan for _, r in P.iterrows()]
P = P[P.temporada.isin(AVAL)].copy()
P.to_csv(os.path.join(o.out, 'msa01_previsoes.csv.gz'), index=False)
seas = sorted(P.temporada.unique())
q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
boots = [list(rng.choice(seas, len(seas))) for _ in range(o.B)]

# triagem e ganho incremental sobre a projeção no mesmo modelo
G = {s: P[P.temporada == s] for s in seas}
def br_by_season(col): return {s: ((G[s][col] - G[s].alta) ** 2).sum() for s in seas}
B0 = br_by_season('p0'); BA = br_by_season('pA'); BP = br_by_season('p_lproj')
def bss(Bn, ref, ix): return 1 - sum(Bn[s] for s in ix) / sum(ref[s] for s in ix)
tri = []
for n in NOMES:
    Bn = br_by_season('p_' + n); row = dict(conjunto=n, n_prev=len(n.split('+')), escolhido_vezes=sum(v == n for v in esc.values()))
    for nm, ref in [('R0', B0), ('A', BA), ('proj', BP)]:
        bb = np.array([bss(Bn, ref, ix) for ix in boots])
        row.update({f'bss_{nm}': bss(Bn, ref, seas), f'bss_{nm}_ic': q(bb), f'chance_{nm}': float(np.mean(bb > 0))})
    tri.append(row)
TRI = pd.DataFrame(tri).sort_values('bss_R0', ascending=False); TRI.to_csv(os.path.join(o.out, 'msa01_triagem.csv'), index=False)

# acerto, sensibilidade e especificidade por semana
for m in ['p0', 'pA', 'pM']:
    P['ok_' + m] = ((P[m] >= 0.5).astype(int) == P.alta).astype(int); P['tp_' + m] = ((P[m] >= 0.5) & (P.alta == 1)).astype(int); P['tn_' + m] = ((P[m] < 0.5) & (P.alta == 0)).astype(int)
pv = lambda col, d=P: d.pivot_table(index='temporada', columns='k', values=col, aggfunc='sum').reindex(columns=KS).fillna(0)
K = {m: pv('ok_' + m) for m in ['p0', 'pA', 'pM']}; TP = {m: pv('tp_' + m) for m in ['pA', 'pM']}; TN = {m: pv('tn_' + m) for m in ['pA', 'pM']}
N = P.pivot_table(index='temporada', columns='k', values='ok_pM', aggfunc='count')[KS]
NP = P[P.alta == 1].pivot_table(index='temporada', columns='k', values='ok_pM', aggfunc='count').reindex(index=seas, columns=KS).fillna(0)
NN = P[P.alta == 0].pivot_table(index='temporada', columns='k', values='ok_pM', aggfunc='count').reindex(index=seas, columns=KS).fillna(0)
BR = {m: P.assign(e=(P[m] - P.alta) ** 2).pivot_table(index='temporada', columns='k', values='e', aggfunc='sum')[KS] for m in ['p0', 'pA', 'pM']}
DEC = P[P.alta == 1].pivot_table(index='temporada', columns='k', values='decidido', aggfunc='sum').reindex(index=seas, columns=KS).fillna(0)
def inicio(acc):
    w = None
    for i in range(len(KS) - 1, -1, -1):
        if acc[i] >= 0.75: w = i
        else: break
    return w
def calc(ix):
    n = N.loc[ix].sum().values
    return ({m: K[m].loc[ix].sum().values / n for m in K}, {m: BR[m].loc[ix].sum().values / n for m in BR},
            DEC.loc[ix].sum().values / NP.loc[ix].sum().values)
acc, bri, dec = calc(seas); BT = [calc(ix) for ix in boots]
res = []
for i, k in enumerate(KS):
    am = np.array([b[0]['pM'][i] for b in BT]); aa = np.array([b[0]['pA'][i] for b in BT])
    accs = {m: (K[m][k] / N[k]) for m in ['pA', 'pM']}
    res.append(dict(k=k, n=int(N[k].sum()), acerto_M=acc['pM'][i], acerto_M_ic=q(am), chance_M=float(np.mean(am >= 0.75)),
                    acerto_A=acc['pA'][i], acerto_A_ic=q(aa), chance_A=float(np.mean(aa >= 0.75)), acerto_R0=acc['p0'][i],
                    sens_M=TP['pM'][k].sum() / NP[k].sum(), espec_M=TN['pM'][k].sum() / NN[k].sum(), sens_A=TP['pA'][k].sum() / NP[k].sum(), espec_A=TN['pA'][k].sum() / NN[k].sum(),
                    acerto_M_temp_min=float(accs['pM'].min()), acerto_M_temp_max=float(accs['pM'].max()), acerto_A_temp_min=float(accs['pA'].min()), acerto_A_temp_max=float(accs['pA'].max()),
                    bss_M_R0=1 - bri['pM'][i] / bri['p0'][i], bss_M_A=1 - bri['pM'][i] / bri['pA'][i], altas_evidentes=dec[i]))
R = pd.DataFrame(res); R.to_csv(os.path.join(o.out, 'msa01_por_semana.csv'), index=False)

def evid(d):
    e = [i for i in range(len(KS)) if d[i] >= o.decidido]
    return (min(e), False) if e else (len(KS), True)   # (semana de evidência, censurada?)
def janela(a, d):
    i0 = inicio(a); ke, cens = evid(d)
    if i0 is None or i0 >= ke: return i0, ke, cens, 0
    return i0, ke, cens, ke - i0
J = {}
for m in ['pM', 'pA']:
    i0, ke, cens, ant = janela(acc[m], dec); bj = [janela(b[0][m], b[2]) for b in BT]
    av = np.array([x[3] for x in bj], float)
    J[m] = dict(inicio=i0, evidencia=ke, censurada=cens, antecedencia=ant, antecedencia_ic=q(av), frac_boot_sem_janela=float(np.mean(av == 0)),
                inicio_ic=q([x[0] if x[0] is not None else len(KS) for x in bj]), frac_boot_sem_inicio=float(np.mean([x[0] is None for x in bj])))
    lo = np.array([r[0] for r in R[('acerto_M_ic' if m == 'pM' else 'acerto_A_ic')]])
    i0s = inicio(lo); J[m]['inicio_estrito'] = i0s; J[m]['antecedencia_estrita'] = (max(ke - i0s, 0) if i0s is not None else 0)
J['composicao_final'] = esc_final; J['escolha_por_temporada'] = {int(k): v for k, v in esc.items()}; J['decidido_limiar'] = o.decidido

# antecedência por temporada alta, em relação à contagem e ao pico
PK = {(r.uf, r.temporada): int(r.k_pico) for r in pd.read_csv(o.pico, dtype={'uf': str}).itertuples()}
def lead_tab(col):
    out = []
    for (uf, Y), g in P[P.alta == 1].groupby(['uf', 'temporada']):
        g = g.set_index('k').sort_index(); ev = g.index[g.decidido == 1]
        kc = int(ev.min()) if len(ev) else 43
        yes = (g[col] >= 0.5).reindex(range(43)).fillna(False).values
        km = None
        for j in range(min(kc, 43) - 1, -1, -1):
            if yes[j]: km = j
            else: break
        kp = PK.get((uf, Y))
        out.append(dict(uf=uf, temporada=Y, k_contagem=kc, contagem_censurada=int(kc >= 43), k_modelo=km, k_pico=kp,
                        antecedencia=(kc - km) if km is not None else 0, antes_do_pico=(kp - km) if (km is not None and kp is not None) else None))
    return pd.DataFrame(out)
for m in ['pM', 'pA']:
    L = lead_tab(m); L.to_csv(os.path.join(o.out, f'msa01_antecedencia_{m[1]}.csv'), index=False)
    Ls = {s: L[L.temporada == s] for s in seas}
    def est(ix):
        x = pd.concat([Ls[s] for s in ix]); return float(np.median(x.antecedencia)), float(np.mean(x.antecedencia >= 4)), float(np.mean(x.antes_do_pico.fillna(-1) > 0))  # denominador: todas as temporadas altas
    bt = [est(ix) for ix in boots]; e0 = est(seas)
    i0 = J[m]['inicio']; fa = float(np.mean(P[(P.alta == 0) & (P.k == i0)][m] >= 0.5)) if i0 is not None else None
    J[m].update(antecedencia_mediana=e0[0], antecedencia_mediana_ic=q([b[0] for b in bt]), frac_4mais=e0[1], frac_4mais_ic=q([b[1] for b in bt]),
                frac_antes_do_pico=e0[2], frac_antes_do_pico_ic=q([b[2] for b in bt]), alarme_falso_no_inicio=fa,
                sens_no_inicio=float(R.loc[i0, 'sens_' + m[1]]) if i0 is not None else None)
json.dump(J, open(os.path.join(o.out, 'msa01_janela.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(TRI[['conjunto', 'bss_R0', 'chance_R0', 'bss_A', 'chance_A', 'bss_proj', 'chance_proj', 'escolhido_vezes']].round(3).to_string())
print(R[['k', 'acerto_M', 'chance_M', 'acerto_A', 'chance_A', 'acerto_R0', 'sens_M', 'espec_M', 'sens_A', 'altas_evidentes']].round(3).to_string())
print(json.dumps(J, indent=1, default=float))

pr = A[A.D == pd.Timestamp('2026-11-01')].copy()
if len(pr) and not EXC:
    cols = esc_final.split('+'); outp = []
    for k, g in pr.groupby('k'):
        sk = A[(A.k == k) & (A.temporada >= 2008) & A.alta.notna() & (A.conhecido <= pd.Timestamp('2026-11-01'))]
        g = g.copy(); g['pA'] = modelo_A(sk, g); g['pM'] = modelo(sk, g, cols); outp.append(g)
    pd.concat(outp)[['uf', 'temporada', 'k', 'D', 'corte', 'p0', 'pA', 'pM', 'proj_inc', 'fora', 'oni', 'decidido']].to_csv(os.path.join(o.out, 'msa01_previsao_2026_27.csv'), index=False)
