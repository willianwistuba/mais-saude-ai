# Mais Saúde AI: geradores

Geradores do site https://mais-saude-ai.vercel.app e dos PDFs das notas de trabalho (REVTeX). Derivados dos geradores do Física Revisitada, com a mesma tipografia e o mesmo formato, identidade visual própria da área da saúde e três idiomas (pt, en, es). As regras completas estão em `INSTRUCOES.md`.

| Caminho | O que é |
|---|---|
| `meta.py` | Constantes do site, rotas por idioma e lista `ARTS` das notas |
| `body.py` | Conversão do corpo das notas para HTML e LaTeX; figuras em `SVGFIG` e `TEXFIG` |
| `site.py` | Gera o site estático inteiro em `public/` |
| `tex.py` | Gera os PDFs de uma nota nos três idiomas (`python3 tex.py MSA-NN`) |
| `estilo.css` | Folha de estilo do site |
| `i18n/*.json` | Textos de interface, agenda, método e metadados das notas em pt, en e es |
| `src/<idioma>/aNN.html` | Corpo de cada nota |
| `codigo_src/` | Scripts publicados em /codigo/ |
| `dados/` | Dados agregados de cada estudo, um arquivo por estudo, abaixo de 50 MB |
| `pdf/` | PDFs publicados |

```sh
apt-get install -y texlive-publishers texlive-lang-portuguese texlive-lang-spanish texlive-latex-extra texlive-pictures
pip install beautifulsoup4
python3 site.py              # site em public/
python3 tex.py MSA-01        # deve informar overfull 0 nos três idiomas
```
