from unittest.mock import patch

from src.queries.rq08 import coletar_amostra


def _repositorio(nome, dono, estrelas, arquivado):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "isArchived": arquivado,
    }


@patch("src.queries.rq08.run_query")
def test_coletar_amostra__repositorio_arquivado_mantem_true(mock_run_query):
    """Repositório arquivado (isArchived: true) deve manter o valor True em 'arquivado'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-arquivado", "dono-exemplo", 500, True),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["arquivado"] is True, (
        "O campo 'arquivado' deve ser True quando isArchived vem true"
    )


@patch("src.queries.rq08.run_query")
def test_coletar_amostra__repositorio_ativo_mantem_false(mock_run_query):
    """Repositório ativo (isArchived: false) deve manter o valor False em 'arquivado'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-ativo", "dono-exemplo", 10000, False),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["arquivado"] is False, (
        "O campo 'arquivado' deve ser False quando isArchived vem false"
    )
    assert resultado[0]["estrelas"] == 10000, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-ativo", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )


@patch("src.queries.rq08.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_item_na_mesma_ordem(mock_run_query):
    """Cada repositório do payload deve virar uma linha própria, na mesma ordem, sem misturar valores."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-um", "dono-um", 1000, False),
                _repositorio("repo-dois", "dono-dois", 50, True),
                _repositorio("repo-tres", "dono-tres", 20000, False),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=3)

    assert len(resultado) == 3, "Deveria retornar uma linha para cada repositório presente no payload"
    assert resultado[0]["arquivado"] is False, "Primeira linha deve trazer o valor exato do primeiro repositório"
    assert resultado[1]["arquivado"] is True, "Segunda linha não deve herdar valores dos outros repositórios do payload"
    assert resultado[2]["arquivado"] is False, "Terceira linha não deve herdar valores dos outros repositórios do payload"


@patch("src.queries.rq08.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=4)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 4, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (4)"
    )
