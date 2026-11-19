"""Gráficos Plotly no tema escuro."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import formatters as fm
import theme as th
from metrics import MESES


# Folga entre o gráfico e as letras dos eixos: "tracinhos" transparentes empurram os rótulos para fora.
_TRANSPARENTE = "rgba(0,0,0,0)"
FOLGA_Y = dict(ticks="outside", ticklen=14, tickcolor=_TRANSPARENTE)   # rótulos à esquerda
FOLGA_X = dict(ticks="outside", ticklen=12, tickcolor=_TRANSPARENTE)   # rótulos embaixo


def _respiro_linha(fig: go.Figure, n: int) -> None:
    """Dá espaço nas pontas do eixo X (n categorias) para a linha/marcador não encostar nos rótulos do eixo Y."""
    fig.update_xaxes(range=[-0.45, n - 0.55])


def _base(fig: go.Figure, altura: int, margem: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=margem or dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=th.TEXTO, size=12, family="Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"),
        hoverlabel=dict(bgcolor="#0B1B36", bordercolor=th.AZUL, font=dict(color=th.TEXTO)),
    )
    return fig


def _ticks(vmax: float, n: int = 5):
    """Eixo em R$ legível (K ou M). Retorna (valores, textos, topo)."""
    if not vmax or vmax <= 0 or vmax != vmax:
        vmax = 1.0
    usa_mi = vmax >= 1e6
    unidade = 1e6 if usa_mi else 1e3
    vm = vmax / unidade
    passo = 500.0
    for candidato in (0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500):
        if vm / candidato <= n:
            passo = candidato
            break
    topo = math.ceil(vm / passo) * passo
    valores = np.arange(0, topo + passo / 2, passo)
    casas = 0 if abs(passo - round(passo)) < 1e-9 else 1
    sufixo = "M" if usa_mi else "K"
    textos = [f"R$ {fm.num(v, casas)}{sufixo}" for v in valores]
    return list(valores * unidade), textos, topo * unidade


def _passo_bonito(span: float, n: int = 4) -> float:
    """Passo 'redondo' (1, 2, 2.5, 5 x 10^k) para dividir um intervalo em ~n partes."""
    if span <= 0:
        return 1.0
    bruto = span / n
    mag = 10 ** math.floor(math.log10(bruto))
    for m in (1, 2, 2.5, 5, 10):
        if bruto <= m * mag:
            return m * mag
    return 10 * mag


def _ticks_numero(vmin: float, vmax: float, comecar_do_zero: bool):
    """Ticks para valores comuns (usuários, equipamentos, tCO₂e), em padrão brasileiro.
    Linhas não começam do zero: o eixo se ajusta para a variação aparecer. Barras começam do zero.
    Retorna (valores, textos, (limite_inferior, limite_superior))."""
    if comecar_do_zero:
        vmin = 0.0
    folga = (vmax - vmin) * 0.12 if vmax > vmin else max(abs(vmax) * 0.05, 1.0)
    baixo = 0.0 if comecar_do_zero else vmin - folga
    alto = vmax + folga
    passo = _passo_bonito(alto - baixo)
    lo = math.floor(baixo / passo) * passo
    hi = math.ceil(alto / passo) * passo
    if comecar_do_zero:
        lo = 0.0
    valores = list(np.arange(lo, hi + passo / 2, passo))
    if abs(passo - round(passo)) < 1e-9:
        casas = 0
    elif abs(passo * 10 - round(passo * 10)) < 1e-9:
        casas = 1
    else:
        casas = 2
    return valores, [fm.num(v, casas) for v in valores], (lo, hi)


def _eixo_y_dinheiro(fig: go.Figure, vmax: float) -> None:
    vals, textos, topo = _ticks(vmax)
    fig.update_yaxes(tickvals=vals, ticktext=textos, range=[0, topo], gridcolor=th.GRADE,
                     zeroline=False, tickfont=dict(color=th.MUTED, size=11), fixedrange=True, automargin=True,
                     **FOLGA_Y)


def _eixo_x(fig: go.Figure) -> None:
    fig.update_xaxes(showgrid=False, tickfont=dict(color=th.MUTED, size=11), fixedrange=True,
                     linecolor=th.GRADE, automargin=True, **FOLGA_X)


# ----------------------------------------------------------------------------
def evolucao(g: pd.DataFrame, ult: int) -> go.Figure:
    """g: índice 1..12 com realizado_plot, forecast, orcado."""
    real = g["realizado_plot"]
    inicio_fc = max(ult, 1)
    forecast = g["forecast"].where(g.index >= inicio_fc)
    orcado = g["orcado"]

    def txt(s):
        return [fm.brl(v) if pd.notna(v) else "—" for v in s]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=MESES, y=real, name="Realizado", mode="lines+markers",
        line=dict(color=th.AZUL, width=2.6), marker=dict(size=6, color=th.AZUL),
        fill="tozeroy", fillcolor="rgba(30,136,255,0.16)",
        customdata=txt(real), hovertemplate="<b>%{fullData.name}</b>: %{customdata}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=MESES, y=forecast, name="Forecast", mode="lines",
        line=dict(color=th.AZUL_CLARO, width=2, dash="dot"),
        customdata=txt(forecast), hovertemplate="<b>%{fullData.name}</b>: %{customdata}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=MESES, y=orcado, name="Orçamento", mode="lines",
        line=dict(color=th.VERDE, width=2, dash="dash"),
        customdata=txt(orcado), hovertemplate="<b>%{fullData.name}</b>: %{customdata}<extra></extra>"))

    _base(fig, 300, dict(l=8, r=8, t=30, b=8))
    fig.update_layout(hovermode="x unified",
                      legend=dict(orientation="h", y=1.14, x=1, xanchor="right", font=dict(size=11, color=th.MUTED)))
    _eixo_x(fig)
    fig.update_xaxes(showspikes=True, spikemode="across", spikecolor="rgba(30,136,255,.6)", spikethickness=1)
    _respiro_linha(fig, len(MESES))
    vmax = float(np.nanmax([real.max(), forecast.max(), orcado.max()])) if len(g) else 1.0
    _eixo_y_dinheiro(fig, vmax)
    return fig


def gauge(pct: float) -> go.Figure:
    rmax = max(100.0, math.ceil(pct / 10) * 10)
    cor = th.VERDE if pct <= 80 else (th.AMARELO if pct <= 95 else th.VERMELHO)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        number=dict(suffix="%", valueformat=".0f", font=dict(size=44, color="#FFFFFF")),
        gauge=dict(
            shape="angular", axis=dict(range=[0, rmax], visible=False),
            bar=dict(color=cor, thickness=0.62), bgcolor="rgba(255,255,255,0.04)", borderwidth=0,
            steps=[dict(range=[0, 80], color="rgba(31,224,165,0.22)"),
                   dict(range=[80, 95], color="rgba(245,197,24,0.22)"),
                   dict(range=[95, rmax], color="rgba(255,77,94,0.22)")])))
    return _base(fig, 210, dict(l=18, r=18, t=18, b=0))


def donut_categorias(serie: pd.Series) -> go.Figure:
    total = float(serie.sum())
    cores = [th.cor_categoria(nome, i) for i, nome in enumerate(serie.index)]
    fig = go.Figure(go.Pie(
        labels=list(serie.index), values=list(serie.values), hole=0.66, sort=False,
        marker=dict(colors=cores, line=dict(color="#07122A", width=2)),
        texttemplate="%{percent:.0%}", textposition="outside", textfont=dict(size=11, color=th.TEXTO),
        customdata=[fm.brl(v) for v in serie.values],
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>"))
    fig.add_annotation(text=f"<b>{fm.mi(total)}</b><br><span style='font-size:11px;color:{th.MUTED}'>Total</span>",
                       showarrow=False, font=dict(size=15, color="#FFFFFF"))
    _base(fig, 250, dict(l=28, r=8, t=18, b=18))
    fig.update_layout(legend=dict(x=1.0, y=0.5, xanchor="left", font=dict(size=11, color=th.TEXTO)))
    return fig


def donut_capex_opex(serie: pd.Series) -> go.Figure:
    total = float(serie.sum())
    rotulos = [f"{t}  {fm.num(v / total * 100 if total else 0, 0)}%" for t, v in serie.items()]
    cores = [th.CORES_TIPO.get(t, th.AZUL_CLARO) for t in serie.index]
    fig = go.Figure(go.Pie(
        labels=rotulos, values=list(serie.values), hole=0.62, sort=False, textinfo="none",
        marker=dict(colors=cores, line=dict(color="#07122A", width=2)),
        customdata=[fm.brl(v) for v in serie.values],
        hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>"))
    fig.add_annotation(text=f"<b>{fm.mi(total)}</b>", showarrow=False, font=dict(size=14, color="#FFFFFF"))
    _base(fig, 230, dict(l=8, r=8, t=8, b=8))
    fig.update_layout(legend=dict(x=1.0, y=0.5, xanchor="left", font=dict(size=12, color=th.TEXTO)))
    return fig


def treemap_fornecedores(serie: pd.Series) -> go.Figure:
    total = float(serie.sum())
    nomes = list(serie.index)
    # cores por posição: azuis (1-3), roxos (4-6), teal (7-9), neutro (Outros)
    escala = ["#1769FF", "#2C86FF", "#3F95D8", "#5B3FD1", "#7A4BE0", "#8A63F5", "#139A9A", "#128F8F", "#1A7A99"]
    cores, textos = [], []
    for i, (nome, v) in enumerate(serie.items()):
        cores.append("#5C4BC7" if nome == "Outros" else escala[min(i, len(escala) - 1)])
        textos.append(f"<b>{nome}</b><br>{fm.mi(v, 1)}<br>{fm.num(v / total * 100 if total else 0, 0)}%")
    fig = go.Figure(go.Treemap(
        labels=nomes, parents=[""] * len(nomes), values=list(serie.values),
        text=textos, textinfo="text", textposition="top left", textfont=dict(size=13, color="#FFFFFF"),
        marker=dict(colors=cores, line=dict(width=2, color="#07122A")),
        pathbar=dict(visible=False), tiling=dict(pad=0),
        customdata=[fm.brl(v) for v in serie.values],
        hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>"))
    return _base(fig, 250, dict(l=0, r=0, t=0, b=0))


def barras_saving(rotulos: list[str], valores: list[float]) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=rotulos, y=valores, marker=dict(color=th.VERDE, opacity=0.85, line=dict(width=0)),
        customdata=[fm.brl(v) for v in valores],
        hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
    _base(fig, 230, dict(l=8, r=8, t=8, b=8))
    fig.update_layout(bargap=0.35)
    _eixo_x(fig)
    _eixo_y_dinheiro(fig, max(valores) if valores else 1.0)
    return fig


# ----------------------------------------------------------------------------
# Auxiliares para as outras páginas
# ----------------------------------------------------------------------------
def barras_horizontais(rotulos, valores, cor: str = th.AZUL, altura: int = 320) -> go.Figure:
    pares = sorted(zip(rotulos, valores), key=lambda p: p[1])
    fig = go.Figure(go.Bar(
        x=[p[1] for p in pares], y=[p[0] for p in pares], orientation="h",
        marker=dict(color=cor, line=dict(width=0)),
        customdata=[fm.brl(p[1]) for p in pares],
        hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
    _base(fig, altura, dict(l=8, r=24, t=8, b=8))
    vals, textos, topo = _ticks(max(valores) if valores else 1.0)
    fig.update_xaxes(tickvals=vals, ticktext=textos, range=[0, topo], showgrid=True, gridcolor=th.GRADE,
                     zeroline=False, tickfont=dict(color=th.MUTED, size=11), fixedrange=True, automargin=True,
                     **FOLGA_X)
    # automargin abre espaço à esquerda para os nomes; a folga afasta as barras das letras
    fig.update_yaxes(tickfont=dict(color=th.TEXTO, size=12), fixedrange=True, automargin=True, **FOLGA_Y)
    fig.update_layout(bargap=0.38)
    return fig


def serie_simples(x, y, cor: str, tipo: str = "linha", casas: int = 0, altura: int = 240) -> go.Figure:
    textos = [fm.num(v, casas) for v in y]
    if tipo == "barra":
        trace = go.Bar(x=x, y=y, marker=dict(color=cor, opacity=0.85), customdata=textos,
                       hovertemplate="<b>%{x}</b>: %{customdata}<extra></extra>")
    else:
        trace = go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=cor, width=2.6),
                           marker=dict(size=6), fill="tozeroy", fillcolor="rgba(30,136,255,0.10)",
                           customdata=textos, hovertemplate="<b>%{x}</b>: %{customdata}<extra></extra>")
    fig = _base(go.Figure(trace), altura, dict(l=8, r=12, t=8, b=8))
    _eixo_x(fig)
    vals, textos, faixa = _ticks_numero(float(min(y)), float(max(y)), comecar_do_zero=(tipo == "barra"))
    fig.update_yaxes(tickvals=vals, ticktext=textos, range=list(faixa), gridcolor=th.GRADE, zeroline=False,
                     tickfont=dict(color=th.MUTED, size=11), fixedrange=True, automargin=True, **FOLGA_Y)
    if tipo != "barra":
        _respiro_linha(fig, len(x))
    return fig
