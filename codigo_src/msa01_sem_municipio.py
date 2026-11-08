#!/usr/bin/env python3
"""MSA-01: fração das notificações prováveis sem município de residência válido, por UF de residência e arquivo anual.
Mesmos filtros de msa01_base.py. Uso: python3 msa01_sem_municipio.py <pasta_zips> <saida.csv> <ano_ini> <ano_fim>"""
import os, sys, subprocess, tempfile, duckdb
RAW, OUT, A0, A1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
con = duckdb.connect(); partes = []
for ano in range(A0, A1 + 1):
    with tempfile.TemporaryDirectory(dir='/tmp') as td:
        subprocess.run(['unzip', '-q', '-o', os.path.join(RAW, f'DENGBR{ano % 100:02d}.csv.zip'), '-d', td], check=True)
        f = os.path.join(td, f'DENGBR{ano % 100:02d}.csv')
        src = f"read_csv('{f}', all_varchar=true, header=true, strict_mode=false, null_padding=true, ignore_errors=true)"
        con.sql(f"""create or replace temp table t{ano} as
            with r as (select coalesce(nullif(SG_UF,''), SG_UF_NOT) as uf, try_cast(DT_SIN_PRI as date) as sin, try_cast(DT_NOTIFIC as date) as nott,
                       coalesce(CLASSI_FIN,'') as cf, coalesce(ID_MN_RESI,'') as mn from {src})
            select uf, {ano} as arquivo, count(*) as n, sum(case when length(mn) < 6 or substr(mn,1,2) <> uf then 1 else 0 end) as sem_municipio
            from r where sin is not null and nott is not null and sin >= date '2006-06-01' and nott >= sin and cf <> '5' group by uf""")
        partes.append(f't{ano}')
con.sql(f"copy ({' union all '.join('select * from ' + p for p in partes)} order by arquivo, uf) to '{OUT}' (header)")
