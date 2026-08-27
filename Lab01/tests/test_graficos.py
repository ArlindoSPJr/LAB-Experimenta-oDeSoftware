import pandas as pd
import pytest

from src.analise import graficos


@pytest.fixture
def df_amostra() -> pd.DataFrame:
    """DataFrame pequeno e determinístico cobrindo as colunas usadas por todos os gráficos."""
    return pd.DataFrame(
        {
            "idade_anos": [1.0, 3.5, 8.2, 12.0, 0.5],
            "total_prs_aceitas": [10, 200, 5, 730, 0],
            "total_releases": [0, 12, 3, 40, 1],
            "dias_desde_atualizacao": [0, 5, 400, 2, 100],
            "linguagem_primaria": ["Python", "Python", "TypeScript", "Go", "TypeScript"],
            "issues_total": [10, 0, 50, 20, 5],
            "razao_issues_fechadas": [0.9, 0.0, 0.5, 0.7, 1.0],
            "arquivado": [False, False, True, False, False],
            "branch_padrao": ["main", "master", "main", "main", "master"],
            "discussions_habilitado": [True, False, False, True, False],
            "possui_funding": [True, False, False, False, True],
        }
    )


@pytest.mark.parametrize(
    "gerador",
    graficos.GERADORES_POR_RQ,
    ids=[gerador.__name__ for gerador in graficos.GERADORES_POR_RQ],
)
def test_geradores__salvam_png_nao_vazio(gerador, df_amostra, tmp_path):
    """Cada gerador de gráfico (RQ01-RQ11) deve salvar um PNG não vazio no caminho esperado."""
    caminho = gerador(df_amostra, tmp_path)

    assert caminho.exists(), f"{gerador.__name__} deveria ter criado o arquivo {caminho}"
    assert caminho.suffix == ".png", "O gráfico deve ser salvo como PNG"
    assert caminho.stat().st_size > 0, "O PNG gerado não deve estar vazio"


def test_carregar_dataset__converte_colunas_booleanas_de_texto_para_bool(tmp_path):
    """As colunas booleanas gravadas como 'True'/'False' em texto devem virar bool de fato."""
    caminho_csv = tmp_path / "amostra.csv"
    caminho_csv.write_text(
        "repositorio,arquivado,discussions_habilitado,possui_funding\n"
        "dono/repo,True,False,True\n",
        encoding="utf-8",
    )

    df = graficos.carregar_dataset(caminho_csv)

    assert df["arquivado"].dtype == bool, "arquivado deve ser convertida para bool"
    assert df["discussions_habilitado"].tolist() == [False], "'False' em texto deve virar bool False"
    assert df["possui_funding"].tolist() == [True], "'True' em texto deve virar bool True"


def test_gerar_todos__retorna_um_caminho_por_rq(df_amostra, tmp_path, monkeypatch):
    """gerar_todos deve produzir exatamente um PNG por RQ01-RQ11, todos existentes."""
    caminho_csv = tmp_path / "dataset.csv"
    df_amostra.assign(
        linguagem_primaria=df_amostra["linguagem_primaria"],
    ).to_csv(caminho_csv, index=False)

    caminhos = graficos.gerar_todos(caminho_csv, tmp_path / "saida")

    assert len(caminhos) == len(graficos.GERADORES_POR_RQ), "Deve haver um caminho por gerador de RQ"
    assert all(caminho.exists() for caminho in caminhos), "Todos os PNGs retornados devem existir em disco"
