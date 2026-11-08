#!/usr/bin/env python3
"""MSA-01: apuração semanal por UF e temporada, reconstruindo o que estava disponível em cada data.
Temporada por UF: começa na semana epidemiológica de vale da UF (menor fração média de casos prováveis, média móvel
de 5 semanas, 2007 a 2013); com --nacional, começa na semana 27 para todas. Para cada UF, temporada e semana k
(0 a 42) da temporada, com corte C = D - defasagem: notificações disponíveis, previsores e "evidente pela contagem".
Só casos prováveis (notificações não descartadas) entram nas contagens, em todos os anos. Desfecho de uma temporada
conhecido a partir do fim da temporada + defasagem + 8 semanas; R0 e a fração esperada da projeção usam só desfechos conhecidos.
Uso: python3 msa01_apuracao.py <base.csv.gz> <populacao_uf_ano.csv> <clima_uf_dia.csv.gz> <oni.data> <defasagem> <saida_dir> [--nacional] [--excluir 2015,2016]
"""
import sys, os, json, numpy as np, pandas as pd
BASE, POP, CLIMA, ONI, LAG, OUT = sys.argv[1:7]; LAG = int(LAG); NAC = '--nacional' in sys.argv; os.makedirs(OUT, exist_ok=True)
EXC = [int(x) for x in sys.argv[sys.argv.index('--excluir') + 1].split(',')] if '--excluir' in sys.argv else []
TODAS = '--todas' in sys.argv  # S5: previsores de contagem com todas as notificações onde o arquivo as traz
UFS = ['11','12','13','14','15','16','17','21','22','23','24','25','26','27','28','29','31','32','33','35','41','42','43','50','51','52','53']
DAY = pd.Timedelta(days=1); WK = 7 * DAY; KMAX = 42; FIM_DADOS = pd.Timestamp('2026-11-01')

def ew(d):  # semana epidemiológica (domingo a sábado; ano = ano da quarta-feira)
    w = d + 3 * DAY; jan1 = pd.Timestamp(w.year, 1, 1); first = jan1 - pd.Timedelta(days=(jan1.dayofweek + 1) % 7)
    if (first + 3 * DAY).year < w.year: first += WK
    return w.year, (d - first).days // 7 + 1
def domingo(Y, s):  # domingo de início da semana epidemiológica s do ano Y
    jan1 = pd.Timestamp(Y, 1, 1); first = jan1 - pd.Timedelta(days=(jan1.dayofweek + 1) % 7)
    if (first + 3 * DAY).year < Y: first += WK
    return first + (s - 1) * WK

pop = pd.read_csv(POP, dtype={'uf': str}).set_index(['uf', 'ano'])['pop']
P = lambda uf, a: float(pop.get((uf, min(max(a, 2006), 2025))))
b = pd.read_csv(BASE, dtype={'uf': str}, parse_dates=['sem_sin', 'sem_not', 'sem_dig']); b = b[b.uf.isin(UFS) & ((b.grupo == 'provavel') | TODAS)].copy()
if 'cap' not in b.columns: b['cap'] = 0  # emenda 6: capital (1) e interior (0)

# semana de vale por UF (2007 a 2013)
pv = b[b.grupo == 'provavel'].groupby(['uf', 'sem_sin']).n.sum().reset_index()
E = [ew(d) for d in pv.sem_sin]; pv['ano'] = [e[0] for e in E]; pv['sem'] = [min(e[1], 52) for e in E]
pv = pv[pv.ano.between(2007, 2013)]
t = pv.groupby(['uf', 'ano', 'sem']).n.sum().reset_index(); t['f'] = t.n / t.groupby(['uf', 'ano']).n.transform('sum')
m = t.groupby(['uf', 'sem']).f.mean().unstack().reindex(columns=range(1, 53)).fillna(0)
sm = sum(np.roll(m.values, s, axis=1) for s in range(-2, 3)) / 5
VALE = {uf: (27 if NAC else int(m.columns[np.argmin(sm[i])])) for i, uf in enumerate(m.index)}
json.dump(VALE, open(os.path.join(OUT, 'msa01_semana_vale.json'), 'w'))
def S0(uf, Y):
    v = VALE[uf]; return domingo(Y if v >= 27 else Y + 1, v)

# atraso notificação -> digitação: distribuição só de anos anteriores ou iguais ao do arquivo
def refanos(f): return [f] if f < 2013 else (list(range(2013, f + 1)) if f <= 2015 else [2013, 2014, 2015])
okd = b[b.sem_dig.notna()].copy()
okd['d'] = ((okd.sem_dig - okd.sem_not).dt.days // 7).clip(0, 104); okd['m'] = okd.sem_not.dt.month
CDF = {}
for f in sorted(b.arquivo.unique()):
    ref = okd[okd.arquivo.isin(refanos(f))]
    if len(ref) == 0: continue
    gl = np.cumsum(np.bincount(ref.d.values, weights=ref.n.values, minlength=105)); gl /= gl[-1]
    cdf = {}
    for (uf, mm), g in ref.groupby(['uf', 'm']):
        h = np.bincount(g.d.values, weights=g.n.values, minlength=105); cdf[(uf, mm)] = np.cumsum(h) / h.sum()
    CDF[f] = (cdf, gl)
# clima: aptidão térmica e anomalia nos 91 dias climatologicamente mais frios
clima = pd.read_csv(CLIMA, dtype={'uf': str}, parse_dates=['dia']); clima['uf'] = clima.uf.str.zfill(2)
T0, TP, TM = 17.8, 29.1, 34.6; al = 3 * (TP - T0) / (TM - T0); be = 3 - al
T = clima.t2m.values; a = np.zeros_like(T); ok = (T > T0) & (T < TM)
a[ok] = ((T[ok] - T0) / (TP - T0)) ** al * ((TM - T[ok]) / (TM - TP)) ** be; clima['apt'] = a
clima['doy'] = np.minimum(clima.dia.dt.dayofyear, 365)
CL, IV = {}, {}
for uf, g in clima.groupby('uf'):
    g = g.set_index('dia'); CL[uf] = g.apt
    c = g[(g.index.year >= 2006) & (g.index.year <= 2013)].groupby('doy').t2m.mean().reindex(range(1, 366)).interpolate()
    c = pd.Series(np.convolve(np.r_[c.values[-15:], c.values, c.values[:15]], np.ones(31) / 31, 'valid'), index=c.index)
    q = np.convolve(np.r_[c.values, c.values[:90]], np.ones(91), 'valid')  # soma de 91 dias a partir de cada dia
    i0 = int(np.argmin(q)); fr = set(((i0 + np.arange(91)) % 365) + 1)
    an = g.t2m - c.reindex(g.doy.values).values
    IV[uf] = an[g.doy.isin(fr).values]
oni = {}
for ln in open(ONI):
    p = ln.split()
    if len(p) == 13 and p[0].isdigit():
        for i, v in enumerate(p[1:]):
            if float(v) > -99: oni[pd.Period(f'{p[0]}-{i+1:02d}', 'M')] = float(v)

rows, des = [], []
for uf in UFS:
    bu = b[b.uf == uf]
    for Y in range(2007, 2027):
        ini, fim = S0(uf, Y), S0(uf, Y + 1)
        if ini > FIM_DADOS: continue
        g = bu[(bu.sem_sin >= ini) & (bu.sem_sin < fim)]
        popm = (P(uf, ini.year) + P(uf, (fim - DAY).year)) / 2
        if fim <= pd.Timestamp('2026-09-20'):
            pr = g[g.grupo == 'provavel'].n.sum()
            des.append(dict(uf=uf, temporada=Y, inicio=ini.date(), fim=fim.date(), conhecido=(fim + (LAG + 8) * WK).date(), casos_provaveis=int(pr), pop=popm,
                            incidencia=pr / popm * 1e5, alta=int(pr / popm * 1e5 >= 300)))
        n = g.n.values.astype(float); sin = g.sem_sin.values; dig = g.sem_dig.values; nt = g.sem_not
        has = ~pd.isna(g.sem_dig).values; mm = nt.dt.month.values
        cd = np.array([CDF[a][0].get((uf, x), CDF[a][1]) for a, x in zip(g.arquivo.values, mm)]) if len(g) else np.zeros((0, 105))
        baixa = sin < np.datetime64(ini + 13 * WK); prov = (g.grupo == 'provavel').values; capm = (g.cap == 1).values
        for k in range(KMAX + 1):
            D = ini + k * WK
            if D > FIM_DADOS: break
            C = D - LAG * WK
            ons = sin + np.timedelta64(7, 'D') <= np.datetime64(C)
            av = np.zeros(len(g))
            av[has] = (dig[has] + np.timedelta64(7, 'D') <= np.datetime64(C)).astype(float)
            if (~has).any():
                lagw = ((np.datetime64(C) - nt.values[~has]).astype('timedelta64[D]').astype(int) // 7) - 1
                av[~has] = np.where(lagw < 0, 0.0, cd[~has, np.clip(lagw, 0, 104)] if len(cd) else 0.0)
            e = n * av * ons
            wk_ = [e[sin == np.datetime64(C - j * WK)].sum() for j in (4, 3, 2, 1)]
            Cc = D - WK
            ap = CL[uf][(CL[uf].index >= Cc - 56 * DAY) & (CL[uf].index < Cc)].mean()
            iv = IV[uf][(IV[uf].index >= Cc - 365 * DAY) & (IV[uf].index < Cc)].mean()
            yy, w = ew(D)
            rows.append(dict(uf=uf, temporada=Y, k=k, D=D.date(), ano_ew=yy, semana=w, corte=C.date(), disp=e.sum(), disp_prov=e[prov].sum(), disp_baixa=e[baixa].sum(), disp_cap=e[capm].sum(),
                             cresc=np.polyfit(np.arange(4), np.log(np.array(wk_) + 1), 1)[0], apt=ap, inverno=iv,
                             oni=oni.get(D.to_period('M') - 2, np.nan), pop=popm))
    print('UF', uf, 'vale', VALE[uf], flush=True)
A = pd.DataFrame(rows); Dd = pd.DataFrame(des)
Dd['conhecido'] = pd.to_datetime(Dd.conhecido)
fin = Dd.set_index(['uf', 'temporada'])
DK = {(r.uf, r.temporada, r.k): (r.disp, r.disp_baixa, r.disp_cap) for r in A.itertuples()}
proj, fora, deci, p0, capv, intv = [], [], [], [], [], []
for r in A.itertuples():
    D = pd.Timestamp(r.D)
    con = [t for t in range(2007, r.temporada) if (r.uf, t) in fin.index and t not in EXC and fin.loc[(r.uf, t), 'conhecido'] <= D]
    h = [fin.loc[(r.uf, t), 'alta'] for t in con]; p0.append((sum(h) + 1) / (len(h) + 2))
    fr = [DK[(r.uf, t, r.k)][0] / max(fin.loc[(r.uf, t), 'casos_provaveis'], 1) for t in con if (r.uf, t, r.k) in DK]
    gk = np.median(fr) if len(fr) >= 3 else np.nan
    proj.append(r.disp / gk / r.pop * 1e5 if gk and gk > 0 else np.nan)
    prev = [t for t in range(2007, r.temporada) if (r.uf, t, r.k) in DK and t not in EXC]
    fb = [np.log(DK[(r.uf, t, r.k)][1] / fin.loc[(r.uf, t), 'pop'] * 1e5 + 1) for t in prev if (r.uf, t) in fin.index]
    fora.append(np.log(r.disp_baixa / r.pop * 1e5 + 1) - np.median(fb) if len(fb) >= 3 else np.nan)
    # emenda 6: capital e interior, cada um comparado com ele mesmo nas temporadas anteriores (contagens)
    pc = [np.log(DK[(r.uf, t, r.k)][2] + 1) for t in prev if (r.uf, t) in fin.index]
    pi = [np.log(max(DK[(r.uf, t, r.k)][0] - DK[(r.uf, t, r.k)][2], 0) + 1) for t in prev if (r.uf, t) in fin.index]
    capv.append(np.log(r.disp_cap + 1) - np.median(pc) if len(pc) >= 3 else np.nan)
    intv.append(0.0 if r.uf == '53' else (np.log(max(r.disp - r.disp_cap, 0) + 1) - np.median(pi) if len(pi) >= 3 else np.nan))
    deci.append(int(r.disp_prov / r.pop * 1e5 >= 300))
A['proj_inc'] = proj; A['fora'] = fora; A['cap'] = capv; A['int'] = intv; A['decidido'] = deci; A['p0'] = p0
A.to_csv(os.path.join(OUT, 'msa01_apuracao.csv.gz'), index=False); Dd.to_csv(os.path.join(OUT, 'msa01_desfecho.csv'), index=False)
print(VALE)
