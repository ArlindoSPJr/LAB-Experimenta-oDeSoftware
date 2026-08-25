from unittest.mock import patch

from src.queries.rq06 import calcular_razao_issues, coletar_amostra


def test_calcular_razao_issues__total_zero_retorna_zero():
    """Quando o total de issues é zero, a razão deve ser 0.0, sem lançar ZeroDivisionError."""
    resultado = calcular_razao_issues(fechadas=0, total=0)

    assert resultado == 0.0, "A razão deveria ser 0.0 quando não há issues"


def test_calcular_razao_issues__fechadas_igual_total_retorna_um():
    """Quando todas as issues estão fechadas, a razão deve ser 1.0."""
    resultado = calcular_razao_issues(fechadas=50, total=50)

    assert resultado == 1.0, "A razão deveria ser 1.0 quando fechadas == total"


def test_calcular_razao_issues__nenhuma_fechada_retorna_zero():
    """Quando nenhuma issue está fechada, mas o total é maior que zero, a razão deve ser 0.0."""
    resultado = calcular_razao_issues(fechadas=0, total=20)

    assert resultado == 0.0, "A razão deveria ser 0.0 quando não há issues fechadas"


def test_calcular_razao_issues__dizima_periodica_arredonda_para_quatro_casas():
    """Uma razão com dízima periódica deve ser arredondada para 4 casas decimais."""
    resultado = calcular_razao_issues(fechadas=1, total=3)

    assert resultado == round(1 / 3, 4) == 0.3333, "A razão deveria ser arredondada para 0.3333"


def _construir_repositorio(nome, dono, estrelas, fechadas, total):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "issuesFechadas": {"totalCount": fechadas},
        "issuesTotal": {"totalCount": total},
    }


@patch("src.queries.rq06.run_query")
def test_coletar_amostra__razao_bate_com_calculo_direto(mock_run_query):
    """A razao_issues_fechadas retornada por coletar_amostra deve coincidir com calcular_razao_issues
    aplicada aos mesmos valores de fechadas/total do payload."""
    fechadas, total = 30, 100
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _construir_repositorio("repo-exemplo", "dono-exemplo", 500, fechadas, total),
            ]
        }
    }

    linhas = coletar_amostra(quantidade=1, token="token-fake")

    assert len(linhas) == 1, "Deveria retornar uma linha para um repositório no payload"
    assert linhas[0]["razao_issues_fechadas"] == calcular_razao_issues(fechadas, total), (
        "A razão calculada em coletar_amostra deveria bater com calcular_razao_issues"
    )
    assert linhas[0]["repositorio"] == "dono-exemplo/repo-exemplo", "O nome do repositório deveria ser owner/name"
    assert linhas[0]["estrelas"] == 500, "A quantidade de estrelas deveria ser preservada do payload"
    assert linhas[0]["issues_fechadas"] == fechadas, "A quantidade de issues fechadas deveria ser preservada do payload"
    assert linhas[0]["issues_total"] == total, "A quantidade total de issues deveria ser preservada do payload"


@patch("src.queries.rq06.run_query")
def test_coletar_amostra__multiplos_repositorios_com_total_zero_nao_quebra(mock_run_query):
    """Com múltiplos repositórios no payload, um deles com issuesTotal.totalCount = 0, coletar_amostra
    não deve lançar ZeroDivisionError e deve retornar 0.0 para esse item, calculando os demais normalmente."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _construir_repositorio("repo-a", "dono-a", 1000, 10, 0),
                _construir_repositorio("repo-b", "dono-b", 500, 25, 50),
                _construir_repositorio("repo-c", "dono-c", 200, 3, 3),
            ]
        }
    }

    linhas = coletar_amostra(quantidade=3, token="token-fake")

    assert len(linhas) == 3, "Deveria retornar uma linha para cada repositório no payload"

    repo_a, repo_b, repo_c = linhas
    assert repo_a["repositorio"] == "dono-a/repo-a", "O repositório com issuesTotal zero deveria ser identificado corretamente"
    assert repo_a["razao_issues_fechadas"] == 0.0, "A razão deveria ser 0.0 quando issuesTotal.totalCount é zero"
    assert repo_b["razao_issues_fechadas"] == calcular_razao_issues(25, 50), "A razão do segundo repositório deveria ser calculada normalmente"
    assert repo_c["razao_issues_fechadas"] == calcular_razao_issues(3, 3) == 1.0, "A razão do terceiro repositório deveria ser 1.0"
