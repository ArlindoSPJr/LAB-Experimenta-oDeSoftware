import json
import os
import urllib.error
import urllib.request
from pathlib import Path

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def _carregar_variaveis_do_env() -> None:
    """Lê `Lab01/.env` (se existir) e popula `os.environ` sem sobrescrever variáveis já definidas.

    Implementado com stdlib apenas, para não introduzir dependência de terceiros.
    """
    caminho_env = Path(__file__).resolve().parent.parent / ".env"
    if not caminho_env.exists():
        return

    for linha in caminho_env.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip())


_carregar_variaveis_do_env()


def obter_quantidade_repos(padrao: int = 10) -> int:
    """Lê `QUANTIDADE_REPOS` do ambiente (`.env`); usa `padrao` se não definida.

    Ponto único de leitura desse parâmetro, para os módulos de RQ não precisarem
    hardcodar o tamanho da amostra/coleta cada um no seu código.
    """
    return int(os.environ.get("QUANTIDADE_REPOS", padrao))


class GitHubGraphQLError(Exception):
    """Levantada quando a API GraphQL do GitHub retorna erros ou falha HTTP."""


def run_query(query: str, variables: dict | None = None, token: str | None = None) -> dict:
    """Executa uma query GraphQL bruta contra a API do GitHub e devolve o campo `data`.

    Ponto único de conexão com a API do GitHub — não sabe qual métrica/RQ está
    sendo solicitada. Quem chama monta sua própria string/campos de query.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise GitHubGraphQLError("GITHUB_TOKEN não definido no ambiente.")

    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            corpo = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise GitHubGraphQLError(f"HTTP {exc.code}: {exc.read().decode('utf-8')}") from exc
    except urllib.error.URLError as exc:
        raise GitHubGraphQLError(f"Falha de conexão com a API do GitHub: {exc.reason}") from exc

    if "errors" in corpo:
        raise GitHubGraphQLError(str(corpo["errors"]))

    return corpo["data"]
