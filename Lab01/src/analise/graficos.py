from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

CAMINHO_CSV_PADRAO = Path(__file__).resolve().parent.parent.parent / "data" / "dataset" / "coleta_1000.csv"
PASTA_SAIDA_PADRAO = Path(__file__).resolve().parent.parent.parent / "docs" / "images" / "graficos"

TOP_N_LINGUAGENS = 8

COR_PRINCIPAL = "#1f77b4"
COR_SECUNDARIA = "#ff7f0e"


def carregar_dataset(caminho_csv: Path = CAMINHO_CSV_PADRAO) -> pd.DataFrame:
    """Carrega o dataset consolidado, convertendo as colunas booleanas ('True'/'False' em texto)."""
    df = pd.read_csv(caminho_csv)
    for coluna in ("arquivado", "discussions_habilitado", "possui_funding"):
        df[coluna] = df[coluna].astype(str) == "True"
    return df


def _salvar(fig: plt.Figure, caminho_saida: Path) -> Path:
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=150)
    plt.close(fig)
    return caminho_saida


def _grafico_histograma(df: pd.DataFrame, coluna: str, titulo: str, rotulo_x: str, caminho_saida: Path) -> Path:
    """Histograma de uma métrica numérica, com a mediana marcada (medida central adequada a distribuições assimétricas)."""
    mediana = df[coluna].median()
    fig, eixo = plt.subplots(figsize=(8, 5))
    eixo.hist(df[coluna], bins=30, color=COR_PRINCIPAL, edgecolor="white")
    eixo.axvline(mediana, color=COR_SECUNDARIA, linestyle="--", linewidth=2, label=f"Mediana = {mediana:.2f}")
    eixo.set_title(titulo)
    eixo.set_xlabel(rotulo_x)
    eixo.set_ylabel("Número de repositórios")
    eixo.legend()
    return _salvar(fig, caminho_saida)


def _grafico_proporcao(df: pd.DataFrame, coluna: str, titulo: str, rotulo_categoria_true: str, rotulo_categoria_false: str, caminho_saida: Path) -> Path:
    """Barra única 100% empilhada para uma métrica booleana."""
    percentual_true = 100 * df[coluna].mean()
    percentual_false = 100 - percentual_true

    fig, eixo = plt.subplots(figsize=(8, 2.5))
    eixo.barh(["Repositórios"], [percentual_true], color=COR_PRINCIPAL, label=f"{rotulo_categoria_true} ({percentual_true:.1f}%)")
    eixo.barh(["Repositórios"], [percentual_false], left=[percentual_true], color="#c7c7c7", label=f"{rotulo_categoria_false} ({percentual_false:.1f}%)")
    eixo.set_xlim(0, 100)
    eixo.set_xlabel("% de repositórios")
    eixo.set_title(titulo)
    eixo.legend(loc="upper center", bbox_to_anchor=(0.5, -0.4), ncol=2)
    return _salvar(fig, caminho_saida)


def rq01_idade(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ01 — Sistemas populares são maduros/antigos? Distribuição da idade dos repositórios."""
    return _grafico_histograma(
        df, "idade_anos",
        "RQ01 — Distribuição da idade dos repositórios populares",
        "Idade (anos)",
        pasta_saida / "rq01.png",
    )


def rq02_contribuicao_externa(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ02 — Sistemas populares recebem muita contribuição externa? Distribuição de PRs aceitas."""
    return _grafico_histograma(
        df, "total_prs_aceitas",
        "RQ02 — Distribuição de pull requests aceitas (contribuição externa)",
        "Total de PRs aceitas",
        pasta_saida / "rq02.png",
    )


def rq03_releases(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ03 — Sistemas populares lançam releases com frequência? Distribuição do total de releases."""
    return _grafico_histograma(
        df, "total_releases",
        "RQ03 — Distribuição do total de releases lançadas",
        "Total de releases",
        pasta_saida / "rq03.png",
    )


def rq04_atualizacao(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ04 — Sistemas populares são atualizados com frequência? Distribuição de dias desde a última atualização."""
    return _grafico_histograma(
        df, "dias_desde_atualizacao",
        "RQ04 — Dias desde a última atualização (quanto menor, mais recente)",
        "Dias desde a última atualização",
        pasta_saida / "rq04.png",
    )


def rq05_linguagens(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ05 — Sistemas populares estão nas linguagens mais populares (TIOBE)? Ranking das linguagens primárias mais frequentes."""
    contagem = df["linguagem_primaria"].value_counts().head(TOP_N_LINGUAGENS).sort_values()

    fig, eixo = plt.subplots(figsize=(8, 5))
    eixo.barh(contagem.index, contagem.values, color=COR_PRINCIPAL)
    eixo.set_title(f"RQ05 — Top {TOP_N_LINGUAGENS} linguagens primárias entre os repositórios populares")
    eixo.set_xlabel("Número de repositórios")
    eixo.set_ylabel("Linguagem primária")
    return _salvar(fig, pasta_saida / "rq05.png")


def rq06_issues_fechadas(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ06 — Sistemas populares possuem alto percentual de issues fechadas? Distribuição da razão de issues fechadas."""
    df_com_issues = df[df["issues_total"] > 0].copy()
    df_com_issues["razao_issues_fechadas_pct"] = df_com_issues["razao_issues_fechadas"] * 100
    return _grafico_histograma(
        df_com_issues, "razao_issues_fechadas_pct",
        "RQ06 — Distribuição do percentual de issues fechadas",
        "% de issues fechadas",
        pasta_saida / "rq06.png",
    )


def rq07_cruzamento_por_linguagem(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ07 — Linguagens mais populares recebem mais contribuição, releases e atualização mais frequente?

    Três painéis lado a lado (um por métrica) com a mediana de PRs aceitas, releases e dias
    desde atualização por linguagem primária (top linguagens por número de repositórios) —
    escalas independentes, já que PRs/releases (centenas a milhares) e dias sem atualizar
    (dezenas) não são comparáveis numa mesma escala.
    """
    linguagens_top = df["linguagem_primaria"].value_counts().head(TOP_N_LINGUAGENS).index
    agrupado = (
        df[df["linguagem_primaria"].isin(linguagens_top)]
        .groupby("linguagem_primaria")[["total_prs_aceitas", "total_releases", "dias_desde_atualizacao"]]
        .median()
        .loc[linguagens_top]
    )

    paineis = [
        ("total_prs_aceitas", "Mediana de PRs aceitas", "#1f77b4"),
        ("total_releases", "Mediana de releases", "#2ca02c"),
        ("dias_desde_atualizacao", "Mediana de dias s/ atualizar", "#d62728"),
    ]

    fig, eixos = plt.subplots(1, 3, figsize=(14, 5))
    for eixo, (metrica, titulo, cor) in zip(eixos, paineis):
        eixo.bar(agrupado.index, agrupado[metrica], color=cor)
        eixo.set_title(titulo, fontsize=10)
        eixo.set_xticks(range(len(agrupado.index)))
        eixo.set_xticklabels(agrupado.index, rotation=45, ha="right", fontsize=8)

    fig.suptitle(f"RQ07 — Mediana de PRs, releases e dias s/ atualizar por linguagem (top {TOP_N_LINGUAGENS})")
    return _salvar(fig, pasta_saida / "rq07.png")


def rq08_arquivados(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ08 — Sistemas populares raramente são arquivados/descontinuados? Proporção de repositórios arquivados."""
    return _grafico_proporcao(
        df, "arquivado",
        "RQ08 — Proporção de repositórios arquivados",
        "Arquivado", "Não arquivado",
        pasta_saida / "rq08.png",
    )


def rq09_branch_padrao(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ09 — Sistemas populares já adotam 'main' como branch padrão? Proporção de branch padrão 'main'."""
    df_branch = df.copy()
    df_branch["branch_main"] = df_branch["branch_padrao"] == "main"
    return _grafico_proporcao(
        df_branch, "branch_main",
        "RQ09 — Proporção de repositórios com branch padrão 'main'",
        "main", "Outra (master/outra)",
        pasta_saida / "rq09.png",
    )


def rq10_discussions(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ10 — Sistemas populares adotam GitHub Discussions? Proporção de repositórios com Discussions habilitado."""
    return _grafico_proporcao(
        df, "discussions_habilitado",
        "RQ10 — Proporção de repositórios com GitHub Discussions habilitado",
        "Habilitado", "Não habilitado",
        pasta_saida / "rq10.png",
    )


def rq11_funding(df: pd.DataFrame, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> Path:
    """RQ11 — Sistemas populares recebem apoio financeiro direto (funding)? Proporção de repositórios com funding configurado."""
    return _grafico_proporcao(
        df, "possui_funding",
        "RQ11 — Proporção de repositórios com funding configurado",
        "Com funding", "Sem funding",
        pasta_saida / "rq11.png",
    )


GERADORES_POR_RQ = [
    rq01_idade,
    rq02_contribuicao_externa,
    rq03_releases,
    rq04_atualizacao,
    rq05_linguagens,
    rq06_issues_fechadas,
    rq07_cruzamento_por_linguagem,
    rq08_arquivados,
    rq09_branch_padrao,
    rq10_discussions,
    rq11_funding,
]


def gerar_todos(caminho_csv: Path = CAMINHO_CSV_PADRAO, pasta_saida: Path = PASTA_SAIDA_PADRAO) -> list[Path]:
    """Gera os 11 gráficos (RQ01–RQ11) a partir do dataset consolidado e retorna os caminhos salvos."""
    df = carregar_dataset(caminho_csv)
    return [gerador(df, pasta_saida) for gerador in GERADORES_POR_RQ]


if __name__ == "__main__":
    caminhos = gerar_todos()
    for caminho in caminhos:
        print(caminho)
    print(f"\n{len(caminhos)} gráficos salvos em {PASTA_SAIDA_PADRAO}")
