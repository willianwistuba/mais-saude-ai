"""Versão 1.1: regra Q20, RNA residual de 25% e denominador comum. Réplicas da MSA-02 no cenário principal (cobas 5800): 40 sementes, intervalo empírico 2,5% a 97,5%.
Rodar: python3 msa02_replicas.py. Depende de msa02_simulacao.py e seus módulos."""
import numpy as np
import msa02_base as s, msa02_regras as v4, msa02_longitudinal as L
from msa02_simulacao import usar

usar("5800 (principal)")
s.RESIDUAL_FRAC = 0.25
q = lambda x, f=100: f"{np.mean(x)*f:.1f} ({np.percentile(x,2.5)*f:.1f} a {np.percentile(x,97.5)*f:.1f})"
ec, df = [], []
for i in range(40):
    rng = np.random.default_rng(1000 + i); vl = s.gerar(rng)
    oi = v4.resumo(vl, dict(reacoes=len(vl), chama=s.medir(vl, rng) >= 200, gat=np.nan, n=len(vl)))
    og = v4.resumo(vl, v4.transversal(vl, 4, "Q20", rng))
    ec.append(1 - og["reac"]); df.append(og["200-499"] - oi["200-499"])
print("Transversal, grupo de 4 regra Q20: reações a menos (%)", q(ec), "| dif. detecção 200-499 (pontos)", q(df))
L.N = 200_000
e, d, m = [], [], []
for i in range(40):
    a = L.resumir("i", L.simular("individual", seed=2000 + i))
    b = L.resumir("g", L.simular("grupo", 4, "Q20", seed=3000 + i))
    e.append(1 - b["reac"] / a["reac"]); d.append(b["ate60"] - a["ate60"]); m.append(b["mediana"] - a["mediana"])
print("Longitudinal, grupo de 4 regra Q20: reações a menos (%)", q(e), "| dif. confirmados em 60 dias (pontos)", q(d), "| dif. mediana (dias)", q(m, 1))
