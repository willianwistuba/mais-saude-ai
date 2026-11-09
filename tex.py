"""Gera os PDFs de uma nota nos três idiomas: python3 tex.py MSA-NN
Derivado do tex.py do Física Revisitada (mesma classe REVTeX e mesmas opções), com a identidade do Mais Saúde AI."""
import os, re, subprocess, shutil, sys
from meta import *
from body import *

AUTHOR='Willian Wistuba Melo da Cunha'; ORCID_ID='0009-0008-2875-6607'

def build_tex(a,lang,L):
    ui=L['ui']; m=L['articles'][a['code']]
    _,body,_=render(a,lang,L)
    refs=''.join(f'\\bibitem{{r{i+1}}} '+esc_text(t)+(' \\href{'+u.replace('%','\\%').replace('#','\\#')+'}{\\nolinkurl{'+u.replace('https://','').replace('%','\\%').replace('#','\\#')+'}}' if u else '')+'\n' for i,(t,u) in enumerate(a['refs']))
    aurl=SITE+url(lang,'art',a['slug'])
    cite=esc_text(ui['cite_tpl'].replace('{title}',m['title']).replace('{code}',a['code']).replace('{date}',m['date_short']).replace('{url}','URLX')).replace('URLX','\\url{'+aurl+'}')
    tn=('\\\\[2pt]\\textit{'+esc_text(ui['translation_note'])+'}') if ui['translation_note'] else ''
    data=esc_text(ui['backmatter_data_text'].replace('{codeurl}','CODEX')).replace('CODEX','\\url{'+SITE+url(lang,'code')+'}')
    doi=a.get('doi')
    doi_tex=('. DOI: \\href{https://doi.org/'+doi+'}{'+doi+'}') if doi else ''
    ai=conv_str(re.sub(r'<[^>]+>','',m['ai_card']))
    bab=BABEL[lang]
    others=','.join(BABEL[x] for x in LANGS if x!=lang)
    T=[]
    T.append(r"""\PassOptionsToPackage{hyphens}{url}
\documentclass[aps,pre,twocolumn,nofootinbib,floatfix,preprintnumbers,10pt]{revtex4-2}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{textcomp}
\usepackage["""+others+','+bab+r"""]{babel}
\usepackage{mathptmx}\usepackage{amsmath,amssymb}\usepackage{microtype}\usepackage{graphicx}
\usepackage{array}\usepackage{xcolor}\definecolor{fraccent}{HTML}{007A55}\definecolor{frhot}{HTML}{C2185B}\definecolor{frink}{HTML}{111318}
\usepackage{pgfplots}\pgfplotsset{compat=1.16}\usetikzlibrary{babel}
\usepackage{framed}\setlength{\FrameSep}{4pt}\usepackage{hyperref}\usepackage{orcidlink}""")
    T.append(r"\hypersetup{colorlinks=true,urlcolor=fraccent,linkcolor=fraccent,citecolor=fraccent,pdfauthor={"+AUTHOR+"},pdftitle={"+esc_text(m['title'])+"},pdfkeywords={"+esc_text(', '.join(m['kw']))+"},pdflang={"+HREFLANG[lang]+"}}\n")
    T.append(r"\AtBeginDocument{\renewcommand{\figurename}{"+esc_text(ui['figure'])+r"}\renewcommand{\tablename}{"+esc_text(ui['table'])+r"}\renewcommand{\refname}{"+esc_text(ui['references'])+r"}\renewcommand{\abstractname}{"+esc_text(ui['abstract'])+"}}\n")
    if lang=='es': T.append(r"\AtBeginDocument{\shorthandoff{<>}}"+"\n")
    T.append(r"\begin{document}"+"\n")
    T.append(r"\preprint{MAIS SA\'{U}DE AI \textperiodcentered{} "+a['code']+"}\n")
    T.append(r"\preprint{"+esc_text(m['type'])+"}\n")
    T.append(r"\title{"+esc_text(m['title'])+"}\n")
    T.append(r"\author{"+AUTHOR+r"\,\orcidlink{"+ORCID_ID+"}}\n")
    T.append(r"\affiliation{"+esc_text(ui['pdf_author'])+"}\n\n")
    T.append(r"\begin{abstract}"+"\n")
    T.append(r"\noindent\textbf{"+esc_text(ui['abstract'])+".} "+esc_text(m['abstract'])+"\n")
    T.append(r"\\[4pt]\noindent\textbf{"+esc_text(ui['keywords'])+":} "+esc_text('; '.join(m['kw']))+".\n")
    T.append(r"\\[2pt]\noindent\textbf{ORCID:} \href{https://orcid.org/"+ORCID_ID+"}{"+ORCID_ID+"}\n")
    T.append(r"\\[2pt]\noindent\textbf{"+esc_text(ui['published'])+":} "+esc_text(m['date_long'])+'. '+esc_text(ui['version'])+' '+a.get('version_num','1')+'. '+esc_text(ui['status_text'])+doi_tex+'.\n')
    T.append(r"\\[2pt]\noindent\url{"+aurl+"}"+tn+"\n")
    T.append(r"\end{abstract}"+"\n"+r"\maketitle"+"\n")
    # bloco extra em linguagem simples, separado do resumo
    T.append(r"\begin{framed}\noindent\textbf{"+esc_text(ui['plain_title'])+r"}\par\vspace{2pt}"+(''.join(r'\noindent\textit{'+esc_text(q)+r'} '+esc_text(a_)+r'\par\vspace{2pt}' for q,a_ in m['plain']) if isinstance(m['plain'],list) else esc_text(m['plain']))+"\\end{framed}\n\n")
    T.append(body+"\n")
    T.append(r"\section*{"+esc_text(ui['aviso_title'])+"}\n"+r"\begin{framed}\noindent\small "+esc_text(ui['aviso_text'])+"\\end{framed}\n")
    T.append(r"\section*{"+esc_text(ui['backmatter_ai_title'])+"}\n"+ai+"\n")
    T.append(r"\section*{"+esc_text(ui['backmatter_data_title'])+"}\n"+data+"\n")
    T.append(r"\section*{"+esc_text(ui['backmatter_ethics_title'])+"}\n"+esc_text(ui['backmatter_ethics_text'])+"\n")
    T.append(r"\section*{"+esc_text(ui['backmatter_coi_title'])+"}\n"+esc_text(ui['backmatter_coi_text'])+' '+esc_text(ui['backmatter_review_text'])+"\n")
    T.append(r"\section*{"+esc_text(ui['cite_as'])+"}\n{\\small "+cite+"}\n")
    T.append(r"\begin{thebibliography}{99}"+"\n"+refs+r"\end{thebibliography}"+"\n"+r"\end{document}"+"\n")
    return ''.join(T)

def main(only=None):
    os.makedirs('texbuild',exist_ok=True)
    for lang in LANGS:
        L=load_i18n(lang); od='pdf' if lang=='pt' else f'pdf/{lang}'; os.makedirs(od,exist_ok=True)
        for a in ARTS:
            if only and a['code']!=only: continue
            name=f"{a['slug']}-{lang}"
            open(f'texbuild/{name}.tex','w',encoding='utf-8').write(build_tex(a,lang,L))
            for _ in range(2):
                r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd='texbuild',capture_output=True,text=True,errors='replace')
            if r.returncode!=0:
                print('ERRO',name); print(r.stdout[-3000:]); sys.exit(1)
            shutil.copy(f'texbuild/{name}.pdf', f"{od}/{a['slug']}.pdf")
            log=open(f'texbuild/{name}.log',errors='replace').read()
            ov=log.count('Overfull \\')
            print('ok',lang,a['code'],os.path.getsize(f"{od}/{a['slug']}.pdf")//1024,'KB overfull',ov)
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else None)
