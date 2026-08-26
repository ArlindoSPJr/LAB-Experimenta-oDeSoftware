from unittest.mock import patch

from src.queries.rq11 import coletar_amostra


def _repositorio(nome, dono, estrelas, plataformas_funding):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "fundingLinks": [{"platform": plataforma} for plataforma in plataformas_funding],
    }


@patch("src.queries.rq11.run_query")
def test_coletar_amostra__repositorio_com_funding_marca_possui_funding_true(mock_run_query):
    """Repositório com fundingLinks preenchido deve marcar possui_funding True e listar plataformas."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-patrocinado", "dono-exemplo", 500, ["GITHUB", "OPEN_COLLECTIVE"]),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["possui_funding"] is True, (
        "O campo 'possui_funding' deve ser True quando fundingLinks não é vazio"
    )
    assert resultado[0]["plataformas_funding"] == "GITHUB;OPEN_COLLECTIVE", (
        "As plataformas devem ser concatenadas na ordem recebida"
    )


@patch("src.queries.rq11.run_query")
def test_coletar_amostra__repositorio_sem_funding_marca_possui_funding_false(mock_run_query):
    """Repositório com fundingLinks vazio deve marcar possui_funding False e plataformas 'N/A'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-sem-funding", "dono-exemplo", 10000, []),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["possui_funding"] is False, (
        "O campo 'possui_funding' deve ser False quando fundingLinks vem vazio"
    )
    assert resultado[0]["plataformas_funding"] == "N/A", (
        "O campo 'plataformas_funding' deve ser 'N/A' quando não há links de financiamento"
    )
    assert resultado[0]["estrelas"] == 10000, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-sem-funding", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )


@patch("src.queries.rq11.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_item_na_mesma_ordem(mock_run_query):
    """Cada repositório do payload deve virar uma linha própria, na mesma ordem, sem misturar valores."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-um", "dono-um", 1000, []),
                _repositorio("repo-dois", "dono-dois", 50, ["GITHUB"]),
                _repositorio("repo-tres", "dono-tres", 20000, []),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=3)

    assert len(resultado) == 3, "Deveria retornar uma linha para cada repositório presente no payload"
    assert resultado[0]["possui_funding"] is False, "Primeira linha deve trazer o valor exato do primeiro repositório"
    assert resultado[1]["possui_funding"] is True, "Segunda linha não deve herdar valores dos outros repositórios do payload"
    assert resultado[2]["possui_funding"] is False, "Terceira linha não deve herdar valores dos outros repositórios do payload"


@patch("src.queries.rq11.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=4)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 4, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (4)"
    )
