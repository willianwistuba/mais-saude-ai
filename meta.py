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
ARTS=[]
