from unittest.mock import patch

from src.queries.rq03 import coletar_amostra


def _payload(repositorios: list[dict]) -> dict:
    """Monta o payload no formato retornado por `run_query` para os testes deste módulo."""
    return {"search": {"nodes": repositorios}}


def _repositorio(nome: str, dono: str, estrelas: int, total_releases: int) -> dict:
    """Monta um nó de repositório no formato bruto devolvido pela API GraphQL."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "releases": {"totalCount": total_releases},
    }


# ---------------------------------------------------------------------------
# coletar_amostra
# ---------------------------------------------------------------------------


def test_coletar_amostra__repositorio_sem_releases_retorna_total_zero():
    """Repositório sem nenhuma release deve aparecer com 'total_releases' igual a 0."""
    payload = _payload([_repositorio("repo-exemplo", "dono-exemplo", 500, 0)])

    with patch("src.queries.rq03.run_query", return_value=payload) as mock_run_query:
        resultado = coletar_amostra(quantidade=1, token="fake-token")

    assert len(resultado) == 1, "Deveria haver exatamente uma linha na amostra"
    assert resultado[0]["total_releases"] == 0, "Repositório sem releases deveria ter total_releases igual a 0"
    mock_run_query.assert_called_once()


def test_coletar_amostra__repositorio_com_releases_repassa_valor_sem_transformacao():
    """Total de releases positivo deve ser repassado sem nenhuma transformação."""
    payload = _payload([_repositorio("repo-exemplo", "dono-exemplo", 500, 87)])

    with patch("src.queries.rq03.run_query", return_value=payload):
        resultado = coletar_amostra(quantidade=1, token="fake-token")

    assert resultado[0]["total_releases"] == 87, "O total de releases deveria ser repassado sem alteração (87)"


def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_repositorio_na_mesma_ordem():
    """Com múltiplos repositórios no payload, deve haver uma linha de saída por repositório, na mesma ordem e com os valores corretos."""
    payload = _payload(
        [
            _repositorio("repo-um", "dono-um", 1000, 5),
            _repositorio("repo-dois", "dono-dois", 200, 0),
            _repositorio("repo-tres", "dono-tres", 50, 42),
        ]
    )

    with patch("src.queries.rq03.run_query", return_value=payload):
        resultado = coletar_amostra(quantidade=3, token="fake-token")

    assert len(resultado) == 3, "Deveria haver uma linha de saída para cada repositório do payload"

    assert resultado[0] == {
        "repositorio": "dono-um/repo-um",
        "estrelas": 1000,
        "total_releases": 5,
    }, "Os valores do primeiro repositório deveriam corresponder ao primeiro nó do payload, na mesma ordem"

    assert resultado[1] == {
        "repositorio": "dono-dois/repo-dois",
        "estrelas": 200,
        "total_releases": 0,
    }, "Os valores do segundo repositório deveriam corresponder ao segundo nó do payload, na mesma ordem"

    assert resultado[2] == {
        "repositorio": "dono-tres/repo-tres",
        "estrelas": 50,
        "total_releases": 42,
    }, "Os valores do terceiro repositório deveriam corresponder ao terceiro nó do payload, na mesma ordem"


def test_coletar_amostra__quantidade_informada_e_enviada_nas_variaveis_da_query():
    """Ao chamar coletar_amostra(quantidade=3), o valor 3 deve ser enviado como variável 'quantidade' da query GraphQL."""
    payload = _payload([_repositorio("repo-exemplo", "dono-exemplo", 500, 10)])

    with patch("src.queries.rq03.run_query", return_value=payload) as mock_run_query:
        coletar_amostra(quantidade=3, token="fake-token")

    variaveis_enviadas = mock_run_query.call_args.args[1]
    assert variaveis_enviadas["quantidade"] == 3, "A quantidade informada deveria ser repassada nas variáveis da query"
