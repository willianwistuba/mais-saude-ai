#!/usr/bin/env python3
"""MSA-01: base agregada por UF de residência a partir dos microdados do SINAN dengue (sem registro individual).
Saída base.csv.gz: uf, semana do início dos sintomas (domingo), semana da notificação, semana da digitação
(vazia quando o arquivo não tem DT_DIGITA ou a data é inválida), grupo (provavel = classificação final diferente
de 5, inclusive em investigação; descartado = 5), arquivo, n.
Uso: python3 msa01_base.py <pasta_zips> <saida.csv.gz> <ano_ini> <ano_fim> <data_coleta AAAA-MM-DD>
"""
import os, sys, subprocess, tempfile, duckdb
RAW, OUT, A0, A1, HOJE = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
con = duckdb.connect(); con.sql('PRAGMA threads=4'); partes = []
wk = lambda c: f"({c} - cast(dayofweek({c}) as integer))"
for ano in range(A0, A1 + 1):
    with tempfile.TemporaryDirectory(dir='/tmp') as td:
        subprocess.run(['unzip', '-q', '-o', os.path.join(RAW, f'DENGBR{ano % 100:02d}.csv.zip'), '-d', td], check=True)
        f = os.path.join(td, f'DENGBR{ano % 100:02d}.csv')
        src = f"read_csv('{f}', all_varchar=true, header=true, strict_mode=false, null_padding=true, ignore_errors=true)"
        cols = {c[0] for c in con.sql(f'describe select * from {src}').fetchall()}
        dig = 'try_cast(DT_DIGITA as date)' if 'DT_DIGITA' in cols else 'null::date'
        con.sql(f"""create or replace temp table t{ano} as
            with r as (select coalesce(nullif(SG_UF,''), SG_UF_NOT) as uf, try_cast(DT_SIN_PRI as date) as sin,
                       try_cast(DT_NOTIFIC as date) as nott, {dig} as dig, coalesce(CLASSI_FIN,'') as cf from {src})
            select uf, {wk('sin')} as sem_sin, {wk('nott')} as sem_not,
                   case when dig is not null and dig >= sin and dig >= nott - interval 7 day and dig <= date '{HOJE}' then {wk('dig')} end as sem_dig,
                   case when cf = '5' then 'descartado' else 'provavel' end as grupo, {ano} as arquivo, count(*) as n
            from r where sin is not null and nott is not null and sin >= date '2006-06-01' and nott >= sin
            group by all""")
        partes.append(f't{ano}'); print(ano, con.sql(f'select sum(n), count(*), sum(case when sem_dig is null then n else 0 end) from t{ano}').fetchall()[0], flush=True)
con.sql(f"copy ({' union all '.join('select * from ' + p for p in partes)}) to '{OUT}' (header, compression gzip)")
