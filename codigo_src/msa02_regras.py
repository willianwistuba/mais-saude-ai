"""Simulação v4: regras de reteste executáveis com a saída do kit Roche.

O kit da rede quantifica a partir de 20 cópias/mL (LLOQ). Abaixo disso, a mistura pode
sair como "detectado, menor que 20", sem valor numérico. Regras comparadas:
  D  = retestar qualquer mistura detectada (inclui detectado < 20);
  Q20 = retestar só misturas quantificadas com 20 cópias/mL ou mais.
Parâmetros de distribuição e ensaio iguais ao msa02_base.py.
"""
import numpy as np
import msa02_base as s

LLOQ = 20.0
FAIXAS = [(200, 250, "200-249"), (250, 300, "250-299"), (300, 500, "300-499"),
          (500, 1000, "500-999"), (1000, np.inf, ">=1000")]


def regra(med, nome):
    if nome == "D":
        return med > 0
    if nome == "Q20":
        return med >= LLOQ
    raise ValueError(nome)


def transversal(vl, k, nome, rng):
    """Reteste é nova medição independente da amostra guardada."""
    n = len(vl) // k * k
    V = vl[:n].reshape(-1, k)
    med = s.medir(V.mean(1), rng)
    flag = regra(med, nome)
    chama = (s.medir(V, rng) >= 200) & flag[:, None]
    return dict(reacoes=V.shape[0] + flag.sum() * k, chama=chama.ravel(),
                gat=flag.mean(), n=n)


def resumo(vl, r):
    v = vl[:r["n"]]
    o = dict(reac=r["reacoes"] / r["n"], gat=r["gat"])
    for lo, hi, lab in FAIXAS:
        m = (v >= lo) & (v < hi)
        o[lab] = r["chama"][m].mean()
    o["200-499"] = r["chama"][(v >= 200) & (v < 500)].mean()
    return o


def discordancias(vl, k, nome, rng):
    """Discordâncias nos dois sentidos, com medidas independentes nos dois braços."""
    n = len(vl) // k * k
    v = vl[:n]
    ind = s.medir(v, rng) >= 200
    V = v.reshape(-1, k)
    flag = np.repeat(regra(s.medir(V.mean(1), rng), nome), k)
    grp = flag & (s.medir(v, rng) >= 200)
    linhas = []
    for lo, hi, lab in FAIXAS[:4]:
        m = (v >= lo) & (v < hi)
        so_ind = (ind & ~grp & m).sum()
        so_grp = (grp & ~ind & m).sum()
        sem_reteste = (ind & ~flag & m).sum()
        linhas.append((lab, m.sum(), so_ind, so_grp, sem_reteste))
    return linhas


if __name__ == "__main__":
    for cen, cfg in s.CENARIOS.items():
        s.CFG.update(cfg)
        rng = np.random.default_rng(11)
        vl = s.gerar(rng)
        ind = s.resumo("i", s.individual(vl, rng), vl)
        rng_i = np.random.default_rng(12)
        ind_r = dict(reacoes=len(vl), chama=s.medir(vl, rng_i) >= 200, gat=np.nan, n=len(vl))
        oi = resumo(vl, ind_r)
        print(f"\n=== Cenário {cen} ===")
        cab = "".join(f"{l:>9}" for _, _, l in FAIXAS)
        print(f"{'Estratégia':<26}{'econ':>6}{'gat':>6}{'200-499':>9}{cab}")
        print(f"{'Individual':<26}{0:>6.0%}{'-':>6}{oi['200-499']:>9.1%}"
              + "".join(f"{oi[l]:>9.1%}" for _, _, l in FAIXAS))
        for k in (3, 4, 5):
            for nome in ("D", "Q20"):
                o = resumo(vl, transversal(vl, k, nome, rng))
                print(f"{f'Grupo de {k}, regra {nome}':<26}{1 - o['reac']:>6.0%}{o['gat']:>6.0%}"
                      f"{o['200-499']:>9.1%}" + "".join(f"{o[l]:>9.1%}" for _, _, l in FAIXAS))
        if cen.startswith("base"):
            for k, nome in ((4, "D"), (4, "Q20")):
                print(f"\nDiscordâncias, grupo de {k}, regra {nome} (medidas independentes):")
                print("faixa      n     só individual  só grupo  individual detecta e grupo sem reteste")
                for lab, n, a, b, c in discordancias(vl, k, nome, np.random.default_rng(21)):
                    print(f"{lab:<9}{n:>6}{a:>14}{b:>10}{c:>10}")
