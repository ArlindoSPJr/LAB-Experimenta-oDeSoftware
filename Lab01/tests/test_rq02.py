from unittest.mock import patch

from src.queries import rq02


def _payload_repositorio(nome="repo-exemplo", login="dono-exemplo", estrelas=500, total_prs=42):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": login},
        "stargazerCount": estrelas,
        "pullRequests": {"totalCount": total_prs},
    }


def test_coletar_amostra__total_prs_zero_e_repassado_sem_transformacao():
    """Quando pullRequests.totalCount é 0, o valor deve ser repassado como 0, sem alterações."""
    payload = {"search": {"nodes": [_payload_repositorio(total_prs=0)]}}

    with patch("src.queries.rq02.run_query", return_value=payload) as mock_run_query:
        resultado = rq02.coletar_amostra(quantidade=1, token="token-fake")

    assert mock_run_query.called, "run_query deveria ter sido chamado"
    assert len(resultado) == 1, "deveria haver exatamente uma linha na amostra"
    assert resultado[0]["total_prs_aceitas"] == 0, "total_prs_aceitas deveria ser 0, sem transformação"


def test_coletar_amostra__total_prs_positivo_e_repassado_sem_arredondamento_ou_calculo():
    """Quando pullRequests.totalCount é positivo, o valor deve ser repassado igual, sem cálculo ou arredondamento."""
    payload = {"search": {"nodes": [_payload_repositorio(total_prs=250)]}}

    with patch("src.queries.rq02.run_query", return_value=payload):
        resultado = rq02.coletar_amostra(quantidade=1, token="token-fake")

    assert resultado[0]["total_prs_aceitas"] == 250, "total_prs_aceitas deveria ser repassado igual a 250"


def test_coletar_amostra__multiplos_repositorios_gera_uma_linha_por_repositorio_na_ordem_correta():
    """Com múltiplos repositórios no payload, cada um deve virar uma linha correspondente, na mesma ordem, sem misturar valores."""
    payload = {
        "search": {
            "nodes": [
                _payload_repositorio(nome="repo-a", login="dono-a", estrelas=100, total_prs=10),
                _payload_repositorio(nome="repo-b", login="dono-b", estrelas=200, total_prs=20),
                _payload_repositorio(nome="repo-c", login="dono-c", estrelas=300, total_prs=30),
            ]
        }
    }

    with patch("src.queries.rq02.run_query", return_value=payload):
        resultado = rq02.coletar_amostra(quantidade=3, token="token-fake")

    assert len(resultado) == 3, "deveria haver uma linha por repositório do payload"

    assert resultado[0]["repositorio"] == "dono-a/repo-a", "primeira linha deveria corresponder ao primeiro repositório"
    assert resultado[0]["estrelas"] == 100, "estrelas do primeiro repositório não deveriam se misturar com as demais"
    assert resultado[0]["total_prs_aceitas"] == 10, "total_prs_aceitas do primeiro repositório está incorreto"

    assert resultado[1]["repositorio"] == "dono-b/repo-b", "segunda linha deveria corresponder ao segundo repositório"
    assert resultado[1]["estrelas"] == 200, "estrelas do segundo repositório não deveriam se misturar com as demais"
    assert resultado[1]["total_prs_aceitas"] == 20, "total_prs_aceitas do segundo repositório está incorreto"

    assert resultado[2]["repositorio"] == "dono-c/repo-c", "terceira linha deveria corresponder ao terceiro repositório"
    assert resultado[2]["estrelas"] == 300, "estrelas do terceiro repositório não deveriam se misturar com as demais"
    assert resultado[2]["total_prs_aceitas"] == 30, "total_prs_aceitas do terceiro repositório está incorreto"


def test_coletar_amostra__quantidade_informada_e_repassada_nas_variaveis_da_query():
    """Ao chamar coletar_amostra(quantidade=7), as variáveis enviadas à query devem conter quantidade=7."""
    payload = {"search": {"nodes": [_payload_repositorio()]}}

    with patch("src.queries.rq02.run_query", return_value=payload) as mock_run_query:
        rq02.coletar_amostra(quantidade=7, token="token-fake")

    _, variaveis = mock_run_query.call_args.args[:2]
    assert variaveis["quantidade"] == 7, "a variável 'quantidade' enviada à query deveria ser 7"
