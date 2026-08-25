from datetime import datetime, timezone
from unittest.mock import patch

from src.queries.rq04 import calcular_dias_desde_atualizacao, coletar_amostra


# ---------------------------------------------------------------------------
# calcular_dias_desde_atualizacao
# ---------------------------------------------------------------------------


def test_calcular_dias_desde_atualizacao__trinta_dias_antes_da_referencia(referencia_fixa):
    """Uma atualização exatamente 30 dias antes da referência deve retornar 30."""
    data_atualizacao = "2023-12-02T00:00:00Z"  # 30 dias antes de 2024-01-01
    dias_esperados = (referencia_fixa - datetime(2023, 12, 2, tzinfo=timezone.utc)).days
    assert dias_esperados == 30, "Pré-condição do teste: a diferença deve ser de exatamente 30 dias"

    resultado = calcular_dias_desde_atualizacao(data_atualizacao, referencia_fixa)

    assert resultado == 30, "O resultado deve ser exatamente 30 dias"
    assert isinstance(resultado, int), "O resultado deve ser um int"


def test_calcular_dias_desde_atualizacao__data_atualizacao_igual_a_referencia(referencia_fixa):
    """Se a data de atualização for igual à referência, o resultado deve ser exatamente 0."""
    data_atualizacao = referencia_fixa.isoformat().replace("+00:00", "Z")

    resultado = calcular_dias_desde_atualizacao(data_atualizacao, referencia_fixa)

    assert resultado == 0, "O número de dias deve ser 0 quando a data de atualização coincide com a referência"


def test_calcular_dias_desde_atualizacao__timestamp_terminado_em_z_e_aceito(referencia_fixa):
    """Um timestamp ISO terminado em 'Z' deve ser aceito sem lançar exceção."""
    data_atualizacao = "2020-01-01T00:00:00Z"

    resultado = calcular_dias_desde_atualizacao(data_atualizacao, referencia_fixa)

    assert isinstance(resultado, int), "O resultado deve ser um int, sem erro de parsing do 'Z'"


# ---------------------------------------------------------------------------
# coletar_amostra
# ---------------------------------------------------------------------------


def _payload_um_repositorio():
    return {
        "search": {
            "nodes": [
                {
                    "name": "repo-exemplo",
                    "owner": {"login": "dono-exemplo"},
                    "stargazerCount": 500,
                    "updatedAt": "2000-01-01T00:00:00Z",
                },
            ]
        }
    }


def _payload_multiplos_repositorios():
    return {
        "search": {
            "nodes": [
                {
                    "name": "repo-um",
                    "owner": {"login": "dono-um"},
                    "stargazerCount": 500,
                    "updatedAt": "2018-06-15T00:00:00Z",
                },
                {
                    "name": "repo-dois",
                    "owner": {"login": "dono-dois"},
                    "stargazerCount": 42,
                    "updatedAt": "2022-03-10T00:00:00Z",
                },
            ]
        }
    }


@patch("src.queries.rq04.run_query")
def test_coletar_amostra__retorna_dict_com_chaves_e_dias_desde_atualizacao_correto(mock_run_query):
    """O dict retornado deve conter repositorio, estrelas, ultima_atualizacao e dias_desde_atualizacao coerentes."""
    mock_run_query.return_value = _payload_um_repositorio()

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deve haver exatamente uma linha para um repositório no payload"
    linha = resultado[0]
    assert set(linha.keys()) == {"repositorio", "estrelas", "ultima_atualizacao", "dias_desde_atualizacao"}, (
        "O dict retornado deve conter exatamente as quatro chaves esperadas"
    )
    assert linha["repositorio"] == "dono-exemplo/repo-exemplo", "O nome do repositório deve ser 'owner/name'"
    assert linha["estrelas"] == 500, "A quantidade de estrelas deve ser repassada sem alteração"
    assert linha["ultima_atualizacao"] == "2000-01-01T00:00:00Z", "A data de atualização deve ser repassada sem alteração"

    # A data de atualização é de muitos anos atrás (2000), então o resultado deve ser um
    # inteiro positivo e razoavelmente grande, sem cravar um valor exato dependente de datetime.now().
    assert isinstance(linha["dias_desde_atualizacao"], int), "dias_desde_atualizacao deve ser um int"
    assert linha["dias_desde_atualizacao"] > 8000, (
        "Uma atualização em 2000 deve resultar em milhares de dias desde então até hoje"
    )


@patch("src.queries.rq04.run_query")
def test_coletar_amostra__quantidade_explicita_tem_prioridade_sobre_padrao(mock_run_query):
    """Quando quantidade é passada explicitamente, ela deve ser usada nas variáveis da query, sem chamar obter_quantidade_repos."""
    mock_run_query.return_value = _payload_um_repositorio()

    coletar_amostra(quantidade=5)

    assert mock_run_query.called, "run_query deve ter sido chamado"
    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 5, "O valor explícito de quantidade deve prevalecer sobre obter_quantidade_repos()"


@patch("src.queries.rq04.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_no_na_ordem(mock_run_query):
    """Com múltiplos nodes no payload, deve haver uma linha por repositório, preservando a ordem e os valores."""
    mock_run_query.return_value = _payload_multiplos_repositorios()

    resultado = coletar_amostra(quantidade=2)

    assert len(resultado) == 2, "Deve haver uma linha para cada node do payload"
    assert resultado[0]["repositorio"] == "dono-um/repo-um", "A primeira linha deve corresponder ao primeiro node"
    assert resultado[1]["repositorio"] == "dono-dois/repo-dois", "A segunda linha deve corresponder ao segundo node"
    assert resultado[0]["estrelas"] == 500, "As estrelas do primeiro repositório devem ser preservadas"
    assert resultado[1]["estrelas"] == 42, "As estrelas do segundo repositório devem ser preservadas"

    dias_repo_um = calcular_dias_desde_atualizacao("2018-06-15T00:00:00Z")
    dias_repo_dois = calcular_dias_desde_atualizacao("2022-03-10T00:00:00Z")
    assert dias_repo_um > dias_repo_dois, (
        "O repositório atualizado há mais tempo (2018) deve ter mais dias desde a atualização que o de 2022"
    )
