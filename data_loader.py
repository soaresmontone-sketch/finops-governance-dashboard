"""Leitura e normalização das tabelas (CSV ou Excel). Só depende de pandas."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

COLUNAS_OBRIGATORIAS = ["ano", "mes", "diretoria", "centro_custo", "area", "fornecedor",
                        "categoria", "tipo", "realizado", "orcado"]
COLUNAS_OPCIONAIS = ["forecast", "economia"]
COLUNAS_INDICADORES = ["ano", "mes", "diretoria", "usuarios_ativos", "equipamentos",
                       "contratos", "co2_evitado_t"]

_MAPA_MES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
             "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def ler_tabela(origem, nome: str | None = None) -> pd.DataFrame:
    """Lê .csv (separador detectado automaticamente) ou .xlsx/.xls."""
    nome = (nome or str(origem)).lower()
    if nome.endswith((".xlsx", ".xlsm", ".xls")):
        return pd.read_excel(origem)
    return pd.read_csv(origem, sep=None, engine="python", encoding_errors="replace")


def _numero(serie: pd.Series) -> pd.Series:
    """Converte para número aceitando 'R$ 1.234,56' e '1234.56'."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    s = serie.astype(str).str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)
    tem_virgula = s.str.contains(",", regex=False)
    convertido = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    s = s.where(~tem_virgula, convertido)
    return pd.to_numeric(s, errors="coerce")


def _mes(serie: pd.Series) -> pd.Series:
    """Aceita 1..12, 'Jan', 'janeiro'..."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    t = serie.astype(str).str.strip().str.lower()
    numerico = pd.to_numeric(t, errors="coerce")
    por_nome = t.str[:3].map(_MAPA_MES)
    return numerico.where(numerico.notna(), por_nome)


# Nomes alternativos aceitos para as colunas (já sem acento, minúsculos, com "_").
_APELIDOS = {
    "centro_de_custo": "centro_custo", "centrocusto": "centro_custo", "cc": "centro_custo",
    "diretorias": "diretoria", "fornecedores": "fornecedor", "categorias": "categoria",
    "capex_opex": "tipo", "capex/opex": "tipo",
    "valor_realizado": "realizado", "gasto": "realizado", "gasto_realizado": "realizado", "real": "realizado",
    "orcamento": "orcado", "valor_orcado": "orcado", "budget": "orcado",
    "previsao": "forecast", "projecao": "forecast",
    "saving": "economia", "savings": "economia",
    "usuarios": "usuarios_ativos", "co2_evitado": "co2_evitado_t", "tco2e": "co2_evitado_t",
}


def _nome_coluna(c) -> str:
    """'Orçado ' -> 'orcado'; 'Centro de Custo' -> 'centro_custo' (sem acento, minúsculo)."""
    s = unicodedata.normalize("NFKD", str(c)).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[\s\-]+", "_", s.strip().lower())
    return _APELIDOS.get(s, s)


def _limpar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [_nome_coluna(c) for c in df.columns]
    return df


def normalizar_gastos(df: pd.DataFrame) -> pd.DataFrame:
    df = _limpar_colunas(df)
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ValueError("Colunas obrigatórias ausentes na tabela de gastos: " + ", ".join(faltando))

    for c in ("diretoria", "centro_custo", "area", "fornecedor", "categoria"):
        df[c] = df[c].astype(str).str.strip()
    df["tipo"] = df["tipo"].astype(str).str.strip().str.upper()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["mes"] = _mes(df["mes"])
    df = df.dropna(subset=["ano", "mes"]).copy()
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)

    for c in ("realizado", "orcado", "forecast", "economia"):
        if c in df.columns:
            df[c] = _numero(df[c])

    df["orcado"] = df["orcado"].fillna(0.0)
    if "forecast" not in df.columns:
        df["forecast"] = df["realizado"].fillna(df["orcado"])
    if "economia" not in df.columns:
        df["economia"] = 0.0
    df["economia"] = df["economia"].fillna(0.0)
    return df.reset_index(drop=True)


def normalizar_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    df = _limpar_colunas(df)
    faltando = [c for c in COLUNAS_INDICADORES if c not in df.columns]
    if faltando:
        raise ValueError("Colunas ausentes na tabela de indicadores: " + ", ".join(faltando))
    df["diretoria"] = df["diretoria"].astype(str).str.strip()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df["mes"] = _mes(df["mes"])
    df = df.dropna(subset=["ano", "mes"]).copy()
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)
    for c in ("usuarios_ativos", "equipamentos", "contratos", "co2_evitado_t"):
        df[c] = _numero(df[c]).fillna(0.0)
    return df.reset_index(drop=True)


def indicadores_vazio() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUNAS_INDICADORES).astype(
        {"ano": int, "mes": int, "diretoria": str, "usuarios_ativos": float,
         "equipamentos": float, "contratos": float, "co2_evitado_t": float})


def carregar_gastos(caminho) -> pd.DataFrame:
    return normalizar_gastos(ler_tabela(caminho))


def carregar_indicadores(caminho) -> pd.DataFrame:
    if not Path(caminho).exists():
        return indicadores_vazio()
    return normalizar_indicadores(ler_tabela(caminho))
