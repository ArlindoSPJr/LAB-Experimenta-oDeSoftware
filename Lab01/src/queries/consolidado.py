import csv
from datetime import datetime, timezone
from pathlib import Path

from src.github_client import obter_quantidade_repos, run_query

CAMINHO_CSV = Path(__file__).resolve().parent.parent.parent / "data" / "coleta_100.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"


def montar_query_busca() -> str:
    """Monta a query GraphQL consolidada com todos os campos das RQs 01 a 06."""
    return """
    query($queryString: String!, $quantidade: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade) {
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    createdAt
                    updatedAt
                    primaryLanguage {
                        name
                    }
                    pullRequests(states: MERGED) {
                        totalCount
                    }
                    releases {
                        totalCount
                    }
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


def calcular_idade_anos(data_criacao_iso: str, referencia: datetime | None = None) -> float:
    data_criacao = datetime.fromisoformat(data_criacao_iso.replace("Z", "+00:00"))
    referencia = referencia or datetime.now(timezone.utc)
    return round((referencia - data_criacao).days / 365.25, 2)


def calcular_dias_desde_atualizacao(data_atualizacao_iso: str, referencia: datetime | None = None) -> int:
    data_atualizacao = datetime.fromisoformat(data_atualizacao_iso.replace("Z", "+00:00"))
    referencia = referencia or datetime.now(timezone.utc)
    return (referencia - data_atualizacao).days


def calcular_razao_issues(fechadas: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(fechadas / total, 4)


def coletar(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta todos os campos das RQs 01–06 em uma única requisição à API."""
    quantidade = quantidade or obter_quantidade_repos()

    dados = run_query(
        montar_query_busca(),
        {"queryString": QUERY_STRING_PADRAO, "quantidade": quantidade},
        token=token,
    )

    linhas = []
    for repo in dados["search"]["nodes"]:
        fechadas = repo["issuesFechadas"]["totalCount"]
        total_issues = repo["issuesTotal"]["totalCount"]
        linguagem = repo["primaryLanguage"]
        linhas.append(
            {
                "repositorio": f"{repo['owner']['login']}/{repo['name']}",
                "estrelas": repo["stargazerCount"],
                "data_criacao": repo["createdAt"],
                "idade_anos": calcular_idade_anos(repo["createdAt"]),
                "total_prs_aceitas": repo["pullRequests"]["totalCount"],
                "total_releases": repo["releases"]["totalCount"],
                "ultima_atualizacao": repo["updatedAt"],
                "dias_desde_atualizacao": calcular_dias_desde_atualizacao(repo["updatedAt"]),
                "linguagem_primaria": linguagem["name"] if linguagem else "N/A",
                "issues_fechadas": fechadas,
                "issues_total": total_issues,
                "razao_issues_fechadas": calcular_razao_issues(fechadas, total_issues),
            }
        )
    return linhas


CAMPOS_CSV = [
    "repositorio", "estrelas",
    "data_criacao", "idade_anos",
    "total_prs_aceitas",
    "total_releases",
    "ultima_atualizacao", "dias_desde_atualizacao",
    "linguagem_primaria",
    "issues_fechadas", "issues_total", "razao_issues_fechadas",
]


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    """Grava as linhas coletadas em um arquivo CSV, criando a pasta pai se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)


if __name__ == "__main__":
    coleta = coletar()
    for linha in coleta:
        print(linha)
    salvar_csv(coleta, CAMINHO_CSV)
    print(f"\n{len(coleta)} repositórios salvos em {CAMINHO_CSV}")
