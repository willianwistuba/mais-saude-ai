"""Gera o site estático do Mais Saúde AI em public/ (derivado do site.py do Física Revisitada)."""
import os, re, json, html, shutil
from meta import *
from body import *
AUTHOR='Willian Wistuba Melo da Cunha'
ORCID_ID='0009-0008-2875-6607'; ORCID='https://orcid.org/'+ORCID_ID
ORCID_SVG='<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#A6CE39"/><path fill="#fff" d="M7.4 17.6H5.9V6.8h1.5zM6.65 4.4a.95.95 0 1 1 0 1.9.95.95 0 0 1 0-1.9zM9.4 6.8h4c3.8 0 5.5 2.7 5.5 5.4 0 2.9-2.3 5.4-5.5 5.4h-4zm1.5 9.4h2.4c3.4 0 4.2-2.6 4.2-4 0-2.3-1.5-4-4.2-4h-2.4z"/></svg>'
OUT='public'; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
def words(s): return len(re.sub(r'<[^>]+>',' ',s).split())
I={l:load_i18n(l) for l in LANGS}
CSS=open('estilo.css',encoding='utf-8').read()
open(os.path.join(OUT,'estilo.css'),'w',encoding='utf-8').write(CSS)

# Logotipo: cruz (sinal de mais) cortada por uma linha de dados, com um ponto magenta de destaque
LOGO='<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><rect width="30" height="30" rx="7" fill="var(--accent)"/><path d="M12 6.5h6v5.5h5.5v6H18v5.5h-6V18H6.5v-6H12z" fill="#fff"/><polyline points="5,19.5 10,19.5 12.5,15.5 15,22 17.5,13 20,19.5 25,19.5" fill="none" stroke="var(--accent)" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/><circle cx="23.6" cy="6.4" r="2.2" fill="var(--hot)"/></svg>'
FAV="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E%3Crect width='30' height='30' rx='7' fill='%23007A55'/%3E%3Cpath d='M12 6.5h6v5.5h5.5v6H18v5.5h-6V18H6.5v-6H12z' fill='%23fff'/%3E%3Cpolyline points='5,19.5 10,19.5 12.5,15.5 15,22 17.5,13 20,19.5 25,19.5' fill='none' stroke='%23007A55' stroke-width='1.7' stroke-linejoin='round' stroke-linecap='round'/%3E%3Ccircle cx='23.6' cy='6.4' r='2.2' fill='%23C2185B'/%3E%3C/svg%3E"
BRAND='<span>Mais Saúde <b>AI</b></span>'
KATEX='''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{delimiters:[{left:'\\\\[',right:'\\\\]',display:true},{left:'\\\\(',right:'\\\\)',display:false}]})"></script>'''
def kurl(lang,key):
    return url(lang,key[0],key[1]) if key[0]=='art' else url(lang,key[0])
def byline(L,big=False):
    return f'<div class="byline{" big" if big else ""}"><span class="av">WC</span><div><b>{AUTHOR}</b><span>{E(L["ui"]["author_role"])} · <a href="{ORCID}">ORCID {ORCID_ID}</a></span></div></div>'
def aviso(L,cls='aviso',site=False):
    ui=L['ui']; t=ui['aviso_site_text'] if site else ui['aviso_text']
    return f'<div class="{cls}" role="note"><span class="eyebrow">{E(ui["aviso_title"])}</span><p>{E(t)}</p></div>'

def page(lang,title,desc,body,key,cur=None,math=False,ld=None,ogtype='website'):
    L=I[lang]; ui=L['ui']; path=kurl(lang,key)
    nav=''.join(f'<a href="{url(lang,k)}"{" aria-current=\"page\"" if cur==k else ""}>{t}</a>' for k,t in [('notes',ui['nav_notes']),('agenda',ui['nav_agenda']),('method',ui['nav_method']),('code',ui['nav_code'])])
    alts=''.join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{SITE}{kurl(l,key)}">' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{SITE}{kurl("pt",key)}">'
    sw=''.join(f'<a href="{kurl(l,key)}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}"{" aria-current=\"true\"" if l==lang else ""}>{l.upper()}</a>' for l in LANGS)
    return f'''<!DOCTYPE html>
<html lang="{HREFLANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}{path}">{alts}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{ogtype}"><meta property="og:url" content="{SITE}{path}"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="{L['locale'].replace('-','_')}"><meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#007A55">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{PREFIX[lang]}/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@600;700;800&family=JetBrains+Mono:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/estilo.css">
<link rel="icon" href="{FAV}">
{extra_meta.get(path,'')}{KATEX if math else ''}{('<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script>') if ld else ''}</head>
<body>
<a class="skip" href="#conteudo">{E(ui['skip'])}</a>
<header class="top"><div class="wrap bar">
<a class="brand" href="{url(lang,'home')}">{LOGO}{BRAND}</a>
<nav class="nav" aria-label="Menu">{nav}</nav>
<form class="search" action="{url(lang,'notes')}" role="search"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2"/></svg><input name="q" type="search" placeholder="{E(ui['search_ph'])}" aria-label="{E(ui['search_ph'])}"></form>
<nav class="lsw" aria-label="{E(ui['language'])}">{sw}</nav>
</div></header>
<main id="conteudo">{body}</main>
<footer class="foot"><div class="wrap fgrid">
<div><a class="brand" href="{url(lang,'home')}">{LOGO}{BRAND}</a><p>{E(ui['foot_about'])}</p><p class="disc">{E(ui['foot_disc'])} <a href="{url(lang,'method')}">{E(ui['foot_how'])}</a>.</p>{aviso(L,'aviso',site=True)}</div>
<div><span class="eyebrow">{E(ui['foot_nav'])}</span><a href="{url(lang,'notes')}">{E(ui['all_notes'])}</a><a href="{url(lang,'agenda')}">{E(ui['foot_agenda'])}</a><a href="{url(lang,'method')}">{E(ui['foot_method'])}</a><a href="{url(lang,'code')}">{E(ui['foot_code'])}</a><a href="{PREFIX[lang]}/rss.xml">RSS</a></div>
</div></footer>
</body>
</html>'''
extra_meta={}
def wr(path,content):
    p=os.path.join(OUT,path.strip('/'),'index.html'); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8').write(content)

# ---------- dados por idioma ----------
D={}
for lang in LANGS:
    L=I[lang]; D[lang]=[]
    for a in ARTS:
        m=L['articles'][a['code']]; h,_,toc=render(a,lang,L)
        pdfp=('pdf/' if lang=='pt' else f'pdf/{lang}/')+a['slug']+'.pdf'
        v=a.get('version_num','1')
        D[lang].append(dict(a, **m, body=h, toc=toc, min=max(3,round(words(h)/200)), url=url(lang,'art',a['slug']), pdf=url(lang,'pdf',a['slug'])+'?v='+v, pdfkb=round(os.path.getsize(pdfp)/1024)))

def plain_html(p):
    if isinstance(p,list): return ''.join(f'<h3>{E(q)}</h3><p>{E(r)}</p>' for q,r in p)
    return f'<p>{E(p)}</p>'
def plain_txt(p): return ' '.join(r for q,r in p) if isinstance(p,list) else p
def card(lang,a):
    return f'''<a class="card" href="{a['url']}" data-q="{E((a['title']+' '+a['abstract']+' '+plain_txt(a.get('plain',''))+' '+' '.join(a['kw'])+' '+a['type']).lower())}"><span class="eyebrow">{E(a['type'])} · {a['code']}</span><h3>{E(a['title'])}</h3><p>{E(plain_txt(a.get('plain',a['abstract']))[:220].rsplit(' ',1)[0])}…</p><span class="meta">{E(a['date_long'])} · {a['min']} min · <span class="tag">PDF</span></span></a>'''

def empty_notes(L):
    ui=L['ui']
    return f'<div class="emptybox"><b>{E(ui["empty_notes_title"])}</b><p>{E(ui["empty_notes_text"])}</p></div>'

for lang in LANGS:
    L=I[lang]; ui=L['ui']; hm=L['home']; AG=L['agenda']; A=D[lang]; N=len(A)
    grid=(f'<div class="grid" id="g">{"".join(card(lang,a) for a in reversed(A))}</div>' if A else empty_notes(L))
    # ---------- início ----------
    steps=''.join(f'<div><span class="n">{i+1:02d}</span><h3>{E(t)}</h3><p>{E(p)}</p></div>' for i,(t,p) in enumerate(hm['steps']))
    items=AG['items']
    ag_parts=''.join(f'<li><a href="{url(lang,"agenda")}#q{i+1}">{E(it["short"])}</a></li>' for i,it in enumerate(items))
    home=f'''<section class="hero wrap"><div class="hot"></div><span class="eyebrow">{E(hm['eyebrow'])}</span>
<h1>{hm['h1']}</h1>
<p class="lead">{E(hm['lead'])}</p>
<div class="ctas"><a class="btn pri" href="{url(lang,'agenda')}">{E(hm['cta_agenda'])}</a><a class="btn" href="{url(lang,'method')}">{E(hm['cta_method'])}</a></div>
<div class="stats"><div><b>{N}</b><span>{E(hm['stat_notes_one'] if N==1 else hm['stat_notes'])}</span></div><div><b>{len(items)}</b><span>{E(hm['stat_agenda'])}</span></div><div><b>{len(LANGS)}</b><span>{E(hm['stat_langs'])}</span></div><div><b>100%</b><span>{E(hm['stat_open'])}</span></div></div>
</section>
<section class="band"><div class="wrap">
<span class="eyebrow">{E(hm['agenda_eyebrow'])}</span><h2>{E(hm['agenda_h2'])}</h2><p class="sub">{E(hm['agenda_sub'])}</p>
<div class="series"><div><span class="eyebrow">{E(hm['agenda_card_eyebrow'])}</span><h3><a href="{url(lang,'agenda')}">{E(AG['title'])}</a></h3><p>{E(AG['lead'])}</p><a class="link" href="{url(lang,'agenda')}">{E(hm['agenda_link'])}</a></div><ol class="parts">{ag_parts}</ol></div>
</div></section>
<section class="wrap sec"><div class="head"><div><span class="eyebrow">{E(hm['latest_eyebrow'])}</span><h2>{E(hm['latest_h2'])}</h2><p class="sub">{E(hm['latest_sub'])}</p></div>{f'<a class="more" href="{url(lang,"notes")}">{E(hm["see_all"])}</a>' if A else ''}</div>
{grid}</section>
<section class="wrap sec"><span class="eyebrow">{E(hm['method_eyebrow'])}</span><h2>{E(hm['method_h2'])}</h2>
<div class="steps">{steps}</div>
<div class="callout"><span class="eyebrow">{E(hm['transp_eyebrow'])}</span><p>{E(hm['transp_text'])} <a href="{url(lang,'method')}">{E(hm['transp_link'])}</a>.</p></div></section>'''
    ld_home={"@context":"https://schema.org","@type":"WebSite","name":NAME,"url":SITE+url(lang,'home'),"inLanguage":HREFLANG[lang],"description":ui['site_desc'],"author":{"@type":"Person","name":AUTHOR,"description":ui['author_role'],"identifier":ORCID,"sameAs":[ORCID]},"potentialAction":{"@type":"SearchAction","target":SITE+url(lang,'notes')+"?q={q}","query-input":"required name=q"}}
    wr(url(lang,'home'),page(lang,ui['site_title'],ui['site_desc'],home,('home',),ld=ld_home))

    # ---------- notas ----------
    filt=(f'<input class="filter" id="f" type="search" placeholder="{E(ui["filter_ph"])}" aria-label="{E(ui["filter_aria"])}">' if A else '')
    notas=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(hm['latest_eyebrow'])}</span><h1>{E(ui['notes_title'])}</h1><p class="lead">{E(ui['notes_lead'])}</p>
{filt}</section>
<section class="wrap">{grid}<p class="empty" id="e" hidden>{E(ui['empty'])}</p></section>'''
    if A: notas+='''<script>(function(){var f=document.getElementById('f'),cards=[].slice.call(document.querySelectorAll('#g .card')),e=document.getElementById('e');
function n(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function run(){var q=n(f.value),k=0;cards.forEach(function(c){var ok=!q||n(c.dataset.q).indexOf(q)>=0;c.hidden=!ok;if(ok)k++;});e.hidden=k>0;}
try{var q=new URLSearchParams(location.search).get('q');if(q)f.value=q;}catch(x){}
f.addEventListener('input',run);run();})();</script>'''
    wr(url(lang,'notes'),page(lang,ui['notes_title']+' · '+NAME,ui['notes_desc'],notas,('notes',),cur='notes'))

    # ---------- agenda de pesquisa ----------
    al=''.join(f'''<li id="q{i+1}"><span class="status">{E(it['status'])}</span><h3>{E(it['title'])}</h3><p>{E(it['text'])}</p></li>''' for i,it in enumerate(items))
    agp=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(AG['eyebrow'])}</span><h1>{E(AG['title'])}</h1><p class="lead">{E(AG['lead'])}</p></section>
<section class="wrap"><ol class="agenda">{al}</ol>
<div class="callout"><span class="eyebrow">{E(AG['how_title'])}</span><p>{E(AG['how_text'])}</p></div></section>'''
    wr(url(lang,'agenda'),page(lang,AG['title']+' · '+NAME,AG['lead'],agp,('agenda',),cur='agenda'))

    # ---------- notas de trabalho ----------
    for i,a in enumerate(A):
        prev=A[i-1] if i else None; nxt=A[i+1] if i<N-1 else None
        refs=''.join(f'<li id="ref-{k+1}"><span class="rn">[{k+1}]</span><span>{E(t)}'+(f' <a href="{u}">{E(u.replace("https://",""))}</a>' if u else '')+'</span></li>' for k,(t,u) in enumerate(a['refs']))
        toc=''.join(f'<li class="l{lv}"><a href="#{sid}"><span>{no}</span> {E(t)}</a></li>' for sid,no,t,lv in a['toc'])
        stoc=''.join(f'<li{" class=\"on\"" if b is a else ""}><span>{b["part"]:02d}</span><a href="{b["url"]}">{E(b["short"])}</a></li>' for b in A)
        cite=ui['cite_tpl'].replace('{title}',a['title']).replace('{code}',a['code']).replace('{date}',a['date_short']).replace('{url}',SITE+a['url'])
        langs=''.join(f'<a href="{url(l,"art",a["slug"])}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}"{" aria-current=\"true\"" if l==lang else ""}>{E(I[l]["name"])}</a>' for l in LANGS)
        tn=f'<p class="trnote">{E(ui["translation_note"])} <a href="{url("pt","art",a["slug"])}" hreflang="pt-BR">PT</a></p>' if ui['translation_note'] else ''
        doi=a.get('doi')
        pager='<nav class="pager">'+(f'<a href="{prev["url"]}"><span class="eyebrow">{E(ui["prev"])}</span>{E(prev["short"])}</a>' if prev else f'<a href="{url(lang,"agenda")}"><span class="eyebrow">{E(ui["nav_agenda"])}</span>{E(AG["title"])}</a>')+(f'<a class="r" href="{nxt["url"]}"><span class="eyebrow">{E(ui["next"])}</span>{E(nxt["short"])}</a>' if nxt else f'<a class="r" href="{url(lang,"notes")}"><span class="eyebrow">{E(ui["more"])}</span>{E(ui["all_notes"])}</a>')+'</nav>'
        data=E(ui['backmatter_data_text']).replace('{codeurl}',f'<a href="{url(lang,"code")}">{SITE}{url(lang,"code")}</a>')
        body=f'''<article class="paper" lang="{HREFLANG[lang]}">
<div class="wrap pgrid"><div class="pmain">
<div class="masthead"><span class="jn">{NAME}</span><span class="js">{E(ui['journal_sub'])}</span><span class="jc">{a['code']} ({a['date_iso'][:4]})</span></div>
<span class="ptype">{E(a['type'])}</span>
<h1 class="ptitle">{E(a['title'])}</h1>
<div class="authors"><span class="aname">{AUTHOR} <a class="orcid" href="{ORCID}" title="ORCID {ORCID_ID}" aria-label="ORCID {ORCID_ID}">{ORCID_SVG}<span>{ORCID_ID}</span></a></span><span class="aff">{E(ui['author_role'])}</span></div>
<dl class="pinfo"><div><dt>{E(ui['published'])}</dt><dd>{E(a['date_long'])}</dd></div><div><dt>{E(ui['version'])}</dt><dd>{E(a['version_note'])}</dd></div><div><dt>{E(ui['status'])}</dt><dd>{E(ui['status_text'])}</dd></div><div><dt>DOI</dt><dd>{f'<a href="https://doi.org/{doi}">{doi}</a>' if doi else E(ui['doi_pending'])}</dd></div></dl>
<div class="pactions"><a class="btn pri" href="{a['pdf']}" download>{E(ui['download_pdf'])} · {a['pdfkb']} KB</a><a class="btn" href="#citar">{E(ui['cite_as'])}</a></div>
<nav class="plangs" aria-label="{E(ui['other_langs'])}"><span>{E(ui['other_langs'])}:</span>{langs}</nav>
{tn}
<section class="abstract"><h2>{E(ui['abstract'])}</h2><p>{E(a['abstract'])}</p><p class="kw"><b>{E(ui['keywords'])}:</b> {E('; '.join(a['kw']))}.</p></section>
<section class="plain"><h2>{E(ui['plain_title'])}</h2>{plain_html(a['plain'])}</section>
{aviso(L)}
<div class="pbody">{a['body']}</div>
<section class="back">
<h2>{E(ui['backmatter_ai_title'])}</h2><p>{a['ai_card']}</p>
<h2>{E(ui['backmatter_data_title'])}</h2><p>{data}</p>
<h2>{E(ui['backmatter_ethics_title'])}</h2><p>{E(ui['backmatter_ethics_text'])}</p>
<h2>{E(ui['backmatter_coi_title'])}</h2><p>{E(ui['backmatter_coi_text'])}</p>
<h2>{E(ui['backmatter_review_title'])}</h2><p>{E(ui['backmatter_review_text'])}</p>
</section>
<section class="refs"><h2>{E(ui['references'])}</h2><ol>{refs}</ol></section>
<section class="citebox" id="citar"><span class="eyebrow">{E(ui['cite_as'])}</span><p class="mono">{E(cite)}</p></section>
{pager}
</div>
<aside class="pside"><div class="stick"><span class="eyebrow">{E(ui['contents'])}</span><ol class="ptoc">{toc}</ol><a class="btn pri full" href="{a['pdf']}" download>{E(ui['download_pdf'])}</a><span class="eyebrow sp">{E(ui['nav_notes'])}</span><ol class="toc">{stoc}</ol></div></aside>
</div></article>'''
        ld={"@context":"https://schema.org","@type":"ScholarlyArticle","headline":a['title'],"abstract":a['abstract'],"keywords":a['kw'],"datePublished":a['date_iso'],"dateModified":a.get('date_modified',a['date_iso']),"version":a.get('version_num','1'),"inLanguage":HREFLANG[lang],"url":SITE+a['url'],"identifier":(['https://doi.org/'+doi] if doi else [])+[a['code']],"isPartOf":{"@type":"Periodical","name":NAME},"author":{"@type":"Person","name":AUTHOR,"description":ui['author_role'],"identifier":ORCID,"sameAs":[ORCID]},"publisher":{"@type":"Organization","name":NAME},"isAccessibleForFree":True,"license":"https://creativecommons.org/licenses/by/4.0/","citation":[t for t,_ in a['refs']],"encoding":{"@type":"MediaObject","contentUrl":SITE+a['pdf'],"encodingFormat":"application/pdf"}}
        if lang!='pt': ld["translationOfWork"]={"@type":"ScholarlyArticle","url":SITE+url('pt','art',a['slug'])}
        hw=f'<meta name="citation_title" content="{E(a["title"])}"><meta name="citation_author" content="Cunha, Willian Wistuba Melo da"><meta name="citation_author_orcid" content="'+ORCID+f'"><meta name="citation_publication_date" content="{a["date_iso"].replace("-","/")}"><meta name="citation_journal_title" content="{NAME}"><meta name="citation_technical_report_number" content="{a["code"]}"><meta name="citation_language" content="{lang}"><meta name="citation_pdf_url" content="{SITE}{a["pdf"]}"><meta name="citation_abstract_html_url" content="{SITE}{a["url"]}">'+(f'<meta name="citation_doi" content="{doi}">' if doi else '')+''.join(f'<meta name="citation_keywords" content="{E(k)}">' for k in a['kw'])+''.join(f'<meta name="citation_reference" content="{E(t)}">' for t,_ in a['refs'])
        extra_meta[a['url']]=hw
        wr(a['url'],page(lang,a['title']+' · '+NAME,plain_txt(a.get('plain',a['abstract']))[:300],body,('art',a['slug']),cur='notes',math=True,ld=ld,ogtype='article'))

    # ---------- método ----------
    mp=L['method_page']
    met=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(mp['eyebrow'])}</span><h1>{E(mp['h1'])}</h1><p class="lead">{E(mp['lead'])}</p></section>
<section class="wrap prose">{mp['body'].replace('{byline}',byline(L,True)).replace('{aviso}',aviso(L))}</section>'''
    wr(url(lang,'method'),page(lang,ui['method_title']+' · '+NAME,ui['method_desc'],met,('method',),cur='method'))

    # ---------- código ----------
    cp=L['code_page']
    if lang=='pt':
        os.makedirs(os.path.join(OUT,'codigo'),exist_ok=True)
        for f in cp['files']:
            os.makedirs(os.path.dirname(os.path.join(OUT,'codigo',f)),exist_ok=True); shutil.copy(f if f.startswith(('dados/','protocolos/')) else 'codigo_src/'+f, os.path.join(OUT,'codigo',f))
    rows=''.join(f'<tr><td><a href="/codigo/{f}"><code>{f}</code></a></td><td>{E(d)}</td></tr>' for f,d in cp['files'].items())
    table=(f'<div class="tblwrap"><table><thead><tr><th>{E(cp["th_file"])}</th><th>{E(cp["th_what"])}</th></tr></thead><tbody>{rows}</tbody></table></div>' if rows else f'<div class="emptybox"><b>{E(cp["empty_title"])}</b><p>{E(cp["empty_text"])}</p></div>')
    cod=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">{E(cp['eyebrow'])}</span><h1>{E(cp['h1'])}</h1><p class="lead">{E(cp['lead'])}</p></section>
<section class="wrap prose"><p>{cp['intro']}</p>
{table}
<p class="note">{cp['note']}</p></section>'''
    wr(url(lang,'code'),page(lang,ui['code_title']+' · '+NAME,ui['code_desc'],cod,('code',),cur='code'))

    # ---------- pdf, rss ----------
    od=os.path.join(OUT,'pdf') if lang=='pt' else os.path.join(OUT,'pdf',lang); os.makedirs(od,exist_ok=True)
    for a in A: shutil.copy(('pdf/' if lang=='pt' else f'pdf/{lang}/')+a['slug']+'.pdf', os.path.join(od,a['slug']+'.pdf'))
    items_rss=''.join(f'<item><title>{E(a["title"])}</title><link>{SITE}{a["url"]}</link><guid>{SITE}{a["url"]}</guid><pubDate>{a["date_rfc"]}</pubDate><description>{E(plain_txt(a.get("plain",a["abstract"])))}</description><enclosure url="{SITE}{a["pdf"]}" type="application/pdf" length="{os.path.getsize(OUT+a["pdf"].split("?")[0])}"/></item>' for a in reversed(A))
    rp=os.path.join(OUT,PREFIX[lang].strip('/'),'rss.xml'); os.makedirs(os.path.dirname(rp),exist_ok=True)
    open(rp,'w',encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}{url(lang,"home")}</link><description>{E(ui["rss_desc"])}</description><language>{HREFLANG[lang]}</language>{items_rss}</channel></rss>')

# ---------- sitemap, robots, 404, índice do Zenodo ----------
keys=[('home',),('notes',),('agenda',),('method',),('code',)]+[('art',a['slug']) for a in ARTS]
sm=''.join(f'<url><loc>{SITE}{kurl(l,k)}</loc><lastmod>{DATE}</lastmod>'+''.join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG[x]}" href="{SITE}{kurl(x,k)}"/>' for x in LANGS)+'</url>' for k in keys for l in LANGS)
open(os.path.join(OUT,'sitemap.xml'),'w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+sm+'</urlset>')
open(os.path.join(OUT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
L=I['pt']; nf=f'''<section class="wrap pagehead"><div class="hot"></div><span class="eyebrow">404</span><h1>{E(L['ui']['nf_title'])}</h1><p class="lead">{E(L['ui']['nf_text'])}</p><div class="ctas"><a class="btn pri" href="/">{E(L['ui']['nf_home'])}</a><a class="btn" href="/en/">English</a><a class="btn" href="/es/">Español</a></div></section>'''
open(os.path.join(OUT,'404.html'),'w',encoding='utf-8').write(page('pt',L['ui']['nf_title']+' · '+NAME,L['ui']['nf_text'],nf,('home',)).replace('<link rel="canonical"','<meta name="robots" content="noindex"><link rel="canonical"'))
ZL={'pt':'por','en':'eng','es':'spa'}
zn=[]
for a in ARTS:
    c=a['code']; s=a['slug']
    zn.append({'code':c,'part':a['part'],'slug':s,'doi':a.get('doi'),
        'langs':{l:{'iso':ZL[l],'title':I[l]['articles'][c]['title'],'abstract':I[l]['articles'][c]['abstract'],
                    'keywords':I[l]['articles'][c]['kw'],'page':SITE+kurl(l,('art',s)),
                    'pdf':SITE+('/pdf/' if l=='pt' else f'/pdf/{l}/')+s+'.pdf'} for l in LANGS}})
json.dump({'site':SITE,'code_page':SITE+'/codigo/','generated':DATE,'notes':zn},open(os.path.join(OUT,'zenodo.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)

print('ok', sum(len(f) for _,_,f in os.walk(OUT)),'arquivos')
