SITE='https://mais-saude-ai.vercel.app'
NAME='Mais Saúde AI'
DATE='2026-11-09'
LANGS=['pt','en','es']
BABEL={'pt':'brazilian','en':'english','es':'spanish'}
HREFLANG={'pt':'pt-BR','en':'en','es':'es'}
PREFIX={'pt':'','en':'/en','es':'/es'}
ROUTES={
 'pt':{'art':'notas','notes':'notas','agenda':'agenda','method':'metodo','code':'codigo'},
 'en':{'art':'notes','notes':'notes','agenda':'agenda','method':'method','code':'code'},
 'es':{'art':'notas','notes':'notas','agenda':'agenda','method':'metodo','code':'codigo'},
}
def url(lang,kind,slug=None):
    p=PREFIX[lang]
    if kind=='home': return p+'/'
    if kind=='art': return f"{p}/{ROUTES[lang]['art']}/{slug}/"
    if kind=='pdf': return f"/pdf/{slug}.pdf" if lang=='pt' else f"/pdf/{lang}/{slug}.pdf"
    return f"{p}/{ROUTES[lang][kind]}/"

# Notas de trabalho publicadas. Cada entrada: slug, src (src/<idioma>/<src>), part, code ('MSA-NN'),
# date_iso, version_num, refs [(texto, url ou None)]. Textos (título, resumo, resumo simples,
# palavras-chave) ficam em i18n/<idioma>.json, em articles['MSA-NN'].
ARTS=[dict(slug='janela-previsao-dengue', src='a01.html', part=1, code='MSA-01', date_iso='2026-11-08', version_num='1', doi='10.5281/zenodo.24057716', refs=[
  ("Mordecai EA, Cohen JM, Evans MV et al. Detecting the impact of temperature on transmission of Zika, dengue, and chikungunya using mechanistic models. PLOS Negl Trop Dis. 2017;11:e0005568.","https://doi.org/10.1371/journal.pntd.0005568"),
  ("Codeço CT, Cruz OG, Riback TIS et al. InfoDengue: a nowcasting system for the surveillance of dengue fever transmission. bioRxiv. 2016.","https://doi.org/10.1101/046193"),
  ("Lowe R, Barcellos C, Coelho CAS et al. Dengue outlook for the World Cup in Brazil: an early warning model framework driven by real-time seasonal climate forecasts. Lancet Infect Dis. 2014;14:619-626.","https://doi.org/10.1016/S1473-3099(14)70781-9"),
  ("Lowe R, Coelho CAS, Barcellos C et al. Evaluating probabilistic dengue risk forecasts from a prototype early warning system for Brazil. eLife. 2016;5:e11285.","https://doi.org/10.7554/eLife.11285"),
  ("Johansson MA, Apfeldorf KM, Dobson S et al. An open challenge to advance probabilistic forecasting for dengue epidemics. PNAS. 2019;116:24268-24274.","https://doi.org/10.1073/pnas.1909865116"),
  ("Colón-González FJ, Soares Bastos L, Hofmann B et al. Probabilistic seasonal dengue forecasting in Vietnam: a modelling study using superensembles. PLOS Med. 2021;18:e1003542.","https://doi.org/10.1371/journal.pmed.1003542"),
  ("Araujo EC, Carvalho LM, Ganem F et al. Leveraging probabilistic forecasts for dengue preparedness and control: the 2024 Dengue Forecasting Sprint in Brazil. PNAS. 2026;123(7):e2508989123.","https://doi.org/10.1073/pnas.2508989123"),
  ("Coelho FC, Codeço CT, Araujo EC et al. Relatório IMDC 2025. Zenodo. 2025.","https://doi.org/10.5281/zenodo.17516518"),
  ("Xiao Y, Soares Bastos L et al. Dengue nowcasting in Brazil by combining official surveillance data and Google Trends information. PLOS Negl Trop Dis. 2025;19:e0012501.","https://doi.org/10.1371/journal.pntd.0012501"),
  ("Brier GW. Verification of forecasts expressed in terms of probability. Mon Weather Rev. 1950;78:1-3.","https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2"),
  ("Efron B, Tibshirani RJ. An Introduction to the Bootstrap. New York: Chapman & Hall; 1993.",None),
  ("Collins GS, Moons KGM, Dhiman P et al. TRIPOD+AI statement. BMJ. 2024;385:e078378.","https://doi.org/10.1136/bmj-2023-078378"),
  ("Pollett S, Johansson MA, Reich NG et al. Recommended reporting items for epidemic forecasting and prediction research: the EPIFORGE 2020 guidelines. PLOS Med. 2021;18:e1003793.","https://doi.org/10.1371/journal.pmed.1003793"),
  ("Benchimol EI, Smeeth L, Guttmann A et al. The RECORD statement. PLOS Med. 2015;12:e1001885.","https://doi.org/10.1371/journal.pmed.1001885"),
  ("Ministério da Saúde. OpenDataSUS: notificações de dengue (SINAN), arquivos DENGBR 2007 a 2026, acesso em 7 nov. 2026.","https://dadosabertos.saude.gov.br/"),
  ("NASA Langley Research Center. POWER Project, dados diários (MERRA-2), acesso em 7 nov. 2026.","https://power.larc.nasa.gov/"),
  ("NOAA Physical Sciences Laboratory. Oceanic Niño Index (ONI), acesso em 7 nov. 2026.","https://psl.noaa.gov/data/correlation/oni.data"),
  ("IBGE. SIDRA, tabela 4709: população residente, Censo 2022.","https://sidra.ibge.gov.br/tabela/4709"),
  ("Kelvins. municipios-brasileiros: coordenadas dos municípios (CSV).","https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"),
  ("Mosqlimate. API de dados e modelos de arboviroses, documentação.","https://api.mosqlimate.org/docs/"),
 ])]
ARTS.append(dict(slug='testagem-grupo-carga-viral-hiv', src='a02.html', part=2, code='MSA-02', date_iso='2026-11-09', date_modified='2026-11-09', version_num='1.2', refs=[
  ("Dorfman R. The detection of defective members of large populations. Ann Math Stat. 1943;14:436-440.","https://doi.org/10.1214/aoms/1177731363"),
  ("Roth WK, Weber M, Seifried E. Feasibility and efficacy of routine PCR screening of blood donations for hepatitis C virus, hepatitis B virus, and HIV-1 in a blood-bank setting. Lancet. 1999;353:359-363.","https://doi.org/10.1016/S0140-6736(98)06318-1"),
  ("Smith DM, May SJ, Pérez-Santiago J et al. The use of pooled viral load testing to identify antiretroviral treatment failure. AIDS. 2009;23(16):2151-2158.","https://doi.org/10.1097/QAD.0b013e3283313ca9"),
  ("May S, Gamst A, Haubrich R, Benson C, Smith DM. Pooled nucleic acid testing to identify antiretroviral treatment failure during HIV infection. J Acquir Immune Defic Syndr. 2010;53(2):194-201.","https://doi.org/10.1097/QAI.0b013e3181ba37a7"),
  ("van Zyl GU, Preiser W, Potschka S et al. Pooling strategies to reduce the cost of HIV-1 RNA load monitoring in a resource-limited setting. Clin Infect Dis. 2011;52(2):264-270.","https://doi.org/10.1093/cid/ciq084"),
  ("Liu T, Hogan JW, Daniels MJ et al. Improved HIV-1 viral load monitoring capacity using pooled testing with marker-assisted deconvolution. J Acquir Immune Defic Syndr. 2017;75(5):580-587.","https://doi.org/10.1097/QAI.0000000000001424"),
  ("Brand A, May S, Hughes JP, Nakigozi G, Reynolds SJ, Gabriel EE. Prediction-driven pooled testing methods: application to HIV treatment monitoring in Rakai, Uganda. Stat Med. 2021;40(19):4185-4199.","https://doi.org/10.1002/sim.9022"),
  ("Fosah Tayong GE et al. Implementation of pooled testing to increase access to routine viral load monitoring for people living with HIV on antiretroviral therapy. Sci Rep. 2025;15:14713.","https://doi.org/10.1038/s41598-025-92709-y"),
  ("Ministério da Saúde. Relatório de Monitoramento Clínico do HIV 2022. Brasília; 2022. Figura 76.",None),
  ("Roche Molecular Systems. cobas HIV-1: teste quantitativo de ácidos nucleicos para utilização com os cobas 5800/6800/8800 Systems. Instruções de uso, 09198911001-02PT, Doc Rev. 2.0.",None),
  ("Roche Molecular Systems. cobas HIV-1: teste de ácidos nucleicos para uso no sistema cobas 4800. Instruções de uso, 08793026001-02PTBR, Doc. Rev 5.0.",None),
  ("Ministério da Saúde. Nota Técnica nº 74/2026-CGHA/DATHI/SVSA/MS.","https://www.gov.br/aids/pt-br/central-de-conteudo/notas-tecnicas/2026/nota-tecnica-no-74_2026_cgha_dathi_svsa_ms.pdf"),
  ("Ministério da Saúde. Nota Técnica nº 286/2023-CGAHV/DATHI/SVSA/MS. SEI 0036440153.","https://www.gov.br/aids/pt-br/central-de-conteudo/notas-tecnicas/2023/nota-tecnica-no-286-2023-cv-hiv-da-sensibilidade-e-implicacoes-laboratorios.pdf"),
  ("Ministério da Saúde. Primeiro Termo Aditivo ao Contrato 386/2022. Processo 25000.176067/2020-05. SEI 0031447991.",None),
  ("Ministério da Saúde. Quinto Termo Aditivo ao Contrato 386/2022. Processo 25000.176067/2020-05. SEI 0052604814.",None),
  ("Ministério da Saúde. Edital do Pregão Eletrônico 108/2022, UASG 250005, e Termo de Referência SEI 0023622980 (processo 25000.176067/2020-05). Itens 17.1.2 a 17.1.4.","https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/pregoes/2022/pregao-eletronico-no-108-2022-uasg-250005-departamento-de-logistica-em-saude-dlog/edital-e-anexos-do-pe-tradicional-no-108-2022.pdf"),
  ("Ministério da Saúde. Reabertura do edital do Pregão Eletrônico SRP 90146/2025 e Termo de Referência 25/2026 (processo 25000.157431/2025-34). Itens 3.10.3, 7.1.2 e 7.1.4.","https://www.gov.br/saude/pt-br/acesso-a-informacao/licitacoes-e-contratos/pregoes/2025/pregao-eletronico-no-90146-2025-dlog/reabertura-edital-pe-srp-no-90146_2025"),
  ("Yukl SA, Li P, Fujimoto K et al. Modification of the Abbott RealTime assay for detection of HIV-1 plasma RNA viral loads less than one copy per milliliter. J Virol Methods. 2011;175(2):261-265.","https://doi.org/10.1016/j.jviromet.2011.04.015"),
  ("Monks T, Currie CSM, Onggo BS et al. Strengthening the reporting of empirical simulation studies: introducing the STRESS guidelines. J Simul. 2019;13(1):55-67.","https://doi.org/10.1080/17477778.2018.1442155"),
  ("Husereau D, Drummond M, Augustovski F et al. Consolidated Health Economic Evaluation Reporting Standards 2022 (CHEERS 2022) statement. BMJ. 2022;376:e067975.","https://doi.org/10.1136/bmj-2021-067975"),
  ("Wirden M, Palich R, Abdi B et al. More HIV-1 RNA detected and quantified with the Cobas 6800 system in patients on antiretroviral therapy. J Antimicrob Chemother. 2022;77(8):2251-2256.","https://doi.org/10.1093/jac/dkac174"),
  ("Pascual-Pareja JF, Martínez-Prats L, Luczkowiak J et al. Detection of HIV-1 at between 20 and 49 copies per milliliter by the Cobas TaqMan HIV-1 v2.0 assay is associated with higher pretherapy viral load and less time on antiretroviral therapy. J Clin Microbiol. 2010;48(5):1911-1912.","https://doi.org/10.1128/JCM.02388-09"),
  ("Helou E, Shenoi S, Kyriakides T et al. Characterizing patients with very-low-level HIV viremia: a community-based study. J Int Assoc Provid AIDS Care. 2016;16(3):261-266.","https://doi.org/10.1177/2325957416680028"),
 ]))
