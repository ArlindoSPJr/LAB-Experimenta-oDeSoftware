import csv
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq02_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa `pullRequests(states: MERGED)` para contar apenas PRs aceitas (merged),
    que representa contribuição externa efetivamente incorporada ao projeto.
    """
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    pullRequests(states: MERGED) {
                        totalCount
                    }
                }
            }
        }
    }
    """


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios e retorna o total de PRs aceitas de cada um."""
    quantidade = quantidade or obter_quantidade_repos()

    dados = run_query(
        montar_query_busca(),
        {"queryString": QUERY_STRING_PADRAO, "quantidade": quantidade},
        token=token,
    )

    linhas = []
    for repositorio in dados["search"]["nodes"]:
        linhas.append(
            {
                "repositorio": f"{repositorio['owner']['login']}/{repositorio['name']}",
                "estrelas": repositorio["stargazerCount"],
                "total_prs_aceitas": repositorio["pullRequests"]["totalCount"],
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["repositorio", "estrelas", "total_prs_aceitas"])
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
