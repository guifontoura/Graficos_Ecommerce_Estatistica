import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from dash import Dash, dcc, html, Input, Output

# =============================================================
# CONFIGURACAO — tema dark centralizado
# Para mudar o tema inteiro, altere apenas este dicionario
# =============================================================
CORES = {
    "fundo_pagina":     "#0f1117",
    "fundo_card":       "#161b22",
    "borda":            "#21262d",
    "texto_titulo":     "#e6edf3",
    "texto_secundario": "#8b949e",
    "destaque":         "#58a6ff",
    "paleta": [
        "#58a6ff",  # azul
        "#3fb950",  # verde
        "#f0883e",  # laranja
        "#d2a8ff",  # lilas
        "#ffa657",  # amarelo
        "#ff7b72",  # vermelho
    ],
}

FONTE = "Segoe UI, Verdana, sans-serif"

# Layout base reutilizado em todos os graficos
BASE_LAYOUT = dict(
    plot_bgcolor=CORES["fundo_card"],
    paper_bgcolor=CORES["fundo_card"],
    font=dict(family=FONTE, size=12, color=CORES["texto_titulo"]),
    legend=dict(font=dict(color=CORES["texto_secundario"]),
                bgcolor=CORES["fundo_card"],
                bordercolor=CORES["borda"]),
    xaxis=dict(gridcolor=CORES["borda"], color=CORES["texto_secundario"],
               linecolor=CORES["borda"]),
    yaxis=dict(gridcolor=CORES["borda"], color=CORES["texto_secundario"],
               linecolor=CORES["borda"]),
    margin=dict(l=50, r=30, t=70, b=50),
)


# =============================================================
# DADOS
# =============================================================
df = pd.read_csv("ecommerce_estatistica.csv")

# Opcoes de filtro de genero
GENEROS = sorted(df["Gênero"].dropna().unique())
GENEROS_COMUNS = [g for g in GENEROS
                  if df["Gênero"].value_counts()[g] / len(df) >= 0.04]

# Limites do slider de preço
PRECO_MIN = int(df["Preço"].min())
PRECO_MAX = int(df["Preço"].max()) + 1

# KPIs globais (calculados uma vez no startup)
KPI_TOTAL_PRODUTOS  = len(df)
KPI_TICKET_MEDIO    = df["Preço"].mean()
KPI_NOTA_MEDIA      = df["Nota"].mean()
KPI_MARCA_TOP       = (
    df.groupby("Marca")["Qtd_Vendidos_Cod"].sum().idxmax()
)


# =============================================================
# GRAFICOS
# Cada funcao e independente — facil de editar ou remover
# =============================================================

def grafico_histograma(df_f: pd.DataFrame) -> go.Figure:
    """Histograma: distribuicao das notas dos produtos."""
    media = df_f["Nota"].mean()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df_f["Nota"], nbinsx=20,
        marker_color=CORES["paleta"][0],
        marker_line=dict(color=CORES["fundo_card"], width=1),
        name="Notas",
        opacity=0.85,
    ))
    fig.add_vline(x=media, line_dash="dash", line_color="#ff7b72",
                  annotation_text=f"Média: {media:.2f}",
                  annotation_font_color=CORES["texto_titulo"])
    fig.update_layout(**BASE_LAYOUT,
                      title=dict(text="<b>Distribuição das Notas dos Produtos</b>",
                                 font=dict(size=15, color=CORES["texto_titulo"])),
                      xaxis_title="Nota",
                      yaxis_title="Frequência (nº de produtos)")
    return fig


def grafico_dispersao(df_f: pd.DataFrame) -> go.Figure:
    """Dispersao com linha de tendencia e tooltip customizado: Preco vs Nota."""
    fig = px.scatter(
        df_f, x="Preço", y="Nota",
        color_discrete_sequence=[CORES["paleta"][1]],
        opacity=0.7,
        labels={"Preço": "Preço (R$)", "Nota": "Nota"},
        trendline="ols",
        trendline_color_override="#ff7b72",
        hover_name="Título",
        hover_data={
            "Preço":        ":.2f",
            "Nota":         ":.1f",
            "Marca":        True,
            "N_Avaliações": ":,.0f",
            "Desconto":     True,
        },
    )
    # Estilo do marker principal (índice 0); a trendline é o trace 1
    fig.data[0].marker.update(size=8, line=dict(color=CORES["fundo_card"], width=0.6))
    fig.update_traces(
        selector=dict(mode="markers"),
        hoverlabel=dict(
            bgcolor="#1f2d3d",
            bordercolor=CORES["destaque"],
            font=dict(size=13, color=CORES["texto_titulo"], family=FONTE),
        ),
    )
    fig.update_layout(**BASE_LAYOUT,
                      title=dict(text="<b>Relação Preço × Satisfação (Nota)</b>",
                                 font=dict(size=15, color=CORES["texto_titulo"])),
                      xaxis_tickprefix="R$")
    return fig


def grafico_heatmap() -> go.Figure:
    """Mapa de calor: correlacao entre variaveis numericas."""
    cols = {
        "Nota": "Nota",
        "N_Avaliações": "Nº Avaliações",
        "Desconto": "Desconto",
        "Preço": "Preço",
        "Qtd_Vendidos_Cod": "Qtd Vendida",
    }
    corr = df[list(cols.keys())].rename(columns=cols).corr()

    # Gera cor do texto célula a célula:
    # valores extremos (|z| > 0.4) → fundo escuro/intenso → texto branco
    # valores próximos de zero      → fundo claro          → texto escuro legível
    z_vals = corr.values
    text_colors = [
        ["#ffffff" if abs(v) > 0.35 else "#1a1a2e" for v in row]
        for row in z_vals
    ]

    fig = go.Figure(go.Heatmap(
        z=z_vals,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="Blues",
        zmid=0,
        zmin=-1, zmax=1,
        text=corr.round(2).values.astype(str),
        texttemplate="<b>%{text}</b>",
        textfont=dict(size=13),
        hoverongaps=False,
        customdata=text_colors,
    ))
    # Injeta anotações individuais para garantir contraste em cada célula
    annotations = []
    cols_list = corr.columns.tolist()
    rows_list = corr.index.tolist()
    for i, row in enumerate(rows_list):
        for j, col in enumerate(cols_list):
            val = corr.values[i][j]
            txt_color = "#ffffff" if abs(val) > 0.35 else "#0d1117"
            annotations.append(dict(
                x=col, y=row,
                text=f"<b>{val:.2f}</b>",
                showarrow=False,
                font=dict(color=txt_color, size=13, family=FONTE),
                xref="x", yref="y",
            ))

    fig.update_layout(
        plot_bgcolor=CORES["fundo_card"],
        paper_bgcolor=CORES["fundo_card"],
        font=dict(family=FONTE, size=12, color=CORES["texto_titulo"]),
        title=dict(text="<b>Mapa de Calor — Correlação entre Variáveis</b>",
                   font=dict(size=15, color=CORES["texto_titulo"])),
        xaxis=dict(color=CORES["texto_secundario"]),
        yaxis=dict(color=CORES["texto_secundario"]),
        margin=dict(l=50, r=30, t=70, b=50),
        annotations=annotations,
    )
    # Remove o texttemplate embutido (as anotações substituem)
    fig.data[0].update(texttemplate="", text=None)
    return fig


def grafico_barras() -> go.Figure:
    """Barras duplas lado a lado: catalogo vs vendas por marca (top 16)."""
    from plotly.subplots import make_subplots

    analise = (
        df.groupby("Marca")
        .agg(Anunciados=("Marca", "count"),
             Vendas=("Qtd_Vendidos_Cod", "sum"))
        .sort_values("Anunciados", ascending=False)
        .head(16)
    )
    # ordena por Anunciados para ambos os painéis ficarem alinhados
    analise = analise.sort_values("Anunciados", ascending=True)

    def fmt_mil(v):
        if v >= 1000:
            return f"{int(v/1000)}mil"
        return str(int(v))

    labels_vendas = [fmt_mil(v) for v in analise["Vendas"]]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Produtos Anunciados (Volume)", "Total de Vendas (Performance)"],
        horizontal_spacing=0.08,
    )

    # Painel esquerdo — Anunciados
    fig.add_trace(go.Bar(
        y=analise.index,
        x=analise["Anunciados"],
        orientation="h",
        marker_color=CORES["paleta"][0],
        text=analise["Anunciados"].astype(str),
        textposition="outside",
        textfont=dict(size=11, color=CORES["texto_titulo"]),
        cliponaxis=False,
        name="Produtos Anunciados",
        showlegend=True,
    ), row=1, col=1)

    # Painel direito — Vendas
    fig.add_trace(go.Bar(
        y=analise.index,
        x=analise["Vendas"],
        orientation="h",
        marker_color=CORES["paleta"][1],
        text=labels_vendas,
        textposition="outside",
        textfont=dict(size=11, color=CORES["texto_titulo"], family=FONTE),
        cliponaxis=False,
        name="Total de Vendas",
        showlegend=True,
    ), row=1, col=2)

    # Formata eixo X direito com "mil"
    max_vendas = analise["Vendas"].max()
    tick_vals = [0, 50000, 100000, 150000, 200000, 250000, 300000]
    tick_vals = [t for t in tick_vals if t <= max_vendas * 1.15]

    fig.update_layout(
        **{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis", "yaxis", "legend")},
        title=dict(text="<b>Análise Comparativa: Presença de Catálogo vs. Giro de Vendas</b>",
                   font=dict(size=15, color=CORES["texto_titulo"])),
        height=560,
        bargap=0.25,
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=-0.08,
            font=dict(color=CORES["texto_secundario"]),
            bgcolor=CORES["fundo_card"],
        ),
    )
    # Estilos dos eixos por subplot
    for col_idx in [1, 2]:
        fig.update_xaxes(
            gridcolor=CORES["borda"], color=CORES["texto_secundario"],
            linecolor=CORES["borda"], row=1, col=col_idx,
        )
        fig.update_yaxes(
            gridcolor=CORES["borda"], color=CORES["texto_secundario"],
            linecolor=CORES["borda"], row=1, col=col_idx,
        )

    # Eixo X direito: ticks em "mil"
    fig.update_xaxes(
        tickvals=tick_vals,
        ticktext=[fmt_mil(v) for v in tick_vals],
        row=1, col=2,
    )
    # Margem extra para rótulos não serem cortados
    fig.update_layout(margin=dict(l=50, r=80, t=80, b=60))

    # Títulos dos subplots em cor legível
    for ann in fig.layout.annotations:
        ann.font.color = CORES["texto_secundario"]
        ann.font.size = 12

    return fig


def grafico_pizza(df_f: pd.DataFrame) -> go.Figure:
    """Pizza: distribuicao por genero — todas as categorias reais."""
    counts = df["Gênero"].value_counts()   # usa df completo, não df_f filtrado

    # Limiar: categorias com < 2% viram legenda separada mas mantêm fatia visível
    LIMIAR_LEGENDA = counts.sum() * 0.02

    # Separa principais e pequenas
    principais = counts[counts >= LIMIAR_LEGENDA]
    pequenas   = counts[counts < LIMIAR_LEGENDA]

    labels = principais.index.tolist()
    values = principais.values.tolist()

    # Adiciona cada categoria pequena como fatia própria (não agrupa em "Outros")
    for lbl, val in pequenas.items():
        # Limpa rótulos muito longos
        lbl_clean = lbl if len(lbl) < 30 else lbl[:27] + "…"
        labels.append(lbl_clean)
        values.append(val)

    paleta_ext = [
        "#58a6ff", "#f0883e", "#3fb950", "#d2a8ff",
        "#ffa657", "#ff7b72", "#79c0ff", "#a5d6a7",
        "#ce93d8", "#ffcc80",
    ]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.35,
        marker=dict(
            colors=paleta_ext[:len(labels)],
            line=dict(color=CORES["fundo_card"], width=2),
        ),
        textinfo="label+percent",
        textfont=dict(size=12, color=CORES["texto_titulo"]),
        insidetextorientation="auto",
    ))
    fig.update_layout(
        plot_bgcolor=CORES["fundo_card"],
        paper_bgcolor=CORES["fundo_card"],
        font=dict(family=FONTE, size=12, color=CORES["texto_titulo"]),
        legend=dict(
            font=dict(color=CORES["texto_secundario"], size=11),
            bgcolor=CORES["fundo_card"],
            title=dict(text="Categorias", font=dict(color=CORES["destaque"])),
        ),
        title=dict(text="<b>Distribuição de Produtos por Gênero</b>",
                   font=dict(size=15, color=CORES["texto_titulo"])),
        margin=dict(l=30, r=30, t=70, b=30),
    )
    return fig


def grafico_densidade(df_f: pd.DataFrame) -> go.Figure:
    """Densidade KDE: concentracao de precos."""
    from scipy.stats import gaussian_kde
    import numpy as np

    precos = df_f["Preço"].dropna()
    kde = gaussian_kde(precos)
    x_range = np.linspace(precos.min(), precos.max(), 300)
    mediana = precos.median()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_range, y=kde(x_range),
        fill="tozeroy", mode="lines",
        line=dict(color=CORES["paleta"][3], width=2),
        fillcolor="rgba(210, 168, 255, 0.25)",
        name="Densidade",
    ))
    fig.add_vline(x=mediana, line_dash="dash", line_color="#ff7b72",
                  annotation_text=f"Mediana: R${mediana:.0f}",
                  annotation_font_color=CORES["texto_titulo"])
    fig.update_layout(**BASE_LAYOUT,
                      title=dict(text="<b>Distribuição de Preços (Densidade)</b>",
                                 font=dict(size=15, color=CORES["texto_titulo"])),
                      xaxis_title="Preço (R$)",
                      yaxis_title="Densidade",
                      xaxis_tickprefix="R$")
    return fig


def grafico_regressao(df_f: pd.DataFrame) -> go.Figure:
    """Regressao linear: Preco vs Quantidade Vendida (escala log no Y)."""
    import numpy as np

    reg = df_f[["Preço", "Qtd_Vendidos_Cod"]].dropna()
    x = reg["Preço"]
    y = reg["Qtd_Vendidos_Cod"]

    # Jitter leve no Y para desempilhar pontos sobrepostos
    rng = np.random.default_rng(42)
    y_jitter = y + rng.uniform(-y * 0.08, y * 0.08)
    y_jitter = y_jitter.clip(lower=1)

    slope, intercept, r, p, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = slope * x_line + intercept

    # Cor dos pontos mapeada pela nota (se disponível) para adicionar dimensão
    cor_pts = df_f.loc[reg.index, "Nota"] if "Nota" in df_f.columns else None

    fig = go.Figure()

    # Pontos com cor por faixa de Qtd_Vendidos
    faixas = {5: "#8b949e", 25: "#58a6ff", 50: "#79c0ff",
              100: "#3fb950", 1000: "#ffa657", 10000: "#ff7b72", 50000: "#d2a8ff"}
    for val, cor in faixas.items():
        mask = y == val
        if mask.sum() == 0:
            continue
        label = f"+{val//1000}mil" if val >= 1000 else f"+{val}"
        fig.add_trace(go.Scatter(
            x=x[mask], y=y_jitter[mask],
            mode="markers",
            marker=dict(color=cor, size=8, opacity=0.80,
                        line=dict(color=CORES["fundo_card"], width=0.8)),
            name=label,
        ))

    # Linha de regressão
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        line=dict(color="#ff7b72", width=2.5, dash="solid"),
        name=f"Regressão (R²={r**2:.3f})",
    ))

    stats_txt = f"R² = {r**2:.3f}  |  p = {p:.4f}<br>y = {slope:.1f}x + {intercept:.0f}"
    fig.add_annotation(
        text=stats_txt, align="right",
        xref="paper", yref="paper", x=0.98, y=0.96,
        showarrow=False,
        bgcolor="#1f2d3d",
        bordercolor=CORES["destaque"],
        borderwidth=1,
        font=dict(size=12, color=CORES["texto_titulo"]),
    )

    fig.update_layout(
        **{k: v for k, v in BASE_LAYOUT.items() if k not in ("yaxis", "legend")},
        title=dict(text="<b>Regressão: Preço × Quantidade Vendida</b>",
                   font=dict(size=15, color=CORES["texto_titulo"])),
        xaxis_title="Preço (R$)",
        yaxis=dict(
            title="Quantidade Vendida (escala log)",
            type="log",
            tickvals=[5, 25, 50, 100, 1000, 10000, 50000],
            ticktext=["+5", "+25", "+50", "+100", "+1mil", "+10mil", "+50mil"],
            gridcolor=CORES["borda"],
            color=CORES["texto_secundario"],
            linecolor=CORES["borda"],
        ),
        xaxis_tickprefix="R$",
        legend=dict(
            title=dict(text="Faixa vendida", font=dict(color=CORES["destaque"])),
            font=dict(color=CORES["texto_secundario"]),
            bgcolor=CORES["fundo_card"],
            bordercolor=CORES["borda"],
        ),
    )
    return fig


# =============================================================
# COMPONENTES DE LAYOUT REUTILIZAVEIS
# =============================================================
def card_grafico(graph_id: str) -> html.Div:
    """Envolve um dcc.Graph num card dark com bordas."""
    return html.Div(
        style={
            "background":   CORES["fundo_card"],
            "border":       f"1px solid {CORES['borda']}",
            "borderRadius": "10px",
            "overflow":     "hidden",
            "marginBottom": "16px",
        },
        children=[dcc.Graph(id=graph_id)],
    )


def kpi_card(icone: str, label: str, valor: str, cor: str = None) -> html.Div:
    """Card de KPI individual para o topo do dashboard."""
    cor_val = cor or CORES["destaque"]
    return html.Div(
        style={
            "background":    CORES["fundo_card"],
            "border":        f"1px solid {CORES['borda']}",
            "borderTop":     f"3px solid {cor_val}",
            "borderRadius":  "10px",
            "padding":       "20px 24px",
            "flex":          "1",
            "minWidth":      "180px",
        },
        children=[
            html.Div(icone, style={"fontSize": "28px", "marginBottom": "8px"}),
            html.Div(valor,
                     style={"color": cor_val, "fontSize": "28px",
                            "fontWeight": "700", "lineHeight": "1"}),
            html.Div(label,
                     style={"color": CORES["texto_secundario"],
                            "fontSize": "12px", "marginTop": "6px",
                            "textTransform": "uppercase", "letterSpacing": "0.8px"}),
        ],
    )


def linha_kpis() -> html.Div:
    """Faixa de 4 KPI cards no topo."""
    return html.Div(
        style={"display": "flex", "gap": "16px",
               "marginBottom": "32px", "flexWrap": "wrap"},
        children=[
            kpi_card("📦", "Total de Produtos",
                     str(KPI_TOTAL_PRODUTOS),
                     CORES["paleta"][0]),
            kpi_card("💰", "Ticket Médio",
                     f"R$ {KPI_TICKET_MEDIO:.0f}",
                     CORES["paleta"][2]),
            kpi_card("⭐", "Nota Média do Catálogo",
                     f"{KPI_NOTA_MEDIA:.2f}",
                     CORES["paleta"][4]),
            kpi_card("🏆", "Marca Líder em Vendas",
                     KPI_MARCA_TOP.title(),
                     CORES["paleta"][1]),
        ],
    )


def secao_insight(titulo: str, texto: str) -> html.Div:
    """Bloco de insight estrategico — destaque máximo, tão importante quanto o gráfico."""
    return html.Div(
        style={
            "background":    "linear-gradient(135deg, #1a2540 0%, #0f1a2e 100%)",
            "border":        f"1px solid {CORES['destaque']}55",
            "borderLeft":    f"5px solid {CORES['destaque']}",
            "borderRadius":  "0 10px 10px 0",
            "padding":       "22px 28px",
            "marginBottom":  "36px",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center",
                       "marginBottom": "10px", "gap": "10px"},
                children=[
                    html.Span("📊", style={"fontSize": "22px"}),
                    html.Span(f"Insight Estratégico — {titulo}",
                              style={"color": CORES["destaque"],
                                     "fontWeight": "700",
                                     "fontSize": "17px",
                                     "letterSpacing": "0.4px"}),
                ],
            ),
            html.P(texto,
                   style={"color":      "#dde4f0",
                          "fontSize":   "16px",
                          "lineHeight": "1.9",
                          "margin":     0}),
        ],
    )


# =============================================================
# LAYOUT COMPLETO
# =============================================================
def criar_layout():
    return html.Div(
        style={
            "backgroundColor": CORES["fundo_pagina"],
            "minHeight":       "100vh",
            "padding":         "32px 40px",
            "fontFamily":      FONTE,
        },
        children=[

            # Cabecalho
            html.Div(
                style={"borderBottom": f"1px solid {CORES['borda']}",
                       "paddingBottom": "20px", "marginBottom": "28px"},
                children=[
                    html.H1("E-commerce — Performance Insights",
                            style={"color": CORES["destaque"], "fontSize": "24px",
                                   "letterSpacing": "1px", "margin": 0}),
                    html.P("Análise Exploratória de Dados | Guilherme Fontoura · EBAC 2026",
                           style={"color": CORES["texto_secundario"],
                                  "marginTop": "6px", "fontSize": "13px"}),
                ],
            ),

            # KPI Cards
            linha_kpis(),

            # Painel de filtros
            html.Div(
                style={"background": CORES["fundo_card"],
                       "border": f"1px solid {CORES['borda']}",
                       "borderRadius": "10px", "padding": "20px 24px",
                       "marginBottom": "32px"},
                children=[
                    html.Div("🎛️ Filtros Interativos",
                             style={"color": CORES["destaque"], "fontWeight": "700",
                                    "fontSize": "13px", "letterSpacing": "0.8px",
                                    "textTransform": "uppercase",
                                    "marginBottom": "18px"}),

                    # Linha 1 — Gênero
                    html.Div(
                        style={"marginBottom": "20px"},
                        children=[
                            html.Label("Filtrar por Gênero:",
                                       style={"color": CORES["texto_secundario"],
                                              "fontSize": "12px", "fontWeight": "600",
                                              "display": "block", "marginBottom": "10px",
                                              "textTransform": "uppercase",
                                              "letterSpacing": "0.6px"}),
                            dcc.Checklist(
                                id="filtro_genero",
                                options=[{"label": g, "value": g} for g in GENEROS_COMUNS],
                                value=GENEROS_COMUNS,
                                labelStyle={"display": "inline-block",
                                            "marginRight": "20px",
                                            "color": CORES["texto_titulo"],
                                            "fontSize": "13px"},
                                inputStyle={"marginRight": "8px", "cursor": "pointer",
                                            "width": "16px", "height": "16px"},
                            ),
                        ],
                    ),

                    # Linha 2 — Faixa de Preço
                    html.Div(
                        children=[
                            html.Label("Faixa de Preço:",
                                       style={"color": CORES["texto_secundario"],
                                              "fontSize": "12px", "fontWeight": "600",
                                              "display": "block", "marginBottom": "10px",
                                              "textTransform": "uppercase",
                                              "letterSpacing": "0.6px"}),
                            dcc.RangeSlider(
                                id="filtro_preco",
                                min=PRECO_MIN,
                                max=PRECO_MAX,
                                step=5,
                                value=[PRECO_MIN, PRECO_MAX],
                                marks={
                                    PRECO_MIN:  {"label": f"R${PRECO_MIN}",
                                                 "style": {"color": CORES["texto_secundario"]}},
                                    100:        {"label": "R$100",
                                                 "style": {"color": CORES["texto_secundario"]}},
                                    200:        {"label": "R$200",
                                                 "style": {"color": CORES["texto_secundario"]}},
                                    PRECO_MAX:  {"label": f"R${PRECO_MAX}",
                                                 "style": {"color": CORES["texto_secundario"]}},
                                },
                                tooltip={"placement": "bottom",
                                         "always_visible": True,
                                         "template": "R${value}"},
                            ),
                        ],
                    ),
                ],
            ),

            # 1. Histograma
            html.H2("1 · Distribuição das Notas",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("hist"),
            secao_insight(
                "Notas do Catálogo",
                "A maioria dos produtos concentra-se entre 4.3 e 4.8 — "
                "catálogo com boa reputação geral. Notas abaixo de 4.0 são raras, "
                "o que indica curadoria ativa ou viés de avaliação positiva. "
                "Ação recomendada: investigar os outliers negativos e considerar sua remoção do catálogo.",
            ),

            # 2. Dispersao
            html.H2("2 · Preço × Satisfação",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("dispersao"),
            secao_insight(
                "Preço não define qualidade percebida",
                "A linha de tendência praticamente plana confirma que preço e nota "
                "são estatisticamente independentes. Produtos baratos e caros recebem avaliações "
                "semelhantes — isso autoriza estratégias de precificação premium "
                "sem risco de queda na satisfação do cliente.",
            ),

            # 3. Heatmap
            html.H2("3 · Correlação entre Variáveis",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("heatmap"),
            secao_insight(
                "Prova Social é o principal driver de vendas",
                "Correlação de 0.91 entre Nº de Avaliações e Quantidade Vendida — "
                "o maior coeficiente do mapa, muito acima do desconto (≈ 0.0). "
                "Ação: priorizar campanhas de pós-venda que incentivem o cliente a avaliar. "
                "Cada review gerado tem impacto direto e mensurável no volume de vendas.",
            ),

            # 4. Barras
            html.H2("4 · Catálogo vs. Giro de Vendas por Marca",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("barras"),
            secao_insight(
                "Eficiência de nicho supera volume de catálogo",
                "Zorba converte 263 mil unidades com apenas 10 produtos anunciados, "
                "enquanto marcas com catálogos 4× maiores registram desempenho 20× inferior. "
                "Ação: reduzir espaço de vitrine de marcas ineficientes e ampliar o investimento "
                "em marcas de alto giro — menos SKUs, mais resultado.",
            ),

            # 5. Pizza
            html.H2("5 · Distribuição por Gênero",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("pizza"),
            secao_insight(
                "Público infantil e unissex são oportunidades inexploradas",
                "O catálogo está concentrado em Masculino (43.7%) e Feminino (38.6%), "
                "somando 82% da oferta. Categorias infantis e unissex representam menos de 10% — "
                "baixa concorrência interna e potencial de expansão imediata "
                "sem canibalização das categorias principais.",
            ),

            # 6. Densidade
            html.H2("6 · Distribuição de Preços",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("densidade"),
            secao_insight(
                "Mercado concentrado no mid-market com lacuna premium",
                "Concentração principal entre R$70 e R$180 — ticket médio acessível, "
                "atendendo majoritariamente classe média. A mediana de R$129 confirma "
                "esse posicionamento. Há espaço estratégico para uma linha premium "
                "acima de R$250, segmento com pouca saturação e margens superiores.",
            ),

            # 7. Regressao
            html.H2("7 · Regressão: Preço × Quantidade Vendida",
                    style={"color": CORES["texto_titulo"], "fontSize": "15px",
                           "marginBottom": "8px"}),
            card_grafico("regressao"),
            secao_insight(
                "Preço não inibe vendas — evite guerra de preços",
                "R² de apenas 1.3% confirma que o preço explica menos de 2% da variação "
                "no volume de vendas. A inclinação positiva da regressão sugere que o público "
                "tolera — e até prefere — produtos de maior valor. "
                "Conclusão: reduzir preços não aumentará vendas de forma significativa. "
                "Invista em prova social (reviews) e curadoria de marcas premium.",
            ),

            # Rodape
            html.Div(
                style={"borderTop": f"1px solid {CORES['borda']}",
                       "marginTop": "20px", "paddingTop": "16px",
                       "color": CORES["texto_secundario"], "fontSize": "12px"},
                children="Guilherme Fontoura · EBAC Analista de Dados 2026 · "
                         "Dados: ecommerce_estatistica.csv",
            ),
        ],
    )


# =============================================================
# APP E CALLBACKS
# =============================================================
app = Dash(
    __name__,
    title="E-commerce Insights | Guilherme Fontoura",
    # Coloque um arquivo favicon.ico dentro de assets/favicon.ico
    # O Dash o carrega automaticamente da pasta assets/
)
app.layout = criar_layout()


@app.callback(
    Output("hist",      "figure"),
    Output("dispersao", "figure"),
    Output("pizza",     "figure"),
    Output("densidade", "figure"),
    Output("regressao", "figure"),
    Input("filtro_genero", "value"),
    Input("filtro_preco",  "value"),
)
def atualizar(generos, faixa_preco):
    """Atualiza os 5 gráficos filtráveis por gênero e faixa de preço."""
    preco_min, preco_max = faixa_preco if faixa_preco else [PRECO_MIN, PRECO_MAX]
    df_f = df[df["Preço"].between(preco_min, preco_max)]
    if generos:
        df_f = df_f[df_f["Gênero"].isin(generos)]
    return (
        grafico_histograma(df_f),
        grafico_dispersao(df_f),
        grafico_pizza(df_f),
        grafico_densidade(df_f),
        grafico_regressao(df_f),
    )


@app.callback(
    Output("heatmap", "figure"),
    Output("barras",  "figure"),
    Input("filtro_genero", "value"),  # recebe mas não usa — gráficos fixos
)
def atualizar_fixos(_):
    """Heatmap e barras usam o dataset completo — não dependem dos filtros."""
    return grafico_heatmap(), grafico_barras()


# =============================================================
# EXECUCAO
# =============================================================
if __name__ == "__main__":
    app.run(debug=True, port=8050)