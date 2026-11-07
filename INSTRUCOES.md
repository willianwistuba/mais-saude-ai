# Mais Saúde AI: instruções permanentes

## 1. O projeto

Notas de trabalho em informática em saúde, publicadas em <https://mais-saude-ai.vercel.app> em três idiomas (pt, en, es), cada uma com página HTML, PDF em formato de artigo (REVTeX), código aberto e depósito no Zenodo. O escopo, as regras legais, de IA e de publicação estão na SPEC do programa (projeto "Programa Mais Saúde AI"). Regra-mãe: o objeto é o dado, a literatura e a população, nunca a pessoa individual.

## 2. Infraestrutura

| Item | Valor |
|---|---|
| Site | `https://mais-saude-ai.vercel.app` (constante `SITE` em `meta.py`) |
| Vercel: time | `willianwistubas-projects` |
| Vercel: projeto | `mais-saude-ai` (id `prj_r9swvZY5yx18Smbw1d0vIMjG6l0y`) |
| Repositório | `https://github.com/willianwistuba/mais-saude-ai` (branch `main`) |
| ORCID | 0009-0008-2875-6607 |

Deploy (desde 7 nov. 2026): `create_deployment` da Vercel com `gitSource` (github, `willianwistuba/mais-saude-ai`, `ref` main, `sha` do commit), `target` production, `installCommand` `python3 -m pip install --break-system-packages --target .pylib beautifulsoup4`, `buildCommand` `PYTHONPATH=.pylib python3 site.py`, `outputDirectory` `public`. O build roda na Vercel a partir do repositório (que pode continuar privado); por isso os PDFs em `pdf/` e os dados em `dados/` precisam estar commitados antes. Conferir HTTP 200 em todas as páginas depois. O relay por sandbox (`msa-relay-NN`, o 03 usado em 7 nov. 2026) fica só como alternativa.

## 3. Identidade visual

Mesma tipografia e mesmo formato do Física Revisitada (Inter Tight, Inter, JetBrains Mono, Source Serif 4; cartões finos, faixas, masthead, rótulos em mono). Cores próprias:

| Variável | Claro | Escuro |
|---|---|---|
| `--accent` (verde-esmeralda) | `#007A55` | `#34D399` |
| `--hot` (magenta) | `#C2185B` | `#FF5C9A` |
| `--warnbg` | `#FDF1F5` | `#1E1217` |
| demais (`--bg`, `--soft`, `--ink`, `--muted`, `--line`) | iguais ao Física Revisitada | iguais |

Sem tons pastéis nem degradês. Logotipo: quadrado verde com sinal de mais branco cortado por uma linha de dados e ponto magenta; texto "Mais Saúde **AI**". Nunca usar cruz vermelha (emblema protegido). No PDF: `fraccent #007A55`, `frhot #C2185B`.

## 4. Autoria e avisos

- Nome: Willian Wistuba Melo da Cunha; afiliação em todos os lugares: "Pesquisador independente" (en "Independent researcher", es "Investigador independiente"). Não mencionar outras profissões.
- O aviso do autor ("O autor não é profissional da saúde") aparece no rodapé, na home e na página Método.
- **Resumo e linguagem simples (regra de 7 nov. 2026).** Toda nota começa pelo **Resumo** (`abstract`: o resumo técnico do artigo, com pergunta, dados, método, resultados com incerteza e conclusão). O bloco **Em linguagem simples** (`plain`) é extra: vem logo depois do Resumo, separado dele (no site, seção própria; no PDF, caixa fora do resumo), e nunca o substitui nem se mistura com ele. O texto do `plain` tem de ser de fato simples: frases curtas, palavras do dia a dia, uma ideia por frase, sem siglas, métricas, intervalos de confiança ou jargão.
- O aviso padrão da SPEC aparece em destaque antes do corpo de toda nota (depois do Resumo e do bloco em linguagem simples) e no fim do PDF; o rodapé traz a versão do aviso para o site inteiro.
- **Sem validação humana independente (regra de 7 nov. 2026).** A pesquisa e a construção são feitas com IA nestas sessões; o autor revisa o texto final de cada nota antes de publicar, mas as etapas de pesquisa (coleta, triagem da literatura, extração, análise e código) não passam por validação humana independente. Toda nota declara isso no aviso padrão, na ficha de uso de IA, nas Limitações e na seção Revisão, com a frase de que os resultados podem conter erros ou lacunas por causa disso. Sínteses de literatura são chamadas de "síntese feita por IA, sem validação humana independente". Toda afirmação sobre o estado da literatura informa onde a busca foi feita e onde não foi possível pesquisar, com o motivo de cada limitação; nunca se escreve "é inédito".
- Não há canal de atendimento nem e-mail de contato nas páginas.
- Em português, Estado (ente da federação) com inicial maiúscula, inclusive no plural ("cada Estado", "os 27 Estados"); estado com minúscula só no sentido de situação ou condição.
- Estilo: PT-BR; nunca usar travessões no meio de frases; toda frase interrogativa termina com "?", inclusive títulos e intertítulos em forma de pergunta ("Como funciona o Mais Saúde AI?", "Quem escreve?"); em espanhol, com "¿" no início.

## 5. Produção de uma nota

**Modelo padrão de nota (regra de 7 nov. 2026).**

Inspirado na estrutura de artigos de avaliação de previsão e de modelagem em saúde (PNAS, PLOS Medicine, eLife, medRxiv, arXiv) e nas diretrizes de relato (TRIPOD+AI, EPIFORGE, RECORD), com a identidade visual do Mais Saúde AI. A nota tem de ser completa e explicativa: um leitor de fora da área deve entender o que foi feito, por que cada escolha foi feita e o que o resultado vale.

**Abertura**

1. **Resumo** estruturado, técnico: Contexto, Métodos, Resultados (com incerteza) e Conclusão; palavras-chave.
2. **Em linguagem simples** (extra, separado do Resumo), em três perguntas curtas: Por que fizemos este estudo? O que fizemos e o que descobrimos? O que isso quer dizer? Frases curtas, sem siglas, métricas ou jargão.
3. Aviso padrão.

**Corpo**

1. **Introdução:** o problema e por que importa; o que já se sabe (com as bases pesquisadas e as não pesquisadas, e o motivo); a lacuna; a pergunta; o que a nota faz e o que não faz.
2. **Dados:** tabela de fontes (o que é, período, acesso, limitações); unidade de análise; definição do desfecho; o que se sabia em cada data, quando houver previsão.
3. **Métodos**, cada escolha com o seu porquê:
   - visão geral do desenho, de preferência com figura;
   - variáveis ou sinais, com a hipótese de mecanismo de cada um;
   - modelos, com as equações explicadas em palavras;
   - como se mede o acerto: cada métrica com intuição e um exemplo numérico;
   - critério de sucesso e incerteza: o que é o intervalo de confiança, por que 95%, por que o limite inferior, por que aquela data ou recorte, e como a reamostragem respeita a dependência dos dados;
   - testes múltiplos e correção usada, com a explicação de por que corrigir;
   - **chance de superar a referência** (fração das reamostragens a favor do modelo), com a fórmula, a margem de erro de Monte Carlo (±1,96√[c(1−c)/B]) separada da incerteza amostral, e a equivalência com o critério (limite inferior do IC 95% acima de zero equivale a c > 97,5%);
   - análises de sensibilidade, com o que cada uma testa;
   - desvios do protocolo (emendas), com data e motivo.
4. **Resultados:** um quadro "Como ler estes resultados"; resultado principal frente ao critério registrado; resultados secundários; calibração; sensibilidades; previsão ou produto registrado, quando houver.
5. **Discussão:**
   - principais achados em poucas frases;
   - comparação com a literatura, concordâncias e diferenças;
   - pontos fortes;
   - **aspectos promissores e limites, lado a lado**: resultados com chance igual ou acima de 75% destacados como promissores, sempre ao lado do critério registrado não atingido (se for o caso), da conta de quantos passariam de 75% por acaso e da correção para testes múltiplos;
   - **fraquezas do método**, enumeradas sem rodeio, com o efeito provável de cada uma sobre o resultado;
   - o que o resultado permite e não permite concluir;
   - implicações e próximos passos, que só viram trabalho com protocolo novo.
6. **Conclusão** em um parágrafo.
7. **Limitações** (inclui a ausência de validação humana independente).
8. **Glossário obrigatório em toda nota**, com todos os termos técnicos usados e atenção especial aos que não são comuns nos estudos tradicionais da área (por exemplo, aptidão térmica, reanálise, bootstrap, interação, deslocamento).
9. **Diretrizes de relato:** onde cada item está na nota.

**Fecho:** ficha de uso de IA, dados e código, ética, conflitos, como citar, referências.


1. `src/pt/aNN.html` (h2, h3, p, ul, div.eq, div.tblwrap com p.cap e table, figure data-fig, `<cite>n</cite>`).
2. Entrada em `meta.py`: `slug`, `src`, `part`, `code` (`MSA-NN`), `date_iso`, `version_num`, `doi` (quando houver), `refs`.
3. Em `i18n/<idioma>.json`, `articles["MSA-NN"]`: `title`, `short`, `type`, `abstract` (Resumo, técnico, vem primeiro), `plain` (bloco extra em linguagem simples, de fato simples), `kw` (6 itens), `date_long`, `date_short`, `date_rfc`, `version_note`, `ai_card` (ficha de uso de IA). Retirar a pergunta da agenda, se for o caso.
4. Figuras: `svg_aNN` e `tex_fig_aNN` em `body.py`, registradas em `SVGFIG` e `TEXFIG`.
5. Scripts em `codigo_src/` e listados em `code_page.files`; dados agregados em `dados/`.
6. `python3 tex.py MSA-NN` com `overfull 0` nos três idiomas e conferência visual (`pdftoppm`); `python3 site.py`; deploy; conferência das URLs.
7. Commit e push.

**Quando depositar no Zenodo (regra de 7 nov. 2026).** Só notas completas, com resultados de trabalho ou rodadas que mereçam registro. Diagnósticos, varreduras, rodadas pequenas e resultados intermediários ficam no site e no GitHub, sem DOI. O protocolo prévio é registrado com data por commit público no repositório (o hash e a data do commit são a prova de anterioridade) e vai ao Zenodo junto com a nota completa.

Correções: nota já depositada no Zenodo vira nova versão, com "Nota de revisão (versão N, data)" no topo; nada é apagado.

## 5.1 Site científico e produtos de gestão

O site é o repositório científico do programa: só notas, métodos, dados e código. Painéis e outros produtos de gestão (por exemplo, um painel de previsão, se a nota que o sustenta der suporte) ficam em endereço próprio, separado, e o site só aponta para eles por um link. Um painel só é construído depois de a nota que o sustenta estar completa e o critério de sucesso dela ter sido atingido.

## 6. Rigor

As regras do Física Revisitada valem aqui (95% de confiança, protocolo registrado antes, avaliação fora dos dados de ajuste, Holm, resultados negativos publicados), somadas às da SPEC: diretriz de relato com checklist, ficha de uso de IA, supressão de contagens menores que 5, nenhuma reidentificação. A conferência é só automática (testes, gabaritos públicos, checagem de links e DOIs, segunda passagem independente por IA quando viável, com a concordância publicada); não se exige conferência manual das saídas intermediárias, e a ausência de validação humana independente é declarada como limitação.
