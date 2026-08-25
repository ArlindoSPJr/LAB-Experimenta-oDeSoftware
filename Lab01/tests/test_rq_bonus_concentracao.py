from unittest.mock import patch

from src.queries.rq_bonus_concentracao import calcular_top_contribuidor, coletar_amostra


def _pr(login):
    """Monta um nó de pullRequests no formato retornado pela API GraphQL do GitHub.

    `login=None` representa uma PR cujo autor é nulo (conta deletada/anônima).
    """
    return {"author": {"login": login} if login else None}


def _repositorio(nome, dono, estrelas, total_prs, autores_prs):
    """Monta um nó de repositório no formato retornado pela API GraphQL do GitHub."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "pullRequests": {
            "totalCount": total_prs,
            "nodes": [_pr(autor) for autor in autores_prs],
        },
    }


# ---------------------------------------------------------------------------
# calcular_top_contribuidor
# ---------------------------------------------------------------------------


def test_calcular_top_contribuidor__lista_vazia_retorna_na_e_zero():
    """Sem nenhuma PR na amostra, deve retornar ('N/A', 0.0)."""
    resultado = calcular_top_contribuidor([])

    assert resultado == ("N/A", 0.0), (
        "Amostra vazia deve retornar ('N/A', 0.0), sem tentar calcular o mais frequente"
    )


def test_calcular_top_contribuidor__todos_autores_nulos_retorna_na_e_zero():
    """Amostra só com autores nulos (contas deletadas/anônimas) deve retornar ('N/A', 0.0)
    após o filtro, mesmo a lista de entrada não sendo vazia antes do filtro."""
    resultado = calcular_top_contribuidor([None, None])

    assert resultado == ("N/A", 0.0), (
        "Amostra em que todos os autores são None deve retornar ('N/A', 0.0) após o filtro"
    )


def test_calcular_top_contribuidor__unico_autor_concentra_cem_por_cento():
    """Um único autor presente em todas as PRs da amostra deve concentrar 100%."""
    resultado = calcular_top_contribuidor(["alice", "alice", "alice"])

    assert resultado == ("alice", 1.0), (
        "Quando só 'alice' aparece na amostra, ela deve ser o top contribuidor com concentração 1.0"
    )


def test_calcular_top_contribuidor__autor_majoritario_entre_distintos():
    """30 PRs amostradas: 15 de 'alice' e as outras 15 distribuídas uma para cada
    um de 15 autores diferentes. 'alice' deve ser o top contribuidor com 50%."""
    outros_autores = [f"autor-{i}" for i in range(15)]
    autores = ["alice"] * 15 + outros_autores

    resultado = calcular_top_contribuidor(autores)

    assert resultado == ("alice", 0.5), (
        "'alice' concentra 15 das 30 PRs amostradas (15/30 = 0.5), deve ser o top contribuidor"
    )


def test_calcular_top_contribuidor__empate_documenta_contrato_do_counter_most_common():
    """Em caso de empate (2 PRs para 'alice' e 2 para 'bob'), o Counter.most_common(1)
    do Python é determinístico: resolve o empate pela ordem de inserção da primeira
    ocorrência de cada chave distinta. Como 'alice' aparece primeiro na lista,
    Counter(['alice', 'alice', 'bob', 'bob']).most_common(1) retorna [('alice', 2)].
    Este teste trava esse contrato atual do código (não é um comportamento
    "correto" no sentido estatístico, é apenas o que o código de fato produz)."""
    resultado = calcular_top_contribuidor(["alice", "alice", "bob", "bob"])

    assert resultado == ("alice", 0.5), (
        "Em empate, most_common(1) deve retornar o autor que apareceu primeiro na amostra "
        "('alice'), com concentração 2/4 = 0.5 — contrato atual do Counter, não uma regra de "
        "desempate explícita do código"
    )


# ---------------------------------------------------------------------------
# coletar_amostra
# ---------------------------------------------------------------------------


@patch("src.queries.rq_bonus_concentracao.run_query")
def test_coletar_amostra__autor_nulo_misturado_bate_com_calculo_direto(mock_run_query):
    """Com autor None misturado a autores válidos, 'top_contribuidor' e
    'concentracao_top_contribuidor' devem bater com calcular_top_contribuidor
    chamada diretamente com a lista de logins equivalente (sem duplicar a lógica no teste)."""
    autores_prs = ["alice", None, "bob"]
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-exemplo", "dono-exemplo", 500, 42, autores_prs),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=1)

    top_esperado, concentracao_esperada = calcular_top_contribuidor(autores_prs)

    assert len(resultado) == 1, "Deveria retornar exatamente uma linha para um repositório"
    assert resultado[0]["repositorio"] == "dono-exemplo/repo-exemplo", (
        "O campo 'repositorio' deve combinar owner/login e name"
    )
    assert resultado[0]["estrelas"] == 500, "O campo 'estrelas' deve refletir stargazerCount"
    assert resultado[0]["total_prs_aceitas"] == 42, (
        "O campo 'total_prs_aceitas' deve refletir pullRequests.totalCount"
    )
    assert resultado[0]["top_contribuidor"] == top_esperado, (
        "'top_contribuidor' deve bater com o resultado de calcular_top_contribuidor "
        "chamada com a mesma lista de logins extraída das PRs"
    )
    assert resultado[0]["concentracao_top_contribuidor"] == concentracao_esperada, (
        "'concentracao_top_contribuidor' deve bater com o resultado de calcular_top_contribuidor "
        "chamada com a mesma lista de logins extraída das PRs"
    )


@patch("src.queries.rq_bonus_concentracao.run_query")
def test_coletar_amostra__multiplos_repositorios_calculados_independentemente(mock_run_query):
    """Payload com múltiplos repositórios deve gerar uma linha por repositório,
    cada um calculado a partir apenas das próprias PRs, sem vazamento de estado
    entre repositórios (ex: reaproveitar o mesmo Counter por engano)."""
    autores_repo_um = ["alice", "alice", "bob"]
    autores_repo_dois = ["carol", "dave", "dave", "dave"]
    mock_run_query.return_value = {
        "search": {
            "nodes": [
                _repositorio("repo-um", "dono-um", 1000, 10, autores_repo_um),
                _repositorio("repo-dois", "dono-dois", 50, 20, autores_repo_dois),
            ]
        }
    }

    resultado = coletar_amostra(quantidade=2)

    assert len(resultado) == 2, "Deveria retornar uma linha para cada repositório presente no payload"

    top_um, concentracao_um = calcular_top_contribuidor(autores_repo_um)
    top_dois, concentracao_dois = calcular_top_contribuidor(autores_repo_dois)

    assert resultado[0]["repositorio"] == "dono-um/repo-um"
    assert resultado[0]["top_contribuidor"] == top_um == "alice", (
        "Repositório 'repo-um' deve ter 'alice' como top contribuidor, sem interferência do outro repositório"
    )
    assert resultado[0]["concentracao_top_contribuidor"] == concentracao_um

    assert resultado[1]["repositorio"] == "dono-dois/repo-dois"
    assert resultado[1]["top_contribuidor"] == top_dois == "dave", (
        "Repositório 'repo-dois' deve ter 'dave' como top contribuidor, sem herdar a contagem do 'repo-um'"
    )
    assert resultado[1]["concentracao_top_contribuidor"] == concentracao_dois
