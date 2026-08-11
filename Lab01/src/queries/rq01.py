import csv
from datetime import datetime, timezone
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq01_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa `search(type: REPOSITORY)`, que não tem argumento `orderBy` explícito —
    a ordenação por estrelas vem do qualificador `sort:stars-desc` dentro da
    própria string de busca (`queryString`).
    """
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    createdAt
                }
            }
        }
    }
    """


def calcular_idade_anos(data_criacao_iso: str, referencia: datetime | None = None) -> float:
    """Calcula a idade do repositório em anos, a partir da data de criação (`createdAt`)."""
    data_criacao = datetime.fromisoformat(data_criacao_iso.replace("Z", "+00:00"))
    referencia = referencia or datetime.now(timezone.utc)
    dias = (referencia - data_criacao).days
    return round(dias / 365.25, 2)


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios e calcula a idade de cada um."""
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
                "data_criacao": repositorio["createdAt"],
                "idade_anos": calcular_idade_anos(repositorio["createdAt"]),
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["repositorio", "estrelas", "data_criacao", "idade_anos"])
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
