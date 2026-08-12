import csv
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq06_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa aliases para buscar issues fechadas e total (abertas + fechadas) em uma
    única requisição, evitando duas chamadas à API por repositório.
    """
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    issuesFechadas: issues(states: CLOSED) {
                        totalCount
                    }
                    issuesTotal: issues(states: [OPEN, CLOSED]) {
                        totalCount
                    }
                }
            }
        }
    }
    """


def calcular_razao_issues(fechadas: int, total: int) -> float:
    """Calcula a razão de issues fechadas sobre o total. Retorna 0.0 se não há issues."""
    if total == 0:
        return 0.0
    return round(fechadas / total, 4)


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios e calcula a razão de issues fechadas."""
    quantidade = quantidade or obter_quantidade_repos()

    dados = run_query(
        montar_query_busca(),
        {"queryString": QUERY_STRING_PADRAO, "quantidade": quantidade},
        token=token,
    )

    linhas = []
    for repositorio in dados["search"]["nodes"]:
        fechadas = repositorio["issuesFechadas"]["totalCount"]
        total = repositorio["issuesTotal"]["totalCount"]
        linhas.append(
            {
                "repositorio": f"{repositorio['owner']['login']}/{repositorio['name']}",
                "estrelas": repositorio["stargazerCount"],
                "issues_fechadas": fechadas,
                "issues_total": total,
                "razao_issues_fechadas": calcular_razao_issues(fechadas, total),
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["repositorio", "estrelas", "issues_fechadas", "issues_total", "razao_issues_fechadas"])
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
