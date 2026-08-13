import csv
import os
from pathlib import Path

from src.github_client import GitHubGraphQLError, run_query

# Atualizar a cada nova sprint (nome/pasta do snapshot desta sprint).
CAMINHO_SNAPSHOT = Path(__file__).resolve().parent.parent / "Sprint01" / "snapshot_sprint01.csv"

DONO_PROJETO = os.environ.get("GITHUB_PROJECT_OWNER")
TIPO_DONO_PROJETO = os.environ.get("GITHUB_PROJECT_OWNER_TYPE", "user")
NUMERO_PROJETO = int(os.environ.get("GITHUB_PROJECT_NUMBER", 0))

TAMANHO_PAGINA = 50


def montar_query_snapshot(tipo_dono: str) -> str:
    """Monta a query GraphQL que lista os itens do GitHub Projects (v2) e seu status atual.

    O campo raiz muda conforme o dono do Project ser um usuário ou uma organização
    (`user(login:)` vs `organization(login:)`), configurado via GITHUB_PROJECT_OWNER_TYPE.
    """
    campo_dono = "organization" if tipo_dono == "organization" else "user"
    return f"""
    query($login: String!, $numero: Int!, $tamanho: Int!, $cursor: String) {{
        {campo_dono}(login: $login) {{
            projectV2(number: $numero) {{
                items(first: $tamanho, after: $cursor) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    nodes {{
                        fieldValueByName(name: "Status") {{
                            ... on ProjectV2ItemFieldSingleSelectValue {{
                                name
                            }}
                        }}
                        content {{
                            ... on Issue {{
                                number
                                title
                                url
                                assignees(first: 10) {{
                                    nodes {{
                                        login
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """


def exportar_snapshot(token: str | None = None) -> list[dict]:
    """Exporta os itens do GitHub Projects do grupo e seu status atual (coluna do Kanban).

    Pensado para ser chamado ao final de cada sprint — o resultado é um retrato do
    board naquele momento, já que a API de Projects não guarda histórico de
    mudança de coluna consultável.
    """
    if not DONO_PROJETO or not NUMERO_PROJETO:
        raise GitHubGraphQLError(
            "GITHUB_PROJECT_OWNER e GITHUB_PROJECT_NUMBER precisam estar definidos no .env."
        )

    query = montar_query_snapshot(TIPO_DONO_PROJETO)
    campo_dono = "organization" if TIPO_DONO_PROJETO == "organization" else "user"

    linhas = []
    cursor = None
    while True:
        dados = run_query(
            query,
            {
                "login": DONO_PROJETO,
                "numero": NUMERO_PROJETO,
                "tamanho": TAMANHO_PAGINA,
                "cursor": cursor,
            },
            token=token,
        )
        itens = dados[campo_dono]["projectV2"]["items"]

        for item in itens["nodes"]:
            conteudo = item["content"]
            if not conteudo:
                print("Aviso: item do Project sem conteúdo associado (draft issue?) — pulando.")
                continue

            valor_status = item["fieldValueByName"]
            status = valor_status["name"] if valor_status else "Sem status"
            responsaveis = ";".join(a["login"] for a in conteudo["assignees"]["nodes"])

            linhas.append(
                {
                    "numero_issue": conteudo["number"],
                    "titulo": conteudo["title"],
                    "status": status,
                    "responsaveis": responsaveis,
                    "url": conteudo["url"],
                }
            )

        if not itens["pageInfo"]["hasNextPage"]:
            break
        cursor = itens["pageInfo"]["endCursor"]

    return linhas


CAMPOS_CSV = ["numero_issue", "titulo", "status", "responsaveis", "url"]


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    snapshot = exportar_snapshot()
    for linha in snapshot:
        print(linha)
    salvar_csv(snapshot, CAMINHO_SNAPSHOT)
    print(f"\n{len(snapshot)} itens do Project salvos em {CAMINHO_SNAPSHOT}")
