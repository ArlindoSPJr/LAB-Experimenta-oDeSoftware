import csv
from collections import Counter
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV_AMOSTRA = Path(__file__).resolve().parent.parent.parent / "data" / "amostras" / "rq_bonus_concentracao_amostra.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"

# O GraphQL não expõe estatística de contribuidores pronta, então aproximamos
# a concentração usando os autores das N PRs aceitas mais recentes (amostra),
# em vez do histórico completo de commits — inviável em escala para
# repositórios grandes (ex.: torvalds/linux tem milhões de commits).
TAMANHO_AMOSTRA_PRS = 30


def montar_query_busca() -> str:
    """Monta a query GraphQL de busca de repositórios ordenados por estrelas.

    Usa `pullRequests(states: MERGED)` com os autores das PRs mais recentes
    para estimar a concentração de contribuição no repositório.
    """
    return """
    query($queryString: String!, $quantidade: Int!, $amostraPrs: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    pullRequests(states: MERGED, first: $amostraPrs, orderBy: {field: CREATED_AT, direction: DESC}) {
                        totalCount
                        nodes {
                            author { login }
                        }
                    }
                }
            }
        }
    }
    """


def calcular_top_contribuidor(autores: list[str | None]) -> tuple[str, float]:
    """Autor mais frequente entre as PRs amostradas e sua % de participação.

    Retorna ("N/A", 0.0) se a amostra não tem PRs. Autores com `login` nulo
    (conta deletada/anônima) são descartados da amostra.
    """
    logins = [autor for autor in autores if autor]
    if not logins:
        return "N/A", 0.0
    login, quantidade = Counter(logins).most_common(1)[0]
    return login, round(quantidade / len(logins), 4)


def coletar_amostra(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta a amostra de repositórios e calcula a concentração do maior contribuidor."""
    quantidade = quantidade or obter_quantidade_repos()

    dados = run_query(
        montar_query_busca(),
        {"queryString": QUERY_STRING_PADRAO, "quantidade": quantidade, "amostraPrs": TAMANHO_AMOSTRA_PRS},
        token=token,
    )

    linhas = []
    for repositorio in dados["search"]["nodes"]:
        autores_prs = [
            pr["author"]["login"] if pr["author"] else None
            for pr in repositorio["pullRequests"]["nodes"]
        ]
        top_contribuidor, concentracao = calcular_top_contribuidor(autores_prs)
        linhas.append(
            {
                "repositorio": f"{repositorio['owner']['login']}/{repositorio['name']}",
                "estrelas": repositorio["stargazerCount"],
                "total_prs_aceitas": repositorio["pullRequests"]["totalCount"],
                "top_contribuidor": top_contribuidor,
                "concentracao_top_contribuidor": concentracao,
            }
        )
    return linhas


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=["repositorio", "estrelas", "total_prs_aceitas", "top_contribuidor", "concentracao_top_contribuidor"],
        )
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    amostra = coletar_amostra()
    for linha in amostra:
        print(linha)
    salvar_csv(amostra, CAMINHO_CSV_AMOSTRA)
    print(f"\n{len(amostra)} repositórios salvos em {CAMINHO_CSV_AMOSTRA}")
