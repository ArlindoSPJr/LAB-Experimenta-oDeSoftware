import io
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src import github_client
from src.github_client import (
    GitHubGraphQLError,
    _carregar_variaveis_do_env,
    obter_quantidade_repos,
    run_query,
)


# ---------------------------------------------------------------------------
# obter_quantidade_repos
# ---------------------------------------------------------------------------


def test_obter_quantidade_repos__sem_variavel_no_ambiente_retorna_padrao(monkeypatch):
    """Sem `QUANTIDADE_REPOS` definida, deve retornar o valor padrão informado."""
    monkeypatch.delenv("QUANTIDADE_REPOS", raising=False)

    resultado = obter_quantidade_repos(padrao=10)

    assert resultado == 10, "Deveria retornar o padrão quando a variável não está definida"


def test_obter_quantidade_repos__com_variavel_no_ambiente_ignora_padrao(monkeypatch):
    """Com `QUANTIDADE_REPOS` definida no ambiente, deve retornar seu valor como int, ignorando o padrão."""
    monkeypatch.setenv("QUANTIDADE_REPOS", "42")

    resultado = obter_quantidade_repos(padrao=10)

    assert resultado == 42, "Deveria retornar o valor da variável de ambiente, não o padrão"
    assert isinstance(resultado, int), "O retorno deveria ser um inteiro"


def test_obter_quantidade_repos__valor_nao_numerico_levanta_value_error(monkeypatch):
    """Com `QUANTIDADE_REPOS` contendo valor não numérico, o erro de conversão deve propagar."""
    monkeypatch.setenv("QUANTIDADE_REPOS", "abc")

    with pytest.raises(ValueError):
        obter_quantidade_repos(padrao=10)


# ---------------------------------------------------------------------------
# run_query
# ---------------------------------------------------------------------------


def test_run_query__resposta_valida_retorna_campo_data():
    """Quando a API responde com sucesso, `run_query` deve retornar apenas o campo `data`."""
    corpo_resposta = json.dumps({"data": {"chave": "valor"}}).encode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = corpo_resposta

    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_response
    mock_context.__exit__.return_value = False

    with patch("src.github_client.urllib.request.urlopen", return_value=mock_context):
        resultado = run_query("query { x }", token="fake-token")

    assert resultado == {"chave": "valor"}, "Deveria retornar apenas o conteúdo do campo 'data'"


def test_run_query__sem_token_levanta_erro(monkeypatch):
    """Sem token explícito nem `GITHUB_TOKEN` no ambiente, deve levantar GitHubGraphQLError mencionando o token."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(GitHubGraphQLError, match="GITHUB_TOKEN"):
        run_query("query { x }")


def test_run_query__http_error_levanta_erro_com_codigo():
    """Quando `urlopen` levanta HTTPError, `run_query` deve levantar GitHubGraphQLError contendo o código HTTP."""
    erro_http = urllib.error.HTTPError(
        url="https://api.github.com/graphql",
        code=502,
        msg="Bad Gateway",
        hdrs=None,
        fp=io.BytesIO(b"corpo do erro"),
    )

    with patch("src.github_client.urllib.request.urlopen", side_effect=erro_http):
        with pytest.raises(GitHubGraphQLError, match="502"):
            run_query("query { x }", token="fake-token")


def test_run_query__url_error_levanta_erro_com_motivo_da_falha():
    """Quando `urlopen` levanta URLError, `run_query` deve levantar GitHubGraphQLError mencionando a falha de conexão."""
    erro_url = urllib.error.URLError("falha de conexão")

    with patch("src.github_client.urllib.request.urlopen", side_effect=erro_url):
        with pytest.raises(GitHubGraphQLError, match="falha de conexão"):
            run_query("query { x }", token="fake-token")


def test_run_query__resposta_com_campo_errors_levanta_erro():
    """Quando o corpo JSON traz a chave 'errors', `run_query` deve levantar GitHubGraphQLError com a mensagem de erro."""
    corpo_resposta = json.dumps(
        {"errors": [{"message": "campo inválido"}], "data": None}
    ).encode("utf-8")

    mock_response = MagicMock()
    mock_response.read.return_value = corpo_resposta

    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_response
    mock_context.__exit__.return_value = False

    with patch("src.github_client.urllib.request.urlopen", return_value=mock_context):
        with pytest.raises(GitHubGraphQLError, match="campo inválido"):
            run_query("query { x }", token="fake-token")


# ---------------------------------------------------------------------------
# _carregar_variaveis_do_env
# ---------------------------------------------------------------------------


def test_carregar_variaveis_do_env__arquivo_inexistente_nao_altera_ambiente(tmp_path):
    """Quando o `.env` não existe, a função deve retornar sem erro e sem alterar o ambiente."""
    diretorio_vazio = tmp_path / "sem_env"
    diretorio_vazio.mkdir()

    with patch("src.github_client.Path") as mock_path_cls:
        mock_path_cls.return_value.resolve.return_value.parent.parent = diretorio_vazio

        import os

        ambiente_antes = dict(os.environ)
        _carregar_variaveis_do_env()
        ambiente_depois = dict(os.environ)

    assert ambiente_antes == ambiente_depois, "O ambiente não deveria ser alterado quando o .env não existe"


def test_carregar_variaveis_do_env__arquivo_existente_popula_ambiente(monkeypatch, tmp_path):
    """Com um `.env` real contendo pares chave=valor, comentários e linhas vazias, deve popular apenas as chaves válidas."""
    arquivo_env = tmp_path / ".env"
    arquivo_env.write_text("CHAVE=valor\n# comentário\n\nOUTRA=x", encoding="utf-8")

    monkeypatch.delenv("CHAVE", raising=False)
    monkeypatch.delenv("OUTRA", raising=False)

    with patch("src.github_client.Path") as mock_path_cls:
        mock_path_cls.return_value.resolve.return_value.parent.parent = tmp_path

        _carregar_variaveis_do_env()

    try:
        import os

        assert os.environ.get("CHAVE") == "valor", "CHAVE deveria ser populada com 'valor'"
        assert os.environ.get("OUTRA") == "x", "OUTRA deveria ser populada com 'x'"
    finally:
        monkeypatch.delenv("CHAVE", raising=False)
        monkeypatch.delenv("OUTRA", raising=False)


def test_carregar_variaveis_do_env__nao_sobrescreve_variavel_ja_definida(monkeypatch, tmp_path):
    """Se a variável já existir no ambiente antes da chamada, o valor do .env não deve sobrescrevê-la (setdefault)."""
    arquivo_env = tmp_path / ".env"
    arquivo_env.write_text("CHAVE=valor_do_arquivo", encoding="utf-8")

    monkeypatch.setenv("CHAVE", "valor_original")

    with patch("src.github_client.Path") as mock_path_cls:
        mock_path_cls.return_value.resolve.return_value.parent.parent = tmp_path

        _carregar_variaveis_do_env()

    import os

    assert os.environ.get("CHAVE") == "valor_original", (
        "A variável já existente no ambiente não deveria ser sobrescrita pelo .env"
    )
