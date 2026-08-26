from unittest.mock import patch

from src.queries.rq10 import coletar_amostra


def _repositorio(nome, dono, estrelas, discussions_habilitado):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "hasDiscussionsEnabled": discussions_habilitado,
    }


@patch("src.queries.rq10.run_query")
def test_coletar_amostra__repositorio_com_discussions_mantem_true(mock_run_query):
    """Repositório com Discussions habilitado (hasDiscussionsEnabled: true) deve manter True."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-com-discussions", "dono-exemplo", 500, True),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["discussions_habilitado"] is True, (
        "O campo 'discussions_habilitado' deve ser True quando hasDiscussionsEnabled vem true"
    )


@patch("src.queries.rq10.run_query")
def test_coletar_amostra__repositorio_sem_discussions_mantem_false(mock_run_query):
    """Repositório sem Discussions habilitado (hasDiscussionsEnabled: false) deve manter False."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-sem-discussions", "dono-exemplo", 10000, False),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["discussions_habilitado"] is False, (
        "O campo 'discussions_habilitado' deve ser False quando hasDiscussionsEnabled vem false"
    )
    assert resultado[0]["estrelas"] == 10000, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-sem-discussions", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )


@patch("src.queries.rq10.run_query")
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
    assert resultado[0]["discussions_habilitado"] is False, "Primeira linha deve trazer o valor exato do primeiro repositório"
    assert resultado[1]["discussions_habilitado"] is True, "Segunda linha não deve herdar valores dos outros repositórios do payload"
    assert resultado[2]["discussions_habilitado"] is False, "Terceira linha não deve herdar valores dos outros repositórios do payload"


@patch("src.queries.rq10.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=4)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 4, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (4)"
    )
