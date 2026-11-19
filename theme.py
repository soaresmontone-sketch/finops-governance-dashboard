"""Cores e paletas do tema escuro (azul/neon)."""

AZUL = "#1E88FF"
AZUL_CLARO = "#4DA3FF"
VERDE = "#1FE0A5"
AMARELO = "#F5C518"
VERMELHO = "#FF4D5E"
ROXO = "#8A63F5"
ROSA = "#FF5C7A"
INDIGO = "#5B6CFF"
TEAL = "#139A9A"

FUNDO = "#050B18"
TEXTO = "#E6EEF8"
MUTED = "#8FA6C4"
GRADE = "rgba(120,160,220,0.12)"

CORES_CATEGORIA = {
    "Workplace": "#2C9BFF",
    "Infraestrutura": "#1769FF",
    "Telecom": VERDE,
    "Projetos": ROSA,
    "Segurança": ROXO,
    "Service Desk": INDIGO,
}
# Usadas quando surgir uma categoria que não está acima (dados reais).
PALETA = ["#2C9BFF", "#1769FF", VERDE, ROSA, ROXO, INDIGO, AMARELO, TEAL, "#FF9F43", "#9AA9BF"]

CORES_TIPO = {"OPEX": AZUL, "CAPEX": ROXO}


def cor_categoria(nome: str, indice: int) -> str:
    return CORES_CATEGORIA.get(nome, PALETA[indice % len(PALETA)])
