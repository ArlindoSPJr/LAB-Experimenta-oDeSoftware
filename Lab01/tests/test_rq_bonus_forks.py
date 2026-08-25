from unittest.mock import patch

from src.queries.rq_bonus_forks import coletar_amostra


def _repositorio(nome, dono, estrelas, forks):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "forkCount": forks,
    }


@patch("src.queries.rq_bonus_forks.run_query")
def test_coletar_amostra__fork_count_zero_e_repassado_sem_transformacao(mock_run_query):
    """Repositório sem nenhum fork (forkCount: 0) deve manter o valor 0 em 'total_forks'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-sem-fork", "dono-exemplo", 500, 0),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["total_forks"] == 0, (
        "O campo 'total_forks' deve ser 0 quando forkCount vem zerado, sem virar None ou 'N/A'"
    )


@patch("src.queries.rq_bonus_forks.run_query")
def test_coletar_amostra__fork_count_positivo_e_repassado_sem_transformacao(mock_run_query):
    """Repositório com forkCount positivo deve ter o mesmo valor repassado em 'total_forks'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-popular", "dono-exemplo", 10000, 1500),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["total_forks"] == 1500, (
        "O campo 'total_forks' deve refletir exatamente o valor de forkCount (1500)"
    )
    assert resultado[0]["estrelas"] == 10000, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-popular", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )


@patch("src.queries.rq_bonus_forks.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_item_na_mesma_ordem(mock_run_query):
    """Cada repositório do payload deve virar uma linha própria, na mesma ordem, sem misturar valores."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-um", "dono-um", 1000, 200),
                _repositorio("repo-dois", "dono-dois", 50, 3),
                _repositorio("repo-tres", "dono-tres", 20000, 4500),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=3)

    assert len(resultado) == 3, "Deveria retornar uma linha para cada repositório presente no payload"

    assert resultado[0]["repositorio"] == "dono-um/repo-um", (
        "Primeira linha deve corresponder ao primeiro repositório do payload"
    )
    assert resultado[0]["estrelas"] == 1000 and resultado[0]["total_forks"] == 200, (
        "Primeira linha deve trazer os valores exatos do primeiro repositório"
    )

    assert resultado[1]["repositorio"] == "dono-dois/repo-dois", (
        "Segunda linha deve corresponder ao segundo repositório do payload"
    )
    assert resultado[1]["estrelas"] == 50 and resultado[1]["total_forks"] == 3, (
        "Segunda linha não deve herdar valores dos outros repositórios do payload"
    )

    assert resultado[2]["repositorio"] == "dono-tres/repo-tres", (
        "Terceira linha deve corresponder ao terceiro repositório do payload"
    )
    assert resultado[2]["estrelas"] == 20000 and resultado[2]["total_forks"] == 4500, (
        "Terceira linha não deve herdar valores dos outros repositórios do payload"
    )


@patch("src.queries.rq_bonus_forks.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=4)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 4, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (4)"
    )
