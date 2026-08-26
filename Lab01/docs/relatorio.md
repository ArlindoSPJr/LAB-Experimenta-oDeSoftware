**Relatório Final**

**Alunos: Arlindo Júnior, Arthur Astolfi e Camila Melo**

**SEÇÃO I - Introdução com hipóteses informais sobre as RQs**

**RQ I - Sistemas populares são maduros/antigos?**
*Resposta: Sistemas populares tendem a ser mais antigos, por conta da confiabilidade. Porém não é algo necessário: repositórios novos também podem ser extremamente populares por conta de assuntos novos que estão em alta, por exemplo, a skill do Claude Code.*

**RQ II - Sistemas populares recebem muita contribuição externa?**
*Resposta: Sistemas populares tendem a receber uma boa quantidade de contribuições, visto que, por serem populares, atraem mais interesse da comunidade em gerar contribuição do que os repositórios com menor popularidade.*

**RQ III - Sistemas populares lançam releases com frequência?**
*Resposta: Por serem repositórios populares, tendem a ter bastantes atualizações e, consequentemente, vários pacotes de lançamentos, ainda mais se tiverem uma grande quantidade de contribuições externas.*

**RQ IV - Sistemas populares são atualizados com frequência?**
*Resposta: Sim, é esperado que, quanto mais popular um repositório for, mais atualizado ele tende a ser, até por conta de grandes contribuições da comunidade.*

**RQ V - Sistemas populares são escritos nas linguagens mais populares?**
*Referência: https://www.tiobe.com/tiobe-index/*
*Resposta: Não necessariamente, visto que muitos repositórios populares podem ter sido iniciados há bastante tempo, mantendo até hoje atualizações em linguagens antigas, que não são populares hoje em dia.*

**RQ VI - Sistemas populares possuem um alto percentual de issues fechadas?**
*Resposta: É necessário avaliar a regra de issue para cada repositório, porém geralmente cada issue equivale a uma nova feature. Sendo assim, sistemas populares tendem a possuir um alto percentual de issues fechadas; comparado a issues abertas, esse valor deve ficar na faixa de 70%.*

**RQ VII - Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência? (divida os resultados das RQs 02, 03 e 04 por linguagem)**
*Resposta: Não necessariamente, existem diversos repositórios ativos que recebem uma alta taxa de contribuição, mas que são escritos em linguagens antigas.*

**RQ VIII - Sistemas populares raramente são arquivados/descontinuados?**
*Métrica: `isArchived` do repositório.*
*Resposta: Sim, é esperado que a grande maioria dos repositórios populares esteja ativa — um projeto precisa de manutenção contínua para atrair e manter estrelas, então o arquivamento (abandono formal declarado pelo dono) deve ser raro nesse grupo, mesmo entre os mais antigos.*

**RQ IX - Sistemas populares já adotam "main" como branch padrão, em vez de "master"?**
*Métrica: `defaultBranchRef.name` do repositório.*
*Resposta: A maioria deve usar "main", já que o GitHub passou a criar novos repositórios com esse nome por padrão desde 2020 e incentivou a migração de repositórios antigos. Repositórios mais antigos e populares, porém, podem manter "master" caso nunca tenham feito a migração manual.*

**RQ X - Sistemas populares adotam GitHub Discussions como canal de comunidade, além de Issues/PRs?**
*Métrica: `hasDiscussionsEnabled` do repositório.*
*Resposta: Não deve ser maioria. Discussions é um recurso opcional e mais recente que Issues; repositórios populares tendem a já ter um fluxo de comunidade consolidado em Issues/PRs (e às vezes em canais externos, como Discord/Slack), então esperamos habilitação relevante só numa minoria — mais comum em projetos grandes com necessidade de separar dúvidas de uso de bugs reais.*

**RQ XI - Sistemas populares recebem apoio financeiro direto via GitHub Sponsors/funding?**
*Métrica: presença de `fundingLinks` (lista de plataformas de financiamento configuradas).*
*Resposta: Deve ser uma minoria pequena. Configurar `fundingLinks` exige uma ação deliberada do mantenedor (criar `FUNDING.yml`), e nem todo projeto popular tem um mantenedor individual buscando patrocínio — muitos são mantidos por empresas ou organizações que já monetizam o produto por outra via, então esperamos essa métrica concentrada em projetos individuais/comunitários.*


**SEÇÃO II - Metodologia de coleta**

*Fonte e ferramenta: API GraphQL do GitHub (`https://api.github.com/graphql`), consumida por script próprio em Python (só biblioteca padrão, sem dependências de terceiros para acesso à API — ver `Lab01/src/github_client.py`), autenticado via Personal Access Token com escopos `public_repo` e `read:project`.*

*Critério de seleção: os 1.000 repositórios com maior número de estrelas no GitHub, via `search(query: "stars:>1 sort:stars-desc", type: REPOSITORY)`.*

*Coleta consolidada: uma única query GraphQL (`Lab01/src/queries/consolidada.py`) traz, numa única passada por repositório, todos os campos usados pelas RQ I a XI e pelas métricas bônus (concentração do maior contribuidor, forks, licença): data de criação, data da última atualização, linguagem primária, licença, status de arquivamento, branch padrão, Discussions habilitado, plataformas de financiamento (funding), total de releases, total de PRs aceitas (com os autores de uma amostra das 30 PRs mais recentes) e issues (abertas/fechadas).*

*Paginação: via cursor (`after`), com tamanho de página adaptativo — a busca começa pedindo 25 repositórios por página e reduz o tamanho pela metade automaticamente quando a API responde com erro 502 (o resolver do GitHub estoura o timeout interno por causa das 4 conexões aninhadas por repositório: pullRequests, releases e as 2 variações de issues), com até 4 tentativas por página e espera crescente entre elas, até reunir os 1.000 repositórios.*

*Validação incremental: cada métrica foi primeiro implementada e testada isoladamente numa amostra pequena de 5–10 repositórios (scripts individuais `rq01.py` a `rq11.py` e `rq_bonus_*.py`, com saída em `Lab01/data/amostras/`), antes de ser integrada à query única de coleta em massa — evitando gastar tempo/requisições rodando os 1.000 repositórios com uma métrica ainda não validada.*

*Armazenamento: resultado salvo em CSV (`Lab01/data/dataset/coleta_1000.csv`), com 998 repositórios válidos coletados dos 1.000 buscados. Última coleta completa realizada em 20/08/2026 — ainda não inclui as colunas de arquivamento (RQ VIII), branch padrão (RQ IX), Discussions (RQ X) e funding (RQ XI), adicionadas depois; requer nova rodada de coleta para preencher os resultados dessas RQs na Seção IV.*

*Testes automatizados: a partir da Sprint02, toda métrica nova passou a exigir teste unitário correspondente (mockando a resposta da API), rodado automaticamente via GitHub Actions a cada push/PR para a `main` (`Lab01/tests/`, `.github/workflows/tests.yml`).*


**SEÇÃO III - Resultados por RQ**

*Base: coleta consolidada com 998 repositórios válidos (de 1.000 buscados) em `Lab01/data/dataset/coleta_1000.csv`.*

**RQ I - Idade do repositório**
*Mediana: 7,72 anos | Mínimo: 0,02 anos | Máximo: 18,36 anos*

**RQ II - Total de pull requests aceitas**
*Mediana: 768 PRs | Mínimo: 0 | Máximo: 103.387*

**RQ III - Total de releases**
*Mediana: 39 releases | 286 repositórios (28,7%) sem nenhuma release*

**RQ IV - Dias desde a última atualização**
*Mediana: 0 dias | 998 repositórios (100%) atualizados nos últimos 30 dias*

**RQ V - Linguagem primária (contagem por categoria, top 10)**

| Linguagem | Repositórios |
|---|---|
| Python | 227 |
| TypeScript | 173 |
| JavaScript | 110 |
| N/A (sem linguagem identificada) | 87 |
| Go | 77 |
| Rust | 57 |
| C++ | 41 |
| Java | 41 |
| Jupyter Notebook | 24 |
| C | 21 |

**RQ VI - Razão de issues fechadas**
*Mediana: 0,864 (86,4%) | 721 repositórios (72,2%) com razão ≥ 0,70*

**RQ VII - PRs, releases e atualização por linguagem (mediana, linguagens mais frequentes)**

| Linguagem | Mediana PRs aceitas | Mediana releases | Mediana dias desde atualização |
|---|---|---|---|
| Python | 559 | 20 | 0 |
| TypeScript | 1.979 | 134 | 0 |
| JavaScript | 630,5 | 38 | 0 |
| Go | 1.958 | 140 | 0 |
| Rust | 2.212 | 75 | 0 |

**RQ VIII - Status de arquivamento** e **RQ IX - Branch padrão**
*Pendente: as colunas `arquivado` e `branch_padrao` foram adicionadas à coleta consolidada depois da última rodada completa (20/08/2026). Requer nova execução de `python -m src.queries.consolidada` com os 1.000 repositórios para gerar os valores.*

**Bônus - Métricas complementares**
*Forks: mediana de 6.348 (mínimo 39, máximo 109.021).*
*Concentração do maior contribuidor: mediana de 0,333 (33,3%) entre os 978 repositórios com PRs identificáveis na amostra.*
*Licença (contagem, top 5): MIT License (393), Apache License 2.0 (181), Other (148), N/A/sem licença (83), GNU GPL v3.0 (50).*


**SEÇÃO IV - Discussão hipóteses vs Resultado**

*Base: coleta consolidada com 998 repositórios válidos (de 1.000 buscados) em `Lab01/data/dataset/coleta_1000.csv`.*

**RQ I - Sistemas populares são maduros/antigos?**
*Hipótese: tendem a ser mais antigos pela confiabilidade, mas não é regra, repositórios novos também podem viralizar.*
*Resultado: idade mediana de 7,72 anos (mínimo 0,02, máximo 18,36 anos). A hipótese se confirma no geral, já que a maioria dos repositórios populares já é madura, com quase 8 anos de mediana, mas o intervalo confirma também a exceção prevista: há repositórios com poucos dias de existência (0,02 ano) entre os mais populares, provavelmente por assuntos em alta no momento da coleta.*

**RQ II - Sistemas populares recebem muita contribuição externa?**
*Hipótese: sim, por atraírem mais interesse da comunidade.*
*Resultado: mediana de 768 pull requests aceitas (variando de 0 a 103.387). O valor mediano é alto e confirma a hipótese, mas a variação extrema mostra que popularidade (estrelas) não garante contribuição uniforme. Alguns repositórios muito populares (ex.: listas "awesome") recebem poucas PRs por não serem projetos de código executável.*

**RQ III - Sistemas populares lançam releases com frequência?**
*Hipótese: sim, tendem a ter muitas atualizações e pacotes de lançamento, especialmente com bastante contribuição externa.*
*Resultado: mediana de 39 releases, mas 28,7% dos repositórios têm zero releases. A hipótese se confirma apenas parcialmente: a mediana é alta, porém quase 3 em cada 10 repositórios populares nunca lançaram uma release, geralmente repositórios de conteúdo/curadoria (listas, tutoriais, coleções de recursos) em vez de pacotes de software versionado, categoria que a hipótese inicial não diferenciava.*

**RQ IV - Sistemas populares são atualizados com frequência?**
*Hipótese: sim, quanto mais popular, mais atualizado, por conta da comunidade.*
*Resultado: mediana de 0 dias desde a última atualização e 100% dos repositórios atualizados nos últimos 30 dias. Hipótese totalmente confirmada. Nenhum repositório popular da amostra está abandonado.*

**RQ V - Sistemas populares são escritos nas linguagens mais populares?**
*Referência: TIOBE Index (https://www.tiobe.com/tiobe-index/).*
*Hipótese: não necessariamente, pois muitos repositórios populares e antigos mantêm linguagens que já não são as mais populares hoje.*
*Resultado: as linguagens mais frequentes na amostra são Python (227), TypeScript (173), JavaScript (110), Go (77) e Rust (57), com 87 repositórios sem linguagem primária identificada (ex.: documentação). Confrontando com o TIOBE Index, que hoje lidera com Python, C++, C, Java e C#, a hipótese se confirma: TypeScript, Go e Rust aparecem entre as linguagens mais usadas nos repositórios populares do GitHub sem estarem entre as líderes do TIOBE, enquanto linguagens historicamente dominantes no índice (C, C#, Java) aparecem com bem menos representatividade nesta amostra.*

**RQ VI - Sistemas populares possuem um alto percentual de issues fechadas?**
*Hipótese: sim, na faixa de 70% de issues fechadas em relação ao total.*
*Resultado: razão mediana de 0,864 (86,4%) e 72,2% dos repositórios com razão igual ou acima de 0,70. A hipótese se confirma e o resultado real supera a expectativa inicial, já que a maioria dos repositórios populares fecha uma proporção ainda maior de issues do que os 70% estimados.*

**RQ VII - Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?**
*Hipótese: não necessariamente, pois há repositórios ativos e muito contribuídos escritos em linguagens mais antigas.*
*Resultado: cruzando RQ02/RQ03/RQ04 por linguagem, TypeScript (mediana de 1.979 PRs e 134 releases), Go (1.958 PRs, 140 releases) e Rust (2.212 PRs, 75 releases) superam claramente Python (559 PRs, 20 releases) e JavaScript (630,5 PRs, 38 releases) em contribuição e frequência de releases, mesmo Python sendo a linguagem líder do TIOBE e a mais frequente nesta amostra. Todas as linguagens analisadas, porém, seguem com mediana de 0 dias desde a última atualização, ou seja, a frequência de atualização não varia por linguagem. A hipótese se confirma parcialmente: não há relação direta entre "linguagem mais popular" (no sentido do TIOBE) e mais contribuição/releases — o fator determinante parece ser o ecossistema/tipo de projeto (bibliotecas e ferramentas em TypeScript/Go/Rust) mais do que o ranking geral da linguagem.*


**SEÇÃO V - Configuração do Processo**

*Ferramenta: GitHub Projects (v2), vinculado ao repositório do grupo — [github.com/users/ArlindoSPJr/projects/3/views/1](https://github.com/users/ArlindoSPJr/projects/3/views/1).*

*Colunas (campo Status): `Backlog → To Do → Doing → Review → Done`. Cartões são sempre Issues reais do repositório (nunca draft issues soltas), cada uma com Assignee definido, e o board é atualizado em tempo real conforme o progresso do trabalho — nunca retroativamente.*

*Limite de WIP: 3 itens na coluna Doing, um por integrante do trio. A ideia é garantir que cada pessoa tenha no máximo uma tarefa em andamento por vez, evitando fragmentação de foco e commits parciais desorganizados — cada integrante só puxa uma nova tarefa para Doing depois de mover a anterior para Review/Done.*

*Rastreabilidade: todo commit referencia o número da Issue correspondente (ex.: `#45 implementação e validação RQ8`), permitindo ao GitHub vincular automaticamente commit ↔ Issue no histórico do board.*

*Print do board: 

