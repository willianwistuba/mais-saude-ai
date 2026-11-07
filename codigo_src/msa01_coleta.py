#!/usr/bin/env python3
"""MSA-01: baixa os microdados do SINAN dengue (OpenDataSUS, espelho S3 do Ministério da Saúde) e registra hash e data.
Uso: python3 msa01_coleta.py <pasta_saida> <ano_ini> <ano_fim>
"""
import sys, os, hashlib, subprocess, datetime
OUT, A0, A1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); os.makedirs(OUT, exist_ok=True)
URL = 'https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/csv/DENGBR{:02d}.csv.zip'
with open(os.path.join(OUT, 'SHA256SUMS'), 'w') as h, open(os.path.join(OUT, 'coleta.log'), 'w') as log:
    for a in range(A0, A1 + 1):
        u = URL.format(a % 100); f = os.path.join(OUT, os.path.basename(u))
        subprocess.run(['curl', '-sS', '--retry', '3', '-o', f, u], check=True)
        hd = subprocess.run(['curl', '-sSI', u], capture_output=True, text=True).stdout
        lm = next((l.split(':', 1)[1].strip() for l in hd.splitlines() if l.lower().startswith('last-modified')), '')
        d = hashlib.sha256(open(f, 'rb').read()).hexdigest()
        h.write(f'{d}  {os.path.basename(f)}\n')
        log.write(f'{datetime.datetime.now(datetime.timezone.utc).isoformat()}\t{u}\t{os.path.getsize(f)}\tLast-Modified: {lm}\n'); print(a, os.path.getsize(f) // 1e6, 'MB', lm, flush=True)
