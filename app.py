"""FinOps Governance Center — dashboard interativo (Streamlit + Plotly).

Rodar:  streamlit run app.py
"""
from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
import streamlit as st

import charts as ch
import components as cp
import config
import data_loader as dl
import formatters as fm
import metrics as mt
import styles
import theme as th

st.set_page_config(page_title=config.APP_TITULO, page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(styles.CSS, unsafe_allow_html=True)

def _fuso():
    """Horário de São Paulo (na nuvem o servidor roda em UTC). Sem o pacote tzdata, usa o horário local."""
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("America/Sao_Paulo")
    except Exception:  # noqa: BLE001
        return None


def agora() -> datetime:
    return datetime.now(_fuso())


PLOTLY_CFG = {"displayModeBar": False}
SEM_DADOS = "Sem dados para os filtros selecionados."


# ============================================================================
# Utilidades
# ============================================================================
def grafico(fig, chave: str) -> None:
    st.plotly_chart(fig, theme=None, config=PLOTLY_CFG, key=chave)


_JS_SELECTS_SO_CLIQUE = """
<script>
(function () {
  var doc;
  try { doc = window.parent.document; } catch (e) { return; }
  function travar() {
    doc.querySelectorAll('div[data-baseweb="select"] input').forEach(function (el) {
      if (!el.readOnly) {
        el.readOnly = true;                    // não aceita texto: só abre a lista e escolhe
        el.setAttribute('inputmode', 'none');
        el.setAttribute('autocomplete', 'off');
      }
    });
  }
  if (doc.__finopsObs) { try { doc.__finopsObs.disconnect(); } catch (e) {} }
  var agendado = false;
  doc.__finopsObs = new MutationObserver(function () {
    if (agendado) return;
    agendado = true;
    requestAnimationFrame(function () { agendado = false; travar(); });
  });
  doc.__finopsObs.observe(doc.body, { childList: true, subtree: true });
  travar();
})();
</script>
"""


def travar_digitacao_nos_seletores() -> None:
    """Os seletores (Ano, Mês, Diretoria…) só abrem a lista; não dá para digitar dentro deles."""
    try:
        import streamlit.components.v1 as stc
        stc.html(_JS_SELECTS_SO_CLIQUE, height=0)
    except Exception:  # noqa: BLE001 — é só um refinamento visual; nunca deve derrubar o app
        pass


def espaco(rem: float = 0.7) -> None:
    st.markdown(f'<div style="height:{rem}rem"></div>', unsafe_allow_html=True)


def csv_br(df: pd.DataFrame) -> bytes:
    """CSV com ';' e vírgula decimal, que o Excel em português abre direto."""
    return df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


# ============================================================================
# Dados
# ============================================================================
@st.cache_data(show_spinner="Carregando dados…")
def _gastos_arquivo(caminho: str, mtime: float) -> pd.DataFrame:
    return dl.carregar_gastos(caminho)


@st.cache_data(show_spinner=False)
def _indicadores_arquivo(caminho: str, mtime: float) -> pd.DataFrame:
    return dl.carregar_indicadores(caminho)


def obter_dados():
    try:
        if "gastos_upload" in st.session_state:
            df = st.session_state["gastos_upload"]
            origem = "upload: " + st.session_state.get("gastos_upload_nome", "")
            atualizado = st.session_state.get("gastos_upload_hora", agora())
        else:
            arq = config.ARQ_GASTOS
            if not arq.exists():
                st.error(f"Arquivo de dados não encontrado: {arq}. Rode `python generate_data.py` "
                         "para gerar dados fictícios ou coloque sua tabela nessa pasta.")
                st.stop()
            df = _gastos_arquivo(str(arq), arq.stat().st_mtime)
            origem = arq.name
            atualizado = datetime.fromtimestamp(arq.stat().st_mtime, _fuso())

        if "ind_upload" in st.session_state:
            ind = st.session_state["ind_upload"]
        else:
            arq_i = config.ARQ_INDICADORES
            ind = _indicadores_arquivo(str(arq_i), arq_i.stat().st_mtime if arq_i.exists() else 0.0)
    except ValueError as erro:
        st.error(f"Problema ao ler os dados: {erro}")
        st.stop()
    return df, ind, atualizado, origem


# ============================================================================
# Filtros
# ============================================================================
def _reset_cc_area() -> None:
    st.session_state["f_cc"] = mt.TODOS
    st.session_state["f_area"] = mt.TODOS


def _reset_area() -> None:
    st.session_state["f_area"] = mt.TODOS


def _select(coluna, rotulo: str, opcoes: list, chave: str, **kw):
    if chave in st.session_state and st.session_state[chave] not in opcoes:
        st.session_state[chave] = opcoes[0]
    return coluna.selectbox(rotulo, opcoes, key=chave, **kw)


def barra_filtros(df: pd.DataFrame):
    anos = sorted(int(a) for a in df["ano"].unique())[::-1]
    c = st.columns([0.9, 0.9, 1.3, 1.6, 1.2, 1.2, 1.7])

    ano = _select(c[0], "Ano", anos, "f_ano")
    mes_txt = _select(c[1], "Mês", [mt.TODOS] + mt.MESES, "f_mes")
    dire = _select(c[2], "Diretoria", [mt.TODOS] + sorted(df["diretoria"].unique()), "f_dir",
                   on_change=_reset_cc_area)

    base = df if dire == mt.TODOS else df[df["diretoria"] == dire]
    cc = _select(c[3], "Centro de Custo", [mt.TODOS] + sorted(base["centro_custo"].unique()), "f_cc",
                 on_change=_reset_area)

    base2 = base if cc == mt.TODOS else base[base["centro_custo"] == cc]
    area = _select(c[4], "Área", [mt.TODOS] + sorted(base2["area"].unique()), "f_area")
    forn = _select(c[5], "Fornecedor", [mt.TODOS] + sorted(df["fornecedor"].unique()), "f_forn")

    modo = c[6].radio("Modo", ["Showback", "Chargeback"], horizontal=True, key="modo",
                      label_visibility="collapsed")

    filtros = mt.Filtros(
        ano=int(ano),
        mes=None if mes_txt == mt.TODOS else mt.MESES.index(mes_txt) + 1,
        diretoria=None if dire == mt.TODOS else dire,
        centro_custo=None if cc == mt.TODOS else cc,
        area=None if area == mt.TODOS else area,
        fornecedor=None if forn == mt.TODOS else forn,
    )
    return filtros, modo


def taxa_atual(modo: str) -> float:
    if modo != "Chargeback":
        return 0.0
    return float(st.session_state.get("taxa_val", config.TAXA_CHARGEBACK * 100)) / 100.0


# ============================================================================
# Página: Visão Geral
# ============================================================================
def pagina_visao_geral(df, ind, f, modo) -> None:
    k = mt.calcular_kpis(df, ind, f)
    meses, mes_ref = k["meses"], k["mes_ref"]
    g, ult = mt.serie_mensal(df, f)

    # ---- KPIs --------------------------------------------------------------
    cc_leg = "sem alteração" if not k["d_cc"] else "vs. mesmo período ano anterior"
    cards = [
        cp.kpi_card("moedas", th.AZUL, fm.brl(k["total"]), "Total Spend TI", k["d_total"],
                    "vs. mesmo período ano anterior", inverso=True),
        cp.kpi_card("usuario", th.AZUL, fm.brl(k["custo_usuario"]), "Custo por Usuário",
                    k["d_custo_usuario"], "vs. mês anterior", inverso=True),
        cp.kpi_card("predio", th.AZUL, fm.inteiro(k["cc_ativos"]), "Centros de Custo Ativos", k["d_cc"], cc_leg),
        cp.kpi_card("folha", th.VERDE, fm.brl(k["economia"]), "Economia Acumulada", k["d_economia"],
                    "vs. mesmo período ano anterior"),
        cp.kpi_card("barras", th.AZUL, fm.brl(k["forecast"]), f"Forecast FY{str(f.ano)[-2:]}", k["d_forecast"],
                    f"vs. FY{str(f.ano - 1)[-2:]}", inverso=True),
        cp.kpi_orcamento(k["consumo_pct"]),
    ]
    for coluna, html in zip(st.columns(6), cards):
        coluna.markdown(html, unsafe_allow_html=True)
    espaco()

    # ---- Evolução | Budget | Painel ---------------------------------------
    c1, c2, c3 = st.columns([2.3, 1.25, 1.45])
    with c1:
        with st.container(border=True, key="card_evolucao"):
            st.markdown(cp.titulo_card("Evolução de Gastos de TI"), unsafe_allow_html=True)
            grafico(ch.evolucao(g, ult), "pc_evolucao")
    with c2:
        with st.container(border=True, key="card_gauge"):
            st.markdown(cp.titulo_card("Budget Consumed"), unsafe_allow_html=True)
            grafico(ch.gauge(k["consumo_pct"]), "pc_gauge")
            st.markdown(cp.gauge_info(k["total"], k["orcado_periodo"]), unsafe_allow_html=True)
    with c3:
        st.markdown(cp.hero_html(), unsafe_allow_html=True)
    espaco()

    # ---- Categorias | Fornecedores | Diretorias ---------------------------
    c1, c2, c3 = st.columns([1.45, 1.75, 1.5])
    with c1:
        with st.container(border=True, key="card_categorias"):
            st.markdown(cp.titulo_card("Distribuição de Custos por Categoria"), unsafe_allow_html=True)
            serie = mt.por_categoria(df, f)
            if serie.sum() > 0:
                grafico(ch.donut_categorias(serie), "pc_categorias")
            else:
                st.caption(SEM_DADOS)
    with c2:
        with st.container(border=True, key="card_fornecedores"):
            h1, h2 = st.columns([3, 1.3])
            h1.markdown(cp.titulo_card("Top 10 Fornecedores"), unsafe_allow_html=True)
            base = h2.selectbox("Base", ["Realizado", "Orçado"], key="sel_forn", label_visibility="collapsed")
            serie = mt.por_fornecedor(df, f, "realizado" if base == "Realizado" else "orcado")
            if len(serie):
                grafico(ch.treemap_fornecedores(serie), "pc_fornecedores")
            else:
                st.caption(SEM_DADOS)
    with c3:
        with st.container(border=True, key="card_diretorias"):
            taxa = taxa_atual(modo)
            sub = (f"Chargeback: realizado + taxa administrativa de {fm.num(taxa * 100, 1)}%"
                   if modo == "Chargeback" else "Showback: custo realizado alocado")
            st.markdown(cp.titulo_card("Custos por Diretoria", sub), unsafe_allow_html=True)
            dd = mt.por_diretoria(df, f)
            if len(dd) and dd["realizado"].sum() > 0:
                st.markdown(cp.tabela_diretorias(dd, taxa), unsafe_allow_html=True)
            else:
                st.caption(SEM_DADOS)
    espaco()

    # ---- Indicadores | CAPEX x OPEX | Saving ------------------------------
    c1, c2, c3 = st.columns([1.5, 1.1, 1.4])
    with c1:
        with st.container(border=True, key="card_indicadores"):
            st.markdown(cp.titulo_card("Principais Indicadores"), unsafe_allow_html=True)
            op = mt.indicadores_operacionais(df, ind, f, meses, mes_ref)
            definicoes = [
                ("monitor", th.AZUL, "usuarios", "Usuários Ativos", 0),
                ("notebook", th.AZUL, "equipamentos", "Equipamentos", 0),
                ("contrato", th.AZUL, "contratos", "Contratos", 0),
                ("folha", th.VERDE, "co2", "tCO₂e evitadas", 1),
            ]
            minis = []
            for icone, cor, chave, titulo, casas in definicoes:
                valor, delta = op[chave]
                minis.append(cp.mini_indicador(icone, cor, fm.num(valor, casas) if valor is not None else "—",
                                               titulo, delta))
            st.markdown(cp.mini_grid(minis), unsafe_allow_html=True)
    with c2:
        with st.container(border=True, key="card_capex"):
            st.markdown(cp.titulo_card("CAPEX x OPEX"), unsafe_allow_html=True)
            serie = mt.capex_opex(df, f)
            if serie.sum() > 0:
                grafico(ch.donut_capex_opex(serie), "pc_capex")
            else:
                st.caption(SEM_DADOS)
    with c3:
        with st.container(border=True, key="card_saving"):
            h1, h2 = st.columns([2, 1.2])
            h1.markdown(cp.titulo_card("Saving Tracker"), unsafe_allow_html=True)
            period = h2.selectbox("Periodicidade", ["Mensal", "Trimestral"], key="sel_sav",
                                  label_visibility="collapsed")
            rotulos, valores = mt.saving_serie(df, f, period)
            s1, s2 = st.columns([2.3, 1])
            with s1:
                if valores and sum(valores) > 0:
                    grafico(ch.barras_saving(rotulos, valores), "pc_saving")
                else:
                    st.caption(SEM_DADOS)
            with s2:
                st.markdown(cp.saving_resumo(k["economia"], k["d_economia"]), unsafe_allow_html=True)


# ============================================================================
# Página: Showback / Chargeback
# ============================================================================
def pagina_alocacao(df, ind, f, modo_fixo: str) -> None:
    chargeback = modo_fixo == "Chargeback"
    st.markdown(cp.titulo_pagina(
        modo_fixo,
        "Custo realizado cobrado dos centros de custo, com taxa administrativa." if chargeback
        else "Transparência: quanto cada diretoria e centro de custo consome de TI."), unsafe_allow_html=True)

    taxa = 0.0
    if chargeback:
        pct_taxa = st.slider("Taxa administrativa (%)", 0.0, 20.0,
                             float(st.session_state.get("taxa_val", config.TAXA_CHARGEBACK * 100)), 0.5)
        st.session_state["taxa_val"] = pct_taxa   # guarda para a Visão Geral
        taxa = pct_taxa / 100.0

    t = mt.tabela_alocacao(df, ind, f, taxa)
    if t.empty:
        st.info(SEM_DADOS)
        return

    m = st.columns(3)
    m[0].metric("Total realizado", fm.brl(t["realizado"].sum()))
    m[1].metric("Total orçado", fm.brl(t["orcado"].sum()))
    if chargeback:
        m[2].metric("Total a cobrar", fm.brl(t["a_cobrar"].sum()))
    else:
        m[2].metric("Centros de custo", fm.inteiro(len(t)))
    espaco(0.4)

    coluna_valor = "a_cobrar" if chargeback else "realizado"
    por_dir = t.groupby("diretoria")[coluna_valor].sum()
    with st.container(border=True, key="card_aloc_grafico"):
        st.markdown(cp.titulo_card("Custo por diretoria" + (" (a cobrar)" if chargeback else "")),
                    unsafe_allow_html=True)
        grafico(ch.barras_horizontais(list(por_dir.index), list(por_dir.values), altura=300), "pc_aloc")

    cols = ["diretoria", "centro_custo", "realizado", "orcado", "pct_total"] + (["a_cobrar"] if chargeback else [])
    cfg = {
        "diretoria": st.column_config.TextColumn("Diretoria"),
        "centro_custo": st.column_config.TextColumn("Centro de Custo"),
        "realizado": st.column_config.NumberColumn("Realizado (R$)", format="%.0f"),
        "orcado": st.column_config.NumberColumn("Orçado (R$)", format="%.0f"),
        "pct_total": st.column_config.NumberColumn("% do total", format="%.1f"),
        "a_cobrar": st.column_config.NumberColumn("A cobrar (R$)", format="%.0f"),
    }
    st.dataframe(t[cols], column_config=cfg, hide_index=True)
    st.download_button(f"Baixar {modo_fixo} (CSV)", csv_br(t[cols]), file_name=f"{modo_fixo.lower()}.csv",
                       mime="text/csv")


# ============================================================================
# Página: Torre de Controle
# ============================================================================
def pagina_torre(df, ind, f, modo) -> None:
    st.markdown(cp.titulo_pagina("Torre de Controle",
                                 "Consumo do orçamento por centro de custo no período filtrado."),
                unsafe_allow_html=True)
    t = mt.tabela_controle(df, f)
    if t.empty:
        st.info(SEM_DADOS)
        return

    contagem = t["status"].value_counts()
    m = st.columns(3)
    for coluna, rotulo in zip(m, ["🟢 Dentro do previsto", "🟡 Atenção", "🔴 Acima do orçado"]):
        coluna.metric(rotulo, int(contagem.get(rotulo, 0)))
    espaco(0.4)

    cfg = {
        "diretoria": st.column_config.TextColumn("Diretoria"),
        "centro_custo": st.column_config.TextColumn("Centro de Custo"),
        "realizado": st.column_config.NumberColumn("Realizado (R$)", format="%.0f"),
        "orcado": st.column_config.NumberColumn("Orçado (R$)", format="%.0f"),
        "variacao": st.column_config.NumberColumn("Variação (R$)", format="%.0f"),
        "consumo_pct": st.column_config.ProgressColumn("Consumo (%)", min_value=0, max_value=150, format="%.0f"),
        "status": st.column_config.TextColumn("Status"),
    }
    st.dataframe(t, column_config=cfg, hide_index=True)


# ============================================================================
# Página: Operações de TI
# ============================================================================
def pagina_operacoes(df, ind, f, modo) -> None:
    st.markdown(cp.titulo_pagina("Operações de TI",
                                 "Evolução mensal dos indicadores operacionais (respeita Ano e Diretoria)."),
                unsafe_allow_html=True)
    s = mt.serie_indicadores(ind, f)
    if s.empty:
        st.info("Sem tabela de indicadores (data/indicadores.csv) para os filtros selecionados.")
        return
    x = [mt.MESES[int(m) - 1] for m in s.index]
    paineis = [
        ("Usuários ativos", "usuarios_ativos", th.AZUL, "linha", 0),
        ("Equipamentos", "equipamentos", th.AZUL_CLARO, "linha", 0),
        ("Contratos", "contratos", th.ROXO, "barra", 0),
        ("tCO₂e evitadas por mês", "co2_evitado_t", th.VERDE, "barra", 2),
    ]
    for linha in (paineis[:2], paineis[2:]):
        for coluna, (titulo, campo, cor, tipo, casas) in zip(st.columns(2), linha):
            with coluna:
                with st.container(border=True, key=f"card_op_{campo}"):
                    st.markdown(cp.titulo_card(titulo), unsafe_allow_html=True)
                    grafico(ch.serie_simples(x, list(s[campo].values), cor, tipo, casas), f"pc_op_{campo}")
        espaco(0.5)


# ============================================================================
# Página: Relatórios
# ============================================================================
RELATORIOS = {
    "Por diretoria": "diretoria",
    "Por centro de custo": "centro_custo",
    "Por área": "area",
    "Por fornecedor": "fornecedor",
    "Por categoria": "categoria",
    "Por tipo (CAPEX/OPEX)": "tipo",
}


def pagina_relatorios(df, ind, f, modo) -> None:
    st.markdown(cp.titulo_pagina("Relatórios", "Resumos do período filtrado, prontos para baixar."),
                unsafe_allow_html=True)
    escolha = st.selectbox("Relatório", list(RELATORIOS), key="rel_sel")
    coluna = RELATORIOS[escolha]
    t = mt.resumo_por(df, f, coluna)
    if t.empty:
        st.info(SEM_DADOS)
        return

    cfg = {
        coluna: st.column_config.TextColumn(escolha.replace("Por ", "").capitalize()),
        "realizado": st.column_config.NumberColumn("Realizado (R$)", format="%.0f"),
        "orcado": st.column_config.NumberColumn("Orçado (R$)", format="%.0f"),
        "economia": st.column_config.NumberColumn("Economia (R$)", format="%.0f"),
        "variacao": st.column_config.NumberColumn("Variação (R$)", format="%.0f"),
        "consumo_pct": st.column_config.NumberColumn("Consumo (%)", format="%.1f"),
        "pct_total": st.column_config.NumberColumn("% do total", format="%.1f"),
    }
    st.dataframe(t, column_config=cfg, hide_index=True)

    b1, b2 = st.columns([1, 1])
    b1.download_button("Baixar este relatório (CSV)", csv_br(t), file_name=f"relatorio_{coluna}.csv", mime="text/csv")

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as escritor:
        for nome, col in RELATORIOS.items():
            mt.resumo_por(df, f, col).to_excel(escritor, sheet_name=nome.replace("Por ", "")[:31]
                                               .replace("/", "-").replace("(", "").replace(")", ""), index=False)
    b2.download_button("Baixar todos (Excel)", buf.getvalue(), file_name="relatorios_finops.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================================
# Página: Dados
# ============================================================================
def _enviar_tabela(rotulo: str, chave_up: str, chave_sig: str, normalizar, chave_df: str, chave_nome: str) -> None:
    up = st.file_uploader(rotulo, type=["csv", "xlsx", "xls"], key=chave_up)
    if up is None:
        return
    assinatura = f"{up.name}:{up.size}"
    if st.session_state.get(chave_sig) == assinatura:
        return
    try:
        novo = normalizar(dl.ler_tabela(up, up.name))
    except Exception as erro:  # noqa: BLE001 — mostra qualquer problema de leitura ao usuário
        st.error(f"Não consegui usar esse arquivo: {erro}")
        st.session_state[chave_sig] = assinatura
        return
    st.session_state[chave_df] = novo
    st.session_state[chave_nome] = up.name
    st.session_state[chave_sig] = assinatura
    if chave_df == "gastos_upload":
        st.session_state["gastos_upload_hora"] = agora()
    st.rerun()


def pagina_dados(df, ind, f, modo) -> None:
    st.markdown(cp.titulo_pagina("Dados", "Veja a tabela usada pelo dashboard ou envie a sua."),
                unsafe_allow_html=True)

    with st.expander("Enviar tabela real (vale só nesta sessão do navegador)"):
        st.caption("Para tornar definitivo, salve o arquivo como data/gastos.csv (veja o README).")
        _enviar_tabela("Tabela de gastos (.csv ou .xlsx)", "up_gastos", "up_gastos_sig",
                       dl.normalizar_gastos, "gastos_upload", "gastos_upload_nome")
        _enviar_tabela("Tabela de indicadores (opcional)", "up_ind", "up_ind_sig",
                       dl.normalizar_indicadores, "ind_upload", "ind_upload_nome")
        if "gastos_upload" in st.session_state or "ind_upload" in st.session_state:
            if st.button("Voltar aos arquivos da pasta data/"):
                for chave in ("gastos_upload", "gastos_upload_nome", "gastos_upload_hora",
                              "ind_upload", "ind_upload_nome"):
                    st.session_state.pop(chave, None)
                st.rerun()

        modelo = pd.DataFrame([{c: "" for c in dl.COLUNAS_OBRIGATORIAS + dl.COLUNAS_OPCIONAIS}])
        st.download_button("Baixar modelo de colunas (CSV)", csv_br(modelo), file_name="modelo_gastos.csv",
                           mime="text/csv")

    filtrado = mt.recorte(df, f)
    m = st.columns(3)
    m[0].metric("Linhas (filtro atual)", fm.inteiro(len(filtrado)))
    m[1].metric("Linhas (tabela inteira)", fm.inteiro(len(df)))
    m[2].metric("Anos disponíveis", ", ".join(str(a) for a in sorted(df["ano"].unique())))
    st.dataframe(filtrado.head(5000), hide_index=True)
    if len(filtrado) > 5000:
        st.caption("Mostrando as primeiras 5.000 linhas; o download traz todas.")
    st.download_button("Baixar dados filtrados (CSV)", csv_br(filtrado), file_name="dados_filtrados.csv",
                       mime="text/csv")


# ============================================================================
# Página: Ajuda
# ============================================================================
def pagina_ajuda(df, ind, f, modo) -> None:
    st.markdown(cp.titulo_pagina("Ajuda", "Como usar e como trocar os dados fictícios pelos reais."),
                unsafe_allow_html=True)
    st.markdown("""
**Filtros** — Ano, Mês, Diretoria, Centro de Custo, Área e Fornecedor valem para todas as páginas.
Escolher uma diretoria reduz as opções de centro de custo e de área.
Com Mês = *Todos*, o período é de janeiro até o último mês com valor realizado.

**Showback / Chargeback** — o botão no canto superior direito muda o painel *Custos por Diretoria*:
Showback mostra o custo realizado; Chargeback soma a taxa administrativa (ajuste na página Chargeback).

**Cores dos indicadores** — nos custos, subir é vermelho e descer é verde; na economia, é o contrário.

**Troca de dados** — coloque sua tabela em `data/gastos.csv` (ou `.xlsx` renomeando em `config.py`)
com as colunas abaixo, ou envie pela página *Dados*.

| Coluna | Descrição |
|---|---|
| `ano`, `mes` | Ano e mês (1–12 ou Jan, Fev…) |
| `diretoria`, `centro_custo`, `area` | Estrutura organizacional |
| `fornecedor`, `categoria` | Quem recebe e em que grupo o gasto entra |
| `tipo` | `CAPEX` ou `OPEX` |
| `realizado` | Gasto efetivo (deixe vazio nos meses futuros) |
| `orcado` | Orçamento do mês |
| `forecast` *(opcional)* | Projeção; se faltar, usa o realizado |
| `economia` *(opcional)* | Saving obtido no mês |

`data/indicadores.csv` (opcional) alimenta usuários, equipamentos, contratos e tCO₂e: colunas
`ano, mes, diretoria, usuarios_ativos, equipamentos, contratos, co2_evitado_t`.
""")


# ============================================================================
# Navegação
# ============================================================================
PAGINAS = {
    "⌂  Visão Geral": pagina_visao_geral,
    "◧  Showback": lambda df, ind, f, modo: pagina_alocacao(df, ind, f, "Showback"),
    "◨  Chargeback": lambda df, ind, f, modo: pagina_alocacao(df, ind, f, "Chargeback"),
    "✺  Torre de Controle": pagina_torre,
    "▣  Operações de TI": pagina_operacoes,
    "☰  Relatórios": pagina_relatorios,
    "⛁  Dados": pagina_dados,
    "?  Ajuda": pagina_ajuda,
}


def main() -> None:
    df, ind, atualizado, origem = obter_dados()

    with st.sidebar:
        st.markdown(cp.marca_html(), unsafe_allow_html=True)
        pagina = st.radio("Menu", list(PAGINAS), key="nav", label_visibility="collapsed")
        st.markdown(cp.sidebar_rodape_html(), unsafe_allow_html=True)

    if getattr(config, "ANIMACOES", True):  # para desligar: ANIMACOES = False em config.py
        st.markdown(styles.css_animacao(list(PAGINAS).index(pagina)), unsafe_allow_html=True)
        st.markdown(cp.boot_html(), unsafe_allow_html=True)   # varredura de tela (separado do <style>)
    travar_digitacao_nos_seletores()
    st.markdown(cp.cabecalho_html(agora()), unsafe_allow_html=True)
    filtros, modo = barra_filtros(df)
    PAGINAS[pagina](df, ind, filtros, modo)
    st.markdown(cp.rodape_html(atualizado, origem), unsafe_allow_html=True)


main()
