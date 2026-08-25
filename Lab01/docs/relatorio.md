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

