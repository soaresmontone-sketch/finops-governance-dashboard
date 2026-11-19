"""Configurações gerais do dashboard.

Edite este arquivo para trocar textos, nome da empresa e regras de negócio.
Logo e imagem do painel ficam na pasta `assets/` (veja o README).
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Arquivos de dados (troque pelos seus quando tiver a tabela real)
ARQ_GASTOS = DATA_DIR / "gastos.csv"
ARQ_INDICADORES = DATA_DIR / "indicadores.csv"

# ----------------------------------------------------------------------------
# Textos
# ----------------------------------------------------------------------------
APP_TITULO = "FinOps Governance Center"
APP_SUBTITULO = "Governança de custos de TI"
APP_PILARES = "Transparência | Eficiência | Inovação"
APP_LEMA_1 = "Visibilidade hoje."
APP_LEMA_2 = "Decisões melhores amanhã."

# Nome fictício de empresa (não use a marca de uma empresa real em versão pública).
EMPRESA = "ACME INDUSTRIAL"
EMPRESA_LEMA = "Demonstração de portfólio"
CIDADE = "São Paulo, SP"
RODAPE_FRASE = "Governança financeira de TI"
SIDEBAR_FRASE = "Cada real sob controle"
VERSAO = "v1.0"

# Aviso mostrado no rodapé. Preencha AUTOR (e, se quiser, LINK_PERFIL) para assinar o projeto.
AVISO_DEMO = "Projeto de portfólio · todos os dados são fictícios"
AUTOR = ""          # ex.: "Maria Silva"
LINK_PERFIL = ""    # ex.: "https://www.linkedin.com/in/seu-perfil"

# Painel decorativo (no lugar da foto). Se existir assets/painel.jpg (ou .png),
# ele aparece por baixo de uma camada translúcida azul.
PAINEL_PALAVRAS = ["Dados", "Governança", "Eficiência"]
PAINEL_FRASE = ["Gestão de custos", "com transparência"]

# ----------------------------------------------------------------------------
# Regras de negócio
# ----------------------------------------------------------------------------
# Taxa administrativa aplicada sobre o realizado no modo Chargeback (5% = 0.05).
TAXA_CHARGEBACK = 0.05

# Consumo do orçamento: acima de LIMITE_ATENCAO = "Atenção"; acima de
# LIMITE_CRITICO = "Acima do orçado".
LIMITE_ATENCAO = 0.95
LIMITE_CRITICO = 1.00
