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
