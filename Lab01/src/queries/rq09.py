import csv
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq09_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa `defaultBranchRef.name`, exposto direto pela API, para verificar se
    repositórios populares já adotaram "main" como branch padrão.
    """
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    defaultBranchRef {
                        name
                    }
                }
            }
        }
    }
    """


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios com estrelas e nome da branch padrão."""
    quantidade = quantidade or obter_quantidade_repos()

    dados = run_query(
        montar_query_busca(),
        {"queryString": QUERY_STRING_PADRAO, "quantidade": quantidade},
        token=token,
    )

    linhas = []
    for repositorio in dados["search"]["nodes"]:
        branch_padrao = repositorio["defaultBranchRef"]
        linhas.append(
            {
                "repositorio": f"{repositorio['owner']['login']}/{repositorio['name']}",
                "estrelas": repositorio["stargazerCount"],
                "branch_padrao": branch_padrao["name"] if branch_padrao else "N/A",
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["repositorio", "estrelas", "branch_padrao"])
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
