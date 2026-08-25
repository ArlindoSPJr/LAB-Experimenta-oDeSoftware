from unittest.mock import patch

import pytest

from src.github_client import GitHubGraphQLError
from src.snapshot_projeto import exportar_snapshot, montar_query_snapshot


# ---------------------------------------------------------------------------
# montar_query_snapshot
# ---------------------------------------------------------------------------


def test_montar_query_snapshot__tipo_dono_user_usa_campo_user():
    """Para tipo_dono='user' a query deve consultar o campo raiz 'user(login:' e não 'organization(login:'."""
    query = montar_query_snapshot("user")

    assert "user(login:" in query, "A query deve conter o campo raiz 'user(login:' para dono do tipo usuário"
    assert "organization(login:" not in query, "A query não deve conter o campo raiz 'organization(login:' quando o dono é um usuário"


def test_montar_query_snapshot__tipo_dono_organization_usa_campo_organization():
    """Para tipo_dono='organization' a query deve consultar o campo raiz 'organization(login:'."""
    query = montar_query_snapshot("organization")

    assert "organization(login:" in query, "A query deve conter o campo raiz 'organization(login:' para dono do tipo organização"


# ---------------------------------------------------------------------------
# exportar_snapshot - validação de variáveis de ambiente
# ---------------------------------------------------------------------------


def test_exportar_snapshot__dono_projeto_ausente_levanta_erro(monkeypatch):
    """Sem GITHUB_PROJECT_OWNER definido, exportar_snapshot deve levantar GitHubGraphQLError."""
    monkeypatch.setattr("src.snapshot_projeto.DONO_PROJETO", None)
    monkeypatch.setattr("src.snapshot_projeto.NUMERO_PROJETO", 1)

    with pytest.raises(GitHubGraphQLError) as excinfo:
        exportar_snapshot()

    mensagem = str(excinfo.value)
    assert "GITHUB_PROJECT_OWNER" in mensagem, "A mensagem de erro deve mencionar a variável GITHUB_PROJECT_OWNER"
    assert "GITHUB_PROJECT_NUMBER" in mensagem, "A mensagem de erro deve mencionar a variável GITHUB_PROJECT_NUMBER"


def test_exportar_snapshot__numero_projeto_zero_levanta_erro(monkeypatch):
    """Com NUMERO_PROJETO=0 (falsy) e DONO_PROJETO válido, exportar_snapshot deve levantar GitHubGraphQLError."""
    monkeypatch.setattr("src.snapshot_projeto.DONO_PROJETO", "dono-fake")
    monkeypatch.setattr("src.snapshot_projeto.NUMERO_PROJETO", 0)

    with pytest.raises(GitHubGraphQLError):
        exportar_snapshot()


# ---------------------------------------------------------------------------
# exportar_snapshot - coleta e transformação dos itens
# ---------------------------------------------------------------------------


def _pagina_exemplo(hasNextPage=False, endCursor=None, nodes=None):
    return {
        "user": {
            "projectV2": {
                "items": {
                    "pageInfo": {"hasNextPage": hasNextPage, "endCursor": endCursor},
                    "nodes": nodes if nodes is not None else [],
                }
            }
        }
    }


@pytest.fixture(autouse=True)
def _dono_e_numero_validos(monkeypatch):
    """Garante DONO_PROJETO/NUMERO_PROJETO válidos em todos os testes de coleta deste módulo."""
    monkeypatch.setattr("src.snapshot_projeto.DONO_PROJETO", "dono-fake")
    monkeypatch.setattr("src.snapshot_projeto.NUMERO_PROJETO", 1)
    monkeypatch.setattr("src.snapshot_projeto.TIPO_DONO_PROJETO", "user")


def test_exportar_snapshot__item_draft_sem_conteudo_e_pulado():
    """Um item do Project sem 'content' (draft issue) deve ser ignorado, sem quebrar a coleta."""
    nodes = [
        {
            "fieldValueByName": {"name": "Em andamento"},
            "content": {
                "number": 12,
                "title": "Implementar RQ01",
                "url": "https://github.com/owner/repo/issues/12",
                "assignees": {"nodes": [{"login": "alice"}, {"login": "bob"}]},
            },
        },
        {
            "fieldValueByName": None,
            "content": None,
        },
    ]
    payload = _pagina_exemplo(nodes=nodes)

    with patch("src.snapshot_projeto.run_query", return_value=payload):
        resultado = exportar_snapshot()

    assert len(resultado) == 1, "Apenas o item com conteúdo deve ser incluído no resultado, o draft deve ser pulado"
    assert resultado[0]["numero_issue"] == 12, "O item retornado deve corresponder ao issue de número 12"


def test_exportar_snapshot__sem_field_value_by_name_status_e_sem_status():
    """Quando fieldValueByName é None, o status resultante deve ser 'Sem status'."""
    nodes = [
        {
            "fieldValueByName": None,
            "content": {
                "number": 1,
                "title": "Issue sem status",
                "url": "https://github.com/owner/repo/issues/1",
                "assignees": {"nodes": []},
            },
        }
    ]
    payload = _pagina_exemplo(nodes=nodes)

    with patch("src.snapshot_projeto.run_query", return_value=payload):
        resultado = exportar_snapshot()

    assert resultado[0]["status"] == "Sem status", "Status deve ser 'Sem status' quando fieldValueByName é None"


def test_exportar_snapshot__com_field_value_by_name_status_e_o_nome_do_valor():
    """Quando fieldValueByName está presente, o status resultante deve ser o nome informado."""
    nodes = [
        {
            "fieldValueByName": {"name": "Em andamento"},
            "content": {
                "number": 2,
                "title": "Issue em andamento",
                "url": "https://github.com/owner/repo/issues/2",
                "assignees": {"nodes": []},
            },
        }
    ]
    payload = _pagina_exemplo(nodes=nodes)

    with patch("src.snapshot_projeto.run_query", return_value=payload):
        resultado = exportar_snapshot()

    assert resultado[0]["status"] == "Em andamento", "Status deve refletir o nome retornado em fieldValueByName"


def test_exportar_snapshot__multiplos_assignees_sao_unidos_com_ponto_e_virgula():
    """Múltiplos assignees devem ser concatenados em uma string única separada por ';'."""
    nodes = [
        {
            "fieldValueByName": {"name": "A fazer"},
            "content": {
                "number": 3,
                "title": "Issue com múltiplos responsáveis",
                "url": "https://github.com/owner/repo/issues/3",
                "assignees": {"nodes": [{"login": "alice"}, {"login": "bob"}]},
            },
        }
    ]
    payload = _pagina_exemplo(nodes=nodes)

    with patch("src.snapshot_projeto.run_query", return_value=payload):
        resultado = exportar_snapshot()

    assert resultado[0]["responsaveis"] == "alice;bob", "Os responsáveis devem ser unidos com ';' na ordem retornada pela API"


def test_exportar_snapshot__pagina_multiplas_paginas_e_ordena_por_numero_issue():
    """Com paginação em 2 páginas, o resultado final deve conter os itens de ambas, ordenados por numero_issue."""
    primeira_pagina = _pagina_exemplo(
        hasNextPage=True,
        endCursor="cursor-x",
        nodes=[
            {
                "fieldValueByName": {"name": "Em andamento"},
                "content": {
                    "number": 20,
                    "title": "Issue 20",
                    "url": "https://github.com/owner/repo/issues/20",
                    "assignees": {"nodes": []},
                },
            }
        ],
    )
    segunda_pagina = _pagina_exemplo(
        hasNextPage=False,
        endCursor=None,
        nodes=[
            {
                "fieldValueByName": {"name": "Concluído"},
                "content": {
                    "number": 5,
                    "title": "Issue 5",
                    "url": "https://github.com/owner/repo/issues/5",
                    "assignees": {"nodes": []},
                },
            }
        ],
    )

    with patch("src.snapshot_projeto.run_query", side_effect=[primeira_pagina, segunda_pagina]) as mock_run_query:
        resultado = exportar_snapshot()

    assert mock_run_query.call_count == 2, "run_query deve ser chamado uma vez por página"
    assert [linha["numero_issue"] for linha in resultado] == [5, 20], (
        "O resultado final deve estar ordenado por numero_issue, mesmo que o item 5 tenha vindo na 2ª página"
    )
