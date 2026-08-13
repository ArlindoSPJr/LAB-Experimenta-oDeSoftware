# LAB-Experimentação de Software

Repositório de trabalhos da disciplina "Laboratório de Experimentação de Software". Cada laboratório vive em sua própria pasta na raiz (`Lab01/`, `Lab02/`, ...).

## Lab01 — Características de repositórios populares

Minera a API GraphQL do GitHub para responder 7 questões de pesquisa sobre os repositórios mais populares (mais estrelas), com script próprio (sem bibliotecas de terceiros de acesso à API GitHub). Enunciado completo: [`Lab01/01 - LABORATORIO 01 - Repositorios populares + Setup do Kanban.md`](<Lab01/01 - LABORATORIO 01 - Repositorios populares + Setup do Kanban.md>).

### Pré-requisitos

- Python 3.13+ (só biblioteca padrão — nenhuma dependência externa para instalar).
- Um [Personal Access Token do GitHub](https://github.com/settings/tokens) (sem escopos especiais, apenas para consultas de leitura na API GraphQL).

### Configuração

1. Copie o arquivo de exemplo de variáveis de ambiente:

   ```
   cp Lab01/.env.example Lab01/.env
   ```

2. Edite `Lab01/.env` e preencha:

   ```
   GITHUB_TOKEN=<seu_token_aqui>
   QUANTIDADE_REPOS=100
   GITHUB_PROJECT_OWNER=<login do dono do Project, ex.: ArlindoSPJr>
   GITHUB_PROJECT_OWNER_TYPE=user
   GITHUB_PROJECT_NUMBER=<número do Project, visível na URL do board>
   ```

   `QUANTIDADE_REPOS` controla quantos repositórios o script busca (100 na Sprint01, 1000 na Sprint02). As três variáveis `GITHUB_PROJECT_*` são usadas só pelo script de snapshot do Kanban (veja abaixo). O `.env` nunca é versionado (está no `.gitignore`).

   O token precisa do escopo `public_repo` para a coleta de repositórios e de `read:project` para o snapshot do Project — configure ambos de uma vez em https://github.com/settings/tokens.

### Rodando a coleta consolidada

A partir da raiz do repositório:

```
cd Lab01
python -m src.queries.consolidada
```

O script:

1. Lê `GITHUB_TOKEN` e `QUANTIDADE_REPOS` de `Lab01/.env`.
2. Faz uma única query GraphQL trazendo os campos de todas as RQs 01–06 (idade, PRs aceitas, releases, tempo desde a última atualização, linguagem primária, razão de issues fechadas), paginando automaticamente quando necessário.
3. Imprime cada repositório coletado no terminal.
4. Salva o resultado em `Lab01/data/dataset/coleta_100.csv`.

### Gerando um snapshot do GitHub Projects (fechamento de sprint)

Ao final de cada sprint, o enunciado pede um export do estado atual do Kanban (itens do Project + status de cada um) em CSV — já que a API do GitHub Projects não guarda histórico de mudança de coluna, essa série de snapshots é o único registro da evolução do board ao longo do semestre.

A partir da raiz do repositório:

```
cd Lab01
python -m src.snapshot_projeto
```

O script:

1. Lê `GITHUB_TOKEN`, `GITHUB_PROJECT_OWNER`, `GITHUB_PROJECT_OWNER_TYPE` e `GITHUB_PROJECT_NUMBER` de `Lab01/.env`.
2. Consulta via GraphQL todos os itens do Project e o valor atual do campo "Status" de cada um, paginando automaticamente quando necessário.
3. Imprime cada item coletado no terminal.
4. Salva o resultado no caminho definido pela constante `CAMINHO_SNAPSHOT`, em `Lab01/src/snapshot_projeto.py` — hoje `Lab01/Sprint01/snapshot_sprint01.csv`.

**Importante:** antes de rodar em uma nova sprint, edite `CAMINHO_SNAPSHOT` em `Lab01/src/snapshot_projeto.py` para apontar para o nome/pasta da sprint corrente (ex.: `Lab01/Sprint02/snapshot_sprint02.csv`), para não sobrescrever o snapshot da sprint anterior.
