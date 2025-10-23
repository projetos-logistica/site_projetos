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

# (já existia) app "Cadastro HC"
DEFAULT_URL_NOVO   = "https://cadastroteste.streamlit.app/"

# Link já incluído no portal (Formulário de Visitas)
DEFAULT_URL_EXTRA  = "https://projetos-logistica.app.n8n.cloud/form/600021df-08ca-4c80-a21d-aba8de936842"

# NOVO: link do novo site (card ao lado do último)
DEFAULT_URL_NOVO2  = "https://projetos-logistica.app.n8n.cloud/form/1ce32498-70fe-4baf-9499-6ce127c10dac"

APP_DIR = Path(__file__).parent
LOCAL_LOGO_PATH = APP_DIR / "assets" / "logo.png"  # fallback local

# ===================================
# Helpers de integração com GitHub
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
URL_NOVO2 = DEFAULT_URL_NOVO2  # novo

config_text = gh_get_text("portal/config.json")
if config_text:
    try:
        cfg_json = json.loads(config_text)
        urls = cfg_json.get("urls", {})
        URL_WMS   = urls.get("wms", DEFAULT_URL_WMS)
        URL_LOCAL = urls.get("local", DEFAULT_URL_LOCAL)
        URL_NOVO  = urls.get("novo", DEFAULT_URL_NOVO)
        URL_EXTRA = urls.get("extra", DEFAULT_URL_EXTRA)
        URL_NOVO2 = urls.get("novo2", DEFAULT_URL_NOVO2)  # permite override via JSON
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
)

# ===================================
# Estilos
# ===================================
st.markdown("""
<style>
html, body, .main { background: #f8fafc; }
.main .block-container { padding-top: 12px !important; }

#MainMenu, header, footer,
[data-testid="stToolbar"],
.stApp [data-testid="stHeader"],
.stApp [data-testid="baseLinkButton-footer"] { display: none !important; }

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

:root{
  --bg:#f8fafc; --card:#ffffff; --text:#0f172a; --muted:#64748b;
  --accent:#111827; --ring:#2563eb; --shadow:0 10px 26px rgba(0,0,0,.08);
  --radius:18px;
}
.card{
  background:var(--card);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  padding:22px 22px 18px 22px;
  border:1px solid #e5e7eb;
  height:auto;
}
.kicker{ color:var(--muted); font-weight:600; font-size:.9rem; margin-bottom:6px }
.title-sm{ font-weight:800; font-size:1.15rem; margin:0 0 6px }
.desc{ color:var(--muted); font-size:.95rem; margin:0 0 16px; line-height:1.45 }
a.linkbtn{
  display:inline-block; text-decoration:none; font-weight:700;
  background:var(--accent); color:white; padding:10px 14px;
  border-radius:12px; border:1px solid #0b1220; transition:transform .05s ease;
}
a.linkbtn:hover{ transform: translateY(-1px); }
.badge{
  display:inline-block; font-size:.78rem; padding:4px 8px; border-radius:999px;
  background:#eef2ff; color:#1e40af; border:1px solid #dbe3ff; margin-left:8px;
}
hr{ border:none; border-top:1px solid #e5e7eb; margin:24px 0; }
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
else:
    st.markdown("""
    <div class="hero">
      <div class="logo-wrap"></div>
      <div>
        <h1 class="title">🗂️ Portal Projetos Logística</h1>
        <div class="subtitle">Selecione abaixo a ferramenta desejada. Os formulários abrem em uma nova aba.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ===================================
# Cards principais
# ===================================
col1, col2 = st.columns(2, gap="large")

with col1:
    # Card: Cadastro de Usuário WMS
    st.markdown(
        f"""
        <div class="card">
          <div class="kicker">Formulário</div>
          <p class="title-sm">Cadastro de Usuário WMS</p>
          <p class="desc">
            Crie o usuário no padrão do WMS (turno, setor e regra de TC).
            A planilha e notificações são atualizadas automaticamente pelo fluxo do N8N.
          </p>
          <a class="linkbtn" href="{URL_WMS}" target="_blank" rel="noopener">
            Abrir formulário WMS
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card: Paineis BI - Links Públicos
    st.markdown(
        """
        <div class="card">
          <div class="kicker">Formulário</div>
          <p class="title-sm">Paineis BI - Links Públicos</p>
          <p class="desc">
            Acesse a planilha com os links de painéis BI públicos (Power BI, Tableau, etc.).
            Os acessos estão consolidados e versionados pela equipe.
          </p>
          <a class="linkbtn" href="https://somagrupo.sharepoint.com/:x:/s/Projetos-LogLabs/EVGO7wEaP7lPigdo0dcl6vsBOMVmXMeCBUNdfH6xljI9uw?e=ZDUY4s" 
             target="_blank" rel="noopener">
            Abrir formulário
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card: Formulário de Visitas
    st.markdown(
        f"""
        <div class="card compact">
          <div class="kicker">Formulário</div>
          <p class="title-sm">Formulário de Visitas</p>
          <p class="desc">
            Formulário de Visitas para agendamento.
          </p>
          <a class="linkbtn" href="{URL_EXTRA}" target="_blank" rel="noopener">
            Abrir Formulário de Visitas
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    # Card: Cadastro de Localização
    st.markdown(
        f"""
        <div class="card">
          <div class="kicker">Formulário</div>
          <p class="title-sm">Cadastro de Localização</p>
          <p class="desc">
            Solicite criação de endereços (PA/MP), com validação e preenchimento
            automático de colunas e prateleiras. Integra direto com a planilha.
          </p>
          <a class="linkbtn" href="{URL_LOCAL}" target="_blank" rel="noopener">
            Abrir formulário de Localização
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card: Cadastro HC
    st.markdown(
        f"""
        <div class="card">
          <div class="kicker">Cadastro</div>
          <p class="title-sm">Cadastro HC</p>
          <p class="desc">
            Acesse o ambiente para cadastro de colaboradores.
          </p>
          <a class="linkbtn" href="{URL_NOVO}" target="_blank" rel="noopener">
            Abrir Cadastro HC
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card: Novo Site (ao lado/abaixo do último card)
    st.markdown(
        f"""
        <div class="card">
          <div class="kicker">Formulário</div>
          <p class="title-sm">Formulário de Impressão / Plastificação</p>
          <p class="desc">
            Acesse o formulário de solicitação de impressão / Plastificação.
          </p>
          <a class="linkbtn" href="{URL_NOVO2}" target="_blank" rel="noopener">
            Abrir Formulário de solicitação
          </a>
          <span class="badge">on-line</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===================================
# Espaçador para jogar o contato mais pra baixo
# ===================================
st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)

# ===================================
# Seção de contato
# ===================================
st.markdown("#### 📬 Fale com o time")
st.markdown(
    f"""
<div class="card">
  <p class="desc" style="margin:0">
    Dúvidas, erros ou melhorias? Fale com a equipe de Projetos de Logística.<br/>
    E-mail: <a href="mailto:{CONTATO_EMAIL}">{CONTATO_EMAIL}</a>
  </p>
</div>
""",
    unsafe_allow_html=True
)
