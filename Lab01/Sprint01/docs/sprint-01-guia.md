# Guia da Sprint 01 (Lab01S01) — Tarefas, Regras de GitHub e Penalidades

## 1. Objetivo da Sprint 01

- Query GraphQL cobrindo as 7 RQs para 100 repositórios.
- Script de requisição automática (sem intervenção manual).
- GitHub Projects criado: colunas de Status + limite de WIP definido e justificado.
- Primeiras Issues em uso no board.

## 2. Tarefas (Issues) da Sprint 01

1. **Setup do GitHub Projects (v2)** — colunas de Status, limite de WIP, justificativa.
2. **Setup do cliente de conexão com a API GraphQL do GitHub** — função única de autenticação/requisição, compartilhada por todos.
3. **Extrair e validar RQ01 (idade) e RQ02 (PRs aceitas)** — amostra de 5-10 repositórios. *(Integrante A)*
4. **Extrair e validar RQ03 (releases) e RQ04 (última atualização)** — amostra de 5-10 repositórios. *(Integrante B)*
5. **Extrair e validar RQ05 (linguagem), RQ06 (% issues fechadas) e base RQ07** — amostra de 5-10 repositórios, com fonte de "linguagens mais populares" documentada (TIOBE/GitHut/Octoverse). *(Integrante C)*
6. **Consolidar query única do grupo** — 100 repositórios ordenados por estrelas, juntando os campos das Issues #3, #4 e #5.
7. **Script de requisição automática end-to-end** — executa a coleta completa sem intervenção manual.

## 3. Regras de gerenciamento do GitHub/Projects

- Cartões = Issues reais (nunca draft issues soltas), rastreáveis pela API.
- Toda Issue precisa ter **Assignee**.
- Colunas mínimas do board: `Backlog → To Do → Doing → Review → Done`.
- Limite de **WIP** definido para a coluna Doing, com justificativa registrada (no Project e na seção "Configuração do processo" do relatório final).
- Board deve refletir o **progresso real**, movimentado conforme o trabalho acontece — nunca preenchido retroativamente.
- Criar Issues apenas da sprint corrente; as das sprints seguintes entram quando essas sprints começarem.
- Cada commit deve **referenciar o número da Issue** correspondente (ex.: `#3 implementa extração RQ01 e RQ02`) — sem essa referência o commit não conta na correção, mesmo estando no repositório.
- Ao final da sprint: rodar o script GraphQL de snapshot e exportar o CSV do estado do Project (base para os Labs 04 e 05).
- Não usar bibliotecas de terceiros para consultar a API do GitHub — script GraphQL próprio do grupo.

## 4. Fluxo de trabalho sugerido (Git)

- Uma branch por integrante/bloco de RQ (ex.: `feature/rq01-rq02`).
- Commits sempre referenciando a Issue correspondente.
- Abrir PR para a branch principal após validação individual na amostra de 5-10 repositórios.
- A integração (Issues #6 e #7) só começa após o merge das 3 partes.

## 5. Penalidades a evitar (do enunciado)

- **-1,0 ponto por dia de atraso** na entrega.
- **Até -10% da nota da sprint** por: WIP não respeitado, Issues sem Assignee, cartões desatualizados, ausência de evolução semanal.
- **Commits sem referência à Issue** correspondente não são considerados na avaliação.

## 6. Checklist de saída da Sprint 01

- [ ] GitHub Projects criado com colunas e WIP definidos e justificados
- [ ] Issues #1-#7 criadas, com Assignee, movimentadas no board
- [ ] Cliente de conexão GraphQL funcionando e testado
- [ ] 3 blocos de RQs implementados e validados em amostra (5-10 repos)
- [ ] Query consolidada rodando para 100 repositórios
- [ ] Script de requisição automática executando fim a fim
- [ ] Snapshot da sprint exportado em CSV
- [ ] Commits referenciando as Issues correspondentes
