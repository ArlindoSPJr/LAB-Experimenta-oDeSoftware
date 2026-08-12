import csv
from datetime import datetime, timezone
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq04_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa `updatedAt` para calcular o tempo decorrido desde a última atualização.
    """
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    updatedAt
                }
            }
        }
    }
    """


def calcular_dias_desde_atualizacao(data_atualizacao_iso: str, referencia: datetime | None = None) -> int:
    """Calcula quantos dias se passaram desde a última atualização do repositório."""
    data_atualizacao = datetime.fromisoformat(data_atualizacao_iso.replace("Z", "+00:00"))
    referencia = referencia or datetime.now(timezone.utc)
    return (referencia - data_atualizacao).days


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios e calcula o tempo desde a última atualização."""
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
                "ultima_atualizacao": repositorio["updatedAt"],
                "dias_desde_atualizacao": calcular_dias_desde_atualizacao(repositorio["updatedAt"]),
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["repositorio", "estrelas", "ultima_atualizacao", "dias_desde_atualizacao"])
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
