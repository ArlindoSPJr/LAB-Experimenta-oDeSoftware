import csv
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from src.github_client import GitHubGraphQLError, obter_quantidade_repos, run_query

CAMINHO_CSV = Path(__file__).resolve().parent.parent.parent / "data" / "dataset" / "coleta_1000.csv"

QUERY_STRING_PADRAO = "stars:>1 sort:stars-desc"

# A query pede 4 conexões aninhadas por repositório (pullRequests, releases e
# as duas variações de issues). Com `first` grande (>~30) o resolver de busca
# do GitHub estoura o timeout interno e devolve HTTP 502, mesmo estando dentro
# do limite de schema (100) — e o offset (quão fundo o cursor já está) também
# pesa nesse tempo. Por isso a página começa otimista e encolhe pela metade
# só quando a API efetivamente falhar naquele offset (redução adaptativa, em
# vez de um tamanho fixo "chutado").
TAMANHO_PAGINA_INICIAL = 25
TAMANHO_PAGINA_MINIMO = 5
TENTATIVAS_POR_OFFSET = 4
ESPERA_BASE_SEGUNDOS = 3

# Métrica bônus: concentração do maior contribuidor. O GraphQL não expõe
# estatística de contribuidores pronta, então aproximamos usando os autores
# das N PRs aceitas mais recentes (amostra), em vez do histórico completo de
# commits — isso seria inviável em escala para repositórios grandes.
TAMANHO_AMOSTRA_PRS = 30

# Métrica bônus: popularidade via forks. Estrelas medem interesse/atenção;
# forks medem reaproveitamento efetivo do código (quantas pessoas partiram
# do repositório para desenvolver algo próprio) — sinal complementar de
# popularidade, disponível direto no campo forkCount do repositório.

# Métrica bônus: licença do repositório. Sistemas populares tendem a adotar
# licenças permissivas (MIT, Apache-2.0) para facilitar adoção/contribuição
# externa? Disponível direto no campo licenseInfo do repositório.

# RQ VIII: sistemas populares raramente são arquivados/descontinuados?
# Diferente da RQ IV (que mede recência de atualização), isArchived reflete
# o abandono formal declarado pelo dono do repositório.

# RQ IX: sistemas populares já adotam "main" como branch padrão, em vez de
# "master"? Métrica categórica via defaultBranchRef.name.


def _buscar_pagina_com_retry(cursor: str | None, tamanho_pagina: int, token: str | None) -> tuple[dict, int]:
    """Busca uma página da query consolidada, encolhendo o tamanho pela metade a cada 502.

    Retorna os dados da página e o tamanho de página que efetivamente funcionou,
    para as próximas páginas partirem já reduzidas (não volta a crescer).
    """
    for tentativa in range(1, TENTATIVAS_POR_OFFSET + 1):
        try:
            dados = run_query(
                montar_query_busca(),
                {
                    "queryString": QUERY_STRING_PADRAO,
                    "quantidade": tamanho_pagina,
                    "cursor": cursor,
                    "amostraPrs": TAMANHO_AMOSTRA_PRS,
                },
                token=token,
            )
            return dados, tamanho_pagina
        except GitHubGraphQLError as erro:
            esgotou_tentativas = tentativa == TENTATIVAS_POR_OFFSET
            no_piso = tamanho_pagina <= TAMANHO_PAGINA_MINIMO
            if "502" not in str(erro) or (esgotou_tentativas and no_piso):
                raise
            time.sleep(ESPERA_BASE_SEGUNDOS * tentativa)
            tamanho_pagina = max(TAMANHO_PAGINA_MINIMO, tamanho_pagina // 2)
    raise AssertionError("inalcançável")


def montar_query_busca() -> str:
    """Monta a query GraphQL consolidada com todos os campos das RQs 01 a 06."""
    return """
    query($queryString: String!, $quantidade: Int!, $cursor: String, $amostraPrs: Int!) {
        search(query: $queryString, type: REPOSITORY, first: $quantidade, after: $cursor) {
            pageInfo {
                hasNextPage
                endCursor
            }
            nodes {
                ... on Repository {
                    name
                    owner { login }
                    stargazerCount
                    forkCount
                    createdAt
                    updatedAt
                    primaryLanguage {
                        name
                    }
                    licenseInfo {
                        name
                    }
                    isArchived
                    defaultBranchRef {
                        name
                    }
                    pullRequests(states: MERGED, first: $amostraPrs, orderBy: {field: CREATED_AT, direction: DESC}) {
                        totalCount
                        nodes {
                            author { login }
                        }
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


def coletar(quantidade: int | None = None, token: str | None = None) -> list[dict]:
    """Coleta todos os campos das RQs 01–06, paginando via cursor com redução adaptativa.

    A busca do GitHub aceita `first` até 100, mas com as 4 conexões aninhadas
    desta query o resolver do lado do GitHub estoura o timeout (HTTP 502)
    para páginas grandes — e o offset também pesa nesse tempo. Por isso
    pedimos em páginas via cursor (`after`) que começam em
    `TAMANHO_PAGINA_INICIAL` e encolhem pela metade só quando a API falhar
    naquele offset, até reunir `quantidade` repositórios ou a busca acabar.
    """
    quantidade = quantidade or obter_quantidade_repos()

    linhas = []
    cursor = None
    tamanho_pagina = TAMANHO_PAGINA_INICIAL
    while len(linhas) < quantidade:
        tamanho_pedido = min(tamanho_pagina, quantidade - len(linhas))
        dados, tamanho_pagina = _buscar_pagina_com_retry(cursor, tamanho_pedido, token)
        busca = dados["search"]

        for repo in busca["nodes"]:
            fechadas = repo["issuesFechadas"]["totalCount"]
            total_issues = repo["issuesTotal"]["totalCount"]
            linguagem = repo["primaryLanguage"]
            licenca = repo["licenseInfo"]
            branch_padrao = repo["defaultBranchRef"]
            autores_prs = [
                pr["author"]["login"] if pr["author"] else None
                for pr in repo["pullRequests"]["nodes"]
            ]
            top_contribuidor, concentracao_top_contribuidor = calcular_top_contribuidor(autores_prs)
            linhas.append(
                {
                    "repositorio": f"{repo['owner']['login']}/{repo['name']}",
                    "estrelas": repo["stargazerCount"],
                    "total_forks": repo["forkCount"],
                    "data_criacao": repo["createdAt"],
                    "idade_anos": calcular_idade_anos(repo["createdAt"]),
                    "total_prs_aceitas": repo["pullRequests"]["totalCount"],
                    "total_releases": repo["releases"]["totalCount"],
                    "ultima_atualizacao": repo["updatedAt"],
                    "dias_desde_atualizacao": calcular_dias_desde_atualizacao(repo["updatedAt"]),
                    "linguagem_primaria": linguagem["name"] if linguagem else "N/A",
                    "licenca": licenca["name"] if licenca else "N/A",
                    "arquivado": repo["isArchived"],
                    "branch_padrao": branch_padrao["name"] if branch_padrao else "N/A",
                    "issues_fechadas": fechadas,
                    "issues_total": total_issues,
                    "razao_issues_fechadas": calcular_razao_issues(fechadas, total_issues),
                    "top_contribuidor": top_contribuidor,
                    "concentracao_top_contribuidor": concentracao_top_contribuidor,
                }
            )

        if not busca["pageInfo"]["hasNextPage"]:
            break
        cursor = busca["pageInfo"]["endCursor"]

    return linhas


CAMPOS_CSV = [
    "repositorio", "estrelas", "total_forks",
    "data_criacao", "idade_anos",
    "total_prs_aceitas",
    "total_releases",
    "ultima_atualizacao", "dias_desde_atualizacao",
    "linguagem_primaria", "licenca", "arquivado", "branch_padrao",
    "issues_fechadas", "issues_total", "razao_issues_fechadas",
    "top_contribuidor", "concentracao_top_contribuidor",
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
