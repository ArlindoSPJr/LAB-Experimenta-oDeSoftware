from unittest.mock import patch

from src.github_client import GitHubGraphQLError
from src.queries.consolidada import (
    ESPERA_BASE_SEGUNDOS,
    TAMANHO_PAGINA_INICIAL,
    TAMANHO_PAGINA_MINIMO,
    TENTATIVAS_POR_OFFSET,
    _buscar_pagina_com_retry,
    coletar,
    montar_query_busca,
)


def _repo(
    nome="repo-exemplo",
    dono="dono-exemplo",
    estrelas=500,
    forks=20,
    criado="2020-01-01T00:00:00Z",
    atualizado="2023-06-01T00:00:00Z",
    linguagem={"name": "Python"},
    licenca={"name": "MIT License"},
    arquivado=False,
    autores_prs=("alice",),
    total_prs=10,
    releases=3,
    issues_fechadas=5,
    issues_total=10,
):
    """Monta um node de repositório no formato retornado pela query consolidada."""
    return {
        "name": nome,
        "owner": {"login": dono},
        "stargazerCount": estrelas,
        "forkCount": forks,
        "createdAt": criado,
        "updatedAt": atualizado,
        "primaryLanguage": linguagem,
        "licenseInfo": licenca,
        "isArchived": arquivado,
        "pullRequests": {
            "totalCount": total_prs,
            "nodes": [{"author": {"login": autor} if autor else None} for autor in autores_prs],
        },
        "releases": {"totalCount": releases},
        "issuesFechadas": {"totalCount": issues_fechadas},
        "issuesTotal": {"totalCount": issues_total},
    }


def _pagina(repos, has_next=False, end_cursor=None):
    """Monta o payload completo de uma página de busca."""
    return {"search": {"pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor}, "nodes": repos}}


# ---------------------------------------------------------------------------
# _buscar_pagina_com_retry
# ---------------------------------------------------------------------------


def test_buscar_pagina_com_retry__sucesso_na_primeira_tentativa():
    """Quando run_query tem sucesso de primeira, deve retornar os dados sem retry nem sleep."""
    dados_sucesso = _pagina([_repo()])

    with patch("src.queries.consolidada.run_query", return_value=dados_sucesso) as mock_run_query, patch(
        "src.queries.consolidada.time.sleep"
    ) as mock_sleep:
        dados, tamanho_final = _buscar_pagina_com_retry(cursor=None, tamanho_pagina=20, token="fake")

    assert dados == dados_sucesso, "Os dados retornados devem ser os mesmos produzidos por run_query"
    assert tamanho_final == 20, "O tamanho de página não deve mudar quando a primeira tentativa já tem sucesso"
    assert mock_run_query.call_count == 1, "run_query deve ser chamado apenas uma vez em caso de sucesso imediato"
    mock_sleep.assert_not_called()


def test_buscar_pagina_com_retry__um_502_seguido_de_sucesso_reduz_pagina_pela_metade():
    """Um 502 na 1ª tentativa deve acionar retry com tamanho de página reduzido à metade."""
    dados_sucesso = _pagina([_repo()])
    erro_502 = GitHubGraphQLError("HTTP 502: Bad Gateway")

    with patch(
        "src.queries.consolidada.run_query", side_effect=[erro_502, dados_sucesso]
    ) as mock_run_query, patch("src.queries.consolidada.time.sleep") as mock_sleep:
        dados, tamanho_final = _buscar_pagina_com_retry(cursor=None, tamanho_pagina=20, token="fake")

    assert dados == dados_sucesso, "Após o retry, os dados retornados devem ser os da chamada bem-sucedida"
    assert tamanho_final == 10, "O tamanho de página deve ser reduzido pela metade (20 // 2 = 10) após um 502"
    assert mock_run_query.call_count == 2, "run_query deve ser chamado duas vezes: a que falhou e a que teve sucesso"
    mock_sleep.assert_called_once_with(ESPERA_BASE_SEGUNDOS * 1)


def test_buscar_pagina_com_retry__502_persistente_no_piso_relevanta_erro():
    """Se todas as tentativas falham com 502 e o tamanho já está no piso mínimo, o erro deve ser relevantado."""
    erro_502 = GitHubGraphQLError("HTTP 502: Bad Gateway")

    with patch(
        "src.queries.consolidada.run_query", side_effect=[erro_502] * TENTATIVAS_POR_OFFSET
    ) as mock_run_query, patch("src.queries.consolidada.time.sleep"):
        try:
            _buscar_pagina_com_retry(cursor=None, tamanho_pagina=TAMANHO_PAGINA_MINIMO, token="fake")
            assert False, "Deveria ter relevantado GitHubGraphQLError ao esgotar tentativas no piso mínimo"
        except GitHubGraphQLError:
            pass

    assert mock_run_query.call_count == TENTATIVAS_POR_OFFSET, (
        "run_query deve ser chamado exatamente TENTATIVAS_POR_OFFSET vezes antes de desistir"
    )


def test_buscar_pagina_com_retry__erro_nao_502_relevanta_imediatamente():
    """Um erro que não seja 502 (ex: 401) deve ser relevantado de imediato, sem nenhuma tentativa de retry."""
    erro_401 = GitHubGraphQLError("HTTP 401: Bad credentials")

    with patch("src.queries.consolidada.run_query", side_effect=erro_401) as mock_run_query, patch(
        "src.queries.consolidada.time.sleep"
    ) as mock_sleep:
        try:
            _buscar_pagina_com_retry(cursor=None, tamanho_pagina=20, token="fake")
            assert False, "Deveria ter relevantado o erro 401 imediatamente"
        except GitHubGraphQLError as erro:
            assert "401" in str(erro), "O erro relevantado deve ser o mesmo erro 401 original"

    assert mock_run_query.call_count == 1, "run_query não deve ser chamado novamente para erros que não são 502"
    mock_sleep.assert_not_called()


def test_buscar_pagina_com_retry__backoff_crescente_entre_tentativas():
    """Duas falhas 502 seguidas de sucesso devem produzir sleeps com backoff crescente (base*1, base*2)."""
    dados_sucesso = _pagina([_repo()])
    erro_502 = GitHubGraphQLError("HTTP 502: Bad Gateway")

    with patch(
        "src.queries.consolidada.run_query", side_effect=[erro_502, erro_502, dados_sucesso]
    ) as mock_run_query, patch("src.queries.consolidada.time.sleep") as mock_sleep:
        dados, tamanho_final = _buscar_pagina_com_retry(cursor=None, tamanho_pagina=25, token="fake")

    assert dados == dados_sucesso, "Deve retornar os dados da chamada bem-sucedida (3ª tentativa)"
    assert mock_run_query.call_count == 3, "run_query deve ser chamado 3 vezes: 2 falhas + 1 sucesso"
    assert mock_sleep.call_count == 2, "time.sleep deve ser chamado 2 vezes, uma para cada falha 502"

    primeira_chamada = mock_sleep.call_args_list[0]
    segunda_chamada = mock_sleep.call_args_list[1]
    assert primeira_chamada.args[0] == ESPERA_BASE_SEGUNDOS * 1, (
        "O primeiro sleep deve usar backoff de ESPERA_BASE_SEGUNDOS * 1"
    )
    assert segunda_chamada.args[0] == ESPERA_BASE_SEGUNDOS * 2, (
        "O segundo sleep deve usar backoff de ESPERA_BASE_SEGUNDOS * 2 (crescente)"
    )


# ---------------------------------------------------------------------------
# coletar (paginação)
# ---------------------------------------------------------------------------


def test_coletar__duas_paginas_concatena_repositorios_e_usa_cursor_na_segunda_chamada():
    """coletar deve seguir o cursor entre páginas e concatenar os repositórios de ambas."""
    repo1 = _repo(nome="repo-um", dono="dono-um")
    repo2 = _repo(nome="repo-dois", dono="dono-dois")
    pagina1 = _pagina([repo1], has_next=True, end_cursor="cursor1")
    pagina2 = _pagina([repo2], has_next=False)

    with patch(
        "src.queries.consolidada.run_query", side_effect=[pagina1, pagina2]
    ) as mock_run_query, patch("src.queries.consolidada.time.sleep"):
        resultado = coletar(quantidade=2)

    assert len(resultado) == 2, "O resultado deve conter os 2 repositórios vindos das duas páginas"
    assert resultado[0]["repositorio"] == "dono-um/repo-um", "O primeiro repositório deve ser o da 1ª página"
    assert resultado[1]["repositorio"] == "dono-dois/repo-dois", "O segundo repositório deve ser o da 2ª página"

    variaveis_segunda_chamada = mock_run_query.call_args_list[1][0][1]
    assert variaveis_segunda_chamada["cursor"] == "cursor1", (
        "A segunda chamada a run_query deve usar o endCursor retornado pela primeira página"
    )


def test_coletar__quantidade_um_para_o_loop_apos_uma_pagina_e_pede_tamanho_correto():
    """Ao pedir quantidade=1, o loop deve parar após 1 repositório e pedir apenas o necessário na 1ª chamada."""
    repo1 = _repo(nome="repo-unico", dono="dono-unico")
    pagina1 = _pagina([repo1], has_next=False)

    with patch("src.queries.consolidada.run_query", return_value=pagina1) as mock_run_query, patch(
        "src.queries.consolidada.time.sleep"
    ):
        resultado = coletar(quantidade=1)

    assert len(resultado) == 1, "O resultado deve conter exatamente 1 repositório"
    assert mock_run_query.call_count == 1, "Apenas uma chamada a run_query deve ser necessária"

    variaveis = mock_run_query.call_args_list[0][0][1]
    esperado = min(TAMANHO_PAGINA_INICIAL, 1)
    assert variaveis["quantidade"] == esperado, (
        "A quantidade pedida na primeira chamada deve ser min(TAMANHO_PAGINA_INICIAL, quantidade)"
    )


def test_coletar__linha_resultante_possui_todas_as_chaves_e_valores_corretos():
    """Cada linha do resultado de coletar deve conter todas as chaves esperadas, com N/A para campos ausentes."""
    repo_completo = _repo(
        nome="repo-completo",
        dono="dono-completo",
        estrelas=999,
        forks=42,
        criado="2020-01-01T00:00:00Z",
        atualizado="2023-06-01T00:00:00Z",
        linguagem={"name": "Python"},
        licenca={"name": "MIT License"},
        arquivado=False,
        autores_prs=("alice", "alice", "bob"),
        total_prs=15,
        releases=4,
        issues_fechadas=8,
        issues_total=10,
    )
    repo_sem_linguagem_licenca = _repo(
        nome="repo-sem-meta",
        dono="dono-sem-meta",
        linguagem=None,
        licenca=None,
        arquivado=True,
        autores_prs=(),
        issues_fechadas=0,
        issues_total=0,
    )
    pagina_unica = _pagina([repo_completo, repo_sem_linguagem_licenca], has_next=False)

    with patch("src.queries.consolidada.run_query", return_value=pagina_unica), patch(
        "src.queries.consolidada.time.sleep"
    ):
        resultado = coletar(quantidade=2)

    chaves_esperadas = {
        "repositorio",
        "estrelas",
        "total_forks",
        "data_criacao",
        "idade_anos",
        "total_prs_aceitas",
        "total_releases",
        "ultima_atualizacao",
        "dias_desde_atualizacao",
        "linguagem_primaria",
        "licenca",
        "arquivado",
        "issues_fechadas",
        "issues_total",
        "razao_issues_fechadas",
        "top_contribuidor",
        "concentracao_top_contribuidor",
    }

    linha_completa = resultado[0]
    linha_sem_meta = resultado[1]

    assert set(linha_completa.keys()) == chaves_esperadas, "A linha deve conter exatamente as chaves esperadas"
    assert linha_completa["repositorio"] == "dono-completo/repo-completo"
    assert linha_completa["estrelas"] == 999
    assert linha_completa["total_forks"] == 42
    assert linha_completa["data_criacao"] == "2020-01-01T00:00:00Z"
    assert linha_completa["total_prs_aceitas"] == 15
    assert linha_completa["total_releases"] == 4
    assert linha_completa["ultima_atualizacao"] == "2023-06-01T00:00:00Z"
    assert linha_completa["linguagem_primaria"] == "Python", "Quando primaryLanguage existe, deve usar o nome real"
    assert linha_completa["licenca"] == "MIT License", "Quando licenseInfo existe, deve usar o nome real"
    assert linha_completa["arquivado"] is False
    assert linha_completa["issues_fechadas"] == 8
    assert linha_completa["issues_total"] == 10
    assert linha_completa["razao_issues_fechadas"] == round(8 / 10, 4)
    assert linha_completa["top_contribuidor"] == "alice", "alice aparece 2x contra 1x de bob, deve ser o top"
    assert linha_completa["concentracao_top_contribuidor"] == round(2 / 3, 4)

    assert linha_sem_meta["linguagem_primaria"] == "N/A", "primaryLanguage=None deve resultar em 'N/A'"
    assert linha_sem_meta["licenca"] == "N/A", "licenseInfo=None deve resultar em 'N/A'"
    assert linha_sem_meta["arquivado"] is True
    assert linha_sem_meta["top_contribuidor"] == "N/A", "Sem PRs com autor, o top contribuidor deve ser 'N/A'"
    assert linha_sem_meta["concentracao_top_contribuidor"] == 0.0
    assert linha_sem_meta["razao_issues_fechadas"] == 0.0, "Quando issues_total=0, a razão deve ser 0.0"


# ---------------------------------------------------------------------------
# montar_query_busca
# ---------------------------------------------------------------------------


def test_montar_query_busca__contem_campos_essenciais_da_query_consolidada():
    """A query montada deve conter os campos de pullRequests, releases, issuesFechadas e issuesTotal."""
    query = montar_query_busca()

    assert "pullRequests" in query, "A query deve solicitar o campo pullRequests"
    assert "releases" in query, "A query deve solicitar o campo releases"
    assert "issuesFechadas" in query, "A query deve solicitar o alias issuesFechadas"
    assert "issuesTotal" in query, "A query deve solicitar o alias issuesTotal"
