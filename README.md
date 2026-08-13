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
   ```

   `QUANTIDADE_REPOS` controla quantos repositórios o script busca (100 na Sprint01, 1000 na Sprint02). O `.env` nunca é versionado (está no `.gitignore`).

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
