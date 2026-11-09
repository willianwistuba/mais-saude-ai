"""Números consolidados do rascunho da MSA-02 (cenário principal: bula do cobas HIV-1 5800).
Rodar: python3 msa02_simulacao.py. Depende de msa02_base.py, msa02_regras.py e msa02_longitudinal.py."""
import numpy as np
import msa02_base as s, msa02_regras as v4, msa02_longitudinal as L

CEN = {
    "5800 (principal)": (13.2, [20, 50, 200, 400, 1000, 1e4, 1e5], [0.25, 0.191, 0.116, 0.102, 0.092, 0.081, 0.084]),
    "4800 (sensibilidade)": (14.2, [20, 77, 308, 770, 7700, 77000], [0.25, 0.19, 0.09, 0.09, 0.06, 0.05]),
    "robustez (DP 0,40 perto do limite)": (14.0, [20, 50, 200, 1000], [0.40, 0.40, 0.20, 0.12]),
}


def usar(nome):
    lod, xs, ys = CEN[nome]
    X = np.log10(xs)
    s.sd_de = lambda c: np.interp(np.log10(np.maximum(c, 1)), X, ys)
    s.CFG["lod95"] = lod


def mpa(vl, k, T, rng):
    """Decodificação quantitativa: só usa valores quantificados (>=20 cp/ml);
    'detectado <20' entra como 0, o que não muda a decisão com T=250."""
    n = len(vl) // k * k
    V = vl[:n].reshape(-1, k)
    med = s.medir(V.mean(1), rng)
    med = np.where(med >= 20, med, 0.0)
    reac, chama = V.shape[0], np.zeros(V.shape, bool)
    for g in np.flatnonzero(k * med >= T):
        S = k * med[g]
        for j in rng.permutation(k):
            if S < T:
                break
            reac += 1
            mj = s.medir(V[g, j], rng)
            chama[g, j] = mj >= 200
            S -= mj if mj >= 20 else 0
    return dict(reacoes=reac, chama=chama.ravel(), gat=np.nan, n=n)


def concentrado(vl, k, rec, falha, rng):
    n = len(vl) // k * k
    V = vl[:n].reshape(-1, k)
    R = s.recuperacao(V.shape[0], rec, falha, rng)
    med = s.medir(R * V.sum(1), rng)            # 1 mL de cada amostra concentrado
    flag = med > 0                              # regra D
    chama = (s.medir(V, rng) >= 200) & flag[:, None]
    return dict(reacoes=V.shape[0] + flag.sum() * k, chama=chama.ravel(), gat=flag.mean(), n=n)


def linha(nome, o):
    return (f"{nome:<44}{1 - o['reac']:>6.1%}  " + "  ".join(
        f"{o[l]:>6.1%}" for l in ("200-249", "250-299", "300-499", "500-999", ">=1000")))


if __name__ == "__main__":
    for cen in CEN:
        usar(cen)
        rng = np.random.default_rng(11)
        vl = s.gerar(rng)
        ind = v4.resumo(vl, dict(reacoes=len(vl), chama=s.medir(vl, np.random.default_rng(12)) >= 200,
                                 gat=np.nan, n=len(vl)))
        print(f"\n===== {cen} | transversal (400 mil coletas) =====")
        print(f"{'Estratégia':<44}{'econ':>6}  200-249 250-299 300-499 500-999  >=1000")
        print(linha("Individual", ind))
        for k, r in ((3, "D"), (4, "D"), (4, "Q20"), (5, "D"), (8, "D")):
            print(linha(f"Grupo de {k}, regra {r}", v4.resumo(vl, v4.transversal(vl, k, r, rng))))
        print(linha("Grupo de 5, decodificação (T=250)", v4.resumo(vl, mpa(vl, 5, 250, rng))))
        for f in (0.0, 0.02, 0.05):
            print(linha(f"Concentrado k=4, R=0,7, falhas {f:.0%}", v4.resumo(vl, concentrado(vl, 4, 0.7, f, rng))))
        if cen.startswith("5800"):
            for k, r in ((4, "D"), (4, "Q20")):
                print(f"Discordâncias grupo {k} regra {r}:")
                for lab, n, a, b, c in v4.discordancias(vl, k, r, np.random.default_rng(21)):
                    print(f"   {lab}: n={n} só individual {a} só grupo {b} sem reteste {c}")
        L.N = 200_000
        a = L.resumir("i", L.simular("individual", seed=3))
        print(f"--- longitudinal ({a['episodios']} episódios): individual <=60d {a['ate60']:.1%} "
              f"até rotina seguinte {a['ate_prox']:.1%} mediana {a['mediana']:.0f}d")
        for nome, k, g in (("4 D", 4, None), ("4 Q20", 4, "Q20"), ("3 D", 3, None)):
            b = L.resumir("g", L.simular("grupo", k, g, seed=3))
            print(f"grupo {nome}: econ {1 - b['reac'] / a['reac']:.1%} <=60d {b['ate60']:.1%} "
                  f"até rotina seguinte {b['ate_prox']:.1%} mediana {b['mediana']:.0f}d")
    usar("5800 (principal)")
    print("\n===== Sensibilidade longitudinal (5800, grupo 4 regra D) =====")
    for h in (0.03, 0.06, 0.10):
        for pb in (0.04, 0.08):
            L.RISCO_ANUAL, L.P_BLIP = h, pb
            a = L.resumir("i", L.simular("individual", seed=3))
            b = L.resumir("g", L.simular("grupo", 4, None, seed=3))
            print(f"risco {h:.0%} blip {pb:.0%}: econ {1 - b['reac'] / a['reac']:.0%} <=60d ind {a['ate60']:.1%} grupo {b['ate60']:.1%}")
    L.RISCO_ANUAL, L.P_BLIP = 0.06, 0.04
