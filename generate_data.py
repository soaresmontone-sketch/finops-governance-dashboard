"""Gera dados FICTÍCIOS para o dashboard (data/gastos.csv e data/indicadores.csv).

Uso:  python generate_data.py

Quando você tiver a tabela real, NÃO precisa rodar este script: basta colocar
seus dados em data/gastos.csv (ou enviar pela página "Dados" do dashboard).
O formato esperado das colunas está no README.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import config

SEED = 2025
ANOS = (2024, 2025)
MES_ATUAL = 8  # em 2025 só existe "realizado" até agosto

# diretoria: (peso %, [(código, nome do centro de custo, área)])
DIRETORIAS = {
    "Produção": (28, [("CC-1001", "Usinagem", "Manufatura"), ("CC-1002", "Montagem", "Manufatura"),
                      ("CC-1003", "Pintura", "Manufatura"), ("CC-1004", "Qualidade Industrial", "Qualidade")]),
    "Supply Chain": (17, [("CC-2001", "Compras", "Suprimentos"), ("CC-2002", "Logística", "Logística"),
                          ("CC-2003", "Armazém", "Logística")]),
    "Administrativo": (15, [("CC-3001", "Facilities", "Facilities"), ("CC-3002", "Jurídico", "Corporativo"),
                            ("CC-3003", "Diretoria Geral", "Corporativo")]),
    "Financeiro": (12, [("CC-4001", "Controladoria", "Finanças"), ("CC-4002", "Tesouraria", "Finanças"),
                        ("CC-4003", "Fiscal", "Finanças")]),
    "RH": (8, [("CC-5001", "Recrutamento", "Pessoas"), ("CC-5002", "Treinamento", "Pessoas")]),
    "Comercial": (7, [("CC-6001", "Vendas", "Vendas"), ("CC-6002", "Pós-venda", "Vendas"),
                      ("CC-6003", "Marketing", "Marketing")]),
    "P&D": (6, [("CC-7001", "Engenharia de Produto", "Engenharia"), ("CC-7002", "Laboratório", "Engenharia"),
                ("CC-7003", "Inovação", "Engenharia")]),
    "Outros": (8, [("CC-9001", "Segurança do Trabalho", "Operações"), ("CC-9002", "Sustentabilidade", "Operações"),
                   ("CC-9003", "Projetos Especiais", "Operações")]),
}

# fornecedor, peso % do total, divisão por categoria
FORNECEDORES = [
    ("Microsoft", 25, {"Workplace": 0.75, "Infraestrutura": 0.15, "Segurança": 0.10}),
    ("Dell", 14, {"Workplace": 0.50, "Infraestrutura": 0.50}),
    ("SAP", 10, {"Projetos": 0.80, "Infraestrutura": 0.20}),
    ("Vivo", 9, {"Telecom": 1.0}),
    ("Oracle", 7, {"Infraestrutura": 0.60, "Projetos": 0.40}),
    ("Claro", 6, {"Telecom": 1.0}),
    ("VMware", 5, {"Infraestrutura": 1.0}),
    ("Fortinet", 4, {"Segurança": 1.0}),
    ("Lenovo", 3, {"Workplace": 1.0}),
    ("Outros", 17, {"Service Desk": 0.30, "Projetos": 0.15, "Telecom": 0.20,
                    "Segurança": 0.10, "Workplace": 0.15, "Infraestrutura": 0.10}),
]

CAPEX_POR_CATEGORIA = {"Workplace": 0.30, "Infraestrutura": 0.25, "Telecom": 0.05,
                       "Projetos": 0.30, "Segurança": 0.12, "Service Desk": 0.0}

# Totais-alvo do período jan–ago (para os números ficarem parecidos com o layout de referência)
ALVOS = {
    2025: {"realizado": 12_450_230.0, "orcado": 14_300_000.0, "economia": 1_870_320.0},
    2024: {"realizado": 12_450_230.0 / 1.052, "orcado": 13_250_000.0, "economia": 1_870_320.0 / 1.124},
}


def distribuir_inteiro(total: int, pesos) -> np.ndarray:
    """Reparte um total inteiro entre pesos, garantindo que a soma fecha."""
    pesos = np.array(pesos, dtype=float)
    pesos = pesos / pesos.sum()
    base = np.floor(total * pesos).astype(int)
    resto = int(total - base.sum())
    ordem = np.argsort(-(total * pesos - base))
    for i in range(resto):
        base[ordem[i]] += 1
    return base


def gerar_gastos(rng: np.random.Generator) -> pd.DataFrame:
    cc_fator = {cod: rng.uniform(0.8, 1.2) for _, ccs in DIRETORIAS.values() for cod, _, _ in ccs}
    linhas = []
    for ano in ANOS:
        for mes in range(1, 13):
            sazon_real = 0.85 + 0.045 * (mes - 1)   # gasto cresce ao longo do ano
            sazon_orc = 0.95 + 0.035 * (mes - 1)    # orçamento é mais suave
            sazon_eco = 0.5 + 0.1 * mes             # economia cresce
            for dire, (peso, ccs) in DIRETORIAS.items():
                for cod, nome, area in ccs:
                    cc_peso = peso / len(ccs) * cc_fator[cod]
                    for forn, sup_peso, divisao in FORNECEDORES:
                        for cat, frac in divisao.items():
                            cap = CAPEX_POR_CATEGORIA[cat]
                            for tipo, ftipo in (("OPEX", 1 - cap), ("CAPEX", cap)):
                                if ftipo <= 0:
                                    continue
                                base = cc_peso * sup_peso * frac * ftipo
                                real = base * sazon_real * rng.lognormal(0, 0.07)
                                orc = base * sazon_orc * rng.lognormal(0, 0.02)
                                eco = real * sazon_eco * rng.uniform(0.6, 1.4)
                                linhas.append((ano, mes, dire, f"{cod} {nome}", area, forn, cat, tipo, real, orc, eco))

    df = pd.DataFrame(linhas, columns=[
        "ano", "mes", "diretoria", "centro_custo", "area", "fornecedor", "categoria", "tipo",
        "real_raw", "orc_raw", "eco_raw",
    ])
    for destino in ("realizado", "orcado", "economia"):
        df[destino] = np.nan

    for ano, alvo in ALVOS.items():
        m_ano = df["ano"] == ano
        m_ytd = m_ano & (df["mes"] <= MES_ATUAL)
        for destino, raw in (("realizado", "real_raw"), ("orcado", "orc_raw"), ("economia", "eco_raw")):
            fator = alvo[destino] / df.loc[m_ytd, raw].sum()
            df.loc[m_ano, destino] = df.loc[m_ano, raw] * fator

    futuro = (df["ano"] == 2025) & (df["mes"] > MES_ATUAL)
    df.loc[futuro, "realizado"] = np.nan
    df.loc[futuro, "economia"] = 0.0

    ytd25 = (df["ano"] == 2025) & (df["mes"] <= MES_ATUAL)
    ritmo = df.loc[ytd25, "realizado"].sum() / df.loc[ytd25, "orcado"].sum()
    df["forecast"] = df["realizado"]
    df.loc[futuro, "forecast"] = df.loc[futuro, "orcado"] * ritmo * 1.03

    df = df.drop(columns=["real_raw", "orc_raw", "eco_raw"])
    df[["realizado", "orcado", "forecast", "economia"]] = df[["realizado", "orcado", "forecast", "economia"]].round(2)
    return df.sort_values(["ano", "mes", "diretoria", "centro_custo", "fornecedor", "categoria", "tipo"]).reset_index(drop=True)


def gerar_indicadores() -> pd.DataFrame:
    nomes = list(DIRETORIAS)
    pesos = [p for p, _ in DIRETORIAS.values()]
    usuarios_ago = {2025: 5892, 2024: round(5892 / 1.021)}
    equip_ago = {2025: 8451, 2024: round(8451 / 1.043)}
    co2_ytd = {2025: 12.4, 2024: 12.4 / 1.18}
    soma_w = sum(0.8 + 0.05 * m for m in range(1, MES_ATUAL + 1))

    linhas = []
    for ano in ANOS:
        fator_co2 = co2_ytd[ano] / soma_w
        for mes in range(1, 13):
            if ano == 2025 and mes > MES_ATUAL:
                continue
            usuarios = distribuir_inteiro(usuarios_ago[ano] - 12 * (MES_ATUAL - mes), pesos)
            equip = distribuir_inteiro(equip_ago[ano] - 20 * (MES_ATUAL - mes), pesos)
            contratos = distribuir_inteiro(324, pesos)
            co2_total = (0.8 + 0.05 * mes) * fator_co2
            share = np.array(pesos, dtype=float) / sum(pesos)
            for i, dire in enumerate(nomes):
                linhas.append((ano, mes, dire, int(usuarios[i]), int(equip[i]), int(contratos[i]),
                               round(float(co2_total * share[i]), 4)))
    return pd.DataFrame(linhas, columns=["ano", "mes", "diretoria", "usuarios_ativos", "equipamentos",
                                         "contratos", "co2_evitado_t"])


def main() -> None:
    rng = np.random.default_rng(SEED)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    gastos = gerar_gastos(rng)
    ind = gerar_indicadores()
    gastos.to_csv(config.ARQ_GASTOS, index=False)
    ind.to_csv(config.ARQ_INDICADORES, index=False)

    a25 = gastos[(gastos.ano == 2025) & (gastos.mes <= MES_ATUAL)]
    print(f"gastos.csv: {len(gastos):,} linhas  |  indicadores.csv: {len(ind):,} linhas")
    print(f"2025 jan-ago  realizado={a25.realizado.sum():,.0f}  orcado={a25.orcado.sum():,.0f}  "
          f"economia={a25.economia.sum():,.0f}")


if __name__ == "__main__":
    main()
