SITE='https://mais-saude-ai.vercel.app'
NAME='Mais Saúde AI'
DATE='2026-11-07'
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
