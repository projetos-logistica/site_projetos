# interface.py
import streamlit as st
import json
import io
import base64
import requests
from PIL import Image
from pathlib import Path


# =========================
# Configurações & Defaults
# =========================
DEFAULT_URL_WMS    = "https://projetos-logistica.app.n8n.cloud/webhook/cadastro-usuarios"
DEFAULT_URL_LOCAL  = "https://projetos-logistica.app.n8n.cloud/webhook/localizacao"
DEFAULT_CONTATO    = "projetos.logistica@somagrupo.com.br"

DEFAULT_URL_NOVO   = "https://cadastroteste.streamlit.app/"
DEFAULT_URL_EXTRA  = "https://projetos-logistica.app.n8n.cloud/form/600021df-08ca-4c80-a21d-aba8de936842"
DEFAULT_URL_NOVO2  = "https://projetos-logistica.app.n8n.cloud/form/1ce32498-70fe-4baf-9499-6ce127c10dac"

APP_DIR = Path(__file__).parent
LOCAL_LOGO_PATH = APP_DIR / "assets" / "logo.png"  # fallback local


# ===================================
# Helpers GitHub
# ===================================
def _get_github_cfg() -> dict:
    try:
        cfg = st.secrets.get("github", {})
        if not isinstance(cfg, dict):
            return {}
        return cfg
    except Exception:
        return {}

def _build_raw_url(owner: str, repo: str, branch: str, path: str, base_raw_host: str | None):
    path = path.lstrip("/")
    if base_raw_host:
        return f"https://{base_raw_host}/{owner}/{repo}/{branch}/{path}"
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

def gh_get_text(path: str) -> str | None:
    try:
        cfg = _get_github_cfg()
        owner = cfg.get("org")
        repo = cfg.get("repo")
        branch = cfg.get("branch", "main")
        base_raw_host = cfg.get("base_raw_host")
        token = cfg.get("token")
        if not owner or not repo:
            return None
        url = _build_raw_url(owner, repo, branch, path, base_raw_host)
        headers = {"Authorization": f"token {token}"} if token else {}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None

def gh_get_bytes(path: str) -> bytes | None:
    try:
        cfg = _get_github_cfg()
        owner = cfg.get("org")
        repo = cfg.get("repo")
        branch = cfg.get("branch", "main")
        base_raw_host = cfg.get("base_raw_host")
        token = cfg.get("token")
        if not owner or not repo:
            return None
        url = _build_raw_url(owner, repo, branch, path, base_raw_host)
        headers = {"Authorization": f"token {token}"} if token else {}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.content
        return None
    except Exception:
        return None

def pil_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ===================================
# Carrega config do repositório
# ===================================
URL_WMS = DEFAULT_URL_WMS
URL_LOCAL = DEFAULT_URL_LOCAL
CONTATO_EMAIL = DEFAULT_CONTATO
URL_NOVO = DEFAULT_URL_NOVO
URL_EXTRA = DEFAULT_URL_EXTRA
URL_NOVO2 = DEFAULT_URL_NOVO2

config_text = gh_get_text("portal/config.json")
if config_text:
    try:
        cfg_json = json.loads(config_text)
        urls = cfg_json.get("urls", {})
        URL_WMS   = urls.get("wms", DEFAULT_URL_WMS)
        URL_LOCAL = urls.get("local", DEFAULT_URL_LOCAL)
        URL_NOVO  = urls.get("novo", DEFAULT_URL_NOVO)
        URL_EXTRA = urls.get("extra", DEFAULT_URL_EXTRA)
        URL_NOVO2 = urls.get("novo2", DEFAULT_URL_NOVO2)
        CONTATO_EMAIL = cfg_json.get("contact_email", DEFAULT_CONTATO)
    except Exception:
        pass


# ===================================
# Carrega logo
# ===================================
logo_img = None
remote_bytes = gh_get_bytes("assets/logo.png")
if remote_bytes:
    try:
        logo_img = Image.open(io.BytesIO(remote_bytes))
    except Exception:
        logo_img = None

if logo_img is None and LOCAL_LOGO_PATH.exists():
    try:
        logo_img = Image.open(str(LOCAL_LOGO_PATH))
    except Exception:
        logo_img = None

logo_b64 = pil_to_base64(logo_img) if logo_img else None


# ===================================
# Config do app
# ===================================
st.set_page_config(
    page_title="Portal Projetos Logística",
    page_icon=logo_img if logo_img else None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===================================
# Estilos
# ===================================
st.markdown("""
<style>
html, body, .main { background: #f8fafc; }
.main .block-container { padding-top: 12px !important; }

#MainMenu, footer, .stApp [data-testid="baseLinkButton-footer"] { display: none !important; }

[data-testid="stSidebarCollapseButton"]{
  display: inline-flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}

/* HERO */
.hero {
  width: 100%;
  min-height: 120px;
  background: linear-gradient(180deg, #0b1220, #111827);
  border-radius: 18px;
  padding: 14px 18px;
  box-shadow: 0 12px 28px rgba(2,6,23,.18), 0 2px 6px rgba(2,6,23,.12);
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 18px;
  border: 1px solid rgba(255,255,255,.06);
}
.hero .logo-wrap{ height: 72px; max-width: 360px; display: flex; align-items: center; }
.hero .logo{ width: 100%; height: 100%; object-fit: contain; filter: drop-shadow(0 6px 14px rgba(0,0,0,.25)); }
.hero .title{ color: #fff; font-weight: 800; line-height: 1.15; margin: 0; font-size: clamp(22px, 3.2vw, 34px); letter-spacing: .2px; }
.hero .subtitle{ color: rgba(255,255,255,.78); margin-top: 4px; font-size: clamp(13px, 1.6vw, 15.5px); }

/* CARD */
.card{
  background:#ffffff;
  border-radius:18px;
  box-shadow:0 10px 26px rgba(0,0,0,.08);
  padding:22px 22px 18px 22px;
  border:1px solid #e5e7eb;
}
.kicker{ color:#64748b; font-weight:600; }
.title-sm{ font-weight:800; font-size:1.15rem; margin:0 0 6px }
.desc{ color:#64748b; font-size:.95rem; margin:0 0 16px; }
a.linkbtn{
  display:inline-block; text-decoration:none; font-weight:700;
  background:#111827; color:white; padding:10px 14px;
  border-radius:12px;
}
.badge{
  display:inline-block; font-size:.78rem; padding:4px 8px;
  background:#eef2ff; color:#1e40af; border-radius:999px; margin-left:8px;
}
</style>
""", unsafe_allow_html=True)


# ===================================
# Banner
# ===================================
if logo_b64:
    st.markdown(f"""
    <div class="hero">
      <div class="logo-wrap">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo">
      </div>
      <div>
        <h1 class="title">🗂️ Portal Projetos Logística</h1>
        <div class="subtitle">Selecione abaixo a ferramenta desejada. Os formulários abrem em uma nova aba.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ===================================
# Sidebar (Áreas)
# ===================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">ÁREAS</div>', unsafe_allow_html=True)
    setor = st.radio(
        "Selecione a área",
        ["Cadastro", "Qualidade", "Indicadores"],
        label_visibility="collapsed",
        index=0,
    )
    st.markdown('<div class="sidebar-help">Escolha um setor para ver apenas os links correspondentes.</div>', unsafe_allow_html=True)


# ===================================
# Função de Card
# ===================================
def card(kicker: str, titulo: str, descricao: str, url: str, botao: str):
    st.markdown(
        f"""
        <div class="card">
            <div class="kicker">{kicker}</div>
            <p class="title-sm">{titulo}</p>
            <p class="desc">{descricao}</p>
            <a class="linkbtn" href="{url}" target="_blank">{botao}</a>
            <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ===================================
# Conteúdo por setor
# ===================================
if setor == "Cadastro":
    st.subheader("Cadastro")

    col1, col2 = st.columns(2)
    with col1:
        card(
            "Formulário",
            "Cadastro de Usuário WMS",
            "Crie o usuário no padrão do WMS (turno, setor e regra de TC).",
            URL_WMS,
            "Abrir formulário WMS",
        )

    with col2:
        card(
            "Formulário",
            "Cadastro de Localização",
            "Solicite criação de endereços com validação automática.",
            URL_LOCAL,
            "Abrir formulário de Localização",
        )

elif setor == "Qualidade":
    st.subheader("Qualidade")

    col1, col2 = st.columns(2)
    with col1:
        card(
            "Formulário",
            "Formulário de Impressão / Plastificação",
            "Solicitações de impressão e plastificação.",
            URL_NOVO2,
            "Abrir Formulário",
        )

    with col2:
        card(
            "Formulário",
            "Formulário de Visitas",
            "Agendamento de visitas.",
            URL_EXTRA,
            "Abrir Formulário de Visitas",
        )

    col3, _ = st.columns(2)
    with col3:
        card(
            "Cadastro",
            "Absenteísmo",
            "Ambiente para cadastro de colaboradores.",
            URL_NOVO,
            "Abrir Absenteísmo",
        )

elif setor == "Indicadores":
    st.subheader("Indicadores")

    col1, _ = st.columns(2)
    with col1:
        card(
            "Formulário",
            "Paineis BI - Links Públicos",
            "Acesse lista consolidada dos dashboards públicos.",
            "https://projetos-logistica.github.io/link_publico/",
            "Abrir Paineis BI",
        )


# ===================================
# Contato
# ===================================
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

st.markdown("#### 📬 Fale com o time")
st.markdown(
    f"""
<div class="card">
  <p class="desc">
    Dúvidas, erros ou melhorias? Fale com a equipe de Projetos de Logística.<br/>
    E-mail: <a href="mailto:{CONTATO_EMAIL}">{CONTATO_EMAIL}</a>
  </p>
</div>
""",
    unsafe_allow_html=True
)
