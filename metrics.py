"""Cálculos do dashboard (KPIs, séries, tabelas). Só depende de pandas/numpy,
por isso pode ser testado sem abrir o Streamlit."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

import config

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
TODOS = "Todos"


@dataclass(frozen=True)
class Filtros:
    ano: int
    mes: int | None = None          # None = todos os meses
    diretoria: str | None = None
    centro_custo: str | None = None
    area: str | None = None
    fornecedor: str | None = None


# ----------------------------------------------------------------------------
# Recortes
# ----------------------------------------------------------------------------
def ultimo_mes_realizado(df: pd.DataFrame, ano: int) -> int:
    d = df[(df["ano"] == ano) & (df["realizado"] > 0)]
    return int(d["mes"].max()) if len(d) else 0


def meses_do_periodo(df: pd.DataFrame, f: Filtros) -> list[int]:
    """Mês escolhido, ou (se 'Todos') de janeiro até o último mês com realizado."""
    if f.mes:
        return [f.mes]
    return list(range(1, ultimo_mes_realizado(df, f.ano) + 1))


def _mask_dimensoes(df: pd.DataFrame, f: Filtros) -> pd.Series:
    m = pd.Series(True, index=df.index)
    for col, val in (("diretoria", f.diretoria), ("centro_custo", f.centro_custo),
                     ("area", f.area), ("fornecedor", f.fornecedor)):
        if val:
            m &= df[col] == val
    return m


def recorte(df: pd.DataFrame, f: Filtros, ano: int | None = None, meses: list[int] | None = None) -> pd.DataFrame:
    ano = f.ano if ano is None else ano
    d = df[(df["ano"] == ano) & _mask_dimensoes(df, f)]
    if meses is not None:
        d = d[d["mes"].isin(meses)]
    return d


def variacao_pct(atual, anterior):
    if anterior is None or pd.isna(anterior) or anterior == 0:
        return None
    return (atual / anterior - 1.0) * 100.0


# ----------------------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------------------
def _usuarios(ind: pd.DataFrame, ano: int, mes: int, diretoria: str | None) -> float:
    d = ind[(ind["ano"] == ano) & (ind["mes"] == mes)]
    if diretoria:
        d = d[d["diretoria"] == diretoria]
    return float(d["usuarios_ativos"].sum())


def _custo_por_usuario(df, ind, f: Filtros, ano: int, mes: int):
    usuarios = _usuarios(ind, ano, mes, f.diretoria)
    if not usuarios:
        return None
    custo = recorte(df, f, ano=ano, meses=[mes])["realizado"].sum()
    return custo / usuarios if custo else None


def calcular_kpis(df: pd.DataFrame, ind: pd.DataFrame, f: Filtros) -> dict:
    meses = meses_do_periodo(df, f)
    atual = recorte(df, f, meses=meses)
    anterior = recorte(df, f, ano=f.ano - 1, meses=meses)

    total, total_ant = atual["realizado"].sum(), anterior["realizado"].sum()
    mes_ref = f.mes or (meses[-1] if meses else 0)

    if mes_ref > 1:
        ano_ant_mes, mes_ant = f.ano, mes_ref - 1
    else:
        ano_ant_mes, mes_ant = f.ano - 1, 12
    cpu = _custo_por_usuario(df, ind, f, f.ano, mes_ref) if mes_ref else None
    cpu_ant = _custo_por_usuario(df, ind, f, ano_ant_mes, mes_ant) if mes_ref else None

    cc = atual.loc[atual["realizado"] > 0, "centro_custo"].nunique()
    cc_ant = anterior.loc[anterior["realizado"] > 0, "centro_custo"].nunique()

    eco, eco_ant = atual["economia"].sum(), anterior["economia"].sum()

    fc = recorte(df, f)["forecast"].sum()
    fc_ant = recorte(df, f, ano=f.ano - 1)["forecast"].sum()

    orcado = atual["orcado"].sum()
    consumo = (total / orcado * 100.0) if orcado else 0.0

    return {
        "meses": meses, "mes_ref": mes_ref,
        "total": total, "d_total": variacao_pct(total, total_ant),
        "custo_usuario": cpu,
        "d_custo_usuario": variacao_pct(cpu, cpu_ant) if (cpu and cpu_ant) else None,
        "cc_ativos": cc, "d_cc": variacao_pct(cc, cc_ant),
        "economia": eco, "d_economia": variacao_pct(eco, eco_ant),
        "forecast": fc, "d_forecast": variacao_pct(fc, fc_ant),
        "orcado_periodo": orcado, "consumo_pct": consumo,
    }


def indicadores_operacionais(df: pd.DataFrame, ind: pd.DataFrame, f: Filtros, meses: list[int], mes_ref: int) -> dict:
    """Usuários, equipamentos, contratos (no mês de referência) e CO2 (acumulado do período).
    Esses indicadores respeitam Ano, Mês e Diretoria (não existem por centro de custo/fornecedor)."""
    def base(ano):
        d = ind[ind["ano"] == ano]
        return d[d["diretoria"] == f.diretoria] if f.diretoria else d

    atual, anterior = base(f.ano), base(f.ano - 1)

    def no_mes(d, col, mes):
        return float(d.loc[d["mes"] == mes, col].sum())

    def acumulado(d, col):
        return float(d.loc[d["mes"].isin(meses), col].sum())

    out = {}
    for chave, col in (("usuarios", "usuarios_ativos"), ("equipamentos", "equipamentos"), ("contratos", "contratos")):
        v, v_ant = no_mes(atual, col, mes_ref), no_mes(anterior, col, mes_ref)
        out[chave] = (v if v else None, variacao_pct(v, v_ant) if v else None)
    co2, co2_ant = acumulado(atual, "co2_evitado_t"), acumulado(anterior, "co2_evitado_t")
    out["co2"] = (co2 if co2 else None, variacao_pct(co2, co2_ant) if co2 else None)
    return out


# ----------------------------------------------------------------------------
# Séries e agrupamentos
# ----------------------------------------------------------------------------
def serie_mensal(df: pd.DataFrame, f: Filtros):
    """Ano inteiro (12 meses), respeitando as dimensões do filtro (não o mês)."""
    d = recorte(df, f)
    g = d.groupby("mes")[["realizado", "orcado", "forecast"]].sum().reindex(range(1, 13), fill_value=0.0)
    ult = ultimo_mes_realizado(df, f.ano)
    g["realizado_plot"] = g["realizado"].where(g.index <= ult)
    return g, ult


def _periodo(df, f):
    return recorte(df, f, meses=meses_do_periodo(df, f))


def por_categoria(df, f) -> pd.Series:
    return _periodo(df, f).groupby("categoria")["realizado"].sum().sort_values(ascending=False)


def por_fornecedor(df, f, coluna: str = "realizado", top: int = 10) -> pd.Series:
    s = _periodo(df, f).groupby("fornecedor")[coluna].sum()
    s = s[s > 0].sort_values(ascending=False)
    # "Outros" (se existir) sempre entra como último bloco do Top
    if "Outros" in s.index:
        outros = s.pop("Outros")
        s = s.head(top - 1)
        s["Outros"] = outros
        return s
    return s.head(top)


def por_diretoria(df, f) -> pd.DataFrame:
    g = _periodo(df, f).groupby("diretoria")[["realizado", "orcado"]].sum()
    return g.sort_values("realizado", ascending=False)


def capex_opex(df, f) -> pd.Series:
    return _periodo(df, f).groupby("tipo")["realizado"].sum().sort_values(ascending=False)


def saving_serie(df: pd.DataFrame, f: Filtros, periodicidade: str = "Mensal"):
    """Retorna (rótulos, valores). Respeita as dimensões do filtro, ano inteiro até o último mês realizado."""
    ult = ultimo_mes_realizado(df, f.ano)
    g = recorte(df, f).groupby("mes")["economia"].sum().reindex(range(1, 13), fill_value=0.0)
    if periodicidade == "Trimestral":
        rot, val = [], []
        for q in range(4):
            if ult >= q * 3 + 1:
                rot.append(f"T{q + 1}")
                val.append(float(g.loc[q * 3 + 1:q * 3 + 3].sum()))
        return rot, val
    return MESES[:ult], [float(v) for v in g.loc[1:ult].values]


def serie_indicadores(ind: pd.DataFrame, f: Filtros) -> pd.DataFrame:
    d = ind[ind["ano"] == f.ano]
    if f.diretoria:
        d = d[d["diretoria"] == f.diretoria]
    cols = ["usuarios_ativos", "equipamentos", "contratos", "co2_evitado_t"]
    return d.groupby("mes")[cols].sum().reindex(range(1, 13)).dropna(how="all")


# ----------------------------------------------------------------------------
# Tabelas (Torre de Controle, Showback/Chargeback, Relatórios)
# ----------------------------------------------------------------------------
def status_consumo(consumo_pct: float) -> str:
    if consumo_pct != consumo_pct:  # NaN
        return "Sem orçamento"
    c = consumo_pct / 100.0
    if c > config.LIMITE_CRITICO:
        return "🔴 Acima do orçado"
    if c > config.LIMITE_ATENCAO:
        return "🟡 Atenção"
    return "🟢 Dentro do previsto"


def tabela_controle(df, f) -> pd.DataFrame:
    g = _periodo(df, f).groupby(["diretoria", "centro_custo"], as_index=False)[["realizado", "orcado"]].sum()
    g["variacao"] = g["realizado"] - g["orcado"]
    g["consumo_pct"] = g["realizado"] / g["orcado"].where(g["orcado"] > 0) * 100.0
    g["status"] = g["consumo_pct"].map(status_consumo)
    return g.sort_values("consumo_pct", ascending=False, na_position="last").reset_index(drop=True)


def tabela_alocacao(df, ind, f, taxa: float = 0.0) -> pd.DataFrame:
    """Showback (taxa=0) / Chargeback (taxa>0): custo por diretoria e centro de custo."""
    meses = meses_do_periodo(df, f)
    g = _periodo(df, f).groupby(["diretoria", "centro_custo"], as_index=False)[["realizado", "orcado"]].sum()
    total = g["realizado"].sum()
    g["pct_total"] = g["realizado"] / total * 100.0 if total else 0.0
    g["a_cobrar"] = g["realizado"] * (1.0 + taxa)
    mes_ref = f.mes or (meses[-1] if meses else 0)
    usuarios_dir = ind[(ind["ano"] == f.ano) & (ind["mes"] == mes_ref)].groupby("diretoria")["usuarios_ativos"].sum()
    g["usuarios_dir"] = g["diretoria"].map(usuarios_dir)
    return g.sort_values("realizado", ascending=False).reset_index(drop=True)


def resumo_por(df, f, coluna: str) -> pd.DataFrame:
    g = _periodo(df, f).groupby(coluna)[["realizado", "orcado", "economia"]].sum()
    g["variacao"] = g["realizado"] - g["orcado"]
    g["consumo_pct"] = g["realizado"] / g["orcado"].where(g["orcado"] > 0) * 100.0
    total = g["realizado"].sum()
    g["pct_total"] = g["realizado"] / total * 100.0 if total else 0.0
    return g.sort_values("realizado", ascending=False).reset_index()
