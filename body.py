"""Leitura das notas (src/<lang>/aNN.html) e renderização para o site e para LaTeX (REVTeX).
Derivado dos geradores do Física Revisitada; as figuras de cada nota entram em SVGFIG e TEXFIG."""
import re, json, math, html as H
from bs4 import BeautifulSoup, NavigableString, Tag
from meta import *

def load_i18n(lang): return json.load(open(f'i18n/{lang}.json',encoding='utf-8'))
def roman(n): return ['','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV'][n]
def num(x,L): return str(x).replace('.',L['decimal'])
E=H.escape


# ---------------- LaTeX: texto ----------------
UMAP={'≈':r'$\approx$','×':r'$\times$','√':r'$\surd$','≤':r'$\leq$','≥':r'$\geq$','÷':r'$\div$','°':r'\textdegree{}','<':r'$<$','>':r'$>$',
      'μ':r'$\mu$','β':r'$\beta$','ε':r'$\varepsilon$','γ':r'$\gamma$','δ':r'$\delta$','λ':r'$\lambda$','π':r'$\pi$','Λ':r'$\Lambda$',
      '₃':r'$_3$','³':r'$^3$','²':r'$^2$','→':r'$\rightarrow$','←':r'$\leftarrow$','∞':r'$\infty$','·':r'\textperiodcentered{}','−':'-',
      '\u202f':r'\,','\u2009':r'\,','≲':r'$\lesssim$','§':r'\S{}'}
def esc_text(s):
    s=s.replace('⁻³','\x00')
    out=[]
    for ch in s:
        if ch=='\x00': out.append(r'$^{-3}$'); continue
        if ch in UMAP: out.append(UMAP[ch]); continue
        if ch in '&%#_$': out.append('\\'+ch); continue
        if ch=='{': out.append(r'\{'); continue
        if ch=='}': out.append(r'\}'); continue
        if ch=='~': out.append(r'\textasciitilde{}'); continue
        if ch=='^': out.append(r'\textasciicircum{}'); continue
        if ch=='\\': out.append(r'\textbackslash{}'); continue
        out.append(ch)
    t=''.join(out)
    t=re.sub(r'"([^"]*)"', r"``\1''", t)
    return t
MATH=re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\])', re.S)
def conv_str(s):
    r=[]
    for p in MATH.split(s):
        if not p: continue
        r.append(p if (p.startswith('\\(') or p.startswith('\\[')) else esc_text(p))
    return ''.join(r)
def tex_inline(node):
    if isinstance(node, NavigableString): return conv_str(str(node))
    if not isinstance(node, Tag): return ''
    n=node.name
    if n=='cite': return r'~\cite{'+','.join('r'+x.strip() for x in node.get_text().split(','))+'}'
    inner=''.join(tex_inline(c) for c in node.children)
    if n in ('b','strong'): return r'\textbf{'+inner+'}'
    if n in ('i','em'): return r'\emph{'+inner+'}'
    if n=='a': return r'\href{'+node.get('href','').replace('%','\\%').replace('#','\\#')+'}{'+inner+'}'
    if n=='code': return r'\texttt{'+inner+'}'
    return inner
def strip_cite_space(t): return re.sub(r'\s+~\\cite',r'~\\cite',t)

# figuras: funções svg_aNN(L) e tex_fig_aNN(L,cap) registradas aqui
SVGFIG={}
TEXFIG={}

def render(a,lang,L):
    """Devolve (html_site, tex_body, toc)."""
    raw=open(f'src/{lang}/{a["src"]}',encoding='utf-8').read()
    soup=BeautifulSoup(raw,'html.parser')
    H_out=[]; T_out=[]; toc=[]
    sec=0; sub=0; eq=0; fig=0; tab=0
    ui=L['ui']
    def site_inline(node):
        if isinstance(node,NavigableString): return str(node)
        if not isinstance(node,Tag): return ''
        if node.name=='cite':
            ns=[x.strip() for x in node.get_text().split(',')]
            return '<span class="cite">['+', '.join(f'<a href="#ref-{x}">{x}</a>' for x in ns)+']</span>'
        inner=''.join(site_inline(c) for c in node.children)
        attrs=''.join(f' {k}="{E(v if isinstance(v,str) else " ".join(v))}"' for k,v in node.attrs.items())
        return f'<{node.name}{attrs}>{inner}</{node.name}>'
    for node in soup.children:
        if isinstance(node,NavigableString):
            if node.strip(): H_out.append(str(node)); T_out.append(conv_str(str(node)))
            continue
        n=node.name; cls=node.get('class') or []
        if n=='h2':
            sec+=1; sub=0; t=node.get_text().strip(); sid=f's{sec}'
            toc.append((sid,roman(sec)+'.',t,2))
            H_out.append(f'<h2 id="{sid}"><span class="no">{roman(sec)}.</span> {E(t)}</h2>')
            T_out.append('\\section{'+conv_str(t)+'}\n')
        elif n=='h3':
            sub+=1; t=node.get_text().strip(); sid=f's{sec}{chr(96+sub)}'
            toc.append((sid,chr(64+sub)+'.',t,3))
            H_out.append(f'<h3 id="{sid}"><span class="no">{chr(64+sub)}.</span> {E(t)}</h3>')
            T_out.append('\\subsection{'+conv_str(t)+'}\n')
        elif n=='p':
            H_out.append(site_inline(node))
            T_out.append(strip_cite_space(''.join(tex_inline(c) for c in node.children))+'\n\n')
        elif n in ('ul','ol'):
            H_out.append(site_inline(node))
            env='itemize' if n=='ul' else 'enumerate'
            T_out.append(f'\\begin{{{env}}}\n'+''.join('\\item '+strip_cite_space(''.join(tex_inline(c) for c in li.children))+'\n' for li in node.find_all('li',recursive=False))+f'\\end{{{env}}}\n')
        elif n=='div' and 'eq' in cls:
            eq+=1; m=node.get_text().strip(); m=m[2:-2].strip() if m.startswith('\\[') else m
            H_out.append(f'<div class="eq" id="eq{eq}">\\[ {m} \\tag{{{eq}}} \\]</div>')
            T_out.append('\\begin{equation}\n'+m+'\n\\end{equation}\n')
        elif n=='figure':
            fig+=1; key=node['data-fig']; capn=node.find('figcaption')
            caph=site_inline(capn)[len('<figcaption>'):-len('</figcaption>')]
            H_out.append(f'<figure id="fig{fig}">{SVGFIG[key](L)}<figcaption><b>{ui["figure"]} {fig}.</b> {caph}</figcaption></figure>')
            T_out.append(TEXFIG[key](L,strip_cite_space(''.join(tex_inline(c) for c in capn.children))))
        elif n=='div' and 'box' in cls:
            tt=node.find('p',class_='boxt'); title=tt.get_text().strip() if tt else ''
            if tt: tt.extract()
            inner=[c for c in node.children if isinstance(c,Tag)]
            H_out.append('<div class="box">'+(f'<span class="eyebrow">{E(title)}</span>' if title else '')+''.join(site_inline(c) for c in inner)+'</div>')
            tb=[]
            for c in inner:
                if c.name in ('ul','ol'):
                    env='itemize' if c.name=='ul' else 'enumerate'
                    tb.append(f'\\begin{{{env}}}\\setlength{{\\itemsep}}{{1pt}}\n'+''.join('\\item '+strip_cite_space(''.join(tex_inline(x) for x in li.children))+'\n' for li in c.find_all('li',recursive=False))+f'\\end{{{env}}}\n')
                else: tb.append(strip_cite_space(''.join(tex_inline(x) for x in c.children))+'\\par\\smallskip\n')
            T_out.append('\\par\\medskip\\noindent\\fbox{\\parbox{\\dimexpr\\columnwidth-2\\fboxsep-2\\fboxrule\\relax}{\\small'+(('\\textbf{'+conv_str(title)+'}\\par\\smallskip\n') if title else '\n')+''.join(tb)+'}}\\par\\medskip\n')
        elif n=='div' and 'tblwrap' in cls:
            tab+=1; capn=node.find('p',class_='cap'); tb=node.find('table')
            caph=site_inline(capn)[len('<p class="cap">'):-len('</p>')]
            H_out.append(f'<div class="tblwrap" id="tab{tab}"><p class="tcap"><b>{ui["table"]} {roman(tab)}.</b> {caph}</p>{site_inline(tb)}</div>')
            rows=tb.find_all('tr'); nc=len(rows[0].find_all(['th','td']))
            lines=[]
            for i,r in enumerate(rows):
                cells=[''.join(tex_inline(c) for c in td.children) for td in r.find_all(['th','td'])]
                lines.append(' & '.join(cells)+r' \\')
                if i==0: lines.append(r'\colrule')
            wide=nc>5 or any(len(td.get_text())>22 for td in tb.find_all('td')) or (nc>=4 and sum(len(th.get_text()) for th in tb.find_all('th'))>45)
            env='table*' if wide else 'table'
            ml=[max(len(r.find_all(['th','td'])[j].get_text()) for r in rows if len(r.find_all(['th','td']))>j) for j in range(nc)]
            if max(ml)>40:
                tot=sum(min(max(x,9),70) for x in ml); colspec=''.join('>{\\raggedright\\arraybackslash}p{%.3f\\textwidth}'%(0.9*min(max(x,9),70)/tot) for x in ml)
            else: colspec='l'*nc
            T_out.append(f'\\begin{{{env}}}[tb]\\caption{{'+strip_cite_space(''.join(tex_inline(c) for c in capn.children))+'}\n\\begin{ruledtabular}\n\\begin{tabular}{'+colspec+'}\n'+'\n'.join(lines)+f'\n\\end{{tabular}}\n\\end{{ruledtabular}}\n\\end{{{env}}}\n')
        else:
            H_out.append(str(node)); T_out.append(conv_str(node.get_text())+'\n')
    return '\n'.join(H_out), ''.join(T_out), toc


# ---------------- figuras da MSA-01 (lidas de dados/msa01) ----------------
import csv as _csv, json as _json
_SEM = list(range(43))
_UFN = {'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
_L = {'pt': {'m': 'modelo M', 'a': 'projeção A', 'r': 'histórico R0', 'x': 'Semanas desde o início da temporada do Estado', 'y': 'Acerto (sim ou não)', 'lim': 'patamar de 75%',
             'yd': 'Temporadas altas já evidentes', 'd6': 'com defasagem de 6 semanas', 'd0': 'sem defasagem', 'meio': 'metade',
             'tx': 'Temperatura média diária (°C)', 'ty': 'Aptidão térmica (relativa)', 'pk': 'ótimo: 29,1 °C',
             'tl_x': 'Semana epidemiológica', 'tl_v': 'início da temporada (vale)', 'tl_p': 'pico mediano das temporadas altas'},
      'en': {'m': 'model M', 'a': 'projection A', 'r': 'history R0', 'x': "Weeks since the start of the state's season", 'y': 'Accuracy (yes or no)', 'lim': '75% level',
             'yd': 'High seasons already evident', 'd6': 'with a 6-week lag', 'd0': 'without lag', 'meio': 'half',
             'tx': 'Mean daily temperature (°C)', 'ty': 'Thermal suitability (relative)', 'pk': 'optimum: 29.1 °C',
             'tl_x': 'Epidemiological week', 'tl_v': 'season start (trough)', 'tl_p': 'median peak of high seasons'},
      'es': {'m': 'modelo M', 'a': 'proyección A', 'r': 'histórico R0', 'x': 'Semanas desde el inicio de la temporada del estado', 'y': 'Acierto (sí o no)', 'lim': 'nivel del 75%',
             'yd': 'Temporadas altas ya evidentes', 'd6': 'con desfase de 6 semanas', 'd0': 'sin desfase', 'meio': 'mitad',
             'tx': 'Temperatura media diaria (°C)', 'ty': 'Aptitud térmica (relativa)', 'pk': 'óptimo: 29,1 °C',
             'tl_x': 'Semana epidemiológica', 'tl_v': 'inicio de la temporada (valle)', 'tl_p': 'pico mediano de las temporadas altas'}}
_TK = (0, 7, 14, 21, 28, 35, 42)
def _ps(path):
    r = {int(d['k']): d for d in _csv.DictReader(open(path, encoding='utf-8'))}
    return [r[s] for s in _SEM]
def _fx(v, L, k=2): return num(f'{v:.{k}f}', L)
def _line_svg(L, series, ylab, ymin, ymax, yt, hline=None, hlab=''):
    t = _L[L['lang']]; x0, x1, y0, y1 = 70, 620, 18, 250; n = len(_SEM)
    X = lambda i: x0 + i * (x1 - x0) / (n - 1); Y = lambda v: y1 - (v - ymin) / (ymax - ymin) * (y1 - y0)
    g = [f'<svg viewBox="0 0 640 320" role="img" aria-label="{E(ylab)}">']
    for v in yt: g.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/><text class="ax" x="{x0-8}" y="{Y(v)+4:.1f}" text-anchor="end">{_fx(v*100,L,0)}%</text>')
    for i in _TK: g.append(f'<text class="ax" x="{X(i):.1f}" y="{y1+18}" text-anchor="middle">{i}</text>')
    if hline is not None: g.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(hline):.1f}" y2="{Y(hline):.1f}" stroke="var(--ink)" stroke-dasharray="5 4"/><text class="ax" x="{x0+4}" y="{Y(hline)-5:.1f}">{E(hlab)}</text>')
    for vals, col, dash, lab in series:
        pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
        g.append(f'<polyline fill="none" stroke="{col}" stroke-width="2.2" {"stroke-dasharray=\"2 4\"" if dash else ""} points="{pts}"/>')
    lg = ''.join(f'<line x1="{x0+10+i*170}" x2="{x0+34+i*170}" y1="296" y2="296" stroke="{c}" stroke-width="2.4" {"stroke-dasharray=\"2 4\"" if d else ""}/><text class="ax" x="{x0+40+i*170}" y="300">{E(l)}</text>' for i, (v, c, d, l) in enumerate(series))
    g.append(lg + f'<text class="lbl" transform="translate(16,{(y0+y1)/2}) rotate(-90)" text-anchor="middle">{E(ylab)}</text><text class="ax" x="{(x0+x1)/2}" y="{y1+34}" text-anchor="middle">{E(t["x"])}</text></svg>')
    return ''.join(g)
def _line_tex(L, series, ylab, ymin, ymax, cap, hline=None):
    t = _L[L['lang']]; n = len(_SEM); uc = 'true' if L['decimal'] == ',' else 'false'
    cols = {'var(--accent)': 'fraccent', 'var(--hot)': 'frhot', 'var(--muted)': 'gray'}
    s = [r"\begin{figure}[tb]\centering\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=5.6cm,xmin=0,xmax=" + str(n - 1) + ",ymin=" + str(ymin) + ",ymax=" + str(ymax) +
         r",xtick={0,7,14,21,28,35,42},yticklabel={\pgfmathparse{\tick*100}\pgfmathprintnumber[fixed,precision=0,use comma=" + uc + r"]{\pgfmathresult}\%},"
         r"xlabel={" + esc_text(t['x']) + r"},ylabel={" + esc_text(ylab) + r"},label style={font=\footnotesize},tick label style={font=\scriptsize},ymajorgrids,grid style={gray!25},axis line style={gray!60},"
         r"legend style={font=\scriptsize,draw=none,at={(0.02,0.98)},anchor=north west,fill=white,fill opacity=0.8,text opacity=1},legend cell align=left]"]
    for vals, col, dash, lab in series:
        s.append(r"\addplot[" + cols[col] + r",thick" + (",densely dotted" if dash else "") + r"] coordinates {" + ' '.join(f'({i},{v:.4f})' for i, v in enumerate(vals)) + r"};\addlegendentry{" + esc_text(lab) + "}")
    if hline is not None: s.append(r"\addplot[black,dashed,forget plot] coordinates {(0," + str(hline) + ")(" + str(n - 1) + "," + str(hline) + ")};")
    s.append(r"\end{axis}\end{tikzpicture}\caption{" + cap + r"}\end{figure}" + "\n"); return ''.join(s)
def _acc_series(L, path):
    t = _L[L['lang']]; R = _ps(path)
    return [([float(d['acerto_M']) for d in R], 'var(--accent)', False, t['m']), ([float(d['acerto_A']) for d in R], 'var(--hot)', False, t['a']), ([float(d['acerto_R0']) for d in R], 'var(--muted)', True, t['r'])]
_P6 = 'dados/msa01/msa01_por_semana.csv'; _P0 = 'dados/msa01/sensibilidades/L0_por_semana.csv'
def svg_m2_acc(L): t = _L[L['lang']]; return _line_svg(L, _acc_series(L, _P6), t['y'], 0.45, 0.95, [0.5, 0.6, 0.7, 0.8, 0.9], 0.75, t['lim'])
def tex_m2_acc(L, cap): t = _L[L['lang']]; return _line_tex(L, _acc_series(L, _P6), t['y'], 0.45, 0.95, cap, 0.75)
def svg_m2_acc0(L): t = _L[L['lang']]; return _line_svg(L, _acc_series(L, _P0), t['y'], 0.45, 0.95, [0.5, 0.6, 0.7, 0.8, 0.9], 0.75, t['lim'])
def tex_m2_acc0(L, cap): t = _L[L['lang']]; return _line_tex(L, _acc_series(L, _P0), t['y'], 0.45, 0.95, cap, 0.75)
def _dec_series(L):
    t = _L[L['lang']]
    return [([float(d['altas_evidentes']) for d in _ps(_P6)], 'var(--accent)', False, t['d6']), ([float(d['altas_evidentes']) for d in _ps(_P0)], 'var(--hot)', False, t['d0'])]
def svg_m2_dec(L): t = _L[L['lang']]; return _line_svg(L, _dec_series(L), t['yd'], 0, 0.85, [0, 0.2, 0.4, 0.6, 0.8], 0.5, t['meio'])
def tex_m2_dec(L, cap): t = _L[L['lang']]; return _line_tex(L, _dec_series(L), t['yd'], 0, 0.85, cap, 0.5)
_T0, _TP, _TM = 17.8, 29.1, 34.6
def _apt(T):
    if T <= _T0 or T >= _TM: return 0.0
    a = 3 * (_TP - _T0) / (_TM - _T0); b = 3 - a
    return ((T - _T0) / (_TP - _T0)) ** a * ((_TM - T) / (_TM - _TP)) ** b
def svg_m2_apt(L):
    t = _L[L['lang']]; x0, x1, y0, y1 = 70, 620, 20, 240; X = lambda T: x0 + (T - 14) / 24 * (x1 - x0); Y = lambda v: y1 - v * (y1 - y0)
    g = [f'<svg viewBox="0 0 640 300" role="img" aria-label="{E(t["ty"])}">']
    for v in [0, 0.25, 0.5, 0.75, 1]: g.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/><text class="ax" x="{x0-8}" y="{Y(v)+4:.1f}" text-anchor="end">{_fx(v,L)}</text>')
    for T in range(14, 39, 4): g.append(f'<text class="ax" x="{X(T):.1f}" y="{y1+18}" text-anchor="middle">{T}</text>')
    g.append('<polyline fill="none" stroke="var(--accent)" stroke-width="2.5" points="' + ' '.join(f'{X(T/10):.1f},{Y(_apt(T/10)):.1f}' for T in range(140, 381, 2)) + '"/>')
    g.append(f'<circle cx="{X(_TP):.1f}" cy="{Y(1):.1f}" r="5" fill="var(--hot)"/><text class="lbl" x="{X(_TP)-10:.1f}" y="{Y(1)-8:.1f}" text-anchor="end">{E(t["pk"])}</text>')
    g.append(f'<text class="lbl" x="{(x0+x1)/2}" y="{y1+42}" text-anchor="middle">{E(t["tx"])}</text><text class="lbl" transform="translate(16,{(y0+y1)/2}) rotate(-90)" text-anchor="middle">{E(t["ty"])}</text></svg>')
    return ''.join(g)
def tex_m2_apt(L, cap):
    t = _L[L['lang']]; uc = 'true' if L['decimal'] == ',' else 'false'
    return (r"\begin{figure}[tb]\centering\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=4.8cm,xmin=14,xmax=38,ymin=0,ymax=1.12,yticklabel style={/pgf/number format/fixed,/pgf/number format/use comma=" + uc + r"},"
            r"xlabel={" + esc_text(t['tx']) + r"},ylabel={" + esc_text(t['ty']) + r"},label style={font=\footnotesize},tick label style={font=\scriptsize},ymajorgrids,grid style={gray!25},axis line style={gray!60}]"
            r"\addplot[color=fraccent,very thick] coordinates {" + ' '.join(f'({T/10:.1f},{_apt(T/10):.4f})' for T in range(140, 381, 2)) + r"};"
            r"\addplot[only marks,mark=*,color=frhot,mark size=2pt] coordinates {(29.1,1)};\node[font=\scriptsize,anchor=south east] at (axis cs:29.1,1) {" + esc_text(t['pk']) + r"};"
            r"\end{axis}\end{tikzpicture}\caption{" + cap + r"}\end{figure}" + "\n")
def _tl_data():
    v = _json.load(open('dados/msa01/msa01_semana_vale.json'))
    pk = {}
    for d in _csv.DictReader(open('dados/msa01/msa01_pico.csv', encoding='utf-8')):
        if d['alta'] == '1': pk.setdefault(d['uf'], []).append(int(d['k_pico']))
    out = []
    for uf, w in v.items():
        p = sorted(pk.get(uf, [])); m = None
        if p: m = (w - 1 + (p[len(p) // 2] if len(p) % 2 else (p[len(p) // 2 - 1] + p[len(p) // 2]) / 2)) % 52 + 1
        out.append((_UFN[uf], w, m))
    return sorted(out, key=lambda r: (r[1] if r[1] >= 27 else r[1] + 52, r[0]))
def svg_m2_tl(L):
    t = _L[L['lang']]; D = _tl_data(); x0, x1, y0 = 50, 620, 20; dy = 13; X = lambda w: x0 + (w - 1) / 51 * (x1 - x0)
    h = y0 + dy * len(D) + 50; g = [f'<svg viewBox="0 0 640 {h}" role="img" aria-label="{E(t["tl_v"])}">']
    for w in (1, 9, 18, 27, 36, 45, 52): g.append(f'<line x1="{X(w):.1f}" x2="{X(w):.1f}" y1="{y0-6}" y2="{y0+dy*len(D)}" stroke="var(--line)"/><text class="ax" x="{X(w):.1f}" y="{y0+dy*len(D)+16}" text-anchor="middle">{w}</text>')
    for i, (uf, w, m) in enumerate(D):
        y = y0 + i * dy + 4; g.append(f'<text class="ax" x="{x0-8}" y="{y+4}" text-anchor="end">{uf}</text><circle cx="{X(w):.1f}" cy="{y}" r="4" fill="var(--accent)"/>')
        if m is not None: g.append(f'<rect x="{X(m)-4:.1f}" y="{y-4}" width="8" height="8" fill="var(--hot)"/>')
    yl = y0 + dy * len(D) + 36
    g.append(f'<circle cx="{x0+6}" cy="{yl-4}" r="4" fill="var(--accent)"/><text class="ax" x="{x0+16}" y="{yl}">{E(t["tl_v"])}</text><rect x="{x0+250}" y="{yl-8}" width="8" height="8" fill="var(--hot)"/><text class="ax" x="{x0+264}" y="{yl}">{E(t["tl_p"])}</text></svg>')
    return ''.join(g)
def tex_m2_tl(L, cap):
    t = _L[L['lang']]; D = _tl_data()
    s = [r"\begin{figure}[tb]\centering\begin{tikzpicture}\begin{axis}[width=\columnwidth,height=9.2cm,xmin=0,xmax=53,ymin=-1,ymax=" + str(len(D)) + r",ytick={" + ','.join(str(i) for i in range(len(D))) + r"},yticklabels={" + ','.join(r[0] for r in D) + r"},y dir=reverse,"
         r"xtick={1,9,18,27,36,45,52},xlabel={" + esc_text(t['tl_x']) + r"},label style={font=\footnotesize},tick label style={font=\tiny},xmajorgrids,grid style={gray!25},axis line style={gray!60},"
         r"legend style={font=\scriptsize,draw=none,at={(0.5,1.02)},anchor=south,legend columns=2},legend cell align=left]"]
    s.append(r"\addplot[only marks,mark=*,color=fraccent,mark size=1.6pt] coordinates {" + ' '.join(f'({w},{i})' for i, (u, w, m) in enumerate(D)) + r"};\addlegendentry{" + esc_text(t['tl_v']) + "}")
    s.append(r"\addplot[only marks,mark=square*,color=frhot,mark size=1.6pt] coordinates {" + ' '.join(f'({m:.1f},{i})' for i, (u, w, m) in enumerate(D) if m is not None) + r"};\addlegendentry{" + esc_text(t['tl_p']) + "}")
    s.append(r"\end{axis}\end{tikzpicture}\caption{" + cap + r"}\end{figure}" + "\n"); return ''.join(s)
SVGFIG.update({'m2_tl': svg_m2_tl, 'm2_apt': svg_m2_apt, 'm2_acc': svg_m2_acc, 'm2_acc0': svg_m2_acc0, 'm2_dec': svg_m2_dec})
TEXFIG.update({'m2_tl': tex_m2_tl, 'm2_apt': tex_m2_apt, 'm2_acc': tex_m2_acc, 'm2_acc0': tex_m2_acc0, 'm2_dec': tex_m2_dec})
