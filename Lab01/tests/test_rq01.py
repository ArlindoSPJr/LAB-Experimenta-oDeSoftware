from datetime import datetime, timezone
from unittest.mock import patch

from src.queries.rq01 import calcular_idade_anos, coletar_amostra


# ---------------------------------------------------------------------------
# calcular_idade_anos
# ---------------------------------------------------------------------------


def test_calcular_idade_anos__um_ano_antes_da_referencia(referencia_fixa):
    """Repositório criado 365 dias antes da referência deve ter idade ~= round(365/365.25, 2)."""
    data_criacao = "2023-01-01T00:00:00Z"  # exatamente 365 dias antes de 2024-01-01 (2023 não é bissexto)
    esperado = round(365 / 365.25, 2)

    resultado = calcular_idade_anos(data_criacao, referencia_fixa)

    assert resultado == esperado, "A idade calculada deve corresponder a round(365/365.25, 2)"


def test_calcular_idade_anos__diferenca_fracionaria_arredonda_corretamente(referencia_fixa):
    """Uma diferença de 100 dias deve ser arredondada para 2 casas decimais conforme a fórmula."""
    data_criacao = "2023-09-23T00:00:00+00:00"  # 100 dias antes de 2024-01-01
    dias_esperados = (referencia_fixa - datetime(2023, 9, 23, tzinfo=timezone.utc)).days
    assert dias_esperados == 100, "Pré-condição do teste: a diferença deve ser de exatamente 100 dias"
    esperado = round(100 / 365.25, 2)

    resultado = calcular_idade_anos(data_criacao, referencia_fixa)

    assert resultado == esperado, "O resultado deve ser round(100/365.25, 2)"


def test_calcular_idade_anos__timestamp_terminado_em_z_e_aceito(referencia_fixa):
    """Um timestamp ISO terminado em 'Z' deve ser aceito sem lançar exceção."""
    data_criacao = "2020-01-01T00:00:00Z"

    resultado = calcular_idade_anos(data_criacao, referencia_fixa)

    assert isinstance(resultado, float), "O resultado deve ser um float, sem erro de parsing do 'Z'"


def test_calcular_idade_anos__data_criacao_igual_a_referencia(referencia_fixa):
    """Se a data de criação for igual à referência, a idade deve ser exatamente 0.0."""
    data_criacao = referencia_fixa.isoformat().replace("+00:00", "Z")

    resultado = calcular_idade_anos(data_criacao, referencia_fixa)

    assert resultado == 0.0, "A idade deve ser 0.0 quando a data de criação coincide com a referência"


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
                    "stargazerCount": 123,
                    "createdAt": "2020-01-01T00:00:00Z",
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
                    "createdAt": "2018-06-15T00:00:00Z",
                },
                {
                    "name": "repo-dois",
                    "owner": {"login": "dono-dois"},
                    "stargazerCount": 42,
                    "createdAt": "2022-03-10T00:00:00Z",
                },
            ]
        }
    }


@patch("src.queries.rq01.run_query")
def test_coletar_amostra__retorna_dict_com_chaves_e_idade_correta(mock_run_query):
    """O dict retornado deve conter repositorio, estrelas, data_criacao e idade_anos corretos.

    `coletar_amostra` não recebe `referencia` (usa `datetime.now()` internamente via
    `calcular_idade_anos`), então o valor esperado de `idade_anos` é obtido chamando a
    própria `calcular_idade_anos` sem referencia explícita, logo em seguida — ambas as
    chamadas ocorrem no mesmo instante de execução do teste, então o resultado deve coincidir.
    """
    mock_run_query.return_value = _payload_um_repositorio()

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deve haver exatamente uma linha para um repositório no payload"
    linha = resultado[0]
    assert set(linha.keys()) == {"repositorio", "estrelas", "data_criacao", "idade_anos"}, (
        "O dict retornado deve conter exatamente as quatro chaves esperadas"
    )
    assert linha["repositorio"] == "dono-exemplo/repo-exemplo", "O nome do repositório deve ser 'owner/name'"
    assert linha["estrelas"] == 123, "A quantidade de estrelas deve ser repassada sem alteração"
    assert linha["data_criacao"] == "2020-01-01T00:00:00Z", "A data de criação deve ser repassada sem alteração"

    idade_esperada = calcular_idade_anos("2020-01-01T00:00:00Z")
    assert linha["idade_anos"] == idade_esperada, "A idade calculada deve bater com calcular_idade_anos para a mesma data"


@patch("src.queries.rq01.run_query")
def test_coletar_amostra__quantidade_explicita_tem_prioridade_sobre_padrao(mock_run_query):
    """Quando quantidade é passada explicitamente, ela deve ser usada nas variáveis da query, sem chamar obter_quantidade_repos."""
    mock_run_query.return_value = _payload_um_repositorio()

    coletar_amostra(quantidade=5)

    assert mock_run_query.called, "run_query deve ter sido chamado"
    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 5, "O valor explícito de quantidade deve prevalecer sobre obter_quantidade_repos()"


@patch("src.queries.rq01.run_query")
def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_no_na_ordem(mock_run_query):
    """Com múltiplos nodes no payload, deve haver uma linha por repositório, preservando a ordem."""
    mock_run_query.return_value = _payload_multiplos_repositorios()

    resultado = coletar_amostra(quantidade=2)

    assert len(resultado) == 2, "Deve haver uma linha para cada node do payload"
    assert resultado[0]["repositorio"] == "dono-um/repo-um", "A primeira linha deve corresponder ao primeiro node"
    assert resultado[1]["repositorio"] == "dono-dois/repo-dois", "A segunda linha deve corresponder ao segundo node"
    assert resultado[0]["estrelas"] == 500, "As estrelas do primeiro repositório devem ser preservadas"
    assert resultado[1]["estrelas"] == 42, "As estrelas do segundo repositório devem ser preservadas"
