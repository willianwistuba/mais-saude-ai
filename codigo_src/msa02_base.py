"""Simulação exploratória v3: carga viral do HIV em grupo, com parâmetros brasileiros.

Fontes dos parâmetros:
- Distribuição por faixa (PVHA com 2 anos ou mais, em TARV há pelo menos 6 meses, Brasil,
  jan. a set. 2022): <50: 89%; 50-199: 4%; 200-999: 2%; 1.000-9.999: 2%; >=10.000: 3%.
  Relatório de Monitoramento Clínico do HIV 2022, Figura 76 (barra BR).
- Ensaio da rede convencional: Roche cobas 4800/5800, limite de detecção 14,2 e 13,2
  cópias/mL (Nota Técnica 286/2023). Imprecisão: DP < 0,19 log10 (cobas 4800, J Clin Virol
  2019) e 0,05 a 0,34 log10, maior em cargas baixas (cobas 5800, Microbiol Spectr 2022).
- Preço por exame na rede convencional: R$ 65,84 (Nota Técnica 129/2025, Tabela 1).
Formas dentro de cada faixa (log-uniforme) e a curva de imprecisão são suposições.
"""
import numpy as np

N = 400_000
FAIXAS = [(200, 500, "200-499"), (500, 1000, "500-999"), (1000, np.inf, ">=1000")]
BANDAS = [(0.89, None), (0.04, (50, 200)), (0.02, (200, 1000)),
          (0.02, (1000, 10000)), (0.03, (10000, 1e6))]
PRECO = 65.84
EXAMES_ANO = 1_200_000   # quantidade contratada (termo de referência de 2020); ordem de grandeza

# Versão 1.1: fração das coletas abaixo de 50 cp/mL com RNA residual (log-uniforme de 1 a 49 cp/mL).
# Na versão 1, todas eram zero (RESIDUAL_FRAC = 0). Só sorteia quando a fração é positiva,
# para que a versão 1 continue reproduzível.
RESIDUAL_FRAC = 0.0
RESIDUAL_MIN = 1.0       # versão 1.2: limite inferior da faixa sorteada (1, 20 ou 40 cp/mL)
RESIDUAL_MAX = 49.0


def residual(vl, rng):
    """Põe RNA residual (log-uniforme entre RESIDUAL_MIN e RESIDUAL_MAX) numa fração RESIDUAL_FRAC das cargas iguais a zero."""
    if RESIDUAL_FRAC <= 0:
        return vl
    z = np.flatnonzero(vl == 0)
    k = z[rng.random(z.size) < RESIDUAL_FRAC]
    vl[k] = 10 ** rng.uniform(np.log10(RESIDUAL_MIN), np.log10(RESIDUAL_MAX), k.size)
    return vl


CFG = dict(lod95=14.0, sd_baixo=0.30, sd_200=0.15, sd_alto=0.10)
CENARIOS = {
    "base (DP 0,30 perto do limite)": dict(lod95=14.0, sd_baixo=0.30, sd_200=0.15, sd_alto=0.10),
    "pessimista (DP 0,40 perto do limite)": dict(lod95=14.0, sd_baixo=0.40, sd_200=0.20, sd_alto=0.12),
}


def gerar(rng):
    u = rng.random(N)
    vl = np.zeros(N)
    acum = 0.0
    for p, faixa in BANDAS:
        m = (u >= acum) & (u < acum + p)
        acum += p
        if faixa:
            lo, hi = faixa
            vl[m] = 10 ** rng.uniform(np.log10(lo), np.log10(hi), m.sum())
    return residual(vl, rng)


def sd_de(c):
    """Imprecisão (DP em log10) em função da concentração na reação."""
    lc = np.log10(np.maximum(c, 1))
    return np.interp(lc, [np.log10(50), np.log10(200), 3.0],
                     [CFG["sd_baixo"], CFG["sd_200"], CFG["sd_alto"]])


def medir(conc, rng):
    conc = np.asarray(conc, float)
    p = 1 - np.exp(-3.0 * conc / CFG["lod95"])
    det = rng.random(conc.shape) < p
    return np.where(det, conc * 10 ** (rng.normal(0, 1, conc.shape) * sd_de(conc)), 0.0)


def recuperacao(n, media, falha, rng):
    if media is None:
        return np.ones(n)
    r = rng.beta(media * 20, (1 - media) * 20, n)
    ruim = rng.random(n) < falha
    r[ruim] = rng.uniform(0, 0.2, ruim.sum())
    return r


def individual(vl, rng):
    return dict(reacoes=len(vl), chama=medir(vl, rng) >= 200, gat=np.nan, n=len(vl))


def grupo(vl, k, gatilho, rng, aliq=None, rec=None, falha=0.0):
    aliq = 1 / k if aliq is None else aliq
    n = len(vl) // k * k
    V = vl[:n].reshape(-1, k)
    R = recuperacao(V.shape[0], rec, falha, rng)
    med = medir(R * aliq * V.sum(1), rng)
    S = med / ((1.0 if rec is None else rec) * aliq)
    flag = (med > 0) if gatilho is None else (S >= gatilho)
    chama = (medir(V, rng) >= 200) & flag[:, None]
    return dict(reacoes=V.shape[0] + flag.sum() * k, chama=chama.ravel(), gat=flag.mean(), n=n)


def minipool_alg(vl, k, T, rng):
    n = len(vl) // k * k
    V = vl[:n].reshape(-1, k)
    med = medir(V.mean(1), rng)
    reac = V.shape[0]
    chama = np.zeros(V.shape, bool)
    for g in np.flatnonzero(med > 0):
        S = k * med[g]
        for j in rng.permutation(k):
            if S < T:
                break
            reac += 1
            mj = medir(V[g, j], rng)
            chama[g, j] = mj >= 200
            S -= mj
    return dict(reacoes=reac, chama=chama.ravel(), gat=(med > 0).mean(), n=n)


def resumo(nome, r, vl):
    v = vl[:r["n"]]
    o = dict(nome=nome, reac=r["reacoes"] / r["n"], gat=r["gat"])
    for lo, hi, lab in FAIXAS:
        m = (v >= lo) & (v < hi)
        o[lab] = r["chama"][m].mean()
    o["falso200"] = r["chama"][v < 200].mean()
    return o


def rodar(nome, cfg, seed=11):
    CFG.update(cfg)
    rng = np.random.default_rng(seed)
    vl = gerar(rng)
    linhas = [resumo("Individual", individual(vl, rng), vl)]
    for k in (3, 4, 5, 6, 8):
        for g in (None, 50, 100, 150):
            gl = "qualquer detecção" if g is None else f"gatilho {g}"
            linhas.append(resumo(f"Comum k={k}, {gl}", grupo(vl, k, g, rng), vl))
    linhas.append(resumo("k=5 + algoritmo (T=250)", minipool_alg(vl, 5, 250, rng), vl))
    for falha in (0.0, 0.02):
        linhas.append(resumo(f"Concentrado k=4 (4 mL), R=0,7, falhas {falha:.0%}, gatilho 100",
                             grupo(vl, 4, 100, rng, aliq=1.0, rec=0.7, falha=falha), vl))
    ind = linhas[0]
    print(f"\n=== Cenário {nome} ===")
    print(f"{'Estratégia':<62}{'reac':>6}{'econ':>6}{'gat':>6}{'200-499':>9}{'500-999':>9}{'>=1000':>8}")
    for o in linhas:
        g = "  -  " if np.isnan(o["gat"]) else f"{o['gat']:.0%}"
        sem_perda = (o["200-499"] >= ind["200-499"] - 0.015) and (o["500-999"] >= ind["500-999"] - 0.01)
        marca = " *" if sem_perda and o["nome"] != "Individual" else ""
        print(f"{o['nome']:<62}{o['reac']:>6.3f}{1 - o['reac']:>6.0%}{g:>6}"
              f"{o['200-499']:>9.1%}{o['500-999']:>9.1%}{o['>=1000']:>8.1%}{marca}")
    cand = [o for o in linhas[1:] if o["200-499"] >= ind["200-499"] - 0.015
            and o["500-999"] >= ind["500-999"] - 0.01 and "Concentrado" not in o["nome"]]
    best = min(cand, key=lambda o: o["reac"])
    econ = 1 - best["reac"]
    print(f"\nMelhor sem perda (tolerância 1,5 ponto em 200-499): {best['nome']} | economia {econ:.0%}")
    print(f"Com {EXAMES_ANO:,} exames/ano a R$ {PRECO}: cerca de R$ {econ * EXAMES_ANO * PRECO / 1e6:.0f} milhões/ano "
          f"em reações, antes de custos de manuseio")
    return best


if __name__ == "__main__":
    for nome, cfg in CENARIOS.items():
        rodar(nome, cfg)
