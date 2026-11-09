"""Simulação longitudinal exploratória: carga viral do HIV em grupo vs individual.

Coorte de adultos suprimidos acompanhada por 24 meses, coletas de rotina semestrais
(meses 6, 12, 18 e 24). Rebotes sustentados surgem com risco anual constante; viremias
baixas transitórias (50 a 199) aparecem ao acaso em cada coleta. Coleta elevada (>=200)
leva a nova coleta em 4 semanas; dois resultados >=200 confirmam a falha.
Ensaio e distribuição de níveis seguem o msa02_base.py. Parâmetros de dinâmica supostos.
"""
import numpy as np
import msa02_base as s

N = 200_000
RISCO_ANUAL = 0.06        # rebote sustentado >=200 entre suprimidos (suposto)
P_BLIP = 0.04             # viremia transitória 50-199 por coleta (Figura 76: 4%)
P_FALHA_BAIXA = 2 / 7     # fração dos rebotes entre 200 e 999 (Figura 76: 2% vs 5%)
RODADAS = [6, 12, 18, 24]
LAUDO = 7 / 30            # prazo do laudo individual (meses)
RODADA_EXTRA = 5 / 30     # rodada adicional de bancada quando o grupo vai a reteste
CONF = 28 / 30            # nova coleta 28 dias após o laudo (meses)


def coorte(rng):
    onset = rng.exponential(12 / RISCO_ANUAL, N)            # meses
    baixa = rng.random(N) < P_FALHA_BAIXA
    vf = np.where(baixa, 10 ** rng.uniform(np.log10(200), 3, N),
                  10 ** rng.uniform(3, 6, N))
    return onset, vf


def vl_em(t, onset, vf, rng):
    v = np.where(onset <= t, vf, 0.0)
    blip = (onset > t) & (rng.random(N) < P_BLIP)
    v[blip] = 10 ** rng.uniform(np.log10(50), np.log10(200), blip.sum())
    return v


def simular(estrategia, k=4, gatilho=50, seed=3):
    rng = np.random.default_rng(seed)
    onset, vf = coorte(np.random.default_rng(1))            # mesma coorte para todos
    ativo = np.ones(N, bool)
    t_conf = np.full(N, np.nan)
    primeira_elev = np.full(N, np.nan)                     # 1a rodada com VL real >=200
    reacoes = 0
    for t in RODADAS:
        v = vl_em(t, onset, vf, rng)
        idx = np.flatnonzero(ativo)
        nova = np.isnan(primeira_elev[idx]) & (v[idx] >= 200)
        primeira_elev[idx[nova]] = t
        if estrategia == "individual":
            elevado = s.medir(v[idx], rng) >= 200
            prazo = np.full(len(idx), LAUDO)
            reacoes += len(idx)
        else:
            rng.shuffle(idx)
            n = len(idx) // k * k
            resto = idx[n:]
            G = idx[:n].reshape(-1, k)
            med = s.medir(v[G].mean(1), rng)
            flag = (med > 0) if gatilho is None else ((med >= 20.0) if gatilho == 'Q20' else (med * k >= gatilho))
            reacoes += G.shape[0] + flag.sum() * k + len(resto)
            elevado_G = (s.medir(v[G], rng) >= 200) & flag[:, None]
            elevado_r = s.medir(v[resto], rng) >= 200
            idx = np.concatenate([G.ravel(), resto])
            elevado = np.concatenate([elevado_G.ravel(), elevado_r])
            prazo = np.concatenate([np.repeat(np.where(flag, LAUDO + RODADA_EXTRA, LAUDO), k),
                                    np.full(len(resto), LAUDO)])
        # confirmação individual em nova coleta
        e = idx[elevado]
        tc = t + prazo[elevado] + CONF
        v2 = np.where(onset[e] <= tc, vf[e], 0.0)
        conf = s.medir(v2, rng) >= 200
        reacoes += len(e)
        t_conf[e[conf]] = tc[conf] + LAUDO
        ativo[e[conf]] = False
    return dict(t_conf=t_conf, primeira=primeira_elev, onset=onset, reacoes=reacoes)


def resumir(nome, r):
    ep = ~np.isnan(r["primeira"]) & (r["primeira"] <= 18)  # há uma rodada seguinte observável
    d = (r["t_conf"][ep] - r["primeira"][ep]) * 30           # dias
    d = np.where(np.isnan(d), np.inf, d)
    out = dict(nome=nome, episodios=ep.sum(), reac=r["reacoes"],
               ate60=(d <= 60).mean(), ate90=(d <= 90).mean(),
               ate_prox=(d <= 6 * 30 + 60).mean(),
               mediana=np.median(d[np.isfinite(d)]))
    return out


if __name__ == "__main__":
    for cen, cfg in s.CENARIOS.items():
        s.CFG.update(cfg)
        res = [resumir("Individual", simular("individual")),
               resumir("Grupo de 4, gatilho 50", simular("grupo", 4, 50)),
               resumir("Grupo de 4, qualquer detecção", simular("grupo", 4, None)),
               resumir("Grupo de 3, gatilho 100", simular("grupo", 3, 100))]
        base = res[0]["reac"]
        print(f"\n=== Cenário {cen} | {res[0]['episodios']} episódios ===")
        print(f"{'Estratégia':<32}{'reações':>9}{'econ':>6}{'<=60d':>8}{'<=90d':>8}{'<=próx.':>9}{'mediana':>9}")
        for o in res:
            print(f"{o['nome']:<32}{o['reac']:>9}{1 - o['reac'] / base:>6.0%}{o['ate60']:>8.1%}"
                  f"{o['ate90']:>8.1%}{o['ate_prox']:>9.1%}{o['mediana']:>8.0f}d")
