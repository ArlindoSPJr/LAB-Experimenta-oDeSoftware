from unittest.mock import patch

from src.queries.rq_bonus_licenca import coletar_amostra


def _repositorio(nome, login, estrelas, licenca):
    """Monta um nó de repositório no formato bruto devolvido por `run_query`."""
    return {
        "name": nome,
        "owner": {"login": login},
        "stargazerCount": estrelas,
        "licenseInfo": licenca,
    }


@patch("src.queries.rq_bonus_licenca.run_query")
def test_coletar_amostra__licenca_presente(mock_run_query):
    """Quando `licenseInfo` vem preenchido, a linha deve trazer o nome da licença."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-exemplo", "dono-exemplo", 500, {"name": "MIT License"}),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1, token="token-fake")

    assert resultado == [
        {
            "repositorio": "dono-exemplo/repo-exemplo",
            "estrelas": 500,
            "licenca": "MIT License",
        }
    ], "A linha deveria refletir o nome da licença retornado pela API."


@patch("src.queries.rq_bonus_licenca.run_query")
def test_coletar_amostra__licenca_ausente(mock_run_query):
    """Quando `licenseInfo` é `None` (repositório sem licença detectada), deve cair em 'N/A'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-sem-licenca", "dono-exemplo", 42, None),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1, token="token-fake")

    assert resultado == [
        {
            "repositorio": "dono-exemplo/repo-sem-licenca",
            "estrelas": 42,
            "licenca": "N/A",
        }
    ], "Repositório sem licença deveria ser marcado como 'N/A'."


@patch("src.queries.rq_bonus_licenca.run_query")
def test_coletar_amostra__multiplos_repositorios_mistos(mock_run_query):
    """Com múltiplos repositórios, cada linha deve refletir seu próprio caso de licença."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-com-licenca", "dono-a", 1000, {"name": "Apache License 2.0"}),
                _repositorio("repo-sem-licenca", "dono-b", 10, None),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=2, token="token-fake")

    assert resultado == [
        {
            "repositorio": "dono-a/repo-com-licenca",
            "estrelas": 1000,
            "licenca": "Apache License 2.0",
        },
        {
            "repositorio": "dono-b/repo-sem-licenca",
            "estrelas": 10,
            "licenca": "N/A",
        },
    ], "Cada linha deveria refletir corretamente seu próprio caso de licença (presente ou ausente)."


@patch("src.queries.rq_bonus_licenca.run_query")
def test_coletar_amostra__quantidade_customizada_repassada_para_run_query(mock_run_query):
    """A `quantidade` informada deve ser repassada como variável `quantidade` para `run_query`."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=6, token="token-fake")

    _, variaveis = mock_run_query.call_args.args[0], mock_run_query.call_args.args[1]
    assert variaveis["quantidade"] == 6, "A quantidade customizada deveria ser enviada em 'variables' para run_query."
