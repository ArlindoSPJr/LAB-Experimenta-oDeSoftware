from unittest.mock import patch

from src.queries.rq09 import coletar_amostra


def _repositorio(nome, dono, estrelas, branch_padrao):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub.

    `branch_padrao=None` simula um repositório vazio, sem branch padrão (defaultBranchRef nulo).
    """
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "defaultBranchRef": {"name": branch_padrao} if branch_padrao is not None else None,
    }


@patch("src.queries.rq09.run_query")
def test_coletar_amostra__branch_padrao_main_e_repassada_sem_transformacao(mock_run_query):
    """Repositório com defaultBranchRef 'main' deve manter esse valor em 'branch_padrao'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-main", "dono-exemplo", 500, "main"),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["branch_padrao"] == "main", (
        "O campo 'branch_padrao' deve refletir exatamente o nome vindo de defaultBranchRef"
    )


@patch("src.queries.rq09.run_query")
def test_coletar_amostra__branch_padrao_master_e_repassada_sem_transformacao(mock_run_query):
    """Repositório com defaultBranchRef 'master' deve manter esse valor em 'branch_padrao'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-master", "dono-exemplo", 10000, "master"),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["branch_padrao"] == "master", (
        "O campo 'branch_padrao' deve refletir exatamente o nome vindo de defaultBranchRef"
    )


@patch("src.queries.rq09.run_query")
def test_coletar_amostra__defaultBranchRef_nulo_vira_na(mock_run_query):
    """Repositório sem branch padrão (defaultBranchRef nulo, ex.: repo vazio) deve virar 'N/A'."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-vazio", "dono-exemplo", 5, None),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["branch_padrao"] == "N/A", (
        "O campo 'branch_padrao' deve ser 'N/A' quando defaultBranchRef vem nulo, sem lançar erro"
    )


@patch("src.queries.rq09.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_item_na_mesma_ordem(mock_run_query):
    """Cada repositório do payload deve virar uma linha própria, na mesma ordem, sem misturar valores."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-um", "dono-um", 1000, "main"),
                _repositorio("repo-dois", "dono-dois", 50, "master"),
                _repositorio("repo-tres", "dono-tres", 20000, "develop"),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=3)

    assert len(resultado) == 3, "Deveria retornar uma linha para cada repositório presente no payload"
    assert resultado[0]["branch_padrao"] == "main", "Primeira linha deve trazer o valor exato do primeiro repositório"
    assert resultado[1]["branch_padrao"] == "master", "Segunda linha não deve herdar valores dos outros repositórios do payload"
    assert resultado[2]["branch_padrao"] == "develop", "Terceira linha não deve herdar valores dos outros repositórios do payload"


@patch("src.queries.rq09.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=4)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 4, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (4)"
    )
