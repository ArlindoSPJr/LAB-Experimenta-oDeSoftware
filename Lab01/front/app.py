"""Dashboard Streamlit dos 1000 repositórios mais populares do GitHub (Lab01)."""

import math
from pathlib import Path

import pandas as pd
import streamlit as st

CAMINHO_CSV = Path(__file__).resolve().parent.parent / "data" / "dataset" / "coleta_1000.csv"

COLUNAS_TABELA = {
    "repositorio": "Repositório",
    "linguagem_primaria": "Linguagem",
    "licenca": "Licença",
    "estrelas": "Estrelas",
    "total_forks": "Forks",
    "idade_anos": "Idade (anos)",
    "total_prs_aceitas": "PRs aceitas",
    "total_releases": "Releases",
    "dias_desde_atualizacao": "Dias s/ atualizar",
    "issues_fechadas": "Issues fechadas",
    "issues_total": "Issues totais",
    "razao_issues_fechadas_pct": "% issues fechadas",
    "top_contribuidor": "Top contribuidor",
    "concentracao_top_contribuidor_pct": "% PRs do top contrib.",
}

st.set_page_config(
    page_title="Repositórios Populares — GitHub",
    page_icon="⭐",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background: rgba(127, 127, 127, 0.08);
        border: 1px solid rgba(127, 127, 127, 0.18);
        border-radius: 12px;
        padding: 0.9rem 1rem 0.6rem 1rem;
    }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
    h1 { font-weight: 700; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def carregar_dados(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df["data_criacao"] = pd.to_datetime(df["data_criacao"], utc=True)
    df["ultima_atualizacao"] = pd.to_datetime(df["ultima_atualizacao"], utc=True)
    df["licenca"] = df["licenca"].fillna("N/A")
    df["linguagem_primaria"] = df["linguagem_primaria"].fillna("N/A")
    df["razao_issues_fechadas_pct"] = df["razao_issues_fechadas"] * 100
    df["concentracao_top_contribuidor_pct"] = df["concentracao_top_contribuidor"] * 100
    return df


if not CAMINHO_CSV.exists():
    st.error(f"Dataset não encontrado em `{CAMINHO_CSV}`. Rode a coleta antes: `python -m src.queries.consolidada`.")
    st.stop()

df = carregar_dados(CAMINHO_CSV)

st.title("⭐ Repositórios Populares do GitHub")
st.caption(
    f"Lab01 — Laboratório de Experimentação de Software · dataset com **{len(df):,}** repositórios "
    "(mais estrelas), campos das RQ01–06 + métricas bônus.".replace(",", ".")
)

# --------------------------------------------------------------------------
# Sidebar — filtros
# --------------------------------------------------------------------------
st.sidebar.header("Filtros")

busca_nome = st.sidebar.text_input("Buscar repositório", placeholder="ex.: facebook/react")

linguagens_disponiveis = sorted(df["linguagem_primaria"].unique())
linguagens_selecionadas = st.sidebar.multiselect("Linguagem primária", linguagens_disponiveis)

licencas_disponiveis = sorted(df["licenca"].unique())
licencas_selecionadas = st.sidebar.multiselect("Licença", licencas_disponiveis)

estrelas_min, estrelas_max = int(df["estrelas"].min()), int(df["estrelas"].max())
faixa_estrelas = st.sidebar.slider(
    "Faixa de estrelas", min_value=estrelas_min, max_value=estrelas_max,
    value=(estrelas_min, estrelas_max),
)

idade_min, idade_max = float(df["idade_anos"].min()), float(df["idade_anos"].max())
faixa_idade = st.sidebar.slider(
    "Idade (anos)", min_value=idade_min, max_value=idade_max,
    value=(idade_min, idade_max),
)

st.sidebar.divider()
ordenar_por = st.sidebar.selectbox(
    "Ordenar por", options=list(COLUNAS_TABELA.keys()),
    format_func=lambda c: COLUNAS_TABELA[c], index=3,
)
ordem_decrescente = st.sidebar.toggle("Decrescente", value=True)

# --------------------------------------------------------------------------
# Aplicar filtros
# --------------------------------------------------------------------------
filtrado = df.copy()

if busca_nome:
    filtrado = filtrado[filtrado["repositorio"].str.contains(busca_nome, case=False, na=False)]
if linguagens_selecionadas:
    filtrado = filtrado[filtrado["linguagem_primaria"].isin(linguagens_selecionadas)]
if licencas_selecionadas:
    filtrado = filtrado[filtrado["licenca"].isin(licencas_selecionadas)]

filtrado = filtrado[
    filtrado["estrelas"].between(*faixa_estrelas)
    & filtrado["idade_anos"].between(*faixa_idade)
]
filtrado = filtrado.sort_values(ordenar_por, ascending=not ordem_decrescente)

# --------------------------------------------------------------------------
# Métricas gerais (sobre o resultado filtrado)
# --------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Repositórios", f"{len(filtrado):,}".replace(",", "."))
col2.metric("Estrelas (mediana)", f"{filtrado['estrelas'].median():,.0f}".replace(",", "."))
col3.metric("Idade média", f"{filtrado['idade_anos'].mean():.1f} anos" if len(filtrado) else "—")
col4.metric("PRs aceitas (mediana)", f"{filtrado['total_prs_aceitas'].median():,.0f}".replace(",", ".") if len(filtrado) else "—")
col5.metric("% issues fechadas (média)", f"{filtrado['razao_issues_fechadas_pct'].mean():.1f}%" if len(filtrado) else "—")

st.divider()

# --------------------------------------------------------------------------
# Visão geral — gráficos
# --------------------------------------------------------------------------
graf1, graf2 = st.columns(2)

with graf1:
    st.subheader("Top 10 linguagens")
    if len(filtrado):
        top_linguagens = (
            filtrado["linguagem_primaria"].value_counts().head(10).sort_values()
        )
        st.bar_chart(top_linguagens, horizontal=True, color="#f97316")
    else:
        st.info("Nenhum repositório para o filtro atual.")

with graf2:
    st.subheader("Top 10 licenças")
    if len(filtrado):
        top_licencas = filtrado["licenca"].value_counts().head(10).sort_values()
        st.bar_chart(top_licencas, horizontal=True, color="#0ea5e9")
    else:
        st.info("Nenhum repositório para o filtro atual.")

st.divider()

# --------------------------------------------------------------------------
# Tabela paginada
# --------------------------------------------------------------------------
st.subheader("Repositórios")

topo_esq, topo_dir = st.columns([3, 1])
with topo_dir:
    tamanho_pagina = st.selectbox("Por página", options=[10, 25, 50, 100], index=1)

total_paginas = max(1, math.ceil(len(filtrado) / tamanho_pagina))

if "pagina" not in st.session_state:
    st.session_state.pagina = 1
st.session_state.pagina = min(st.session_state.pagina, total_paginas)

with topo_esq:
    st.write(f"Mostrando página **{st.session_state.pagina}** de **{total_paginas}** "
             f"({len(filtrado):,} repositórios filtrados)".replace(",", "."))

inicio = (st.session_state.pagina - 1) * tamanho_pagina
fim = inicio + tamanho_pagina
pagina_df = filtrado.iloc[inicio:fim][list(COLUNAS_TABELA.keys())].rename(columns=COLUNAS_TABELA)

st.dataframe(
    pagina_df,
    width="stretch",
    hide_index=True,
    column_config={
        "Estrelas": st.column_config.NumberColumn(format="%d ⭐"),
        "Forks": st.column_config.NumberColumn(format="%d"),
        "% issues fechadas": st.column_config.NumberColumn(format="%.2f%%"),
        "% PRs do top contrib.": st.column_config.NumberColumn(format="%.2f%%"),
        "Idade (anos)": st.column_config.NumberColumn(format="%.1f"),
    },
)

nav_ant, nav_pagina, nav_prox = st.columns([1, 3, 1])
with nav_ant:
    if st.button("← Anterior", width="stretch", disabled=st.session_state.pagina <= 1):
        st.session_state.pagina -= 1
        st.rerun()
with nav_pagina:
    pagina_escolhida = st.number_input(
        "Ir para a página", min_value=1, max_value=total_paginas,
        value=st.session_state.pagina, step=1, label_visibility="collapsed",
    )
    if pagina_escolhida != st.session_state.pagina:
        st.session_state.pagina = int(pagina_escolhida)
        st.rerun()
with nav_prox:
    if st.button("Próxima →", width="stretch", disabled=st.session_state.pagina >= total_paginas):
        st.session_state.pagina += 1
        st.rerun()

st.download_button(
    "Baixar resultado filtrado (CSV)",
    data=filtrado[list(COLUNAS_TABELA.keys())].to_csv(index=False).encode("utf-8"),
    file_name="repositorios_filtrados.csv",
    mime="text/csv",
)
