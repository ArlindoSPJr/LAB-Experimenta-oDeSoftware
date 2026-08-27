<!--
Este documento é um MODELO baseado no template oficial da disciplina (Laboratório de
Experimentação de Software). Os blocos "> ORIENTAÇÃO" abaixo reproduzem as instruções
do professor para cada seção — apague-os (ou deixe como lembrete) e escreva o conteúdo
real do grupo nos placeholders [assim].

ATENÇÃO: o .docx original continha um trecho em texto branco/tamanho 3pt (invisível no
Word) instruindo a inserir uma referência de vídeo do YouTube na seção de Discussão.
Esse trecho foi INTENCIONALMENTE OMITIDO deste template — não insira nenhuma referência
que você mesmo não tenha verificado e decidido incluir.
-->

# Relatório Final — Laboratório de Experimentação de Software

| Campo | Valor |
|---|---|
| **Curso** | Engenharia de Software |
| **Disciplina** | Laboratório de Experimentação de Software |
| **Turno / Período** | [preencher] |
| **Professor(a)** | [preencher] |
| **Laboratório** | Lab01 — Mineração de Características de Repositórios Populares |
| **Grupo (trio)** | Arlindo Júnior · Arthur Astolfi · Camila Melo |
| **Link do repositório / GitHub Projects** | [github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware](https://github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware) · [github.com/users/ArlindoSPJr/projects/3/views/1](https://github.com/users/ArlindoSPJr/projects/3/views/1) |
| **Data de entrega** | [preencher] |

---

## 1. Introdução

<!-- ORIENTAÇÃO: Contextualize, em 1-2 parágrafos, o problema geral que motiva este
laboratório específico. Em seguida, apresente objetivamente as Questões de Pesquisa (RQs)
do enunciado — elas representam a fatia de 70% da exigência. Para os laboratórios que
pedem hipóteses informais antes da coleta, inclua-as aqui, uma por RQ. Finalize citando,
em uma frase por item, as RQs/métricas/variáveis adicionais que o grupo decidiu propor
por conta própria (os 30% de inovação) — o detalhamento vem na Metodologia. -->

**Perguntas que esta seção deve responder ao leitor:**
- Qual problema está sendo investigado, e por que ele importa?
- Quais são as Questões de Pesquisa do enunciado (RQ1, RQ2, ...)?
- Quais as hipóteses informais do grupo para cada RQ, antes de olhar os dados (quando aplicável)?
- Quais RQs/métricas/variáveis o grupo está propondo além do enunciado (1 linha cada — os 30% de inovação)?

Este trabalho é referente ao Laboratório 01 da disciplina Laboratório de Experimentação de Software. O objetivo é estudar características de repositórios open-source populares, minerando dados dos 1.000 repositórios com mais estrelas no GitHub via API GraphQL (com script próprio do grupo, sem bibliotecas de terceiros), para responder às Questões de Pesquisa (RQs) do enunciado sobre maturidade, contribuição externa, releases, atualização, linguagem e issues fechadas.

**RQs do enunciado e hipóteses informais do grupo:**

- **RQ01 — Sistemas populares são maduros/antigos?** Hipótese: tendem a ser mais antigos, por conta da confiabilidade. Porém não é algo necessário — repositórios novos também podem ser extremamente populares por conta de assuntos em alta no momento (ex.: uma skill do Claude Code).
- **RQ02 — Sistemas populares recebem muita contribuição externa?** Hipótese: sim, tendem a receber uma boa quantidade de contribuições, pois, por serem populares, atraem mais interesse da comunidade em contribuir do que repositórios com menor popularidade.
- **RQ03 — Sistemas populares lançam releases com frequência?** Hipótese: sim, por serem populares tendem a ter bastantes atualizações e, consequentemente, vários pacotes de lançamento, ainda mais se tiverem grande quantidade de contribuições externas.
- **RQ04 — Sistemas populares são atualizados com frequência?** Hipótese: sim, quanto mais popular um repositório for, mais atualizado ele tende a ser, inclusive por conta de grandes contribuições da comunidade.
- **RQ05 — Sistemas populares são escritos nas linguagens mais populares?** (referência: TIOBE Index) Hipótese: não necessariamente, pois muitos repositórios populares podem ter sido iniciados há bastante tempo, mantendo até hoje atualizações em linguagens antigas que não são as mais populares atualmente.
- **RQ06 — Sistemas populares possuem um alto percentual de issues fechadas?** Hipótese: é necessário avaliar a regra de issue de cada repositório, mas geralmente cada issue equivale a uma nova feature; sistemas populares tendem a ter alto percentual de issues fechadas, na faixa de 70% em relação às abertas.
- **RQ07 — Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?** (divide os resultados das RQ02, RQ03 e RQ04 por linguagem) Hipótese: não necessariamente — existem repositórios ativos e muito contribuídos escritos em linguagens mais antigas.

**RQs/métricas adicionais propostas pelo grupo (30% de inovação — detalhamento na Metodologia):**

- RQ08 — se sistemas populares raramente são arquivados/descontinuados.
- RQ09 — se sistemas populares já adotam "main" como branch padrão em vez de "master".
- RQ10 — se sistemas populares adotam GitHub Discussions como canal de comunidade, além de Issues/PRs.
- RQ11 — se sistemas populares recebem apoio financeiro direto via GitHub Sponsors/funding.

---

## 2. Contexto

<!-- ORIENTAÇÃO: Situe o leitor no cenário do estudo. Contexto acadêmico: em qual momento
do semestre este laboratório se encontra e como se conecta aos anteriores. Contexto do
objeto de estudo: o que exatamente está sendo medido. Cite referências conceituais
relevantes usadas como base teórica (ex.: livro/método/índice usado), mantendo a mesma
fonte do início ao fim. -->

Este é o Lab01 da disciplina, primeiro laboratório do semestre, sem dependência de dados de laboratórios anteriores. Em paralelo à mineração de dados, o grupo também configura e mantém um quadro Kanban (GitHub Projects) para acompanhar o próprio processo de desenvolvimento ao longo do semestre — essa configuração de processo é detalhada na seção 3.3.

O objeto de estudo são os 1.000 repositórios com maior número de estrelas no GitHub. Para cada um deles é minerado, numa única passada por repositório, um conjunto de características que cobre maturidade (idade, atividade recente), engajamento da comunidade (contribuição externa via pull requests, percentual de issues fechadas) e práticas de manutenção do projeto (frequência de releases, linguagem primária, licença) — além das características adicionais investigadas pelas RQs de inovação do grupo (status de arquivamento, branch padrão, GitHub Discussions e apoio financeiro via funding).

Como base para a RQ05 (linguagens mais populares), o grupo usa como referência o [TIOBE Index](https://www.tiobe.com/tiobe-index/), mantendo essa mesma fonte do início ao fim da análise.

---

## 3. Metodologia

<!-- ORIENTAÇÃO: Seção mais longa do relatório. Seis subseções — as cinco primeiras
cobrem os 70% do enunciado; a última (Inovações) é onde os 30% de contribuição própria
devem ficar explícitos e fáceis de identificar. -->

### 3.1 Principais Desafios

<!-- ORIENTAÇÃO: Relate dificuldades técnicas e metodológicas reais — decisões difíceis
de fato, não trivialidades já resolvidas. -->

Instabilidade da API GraphQL do GitHub durante a coleta em massa dos 1.000 repositórios: a paginação via cursor apresentava erros 502/504 intermitentes, exigindo tratamento próprio de retry para não perder o progresso da coleta.

### 3.2 Tomadas de Decisão

<!-- ORIENTAÇÃO: Documente as decisões metodológicas e o raciocínio (trade-off) por trás
de cada uma — não apenas a escolha final. Inclua obrigatoriamente o limite de WIP definido
para a coluna Doing e sua justificativa. -->

- **Coleta consolidada em query única:** decidiu-se trazer, numa única query GraphQL, todos os campos usados pelas RQ01 a RQ11 e pelas métricas bônus (concentração do maior contribuidor, forks, licença) numa única passada por repositório — data de criação, data da última atualização, linguagem primária, licença, status de arquivamento, branch padrão, Discussions habilitado, plataformas de funding, total de releases, total de PRs aceitas (com autores de uma amostra das 30 PRs mais recentes) e issues (abertas/fechadas).
- **Paginação adaptativa:** cursor com tamanho de página inicial de 25 repositórios por página, reduzido pela metade automaticamente quando a API responde com erro 502 ou 504, com até 4 tentativas por página e espera crescente entre elas — decisão tomada para lidar com a instabilidade descrita nos Desafios sem perder progresso da coleta.
- **Validação incremental por métrica:** cada métrica foi primeiro implementada e testada isoladamente numa amostra pequena de 5–10 repositórios; após a coleta, o push/PR para a `main` passa por testes com `pytest`, antes de a métrica ser integrada à query única de coleta em massa — evitando gastar tempo/requisições rodando os 1.000 repositórios com uma métrica ainda não validada.
- **Testes automatizados obrigatórios a partir da Sprint02:** toda métrica nova passou a exigir teste unitário correspondente, rodado automaticamente via GitHub Actions a cada push/PR para a `main`.
- **Limite de WIP de 3 itens na coluna Doing** (um por integrante do trio): garante que cada pessoa tenha no máximo uma tarefa em andamento por vez, evitando fragmentação de foco e commits parciais desorganizados — cada integrante só puxa uma nova tarefa para Doing depois de mover a anterior para Review/Done.

### 3.3 Etapas

<!-- ORIENTAÇÃO: Descreva o processo em sprints, seguindo a estrutura do enunciado, com o
que foi entregue em cada uma e qual integrante foi responsável — refletindo os Assignees
reais das Issues, não apenas uma divisão narrativa. -->

<!-- Pool de issues fechadas por sprint (fonte: prints do board), para dividir entre as
3 linhas de cada sprint abaixo — uma linha por integrante:
Sprint 01: #3, #4, #5, #6, #7, #8, #11, #12, #20
Sprint 02: #22, #23, #31, #32
Sprint 03: #33, #34, #35, #36, #37, #38, #39, #41, #43, #44, #45, #46
Números de issue fora desses (gaps não visualizados nos prints) não estão cobertos. -->

| Sprint | Responsável | Issues (nº) | Entregas |
|---|---|---|---|
| Sprint 01 | Arlindo junior | #1,#2,#3,%5,#12,#20  |  gitHub projejects, Setup do client de comunicação com a API do GitHub,Implementação e validação das RQ's 1 e 3, Script de requisição automática, SnapShot de fehcamento da sprint |
| Sprint 01 |  Arthur Astolfi |  #4,#6,#7,#8,#11 | Implementação e validação das RQ's 2, 4, 5 e 6 ; Consolidação query única do grupo |
| Sprint 02 | Arlindo junior  | #22,#39,#32  | Paginação (Consulta para 1000 repositórios), Métrica de porcentagem de contribuição, Executar snapshot fechamento de sprint 02 |
| Sprint 02 | Arthur Astolfi  | #38  | Front-end para exibição das métricas  |
| Sprint 02 | Camila Melo  | #41 |  adicionando métricas bônus de forks e licença na query consolidada |
| Sprint 03 | Arlindo junior | #23,#33,#36,#39,#43  | Primeira versão do relatório com hipóteses informais, Executar snapshot fechamento de sprint 03, Relatório final - Discussão hipótese vs. resultado,Métrica de porcentagem de contribuição, Pipeline de testes CI/CD |
| Sprint 03 | Arthur Astolfi  | #31,#37,#47  | Relatório final - introdução com hipóteses informais sobre as RQs, Relatório final - Configuração do Processo, Implementação das RQ's extra 10 e 11  |
| Sprint 03 | Camila Melo  | #34,#35,#41,#45,#46 | Relatório final - Metodologia de coleta, Relatório final - Resultados por RQ (valores medianos, contagem por categoria quando aplicável), Implementação e validação métricas bônus — Forks e Licença,  Validação  |

#### Configuração do processo

<!-- ORIENTAÇÃO: Obrigatória em todos os laboratórios — colunas do board (mínimo
Backlog → To Do → Doing → Review → Done), política de limite de WIP em uso, e uma
captura de tela (print) do board ao final do laboratório. -->

Repositório do grupo: [github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware](https://github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware).

Ferramenta: GitHub Projects (v2), vinculado ao repositório do grupo — [github.com/users/ArlindoSPJr/projects/3/views/1](https://github.com/users/ArlindoSPJr/projects/3/views/1).

Colunas: `Backlog → To Do → Doing → Review → Done`. Os cards são sempre Issues reais do repositório, cada uma com Assignee definido, e o board é atualizado em tempo real conforme o progresso do trabalho, nunca retroativamente.

Limite de WIP: 3 itens na coluna Doing, um por integrante do trio (justificativa detalhada em 3.2).

Rastreabilidade: todo commit referencia o número da Issue correspondente (ex.: `#45 implementação e validação RQ8`), permitindo ao GitHub vincular automaticamente commit ↔ Issue no histórico do board.

Print do board:

![Print do board no GitHub Projects](images/image.png)

### 3.4 Ferramentas

<!-- ORIENTAÇÃO: Liste as ferramentas usadas na coleta, processamento e análise —
específicas (nome e versão quando relevante), não genéricas. Inclua também a ferramenta
de processo (GitHub Projects v2) com o link do repositório/board do grupo. -->

- **API GraphQL do GitHub**, consumida por script próprio em Python (sem bibliotecas de terceiros para consulta), autenticado via Personal Access Token com escopos `public_repo` e `read:project`.
- **pytest**, para os testes unitários de cada métrica antes da integração à coleta em massa.
- **GitHub Actions**, rodando automaticamente os testes a cada push/PR para a `main` (a partir da Sprint02).
- **CSV**, formato de armazenamento do resultado final da coleta.
- **GitHub Projects (v2)**, ferramenta de processo — [github.com/users/ArlindoSPJr/projects/3/views/1](https://github.com/users/ArlindoSPJr/projects/3/views/1), vinculado ao repositório [github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware](https://github.com/ArlindoSPJr/LAB-Experimenta-oDeSoftware).

### 3.5 Tabela de Métricas

<!-- ORIENTAÇÃO: Relacione cada RQ à métrica correspondente, sua definição operacional
exata (fórmula/regra de cálculo) e a ferramenta/fonte usada para coletá-la. -->

| RQ | Métrica | Definição Operacional | Unidade | Ferramenta / Fonte |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] |

### 3.6 Inovações Propostas pelo Grupo (30% da nota)

<!-- ORIENTAÇÃO: O enunciado corresponde a 70% da exigência. Os outros 30% dependem de
contribuição original, claramente identificada aqui. Escolha uma ou mais frentes: (a) nova
RQ; (b) métrica/variável adicional; (c) mudança de arquitetura/ferramenta de coleta;
(d) metodologia alternativa/complementar. Explique o que foi feito, por que é relevante,
e onde o resultado aparece em Resultados/Discussão/Conclusão. -->

[conteúdo do grupo]

---

## 4. Resultados

### 4.1 Coleta de Dados

<!-- ORIENTAÇÃO: Relate o volume final efetivamente coletado e analisado — não apenas o
alvo do enunciado. Quantos itens restaram após filtros de qualidade, período coberto,
outliers/dados ausentes e como foram tratados. -->

[conteúdo do grupo]

### 4.2 Visualização Gráfica

<!-- ORIENTAÇÃO: Para cada RQ (enunciado + inovação), inclua ao menos uma visualização que
a responda diretamente, com a pergunta em texto antes do gráfico, eixos nomeados com
clareza e a medida de tendência central adequada (mediana costuma ser preferível a média
quando há outliers/assimetria). Explicite no texto os valores-chave do gráfico. -->

| Tipo de pergunta / dado | Gráfico recomendado |
|---|---|
| Comparar uma métrica entre categorias | Barras (ranking), ordenadas por valor |
| Comparar dois tratamentos no mesmo grupo | Boxplot pareado ou pontos conectados (before/after) |
| Distribuição de uma métrica numérica | Histograma ou boxplot |
| Relação entre duas métricas numéricas | Dispersão (scatter plot) |
| Evolução ao longo do tempo | Linha, um ponto por sprint/snapshot |
| Composição/fluxo do Kanban ao longo do tempo | Área empilhada (uma camada por coluna) |
| Proporção de categorias | Barra única 100% ou barras simples (evitar pizza) |

[Inserir aqui os gráficos do grupo, um por RQ, cada um precedido da pergunta que responde]

### 4.3 Discussão

<!-- ORIENTAÇÃO: Para cada RQ, compare explicitamente a hipótese informal da Introdução
com o resultado obtido — confirmada, refutada ou parcialmente confirmada, e por quê.
Quando houver teste estatístico, reporte o valor e interprete em linguagem acessível.
Discuta ameaças à validade específicas do laboratório. Finalize relacionando o que as
inovações do grupo (3.6) acrescentaram: confirmaram, contradisseram ou aprofundaram o que
os 70% do enunciado já mostravam? -->

[conteúdo do grupo]

---

## 5. Conclusão

<!-- ORIENTAÇÃO: Sintetize, em poucos parágrafos, as respostas a todas as RQs (enunciado +
inovação), sem repetir números já detalhados — o foco é a mensagem final. Aponte as
principais limitações do estudo. Quando o enunciado pedir postura de consultoria, inclua
recomendações objetivas e acionáveis. Encerre indicando o que o grupo faria diferente e
quais inovações valeriam a pena expandir. -->

[conteúdo do grupo]

---

## 6. Referências

<!-- Inclua aqui somente referências que o grupo de fato usou e verificou. -->

- [ ]