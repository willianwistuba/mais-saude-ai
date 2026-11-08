# MSA-01: protocolo

**Com quantas semanas de antecedência em relação à simples contagem de casos os dados públicos permitem prever, com acerto de 75% ou mais, se a temporada de dengue de um Estado será de alta incidência, e com quais previsores?**

Protocolo registrado pelo commit que adiciona este texto ao repositório do programa. Mudanças posteriores entram como emendas datadas no fim do arquivo. O registro documenta a ordem entre protocolo e resultados; não comprova que os dados não tenham sido explorados antes, e a avaliação retrospectiva não é cega.

Programa Mais Saúde AI. Nota de trabalho em informática em saúde. A pesquisa e a construção são feitas com IA; o autor revisa o texto final. As etapas feitas com IA não têm validação humana independente (SPEC, seção 3). A nota mede o que dados públicos agregados permitem prever para a população de cada Estado; não é orientação a pessoas nem a serviços.

## 1. Ideia e perguntas

A cada semana chegam novos dados. No começo eles dizem pouco; no fim, a própria contagem de casos já mostra o resultado. Interessa saber se um modelo acerta antes que a contagem deixe o resultado evidente, e com quantas semanas de vantagem.

- **P1 (previsores).** Quais previsores, sozinhos e em duplas, melhoram a previsão de temporada de alta incidência em relação ao histórico do Estado, e quanto cada segundo previsor acrescenta à projeção da contagem num modelo de mesma forma?
- **P2 (início).** Qual é a primeira semana da temporada a partir da qual o critério M (e a projeção A) acerta a previsão sim ou não em 75% ou mais dos pares Estado-temporada, e continua acertando 75% ou mais até a semana 42? Regra principal pela estimativa pontual; regra estrita pelo limite inferior do IC 95%.
- **P3 (antecedência).** Quantas semanas separam esse início da semana em que a simples contagem de casos prováveis já disponíveis deixa evidente metade das temporadas altas? Quantas semanas, por temporada alta, a previsão antecipa a contagem e o pico?
- **P4 (comparação).** M e A superam o histórico (R0)? M supera A?
- **P5 (prospectiva).** Probabilidade de temporada alta em 2026/27, por Estado, com os dados disponíveis em 1 nov. 2026.

**Por que 75%.** Erra em no máximo um de cada quatro pares Estado-temporada, em média, e fica acima de quem sempre responde "não" (cerca de 54%) e do histórico do Estado. Patamar de utilidade, não teste de significância. Acerto global não é sensibilidade: relatam-se também a fração das temporadas altas identificadas, os alarmes falsos e o acerto em cada temporada.

## 2. Unidade, temporada, desfecho e dados

- **Unidade:** as 27 UFs.
- **Temporada por Estado.** Começa na semana epidemiológica de menor incidência média da UF (média móvel de 5 semanas da fração anual de casos prováveis por semana, 2007 a 2013, anteriores às temporadas avaliadas) e dura até a véspera do mesmo ponto no ano seguinte. A temporada "Y/Y+1" começa na semana de vale de Y, se ela for 27 ou mais, ou de Y+1, se for menor que 27.
- **Desfecho:** casos prováveis (notificações não descartadas) com início de sintomas na temporada somam 300 ou mais por 100 mil habitantes (média da população dos dois anos civis).
- **Casos prováveis em todos os anos.** Os arquivos abertos de 2014, 2015 e 2022 a 2026 não trazem as notificações descartadas; os demais trazem. Para que a série seja a mesma em todos os anos, todas as contagens (desfecho, projeção, crescimento, casos fora de época e regra de evidência) usam só as notificações não descartadas. Isso usa a classificação final, que não existia em tempo real: quem acompanha o sistema vê também notificações que depois serão descartadas. A limitação será declarada.
- **Dados:** SINAN dengue (OpenDataSUS, arquivos de 2007 a 2026, hashes registrados); população do IBGE; temperatura média diária MERRA-2 pela API NASA POWER (capital e 5 municípios mais populosos por UF, ponderados pela população); ONI da NOAA.
- **Avaliação:** temporadas 2014/15 a 2024/25 (297 pares).

## 3. O que se sabia em cada semana

- **Datas de previsão:** o domingo de cada semana k da temporada, de k = 0 a k = 42.
- **Digitação:** a notificação conta se foi digitada até o corte. Sem data de digitação válida, conta o valor esperado pela distribuição de atrasos da mesma UF e do mesmo mês nos anos de referência, só anteriores ou iguais ao ano do arquivo: o próprio ano para arquivos até 2012; de 2013 até o ano do arquivo para 2013 a 2015; 2013 a 2015 para os arquivos de 2016 em diante.
- **Defasagem de publicação:** corte em D − 6 semanas (diferença entre o download do arquivo de 2026, em 7 nov. 2026, e a última semana completa que ele contém). Clima com 1 semana de atraso; ONI com 2 meses. A série de clima é a versão baixada em 7 nov. 2026, que pode ter sido revisada depois das datas simuladas.
- **Desfecho conhecido:** o resultado de uma temporada (UF, t) só é considerado conhecido a partir do fim da temporada mais a defasagem de publicação mais 8 semanas para a digitação se completar. Essa regra vale para tudo o que usa desfechos passados: o histórico R0, a fração esperada da projeção, o treino dos modelos e a escolha de M.

## 4. Previsores candidatos

1. **Projeção da contagem (proj):** logaritmo da incidência projetada: casos prováveis disponíveis divididos pela fração mediana disponível na mesma semana k nas temporadas anteriores da UF com desfecho conhecido (mínimo 3).
2. **Crescimento recente (cresc):** inclinação do logaritmo dos casos semanais nas 4 últimas semanas disponíveis.
3. **Casos fora de época (fora):** logaritmo da incidência disponível com início nas 13 primeiras semanas da temporada, menos a mediana do mesmo valor, na mesma semana k, nas temporadas anteriores da UF.
4. **Inverno ameno (inverno):** anomalia da temperatura média nos 91 dias climatologicamente mais frios da UF (climatologia 2006 a 2013) dentro dos 365 dias anteriores ao corte do clima.
5. **Aptidão térmica (apt):** média, nas 8 semanas anteriores, de uma curva unimodal construída para este estudo a partir dos limites e do ótimo de transmissão por *Aedes aegypti* publicados por Mordecai et al. (2017): zero abaixo de 17,8 °C e acima de 34,6 °C, máximo em 29,1 °C. É uma aproximação, não o modelo mecanístico do artigo.
6. **El Niño (oni):** último ONI disponível.

## 5. Modelos

- **R0:** frequência de temporadas altas da UF desde 2007/08 com desfecho conhecido na data, com correção de Laplace.
- **A:** logística simples sobre proj (sem histórico como deslocamento, penalização fixa).
- **Conjuntos candidatos:** cada previsor sozinho (6) e cada dupla (15), em logística com penalização L2 e o logito de R0 como deslocamento, penalização escolhida entre 0,01 e 100 pelo menor Brier nas 3 últimas temporadas do treino. Ajuste separado por semana k. Treino da temporada Y na semana k: pares de temporadas desde 2008/09 com desfecho conhecido na data mais cedo entre as datas de previsão da temporada Y nessa semana.
- **M:** para a temporada t, o conjunto com menor Brier médio (semanas 0 a 42) nas previsões das temporadas de 2011/12 a t − 2, todas com desfecho conhecido antes de qualquer previsão de t. A composição declarada é a escolhida com as temporadas até 2024/25.
- **Previsão sim ou não:** "alta" quando a probabilidade é 50% ou mais.

## 6. Medidas e critérios

- **Acerto** (principal), sensibilidade, especificidade, acerto por temporada, Brier e BSS.
- **Incerteza:** 4.000 reamostragens das 11 temporadas com reposição; IC 95% e chance de acerto de 75% ou mais.
- **Evidente pela contagem:** casos prováveis já disponíveis na data somam 300 ou mais por 100 mil. Como só entram casos prováveis, evidência implica temporada alta.
- **Início (P2):** regra principal e regra estrita, como em P2.
- **Antecedência da janela (P3):** semanas entre o início e a primeira semana com metade ou mais das temporadas altas evidentes. Se o início vier depois, a antecedência é zero (sem janela). Se metade não for atingida até a semana 42, a antecedência é um mínimo (censura). Os intervalos incluem as reamostragens sem janela como zero, e relata-se a fração delas.
- **Antecedência por temporada (P3):** para cada temporada alta, semana em que fica evidente menos a primeira semana a partir da qual o modelo diz "alta" sem interrupção até ela; e semana do pico menos essa mesma semana. Relatam-se a mediana, a fração antecipada em 4 semanas ou mais e o alarme falso no início.
- **Ganho incremental (P1):** BSS de cada dupla com a projeção sobre a projeção sozinha, no mesmo modelo, com chance de ganho positivo.
- **Frase de conclusão:** se a janela de M existir pela regra principal, a conclusão dirá: "Com o critério M, composto por [previsores], é possível prever uma temporada alta com [X] semanas de antecedência em relação à simples contagem de casos", com o IC, o número pela regra estrita e a comparação com A. Se não existir, a conclusão dirá isso.

## 7. Previsão prospectiva (P5)

Na data de 1 nov. 2026 (corte de 20 set. 2026), M, A e R0 com as temporadas de desfecho conhecido dão a probabilidade de alta em 2026/27 para as UFs cuja temporada já começou. Gravada por commit antes de qualquer dado posterior.

## 8. Sensibilidades

- S1. Defasagem de publicação de 0 e de 10 semanas.
- S2. Evidência com 25% e 75% das temporadas altas.
- S3. Sem as temporadas 2015/16 a 2017/18 e 2019/20 a 2020/21, excluídas também do cálculo dos previsores e do histórico.
- S4. Temporada nacional (semana 27 à 26).

## 9. Relato e ética

TRIPOD+AI, EPIFORGE e RECORD. Dados públicos agregados por UF; dispensa de comitê de ética (Res. CNS 510/2016; Ofício Circular CONEP 17/2022). Ficha de uso de IA com a declaração de ausência de validação humana independente. Resultado negativo também é publicado.

## Emendas

### Emenda 1 (7 nov. 2026)

Redação. No segundo parágrafo, a frase "O registro documenta a ordem entre protocolo e resultados; não comprova que os dados não tenham sido explorados antes, e a avaliação retrospectiva não é cega." passa a ser lida como: "Como em toda análise retrospectiva de dados públicos, o registro prévio do protocolo documenta a ordem das etapas, mas não equivale a um estudo cego." A emenda só alinha a redação do protocolo à da nota; não muda perguntas, dados, modelos, medidas, critérios nem resultados. O texto original continua acima, sem alteração.

### Emenda 2 (7 nov. 2026)

Análise adicional, definida depois de conhecidos os resultados principais e identificada assim na nota. Para cada um dos 21 modelos da triagem (6 previsores sozinhos e 15 duplas), com as previsões já publicadas, calculam-se as mesmas medidas da seção 6: início pela regra principal e pela regra estrita, antecedência da janela em relação à semana em que metade das temporadas altas fica evidente, IC 95% por 4.000 reamostragens das temporadas (sem janela contada como zero), fração das reamostragens sem janela, acerto máximo e sensibilidade e especificidade no início. Objetivo: saber quanto cada previsor, sozinho ou em dupla, antecipa a contagem. Não muda o critério M, o desfecho principal nem a frase de conclusão.

### Emenda 3 (7 nov. 2026)

Correções e análises acrescentadas depois de revisão externa dos resultados, identificadas assim na nota.

1. **Correção de cálculo.** A fração de temporadas altas antecipadas antes do pico passa a usar como denominador todas as temporadas altas; as que o modelo não antecipou contam como não antecipadas.
2. **Sensibilidade S5 (classificação em tempo real).** Nos arquivos que trazem as notificações descartadas (2007 a 2013 e 2016 a 2021), os previsores de contagem (projeção, crescimento e casos fora de época) passam a usar todas as notificações disponíveis, como as veria quem acompanha o sistema antes da classificação final. O desfecho e a regra de evidência continuam com os casos prováveis. Nos arquivos sem as descartadas (2014, 2015 e 2022 a 2026), nada muda, e isso é declarado.
3. **Brier agregado.** Relata-se o escore de Brier agregado de A, do procedimento M e da dupla fixa escolhida ao final, separando o desempenho do procedimento (que trocou de modelo ao longo das temporadas) do da composição final, que fica como achado a confirmar.

### Emenda 4 (7 nov. 2026)

Comparação limpa para a sensibilidade S5. Como os arquivos de 2014, 2015 e 2022 a 2026 não trazem as notificações descartadas, a versão S5 da emenda 3 mistura dois tipos de contagem. Para isolar o efeito da classificação final, repete-se o desenho principal só com as temporadas cujos arquivos trazem as descartadas (temporadas 2013/14, 2014/15, 2015/16 e de 2021/22 em diante excluídas do treino, do histórico e da avaliação; avaliação em 2016/17 a 2020/21), em duas versões iguais em tudo, exceto na contagem dos previsores: só casos prováveis, ou todas as notificações disponíveis. A diferença de antecedência entre as duas versões é a estimativa do efeito da classificação final. Relatam-se também a antecedência de cada modelo (emenda 2) nas duas versões.

### Emenda 5 (7 nov. 2026)

Correção de código, regra de alerta e teste em temporadas reservadas. Tudo o que está nesta emenda foi definido depois de examinados os resultados anteriores e de revisão externa; são análises retrospectivas adicionais, não validação prospectiva nem independente, e a nota as identifica assim.

1. **Validação interna da penalização.** Na escolha da força da penalização, cada temporada de validação interna passa a usar só pares de treino com desfecho conhecido na data mais cedo das previsões dessa temporada de validação, como já acontecia no treino externo. Rodam de novo a análise principal e todas as sensibilidades. Relata-se a comparação antes e depois: fração dos ajustes em que a penalização escolhida mudou, mudança média absoluta das probabilidades, Brier e antecedência.
2. **Regra de alerta, fixada antes do cálculo.** Monitoramento da semana 0 à 42 da temporada de cada Estado. Alerta é a primeira semana em que a probabilidade do modelo é 50% ou mais nela e na semana anterior; vale só o primeiro alerta, sem cancelamento. Nenhum outro limiar é testado. A mesma regra vale para R0, A, M e a dupla fixa projeção e casos fora de época. Para cada temporada alta: semanas entre o alerta e a semana em que os casos prováveis disponíveis passam de 300 por 100 mil (se não passam até a semana 42, usa-se 43 e a antecedência é marcada como mínimo), e semanas entre o alerta e o pico; temporada alta sem alerta antes da evidência conta como não antecipada, com antecedência zero. Para cada temporada não alta: alarme falso se houver alerta até a semana 42. Resumo: mediana da antecedência, fração antecipada, fração antecipada antes do pico e fração de alarmes falsos, com IC 95% por 4.000 reamostragens das temporadas. Calculado na análise principal e na comparação limpa da S5.
3. **Teste em temporadas reservadas.** Escolhe-se, entre os 21 modelos da triagem, o de menor Brier nas previsões das temporadas de 2011/12 a 2018/19 apenas. Esse modelo, A e R0 são avaliados, com a regra de alerta e com as medidas de acerto e antecedência, só nas temporadas de 2020/21 a 2024/25, que não entraram na escolha.

### Emenda 6 (7 nov. 2026)

Duas análises adicionais, registradas antes de qualquer cálculo. São análises retrospectivas definidas depois de conhecidos os resultados anteriores, e a nota as identifica assim. As temporadas de 2020/21 a 2024/25 já foram usadas no teste da emenda 5 e não servem mais como teste limpo; os resultados nelas são relatados só como descrição.

1. **Regra de três estados com faixa da projeção.**
   - **Erro da projeção:** para cada par (UF, temporada) e semana k, e = log(incidência final + 1) − log(incidência projetada na data + 1), com a projeção como calculada naquela data (previsor proj).
   - **Faixa:** para a previsão da UF na temporada Y na semana k, com data D, tomam-se os quantis de 10% e 90% de e em todos os pares (de qualquer UF) na mesma semana k com desfecho conhecido em D e projeção disponível; mínimo de 30 pares, senão o estado é indefinido. Limite inferior = (projeção + 1)·exp(q10) − 1, nunca abaixo da incidência já disponível; limite superior = (projeção + 1)·exp(q90) − 1.
   - **Estados:** "alta" se o limite inferior for 300 por 100 mil ou mais; "baixa" se o limite superior ficar abaixo de 300; "indefinida" nos demais casos, inclusive sem projeção.
   - **Alerta:** a primeira semana com estado "alta" nela e na anterior, como na regra da emenda 5; vale só o primeiro alerta. Medidas iguais às da emenda 5 (antecedência em relação à evidência e ao pico, fração antecipada, alarme falso, IC 95% por 4.000 reamostragens das temporadas), mais, por semana k: cobertura da faixa (fração de desfechos dentro dela), fração de estados indefinidos e acerto entre os estados decididos.
   - **Onde:** análise principal (temporadas 2014/15 a 2024/25) e comparação limpa da S5 nas duas versões. Sensibilidade única: faixa de 90% (quantis de 5% e 95%). Estado prospectivo de cada UF em 1 nov. 2026.
2. **Capital e interior.**
   - A base agregada passa a separar, em cada UF, as notificações com município de residência igual à capital (códigos do IBGE em `dados/capitais_ibge.csv`, 6 primeiros dígitos) das demais, inclusive as sem município, que contam como interior. Os totais por UF não mudam; confere-se que os previsores já existentes ficam iguais.
   - **Capital (cap):** logaritmo dos casos prováveis disponíveis da capital + 1, menos a mediana do mesmo valor, na mesma semana k, nas temporadas anteriores da UF (mínimo 3), com as mesmas regras de disponibilidade e exclusão de "fora". Usa contagens, não incidência, porque não há população municipal na base; o crescimento da população em 20 anos é pequeno perto da variação entre temporadas.
   - **Interior (int):** o mesmo para as notificações fora da capital. No Distrito Federal, que não tem interior, int = 0.
   - A triagem passa a ter 8 previsores sozinhos e 28 duplas (36 modelos); o procedimento M escolhe entre os 36, com as mesmas regras. Relatam-se o ganho incremental de proj+cap e proj+int sobre a projeção, a antecedência de cada modelo novo (emenda 2) e a regra de alerta da emenda 5 para M e para essas duas duplas. O teste da emenda 5 é refeito com os 36 modelos (escolha em 2011/12 a 2018/19, avaliação em 2020/21 a 2024/25), relatado só como descrição. Todas as sensibilidades rodam de novo.
   - A frase de conclusão segue a seção 6, com a composição de M que resultar.
