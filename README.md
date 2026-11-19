# FinOps Governance Center

Dashboard interativo de governança de custos de TI, com tema escuro azul/neon.
Feito em **Python + Streamlit + Plotly**, roda no VS Code e abre no navegador.

Os números que vêm junto são **fictícios**. Quando você tiver a tabela real, basta trocar o arquivo
(veja [Trocar os dados fictícios pelos reais](#trocar-os-dados-fictícios-pelos-reais)).

## O que tem no dashboard

- **Menu lateral** com 8 páginas: Visão Geral, Showback, Chargeback, Torre de Controle, Operações de TI, Relatórios, Dados e Ajuda.
- **Filtros** (valem em todas as páginas): Ano, Mês, Diretoria, Centro de Custo, Área e Fornecedor, mais o botão **Showback / Chargeback**.
- **Visão Geral**:
  - 6 cards de KPI: Total Spend TI, Custo por Usuário, Centros de Custo Ativos, Economia Acumulada, Forecast do ano e Orçamento Utilizado
  - Evolução de Gastos (Realizado × Forecast × Orçamento) e medidor *Budget Consumed*
  - Painel translúcido (no lugar da foto), distribuição por categoria, Top 10 Fornecedores (treemap) e Custos por Diretoria
  - Principais Indicadores, CAPEX × OPEX e Saving Tracker (mensal ou trimestral)
- **Showback / Chargeback**: tabela e gráfico por diretoria e centro de custo, com taxa administrativa ajustável no Chargeback.
- **Torre de Controle**: consumo do orçamento por centro de custo, com status 🟢 🟡 🔴.
- **Operações de TI**: usuários, equipamentos, contratos e tCO₂e mês a mês.
- **Relatórios**: resumos por diretoria, centro de custo, área, fornecedor, categoria e tipo, com download em CSV e Excel.
- **Dados**: veja a tabela, baixe o filtro atual ou envie a sua tabela real pelo navegador.

## Requisitos

- **Python 3.10 ou mais novo** (https://www.python.org/downloads/). No Windows, marque *Add Python to PATH* na instalação.
- **VS Code** com a extensão **Python** (da Microsoft).
- Internet só na primeira vez, para instalar as bibliotecas.

## Passo a passo no VS Code

1. Descompacte a pasta e abra no VS Code: **File → Open Folder…** e escolha `finops-dashboard`.
2. Abra o terminal do VS Code (**Ctrl + `**) e rode, linha por linha:

   **Windows (PowerShell)**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   streamlit run app.py
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. O navegador abre sozinho em **http://localhost:8501**. Se não abrir, copie esse endereço.
4. Para parar, volte ao terminal e aperte **Ctrl + C**.

Nas próximas vezes, só precisa ativar o ambiente (`.venv\Scripts\Activate.ps1` ou `source .venv/bin/activate`) e rodar `streamlit run app.py`.

> **Dica:** se o VS Code perguntar qual interpretador usar, escolha o que está em `.venv`
> (**Ctrl + Shift + P → Python: Select Interpreter**). Se aparecer o erro *"a execução de scripts foi desabilitada"* no PowerShell,
> rode `Set-ExecutionPolicy -Scope Process Bypass` e ative o ambiente de novo.
>
> **Opcional:** a tecla **F5** também inicia o dashboard (configuração em `.vscode/launch.json`).

## Estrutura de pastas

```
finops-dashboard/
├── app.py               # aplicação: menu, filtros e páginas
├── config.py            # textos, nome da empresa, taxa do chargeback, limites
├── metrics.py           # cálculos (KPIs, séries, tabelas)
├── charts.py            # gráficos Plotly
├── components.py        # blocos HTML (cards, cabeçalho, painel, rodapé)
├── styles.py            # CSS do tema escuro
├── theme.py             # cores e paletas
├── formatters.py        # formatação em padrão brasileiro (R$ 1.234,56)
├── data_loader.py       # leitura de CSV/Excel e normalização
├── generate_data.py     # gera os dados fictícios
├── requirements.txt
├── .streamlit/config.toml   # tema escuro do Streamlit
├── .vscode/launch.json      # F5 para rodar
├── assets/              # coloque aqui logo.png e painel.jpg (opcional)
└── data/
    ├── gastos.csv       # tabela principal (fictícia)
    └── indicadores.csv  # usuários, equipamentos, contratos, tCO₂e (fictícia)
```

## Trocar os dados fictícios pelos reais

### Tabela principal: `data/gastos.csv`

Uma linha por **mês × centro de custo × fornecedor × categoria × tipo**. Colunas:

| Coluna | Obrigatória | Descrição |
|---|---|---|
| `ano` | sim | Ex.: 2025 |
| `mes` | sim | 1 a 12 (também aceita Jan, Fev… ou janeiro, fevereiro…) |
| `diretoria` | sim | Ex.: Produção |
| `centro_custo` | sim | Ex.: `CC-1001 Usinagem` |
| `area` | sim | Ex.: Manufatura |
| `fornecedor` | sim | Ex.: Microsoft |
| `categoria` | sim | Ex.: Workplace, Infraestrutura, Telecom… |
| `tipo` | sim | `CAPEX` ou `OPEX` |
| `realizado` | sim | Gasto efetivo em R$. **Deixe vazio nos meses que ainda não aconteceram** |
| `orcado` | sim | Orçamento do mês em R$ |
| `forecast` | não | Projeção em R$. Se faltar, o dashboard usa o realizado (e o orçado nos meses futuros) |
| `economia` | não | Saving obtido no mês em R$ (alimenta Economia Acumulada e Saving Tracker) |

Facilidades na leitura: aceita **CSV (`,` ou `;`) e Excel (`.xlsx`)**, números como `1.234,56` ou `R$ 1.234,56`, e cabeçalhos com acento
(`Mês`, `Área`, `Orçado`, `Centro de Custo` são reconhecidos).

### Tabela de indicadores (opcional): `data/indicadores.csv`

Colunas: `ano, mes, diretoria, usuarios_ativos, equipamentos, contratos, co2_evitado_t`.
Alimenta os cards **Custo por Usuário** e **Principais Indicadores** e a página Operações de TI.
Sem esse arquivo, o dashboard funciona normalmente, mas esses campos aparecem como "—".

### Como aplicar

- **Jeito fixo:** salve sua tabela como `data/gastos.csv` (substitui a fictícia) e recarregue a página.
  Se for Excel, salve como `.xlsx` e mude `ARQ_GASTOS` em `config.py` para `DATA_DIR / "gastos.xlsx"`.
- **Jeito rápido para testar:** página **Dados → Enviar tabela real**. Vale só naquela sessão do navegador.
  O botão *Baixar modelo de colunas* gera um CSV vazio com os cabeçalhos certos.

Se faltar alguma coluna obrigatória, o dashboard avisa quais são.

## Personalização

| O que mudar | Onde |
|---|---|
| Nome da empresa, frases, cidade, versão | `config.py` |
| Taxa administrativa do Chargeback (padrão 5%) | `config.py` → `TAXA_CHARGEBACK` (ou o controle na página Chargeback) |
| Limites de "Atenção" e "Acima do orçado" | `config.py` → `LIMITE_ATENCAO`, `LIMITE_CRITICO` |
| Logo no menu lateral | coloque `logo.png` em `assets/` |
| Foto no painel à direita do gráfico | coloque `painel.jpg` em `assets/`. A imagem fica por baixo de uma camada azul translúcida. Sem arquivo, o painel é só a camada azul com o texto |
| Textos do painel | `config.py` → `PAINEL_PALAVRAS`, `PAINEL_FRASE` |
| Cores | `theme.py` e `styles.py` |
| Animação de entrada (varredura de tela, quadrados abrindo do centro um a um, gráficos subindo) | Já vem ligada e se repete a cada troca de página. Para desligar, adicione `ANIMACOES = False` no fim de `config.py` |

## Como os números são calculados

- **Período:** com Mês = *Todos*, vai de janeiro até o último mês que tem `realizado`. Com um mês escolhido, é só aquele mês.
- **Total Spend TI:** soma do `realizado` no período. A variação compara com o mesmo período do ano anterior.
- **Custo por Usuário:** `realizado` do mês de referência ÷ usuários ativos do mês, comparado ao mês anterior.
  Mês de referência = o mês escolhido ou o último com realizado.
- **Centros de Custo Ativos:** centros com `realizado` maior que zero no período.
- **Economia Acumulada:** soma de `economia` no período.
- **Forecast do ano:** soma de `forecast` do ano inteiro, comparada ao ano anterior.
- **Orçamento Utilizado / Budget Consumed:** `realizado` ÷ `orcado` nos mesmos meses.
  No medidor: verde até 80%, amarelo de 80% a 95%, vermelho acima de 95%.
- **Cores das variações:** em custos, subir é vermelho e descer é verde. Na economia, é o contrário.
- **Chargeback:** `realizado` × (1 + taxa administrativa).
- Usuários, equipamentos, contratos e tCO₂e respeitam Ano, Mês e Diretoria (não existem por centro de custo ou fornecedor).

## Gerar os dados fictícios de novo

```bash
python generate_data.py
```

Isso **sobrescreve** `data/gastos.csv` e `data/indicadores.csv`. Se já colocou os dados reais lá, não rode.

## Publicar online (portfólio / LinkedIn)

Gratuito, pelo **Streamlit Community Cloud**. Você precisa de uma conta no GitHub e uma no Streamlit (dá para entrar com o próprio GitHub).

1. **GitHub:** crie um repositório **público** (ex.: `finops-dashboard`). Em *Add file → Upload files*, arraste o **conteúdo** da pasta (`app.py`, `requirements.txt`, `data/`, `.streamlit/`, etc.) e clique em *Commit changes*.
2. **Streamlit:** entre em https://share.streamlit.io, clique em **Create app** → **Yup, I have an app**, escolha o repositório, a branch `main` e o arquivo principal `app.py`. Em *App URL* escolha um nome fácil (ex.: `finops-governance`) e clique em **Deploy**.
3. Em poucos minutos o link `https://nome-escolhido.streamlit.app` estará no ar. **Abra numa janela anônima** para confirmar que qualquer pessoa consegue ver sem login.
4. Cole o link no LinkedIn (seção *Projetos* ou *Destaques*) e coloque o link do GitHub como código-fonte.

Cuidados:
- **Nunca suba dados reais** de empresa para um repositório público. Para a versão pública, use só os dados fictícios que já vêm no projeto.
- **Não use marca, logo ou slogan de empresa real.** O projeto já vem com o nome fictício "ACME INDUSTRIAL". Para assinar, preencha `AUTOR` e `LINK_PERFIL` em `config.py`.
- Apps gratuitos **dormem após 12 horas sem visitas**. Quem abrir vê uma tela com o botão "Yes, get this app back up!" e o app volta em instantes. Abra o link você mesmo antes de divulgar.

## Problemas comuns

| Sintoma | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | O ambiente não está ativo ou faltou `pip install -r requirements.txt` |
| `streamlit` não é reconhecido | Use `python -m streamlit run app.py` |
| Porta 8501 ocupada | `streamlit run app.py --server.port 8502` |
| Mudei o CSV e nada mudou | O dashboard recarrega quando o arquivo muda. Atualize a página (F5) ou use *Rerun* no canto superior direito |
| Tudo aparece vazio ou "—" | Confira se o `ano` do filtro existe na tabela e se há valores em `realizado` |
| Colunas obrigatórias ausentes | Compare os cabeçalhos com a tabela acima |
| Acentos estranhos no CSV | Salve como **UTF-8** |
| Layout fora do lugar em tela pequena | O layout foi pensado para tela larga (notebook 1366 px ou maior). Use zoom do navegador em 80–90% |

## Notas

- O cabeçalho mostra a **data de hoje**; os dados fictícios são de 2024 e 2025 (realizado de 2025 só até agosto).
- Pelo layout ser desenhado com CSS próprio, atualizações grandes do Streamlit podem mexer em detalhes visuais.
  Se isso acontecer, os ajustes ficam em `styles.py`.
