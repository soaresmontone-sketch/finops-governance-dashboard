"""Blocos de HTML do dashboard (cards, cabeçalho, painel, rodapé). Devolvem strings."""
from __future__ import annotations

import base64
import re
from html import escape

import config
import formatters as fm
import theme as th


def compactar(html: str) -> str:
    """Tira quebras de linha/indentação: o markdown do Streamlit trata linhas com 4+ espaços como código."""
    html = re.sub(r"\s*\n\s*", " ", html.strip())
    return re.sub(r">\s+<", "><", html)


def procurar_asset(base: str):
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        p = config.ASSETS_DIR / (base + ext)
        if p.exists():
            return p
    return None


def _data_uri(path) -> str:
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".svg": "image/svg+xml"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def _svg(corpo: str) -> str:
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{corpo}</svg>')


ICONES = {
    "moedas": _svg('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>'
                   '<path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>'),
    "usuario": _svg('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>'),
    "predio": _svg('<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>'),
    "folha": _svg('<path d="M5 19c0-9 5-14 15-14 0 10-5 15-14 15"/><path d="M5 19c3-5 6-8 10-10"/>'),
    "barras": _svg('<rect x="4" y="12" width="4" height="8" rx="1"/><rect x="10" y="7" width="4" height="13" rx="1"/>'
                   '<rect x="16" y="3" width="4" height="17" rx="1"/>'),
    "alvo": _svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>'),
    "monitor": _svg('<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'),
    "notebook": _svg('<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M3 19h18"/>'),
    "contrato": _svg('<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>'),
}


# ----------------------------------------------------------------------------
# Estrutura da página
# ----------------------------------------------------------------------------
def marca_html() -> str:
    logo = procurar_asset("logo")
    if logo:
        corpo = f'<img src="{_data_uri(logo)}" alt="logo">'
    else:
        corpo = f'<div class="marca-nome">{escape(config.EMPRESA)}</div>'
    return compactar(f'<div class="marca">{corpo}<div class="marca-lema">{escape(config.EMPRESA_LEMA)}</div></div>')


def sidebar_rodape_html() -> str:
    return f'<div class="side-rodape">{escape(config.SIDEBAR_FRASE)}</div>'


def cabecalho_html(hoje) -> str:
    return compactar(f"""
    <div class="hdr">
      <div>
        <div class="hdr-tit">{escape(config.APP_TITULO.upper())}</div>
        <div class="hdr-sub">{escape(config.APP_SUBTITULO.upper())}</div>
        <div class="hdr-pil">{escape(config.APP_PILARES.upper())}</div>
      </div>
      <div class="hdr-lema">“{escape(config.APP_LEMA_1)}<br>{escape(config.APP_LEMA_2)}”</div>
      <div class="hdr-data"><b>{fm.data_extenso(hoje)}</b><span>{escape(config.CIDADE)}</span></div>
    </div>""")


def rodape_html(atualizado, origem: str) -> str:
    aviso = str(getattr(config, "AVISO_DEMO", "") or "")
    autor = str(getattr(config, "AUTOR", "") or "")
    link = str(getattr(config, "LINK_PERFIL", "") or "")
    if autor:
        nome = escape(autor)
        if link.startswith(("http://", "https://")):
            nome = f'<a href="{escape(link, quote=True)}" target="_blank" rel="noopener noreferrer">{nome}</a>'
        aviso = (aviso + " · " if aviso else "") + "por " + nome
    else:
        aviso = escape(aviso)
    linha_aviso = f'<div class="aviso-demo">{aviso}</div>' if aviso else ""
    return compactar(f"""
    <div class="rodape">
      <div><b>{escape(config.EMPRESA)}</b> &nbsp;|&nbsp; {escape(config.APP_TITULO)} &nbsp;|&nbsp; {escape(config.RODAPE_FRASE)}</div>
      <div>Dados atualizados em {atualizado:%d/%m/%Y %H:%M} ({escape(origem)})
        <span class="on"></span>Conectado &nbsp; {escape(config.VERSAO)}</div>
    </div>{linha_aviso}""")


def boot_html() -> str:
    """Camada fixa da varredura de tela. Precisa ficar num st.markdown separado do <style>."""
    return '<div class="boot"></div>'


def titulo_card(texto: str, sub: str | None = None) -> str:
    s = f'<div class="card-sub">{escape(sub)}</div>' if sub else ""
    return f'<div class="card-tit">{escape(texto)}</div>{s}'


def titulo_pagina(titulo: str, sub: str = "") -> str:
    return f'<div class="pg-tit">{escape(titulo)}</div><div class="pg-sub">{escape(sub)}</div>'


def hero_html() -> str:
    """Painel translúcido no lugar da foto. Com assets/painel.(jpg|png) a imagem aparece por baixo."""
    img = procurar_asset("painel")
    camada = "linear-gradient(135deg, rgba(9,36,78,.62), rgba(5,11,24,.86))"
    fundo = f"{camada}, url('{_data_uri(img)}')" if img else camada
    palavras = "<br>".join(escape(p) for p in config.PAINEL_PALAVRAS)
    frase = "<br>".join(escape(p) for p in config.PAINEL_FRASE)
    return compactar(f"""
    <div class="hero" style="background-image:{fundo};">
      <div class="hero-pal">{palavras}</div>
      <div class="hero-frase">{frase}</div>
      <div class="hero-marca">{escape(config.EMPRESA)}</div>
    </div>""")


# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------
def _delta_html(delta, inverso: bool = False, classe: str = "kpi-delta", casas: int = 1) -> str:
    """inverso=True para métricas de custo: subir é ruim (vermelho), descer é bom (verde)."""
    if delta is None:
        return f'<div class="{classe} neutro">— sem base</div>'
    if abs(delta) < 0.05:
        return f'<div class="{classe} neutro">— 0%</div>'
    sobe = delta > 0
    bom = (not sobe) if inverso else sobe
    seta = "▲" if sobe else "▼"
    return f'<div class="{classe} {"bom" if bom else "ruim"}">{seta} {fm.pct(abs(delta), casas)}</div>'


def kpi_card(icone: str, cor: str, valor: str, titulo: str, delta, legenda: str, inverso: bool = False) -> str:
    return compactar(f"""
    <div class="kpi-wrap"><div class="kpi">
      <div class="kpi-ico" style="--c:{cor}">{ICONES[icone]}</div>
      <div class="kpi-body">
        <div class="kpi-val">{escape(valor)}</div>
        <div class="kpi-tit">{escape(titulo)}</div>
        {_delta_html(delta, inverso)}
        <div class="kpi-leg">{escape(legenda)}</div>
      </div>
    </div></div>""")


def cor_consumo(pct: float) -> str:
    if pct > config.LIMITE_CRITICO * 100:
        return th.VERMELHO
    if pct > config.LIMITE_ATENCAO * 100:
        return th.AMARELO
    return th.VERDE


def kpi_orcamento(pct: float) -> str:
    cor = cor_consumo(pct)
    if pct > config.LIMITE_CRITICO * 100:
        legenda = "Acima do orçado"
    elif pct > config.LIMITE_ATENCAO * 100:
        legenda = "Atenção ao limite"
    else:
        legenda = "Dentro do previsto"
    return compactar(f"""
    <div class="kpi-wrap"><div class="kpi">
      <div class="kpi-ico" style="--c:{th.ROSA}">{ICONES['alvo']}</div>
      <div class="kpi-body">
        <div class="kpi-val">{fm.num(pct, 0)}%</div>
        <div class="kpi-tit">Orçamento Utilizado</div>
        <div class="kpi-bar"><i style="width:{min(max(pct, 0), 100):.0f}%;background:{cor}"></i></div>
        <div class="kpi-leg">{legenda}</div>
      </div>
    </div></div>""")


def mini_indicador(icone: str, cor: str, valor: str, titulo: str, delta, inverso: bool = False) -> str:
    return compactar(f"""
    <div class="mini">
      <div class="ico" style="--c:{cor}">{ICONES[icone]}</div>
      <div class="v">{escape(valor)}</div>
      <div class="t">{escape(titulo)}</div>
      {_delta_html(delta, inverso, classe="d", casas=0 if delta is not None and abs(delta) >= 10 else 1)}
    </div>""")


def mini_grid(minis: list[str]) -> str:
    """Os mini-cards em uma única grade (evita colunas aninhadas, que vazavam do card)."""
    return compactar('<div class="mini-wrap"><div class="mini-grid">' + "".join(minis) + "</div></div>")


def saving_resumo(valor: float, delta) -> str:
    return compactar(f"""
    <div class="sav-resumo">
      <div class="v">{fm.mi(valor)}</div>
      <div class="t">Economia acumulada</div>
      {_delta_html(delta, False, classe="d")}
      <div class="l">vs. mesmo período<br>ano anterior</div>
    </div>""")


# ----------------------------------------------------------------------------
# Gauge e custos por diretoria
# ----------------------------------------------------------------------------
def gauge_info(gasto: float, orcado: float) -> str:
    return compactar(f"""
    <div class="gauge-info"><b>{fm.mi(gasto)}</b><span>de {fm.mi(orcado)}</span></div>
    <div class="gauge-leg">
      <span><i style="background:{th.VERDE}"></i>Até 80%</span>
      <span><i style="background:{th.AMARELO}"></i>80% - 95%</span>
      <span><i style="background:{th.VERMELHO}"></i>&gt; 95%</span>
    </div>""")


def tabela_diretorias(df_dir, taxa: float = 0.0) -> str:
    """df_dir: índice = diretoria, coluna 'realizado'. taxa>0 => modo Chargeback."""
    valores = df_dir["realizado"] * (1.0 + taxa)
    total = valores.sum()
    maximo = valores.max() if len(valores) else 0
    linhas = ['<div class="h">Diretoria</div><div class="h"></div><div class="h" style="text-align:right">Valor</div>'
              '<div class="h" style="text-align:right">%</div>']
    for nome, v in valores.items():
        largura = (v / maximo * 100) if maximo else 0
        p = (v / total * 100) if total else 0
        linhas.append(f'<div class="n">{escape(str(nome))}</div>'
                      f'<div class="b"><i style="width:{largura:.0f}%"></i></div>'
                      f'<div class="v">{fm.brl(v)}</div><div class="p">{fm.num(p, 0)}%</div>')
    return compactar('<div class="dr">' + "".join(linhas) + "</div>")
