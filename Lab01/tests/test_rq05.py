from unittest.mock import patch

from src.queries.rq05 import coletar_amostra


def _repositorio(nome, dono, estrelas, linguagem):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "primaryLanguage": {"name": linguagem} if linguagem else None,
    }


@patch("src.queries.rq05.run_query")
def test_coletar_amostra__com_linguagem_primaria_presente(mock_run_query):
    """Quando primaryLanguage vem preenchido, a linha deve trazer o nome da linguagem."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-exemplo", "dono-exemplo", 500, "Python"),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-exemplo", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )
    assert resultado[0]["estrelas"] == 500, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["linguagem_primaria"] == "Python", (
        "A linguagem primária deve ser extraída de primaryLanguage.name"
    )


@patch("src.queries.rq05.run_query")
def test_coletar_amostra__com_primary_language_nulo_retorna_na(mock_run_query):
    """Repositório sem linguagem detectada (primaryLanguage: null) deve virar 'N/A'.

    Caso de borda real citado no relatório do projeto: 2 de 1000 repositórios
    coletados não têm linguagem primária detectada pelo GitHub.
    """
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-sem-linguagem", "dono-exemplo", 10, None),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    assert resultado[0]["linguagem_primaria"] == "N/A", (
        "Repositório com primaryLanguage nulo deve receber 'N/A' como linguagem primária"
    )


@patch("src.queries.rq05.run_query")
def test_coletar_amostra__multiplos_repositorios_nao_misturam_linguagens(mock_run_query):
    """Cada linha do resultado deve refletir o próprio repositório, sem vazar dados entre eles."""
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-com-linguagem", "dono-um", 1000, "JavaScript"),
                _repositorio("repo-sem-linguagem", "dono-dois", 20, None),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=2)

    assert len(resultado) == 2, "Deveria retornar uma linha por repositório presente no payload"

    linha_com_linguagem = resultado[0]
    linha_sem_linguagem = resultado[1]

    assert linha_com_linguagem["repositorio"] == "dono-um/repo-com-linguagem", (
        "Primeira linha deve corresponder ao primeiro repositório do payload"
    )
    assert linha_com_linguagem["linguagem_primaria"] == "JavaScript", (
        "Primeira linha não deve herdar valor 'N/A' do segundo repositório"
    )

    assert linha_sem_linguagem["repositorio"] == "dono-dois/repo-sem-linguagem", (
        "Segunda linha deve corresponder ao segundo repositório do payload"
    )
    assert linha_sem_linguagem["linguagem_primaria"] == "N/A", (
        "Segunda linha não deve herdar a linguagem do primeiro repositório"
    )


@patch("src.queries.rq05.run_query")
def test_coletar_amostra__envia_quantidade_informada_para_run_query(mock_run_query):
    """A quantidade passada explicitamente deve ser repassada nas variáveis da query GraphQL."""
    mock_run_query.return_value = {"search": {"nodes": []}}

    coletar_amostra(quantidade=9)

    _, variaveis, *_ = mock_run_query.call_args.args
    assert variaveis["quantidade"] == 9, (
        "A variável 'quantidade' enviada a run_query deve ser igual ao valor informado (9)"
    )
