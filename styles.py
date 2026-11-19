"""CSS do tema escuro (azul/neon). Injetado uma vez no app.py."""
import theme as th

_ROOT = f"""
:root{{
  --azul:{th.AZUL}; --azul-claro:{th.AZUL_CLARO}; --verde:{th.VERDE}; --amarelo:{th.AMARELO};
  --vermelho:{th.VERMELHO}; --roxo:{th.ROXO}; --texto:{th.TEXTO}; --muted:{th.MUTED};
  --card:rgba(9,24,48,.72); --borda:rgba(52,128,255,.28);
}}
"""

_BODY = """
/* ---------- base ---------- */
.stApp{
  background:
    radial-gradient(1100px 520px at 88% -8%, rgba(30,136,255,.20), transparent 60%),
    radial-gradient(800px 500px at -5% 105%, rgba(138,99,245,.10), transparent 60%),
    linear-gradient(180deg,#050B18 0%,#07122A 55%,#050B18 100%);
  color:var(--texto);
  font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
}
#MainMenu, footer{visibility:hidden;}
/* elementos que só carregam <style> não ocupam espaço na página */
div[data-testid="stElementContainer"]:has(style), .element-container:has(style){display:none;}
/* NÃO esconda o stToolbar inteiro: é nele que fica a setinha que reabre o menu lateral.
   Escondemos só o menu "⋮" e o botão Deploy. */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"],
.stDeployButton, .stAppDeployButton{display:none!important;}
header[data-testid="stHeader"]{background:transparent;}
/* setinha de reabrir o menu lateral: bem visível no tema escuro */
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"]{
  z-index:1000001;}
[data-testid="stExpandSidebarButton"] button, [data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button, button[data-testid="stExpandSidebarButton"]{
  color:#4DB8FF!important; background:rgba(9,24,48,.9)!important; border:1px solid rgba(52,128,255,.5)!important;
  border-radius:10px!important; box-shadow:0 0 14px rgba(30,136,255,.35);}
/* com o menu fechado, o título não fica por baixo da setinha */
.stApp:has(section[data-testid="stSidebar"][aria-expanded="false"]) .hdr{padding-left:3.4rem;}
.block-container{padding:.6rem 1.4rem 2rem 1.4rem; max-width:100%;}
h1,h2,h3,h4{color:var(--texto);}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#06101F 0%,#071A33 60%,#050B18 100%);
  border-right:1px solid var(--borda);
}
section[data-testid="stSidebar"] .block-container{padding-top:1rem;}
.marca{padding:.2rem .4rem 1rem .4rem; border-bottom:1px solid var(--borda); margin-bottom:.8rem;}
.marca-nome{font-weight:800; font-size:1.55rem; letter-spacing:.04em; color:#fff;}
.marca-lema{font-size:.78rem; color:var(--muted); margin-top:.1rem;}
.marca img{max-width:100%; max-height:54px;}

.st-key-nav label{
  display:flex; align-items:center; width:100%;
  padding:.62rem .85rem; margin:.12rem 0; border-radius:10px;
  border:1px solid transparent; cursor:pointer; color:var(--muted);
  transition:all .15s ease;
}
.st-key-nav label:hover{background:rgba(30,136,255,.10); color:var(--texto);}
.st-key-nav label:has(input:checked){
  background:linear-gradient(90deg, rgba(30,136,255,.55), rgba(30,136,255,.12));
  border-color:rgba(30,136,255,.7); color:#fff;
  box-shadow:0 0 18px rgba(30,136,255,.25);
}
/* esconde a bolinha do radio: qualquer filho do label que NÃO contenha o texto (funciona em qualquer versão) */
.st-key-nav label, .st-key-modo label{position:relative;}
.st-key-nav label > :not(:has([data-testid="stMarkdownContainer"])),
.st-key-modo label > :not(:has([data-testid="stMarkdownContainer"])){
  position:absolute!important; width:0!important; height:0!important; margin:0!important; padding:0!important;
  opacity:0!important; overflow:hidden!important; pointer-events:none!important;
}
.st-key-nav label p{font-size:.95rem; margin:0; color:inherit; white-space:nowrap;}
.st-key-nav [role="radiogroup"]{gap:0;}

.side-rodape{margin-top:2.2rem; padding:.6rem .4rem; font-size:.72rem; letter-spacing:.28em;
  text-transform:uppercase; color:var(--muted); border-top:2px solid var(--verde); width:80%;}

/* ---------- cabeçalho ---------- */
.hdr{display:flex; justify-content:space-between; align-items:center; gap:1rem;
  padding:.4rem .2rem .9rem .2rem; border-bottom:1px solid var(--borda); margin-bottom:.9rem;}
.hdr-tit{font-size:2.05rem; font-weight:800; letter-spacing:.02em; color:var(--azul-claro);
  text-shadow:0 0 18px rgba(30,136,255,.45); line-height:1.1;}
.hdr-sub{font-size:.86rem; letter-spacing:.32em; color:var(--azul); margin-top:.25rem;}
.hdr-pil{font-size:.68rem; letter-spacing:.34em; color:var(--muted); margin-top:.25rem;}
.hdr-lema{font-size:1.02rem; color:#CFE0F7; font-style:italic; text-align:center; line-height:1.45;}
.hdr-data{text-align:right; color:#EAF2FF;}
.hdr-data b{display:block; font-size:1.0rem;}
.hdr-data span{font-size:.8rem; color:var(--muted);}

/* ---------- filtros ---------- */
.stSelectbox label p{font-size:.78rem; color:var(--muted); margin-bottom:.1rem;}
div[data-baseweb="select"] > div{
  background:rgba(9,24,48,.85)!important; border:1px solid var(--borda)!important;
  border-radius:8px!important; min-height:38px; color:var(--texto);
}
div[data-baseweb="select"] *{color:var(--texto);}
/* seletores só abrem a lista: sem cursor de texto (a digitação é bloqueada no app.py) */
div[data-baseweb="select"], div[data-baseweb="select"] *{cursor:pointer!important;}
div[data-baseweb="select"] input{caret-color:transparent!important; user-select:none;}
/* iframe invisível que carrega o script que trava a digitação, e o container da varredura: não ocupam espaço */
div[data-testid="stElementContainer"]:has(iframe), .element-container:has(iframe),
div[data-testid="stElementContainer"]:has(.boot), .element-container:has(.boot){
  position:absolute; width:0; height:0; margin:0; padding:0; pointer-events:none;}
div[data-testid="stElementContainer"]:has(iframe), .element-container:has(iframe){overflow:hidden; opacity:0;}
.st-key-modo{padding-top:1.25rem;}
.st-key-modo [role="radiogroup"]{
  background:rgba(9,24,48,.85); border:1px solid var(--borda); border-radius:10px;
  padding:3px; gap:2px; display:flex; flex-wrap:nowrap;
}
.st-key-modo label{flex:1 1 0; min-width:0; justify-content:center; padding:.42rem .5rem; border-radius:8px; margin:0; cursor:pointer;}
.st-key-modo label p{font-size:.88rem; margin:0; color:var(--muted); white-space:nowrap; word-break:keep-all;}
.st-key-modo label:has(input:checked){background:var(--azul); box-shadow:0 0 14px rgba(30,136,255,.55);}
.st-key-modo label:has(input:checked) p{color:#fff; font-weight:600;}

/* ---------- KPIs ---------- */
.kpi{display:flex; gap:.6rem; align-items:flex-start; height:132px; box-sizing:border-box; overflow:hidden;
  background:var(--card); border:1px solid var(--borda); border-radius:14px; padding:.75rem .75rem;
  box-shadow:0 8px 28px rgba(0,0,0,.35);}
.kpi-ico{flex:0 0 38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  color:var(--c); background:color-mix(in srgb, var(--c) 16%, transparent);
  border:1px solid color-mix(in srgb, var(--c) 40%, transparent);}
.kpi-ico svg{width:20px; height:20px;}
.kpi-body{min-width:0; flex:1; container-type:inline-size;}
/* o número encolhe sozinho para caber no card (cqw = largura do próprio card) */
.kpi-val{font-size:.95rem; font-size:clamp(.62rem, 12cqw, 1.3rem); font-weight:700; color:#fff;
  line-height:1.2; white-space:nowrap;}
.kpi-tit{font-size:.78rem; color:#C5D5EA; margin:.1rem 0 .25rem 0; line-height:1.2;}
.kpi-delta{font-size:.9rem; font-weight:700;}
.kpi-delta.bom{color:var(--verde);} .kpi-delta.ruim{color:var(--vermelho);} .kpi-delta.neutro{color:var(--muted);}
.kpi-leg{font-size:.68rem; color:var(--muted); margin-top:.05rem;}
.kpi-wrap{container-type:inline-size; container-name:kpi;}
/* card estreito (notebook): ícone vai para cima e o número ganha a largura toda */
@container kpi (max-width:185px){
  .kpi{flex-direction:column; gap:.3rem; height:162px;}
  .kpi-ico{flex:0 0 auto; width:28px; height:28px; border-radius:8px;}
  .kpi-ico svg{width:16px; height:16px;}
  .kpi-body{flex:none; width:100%;}
}
.kpi-bar{height:8px; border-radius:99px; background:rgba(255,255,255,.10); margin:.45rem 0 .25rem 0; overflow:hidden;}
.kpi-bar i{display:block; height:100%; border-radius:99px;}

/* ---------- cards de gráfico (st.container com key=card_*) ---------- */
[class*="st-key-card_"]{
  background:var(--card)!important; border:1px solid var(--borda)!important; border-radius:14px!important;
  padding:.8rem 1rem .6rem 1rem!important; box-shadow:0 8px 28px rgba(0,0,0,.35);
}
.card-tit{font-weight:600; font-size:1.02rem; color:#EAF2FF; margin:0 0 .3rem 0;}
.card-sub{font-size:.78rem; color:var(--muted);}

/* ---------- painel decorativo (no lugar da foto) ---------- */
.hero{position:relative; min-height:372px; border-radius:14px; overflow:hidden; padding:1.4rem 1.5rem;
  border:1px solid var(--borda); background-size:cover; background-position:center;
  background-color:rgba(9,24,48,.72);
  display:flex; flex-direction:column; justify-content:center; align-items:flex-end; text-align:right;}
.hero::before{content:""; position:absolute; inset:0;
  background:
    radial-gradient(420px 260px at 20% 100%, rgba(30,136,255,.22), transparent 70%),
    radial-gradient(380px 240px at 100% 0%, rgba(31,224,165,.10), transparent 70%);}
.hero > *{position:relative;}
.hero-pal{font-size:1.05rem; letter-spacing:.2em; text-transform:uppercase; color:#EAF2FF; line-height:1.7; font-weight:500;}
.hero-frase{margin-top:.9rem; font-size:1.0rem; letter-spacing:.14em; text-transform:uppercase; color:#B9CBE4; line-height:1.6;}
.hero-marca{position:absolute!important; right:1.3rem; bottom:1rem; font-weight:800; letter-spacing:.06em; color:#fff;}

/* ---------- gauge ---------- */
.gauge-info{text-align:center; margin-top:-.2rem;}
.gauge-info b{font-size:1.5rem; color:#fff;}
.gauge-info span{display:block; font-size:.82rem; color:var(--muted);}
.gauge-leg{display:flex; justify-content:center; gap:1rem; font-size:.74rem; color:var(--muted); margin-top:.5rem; flex-wrap:wrap;}
.gauge-leg i{display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:.3rem;}

/* ---------- custos por diretoria ---------- */
.dr{display:grid; grid-template-columns:1.15fr 1.55fr .95fr .45fr; gap:.4rem .6rem; align-items:center; font-size:.8rem;}
.dr .h{color:var(--muted); font-size:.72rem;}
.dr .n{color:#D8E5F7;}
.dr .v{text-align:right; color:#D8E5F7; white-space:nowrap;}
.dr .p{text-align:right; color:var(--muted);}
.dr .b{height:9px; background:rgba(255,255,255,.07); border-radius:99px; overflow:hidden;}
.dr .b i{display:block; height:100%; background:linear-gradient(90deg,#1769FF,#4DB8FF); border-radius:99px;}

/* ---------- principais indicadores ---------- */
.mini-wrap{container-type:inline-size; container-name:mini;}
.mini-grid{display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:.6rem; margin-bottom:.4rem;}
@container mini (max-width:440px){ .mini-grid{grid-template-columns:repeat(2, minmax(0,1fr));} }
.mini{background:rgba(5,14,32,.55); border:1px solid var(--borda); border-radius:12px; padding:.65rem .6rem;
  text-align:left; container-type:inline-size; min-width:0;}
.mini .ico{width:36px; height:36px; border-radius:9px; display:flex; align-items:center; justify-content:center;
  color:var(--c); background:color-mix(in srgb, var(--c) 16%, transparent); margin-bottom:.4rem;}
.mini .ico svg{width:20px; height:20px;}
.mini .v{font-size:1.05rem; font-size:clamp(.85rem, 15cqw, 1.2rem); font-weight:700; color:#4DB8FF; line-height:1.15;}
.mini .t{font-size:.7rem; color:#C5D5EA; margin:.1rem 0 .25rem 0; line-height:1.2; overflow-wrap:break-word;}
.mini .d{font-size:.78rem; font-weight:700;}
.mini .d.bom{color:var(--verde);} .mini .d.ruim{color:var(--vermelho);} .mini .d.neutro{color:var(--muted);}

/* ---------- saving ---------- */
.sav-resumo .v{font-size:1.35rem; font-weight:700; color:var(--verde);}
.sav-resumo .t{font-size:.8rem; color:#C5D5EA;}
.sav-resumo .d{font-size:.9rem; font-weight:700; margin-top:.4rem;}
.sav-resumo .d.bom{color:var(--verde);} .sav-resumo .d.ruim{color:var(--vermelho);} .sav-resumo .d.neutro{color:var(--muted);}
.sav-resumo .l{font-size:.7rem; color:var(--muted);}

/* ---------- rodapé ---------- */
.rodape{display:flex; justify-content:space-between; align-items:center; gap:1rem; margin-top:1rem; padding:.7rem .2rem 0 .2rem;
  border-top:1px solid var(--borda); font-size:.76rem; color:var(--muted);}
.rodape b{color:#fff; letter-spacing:.05em;}
.aviso-demo{text-align:center; font-size:.76rem; color:var(--muted); margin-top:.6rem; letter-spacing:.04em;}
.aviso-demo a{color:var(--azul-claro); text-decoration:none;} .aviso-demo a:hover{text-decoration:underline;}
.rodape .on{display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--verde); margin:0 .3rem 0 .6rem;
  box-shadow:0 0 8px var(--verde);}

/* ---------- outras páginas ---------- */
.pg-tit{font-size:1.5rem; font-weight:700; color:#EAF2FF; margin:.2rem 0 .1rem 0;}
.pg-sub{font-size:.9rem; color:var(--muted); margin-bottom:.8rem;}
[data-testid="stDataFrame"]{border:1px solid var(--borda); border-radius:10px;}
.stDownloadButton button, .stButton button{
  background:rgba(30,136,255,.15); border:1px solid rgba(30,136,255,.6); color:#fff; border-radius:8px;}
.stDownloadButton button:hover, .stButton button:hover{background:rgba(30,136,255,.35); border-color:var(--azul);}
"""

CSS = "<style>" + _ROOT + _BODY + "</style>"


# ----------------------------------------------------------------------------
# Animação de entrada. A cada troca de página:
#   1) uma linha de luz varre a tela de cima a baixo, com uma grade que acende e some;
#   2) os quadrados "abrem" do centro para fora, um depois do outro;
#   3) os gráficos sobem e as barras crescem a partir da base.
# O nome das animações muda por página (sufixo _pN), o que as reinicia. Não depende do
# "reduzir movimento" do sistema: para desligar, use ANIMACOES = False no config.py.
# ----------------------------------------------------------------------------
_ATRASOS = {  # chave do card -> atraso em segundos (ordem em que abrem)
    "card_evolucao": 0.40, "card_gauge": 0.52,
    "card_categorias": 0.85, "card_fornecedores": 0.97, "card_diretorias": 1.09,
    "card_indicadores": 1.30, "card_capex": 1.42, "card_saving": 1.54,
    "card_aloc_grafico": 0.30,
    "card_op_usuarios_ativos": 0.30, "card_op_equipamentos": 0.45,
    "card_op_contratos": 0.60, "card_op_co2_evitado_t": 0.75,
}

_MODELO_ANIMACAO = """
@keyframes abrir_N{
  0%{opacity:0; clip-path:inset(46% 46% 46% 46% round 14px); transform:translateY(26px) scale(.94);}
  35%{opacity:1;}
  100%{opacity:1; clip-path:inset(0% 0% 0% 0% round 14px); transform:none;}
}
@keyframes brilho_N{
  0%{box-shadow:0 0 0 rgba(30,136,255,0);}
  40%{box-shadow:0 0 38px rgba(30,136,255,.8);}
  100%{box-shadow:0 8px 28px rgba(0,0,0,.35);}
}
@keyframes subir_N{
  0%{clip-path:inset(100% 0 0 0); opacity:.15; transform:translateY(56px);}
  100%{clip-path:inset(0 0 0 0); opacity:1; transform:none;}
}
@keyframes varrer_N{
  0%{top:0; opacity:0;} 10%{opacity:1;} 90%{opacity:.9;} 100%{top:100%; opacity:0;}
}
@keyframes crescer_N{ 0%{transform:scaleY(0);} 100%{transform:scaleY(1);} }
@keyframes crescerx_N{ 0%{transform:scaleX(0);} 100%{transform:scaleX(1);} }
@keyframes scan_N{ 0%{top:-4px; opacity:1;} 85%{opacity:1;} 100%{top:100vh; opacity:0;} }
@keyframes grade_N{ 0%{opacity:0;} 15%{opacity:.55;} 100%{opacity:0;} }

/* varredura de tela inteira */
.boot{position:fixed; top:0; left:0; right:0; bottom:0; z-index:99999; pointer-events:none; overflow:hidden;}
.boot::before{content:""; position:absolute; left:0; right:0; top:-4px; height:3px;
  background:linear-gradient(90deg, transparent, #4DB8FF 15%, #BDEBFF 50%, #4DB8FF 85%, transparent);
  box-shadow:0 0 28px 8px rgba(30,136,255,.7); animation:scan_N 1.25s cubic-bezier(.45,0,.2,1) both;}
.boot::after{content:""; position:absolute; top:0; left:0; right:0; bottom:0; opacity:0;
  background-image:linear-gradient(rgba(30,136,255,.13) 1px, transparent 1px),
                   linear-gradient(90deg, rgba(30,136,255,.13) 1px, transparent 1px);
  background-size:56px 56px; animation:grade_N 1.6s ease-out both;}

/* quadrados abrindo do centro para fora */
.kpi, .hero, [class*="st-key-card_"]{
  animation:abrir_N .85s cubic-bezier(.2,.8,.2,1) backwards, brilho_N 1.3s ease-out backwards;}
[class*="st-key-card_"]{position:relative;}
[class*="st-key-card_"]::before{content:""; position:absolute; left:0; right:0; top:0; height:2px; z-index:2;
  pointer-events:none; background:linear-gradient(90deg, transparent, #4DB8FF, transparent);
  box-shadow:0 0 12px #1E88FF; animation:varrer_N 1.1s ease-in-out backwards;}

/* gráficos sobem; barras crescem a partir da base (as horizontais, da esquerda) */
[data-testid="stPlotlyChart"]{animation:subir_N 1s cubic-bezier(.2,.8,.2,1) backwards;}
.js-plotly-plot .barlayer .point path{transform-box:fill-box; transform-origin:50% 100%;
  animation:crescer_N .9s cubic-bezier(.2,.8,.2,1) .6s backwards;}
.st-key-card_aloc_grafico .barlayer .point path{transform-origin:0 50%; animation-name:crescerx_N;}
.hero{animation-delay:.65s,.65s;}
"""


def css_animacao(pagina_id: int) -> str:
    css = _MODELO_ANIMACAO.replace("_N", f"_p{pagina_id}")
    for i in range(1, 7):  # os 6 KPIs abrem da esquerda para a direita
        atraso = (i - 1) * 0.08
        for testid in ("stColumn", "column"):
            css += f'[data-testid="{testid}"]:nth-child({i}) .kpi{{animation-delay:{atraso:.2f}s,{atraso:.2f}s;}}\n'
    for chave, atraso in _ATRASOS.items():
        css += (f'.st-key-{chave}{{animation-delay:{atraso:.2f}s,{atraso:.2f}s;}}\n'
                f'.st-key-{chave}::before{{animation-delay:{atraso + 0.1:.2f}s;}}\n'
                f'.st-key-{chave} [data-testid="stPlotlyChart"]{{animation-delay:{atraso + 0.3:.2f}s;}}\n')
    return "<style>" + css + "</style>"
