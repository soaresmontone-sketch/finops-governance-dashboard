"""Formatação de números e datas no padrão brasileiro (sem depender de locale)."""
from __future__ import annotations

MESES_EXTENSO = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _vazio(v) -> bool:
    return v is None or v != v  # None ou NaN


def _sep_pt(texto: str) -> str:
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def num(v, casas: int = 0) -> str:
    """1234567.8 -> '1.234.568' (casas=0) ou '1.234.567,80' (casas=2)."""
    if _vazio(v):
        return "—"
    return _sep_pt(f"{v:,.{casas}f}")


def inteiro(v) -> str:
    return num(v, 0)


def brl(v, casas: int = 0) -> str:
    """R$ 12.450.230"""
    if _vazio(v):
        return "—"
    return "R$ " + num(v, casas)


def mi(v, casas: int = 2) -> str:
    """R$ 12,45M"""
    if _vazio(v):
        return "—"
    return "R$ " + num(v / 1e6, casas) + "M"


def pct(v, casas: int = 1) -> str:
    if _vazio(v):
        return "—"
    return num(v, casas) + "%"


def data_extenso(dt) -> str:
    return f"{dt.day} de {MESES_EXTENSO[dt.month - 1]} de {dt.year}"
