from textwrap import dedent
import streamlit as st

COLORS = {
    "ink": "#172033", "muted": "#667085", "subtle": "#98A2B3",
    "line": "#E4E7EC", "surface": "#FFFFFF", "canvas": "#F5F7FB",
    "sidebar": "#0D1524", "sidebar_line": "#202B3D",
    "blue": "#2F5BEA", "blue_light": "#EEF4FF",
    "green": "#087443", "green_light": "#ECFDF3",
    "amber": "#B54708", "amber_light": "#FFFAEB",
    "red": "#B42318", "red_light": "#FEF3F2",
    "purple": "#6941C6", "purple_light": "#F4F3FF",
}


def configure_page():
    st.set_page_config(
        page_title="RECLAIM | Revenue Recovery",
        page_icon="R",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_theme():
    st.html(dedent("""
    <style>
    :root {
        --ink:#172033; --muted:#667085; --subtle:#98A2B3;
        --line:#E4E7EC; --surface:#FFFFFF; --canvas:#F5F7FB;
        --sidebar:#0D1524; --sidebar-line:#202B3D;
        --blue:#2F5BEA; --blue-light:#EEF4FF;
        --green:#087443; --green-light:#ECFDF3;
        --amber:#B54708; --amber-light:#FFFAEB;
        --red:#B42318; --red-light:#FEF3F2;
        --purple:#6941C6; --purple-light:#F4F3FF;
    }

    html, body, [class*="css"], .stApp {
        font-family:"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    }
    .stApp { background:var(--canvas); color:var(--ink); }
    .main .block-container {
        max-width:1540px; padding-top:1.35rem; padding-bottom:3.5rem;
        padding-left:2.1rem; padding-right:2.1rem;
    }
    #MainMenu, footer { visibility:hidden; }
    header[data-testid="stHeader"] { background:transparent; }
    div[data-testid="stToolbar"] { display:none; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background:var(--sidebar); border-right:1px solid var(--sidebar-line);
    }
    section[data-testid="stSidebar"] > div { padding-top:1rem; }
    section[data-testid="stSidebar"] * { color:#D0D5DD; }
    .sidebar-brand {
        padding:7px 10px 19px; border-bottom:1px solid var(--sidebar-line);
        margin-bottom:14px;
    }
    .brand-row { display:flex; align-items:center; gap:10px; }
    .brand-mark {
        width:34px; height:34px; border-radius:8px; background:var(--blue);
        display:flex; align-items:center; justify-content:center;
        color:white; font-size:18px; font-weight:800; box-shadow:0 4px 14px rgba(47,91,234,.25);
    }
    .sidebar-brand-name { color:#FFF !important; font-size:19px; font-weight:800; letter-spacing:-.04em; }
    .sidebar-brand-sub { color:#7F8BA0 !important; font-size:9px; margin-top:7px; text-transform:uppercase; letter-spacing:.12em; }
    .sidebar-section {
        color:#667085 !important; font-size:9px; font-weight:750;
        text-transform:uppercase; letter-spacing:.11em; margin:17px 10px 7px;
    }

    /* Streamlit radio -> application navigation */
    div[data-testid="stRadio"] > div { gap:3px; }
    div[data-testid="stRadio"] label {
        background:transparent !important; border:1px solid transparent;
        border-radius:7px; padding:8px 10px; margin:0; transition:.12s ease;
    }
    div[data-testid="stRadio"] label:hover { background:#172235 !important; border-color:#24314A; }
    div[data-testid="stRadio"] label p {
        color:#AEB8C8 !important; font-size:12px; font-weight:550; margin:0;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background:#1C2D5E !important; border-color:#2C4386;
        box-shadow:inset 3px 0 0 var(--blue);
    }
    div[data-testid="stRadio"] label:has(input:checked) p { color:#FFF !important; font-weight:700; }
    div[data-testid="stRadio"] label > div:first-child { display:none !important; }
    div[data-testid="stRadio"] label > div { margin:0 !important; }
    div[data-testid="stRadio"] > label { display:none; }

    /* Environment */
    .sidebar-env {
        padding:11px 12px; border:1px solid #263247; border-radius:8px;
        background:#111B2B; margin:0 2px;
    }
    .sidebar-env-label { color:#667085; font-size:8px; text-transform:uppercase; letter-spacing:.1em; }
    .sidebar-env-name { color:#E5E7EB; font-size:11px; font-weight:700; margin-top:5px; }
    .sidebar-env-detail { color:#7F8BA0; font-size:9px; margin-top:4px; }

    /* Header */
    .page-header {
        display:flex; justify-content:space-between; align-items:flex-start;
        padding:2px 0 18px; border-bottom:1px solid var(--line); margin-bottom:1px;
    }
    .page-kicker { color:var(--blue); font-size:9px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:6px; }
    .page-title { color:var(--ink) !important; font-size:27px; line-height:1.08; font-weight:780; letter-spacing:-.04em; }
    .page-description { color:var(--muted) !important; font-size:12px; margin-top:6px; }
    .environment-label { text-align:right; padding-top:4px; }
    .environment-name { color:var(--ink) !important; font-size:11px; font-weight:700; }
    .environment-detail { color:var(--subtle) !important; font-size:9px; margin-top:4px; }
    .environment-dot { display:inline-block; width:6px; height:6px; border-radius:50%; background:#12B76A; margin-right:5px; }

    /* Sections */
    .section-header { display:flex; align-items:baseline; justify-content:space-between; margin-top:24px; margin-bottom:9px; }
    .section-title { color:var(--ink) !important; font-size:15px; font-weight:760; letter-spacing:-.02em; }
    .section-note { color:var(--subtle) !important; font-size:10px; }

    /* Metrics */
    .metric {
        background:var(--surface); border:1px solid var(--line); border-radius:9px;
        padding:14px 15px; min-height:91px; box-shadow:0 1px 2px rgba(16,24,40,.025);
    }
    .metric-label { color:var(--muted) !important; font-size:9px; font-weight:750; letter-spacing:.07em; margin-bottom:9px; }
    .metric-value { color:var(--ink) !important; font-size:23px; line-height:1; font-weight:780; letter-spacing:-.035em; }
    .metric-detail { color:var(--subtle) !important; font-size:9px; margin-top:7px; }
    .metric-accent { border-top:2px solid var(--blue); }
    .metric-success { border-top:2px solid #12B76A; }
    .metric-warning { border-top:2px solid #F79009; }

    /* Panels */
    .panel { background:var(--surface); border:1px solid var(--line); border-radius:9px; padding:16px 18px; box-shadow:0 1px 2px rgba(16,24,40,.025); }
    .panel-title { color:var(--ink) !important; font-size:13px; font-weight:750; margin-bottom:3px; }
    .panel-description { color:var(--muted) !important; font-size:10px; margin-bottom:12px; }

    /* Pipeline */
    .pipeline { display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); width:100%; margin-top:12px; border:1px solid var(--line); border-radius:7px; overflow:hidden; background:#FFF; }
    .pipeline-stage { min-width:0; padding:12px 7px; border-right:1px solid var(--line); background:#FFF; text-align:center; }
    .pipeline-stage:last-child { border-right:none; }
    .pipeline-number { color:var(--blue); font-size:8px; font-weight:800; margin-bottom:5px; }
    .pipeline-name { color:var(--ink) !important; font-size:9px; font-weight:700; }
    .pipeline-detail { color:var(--subtle) !important; font-size:8px; margin-top:4px; }

    /* Decision feed */
    .decision-row { display:grid; grid-template-columns:115px minmax(180px,1fr) 150px 120px; align-items:center; gap:15px; padding:12px 0; border-bottom:1px solid #EEF0F3; }
    .decision-row:last-child { border-bottom:none; }
    .decision-id { color:var(--ink) !important; font-size:10px; font-weight:650; }
    .decision-main { color:var(--ink) !important; font-size:11px; font-weight:650; }
    .decision-sub { color:var(--muted) !important; font-size:9px; margin-top:3px; }
    .decision-prob { color:var(--ink) !important; font-size:11px; font-weight:750; text-align:right; }

    /* Badges */
    .badge { display:inline-block; width:fit-content; padding:4px 7px; border-radius:999px; font-size:8px; line-height:1; font-weight:800; letter-spacing:.04em; text-transform:uppercase; }
    .badge-blue { background:var(--blue-light); color:#175CD3 !important; }
    .badge-green { background:var(--green-light); color:var(--green) !important; }
    .badge-amber { background:var(--amber-light); color:var(--amber) !important; }
    .badge-red { background:var(--red-light); color:var(--red) !important; }
    .badge-purple { background:var(--purple-light); color:var(--purple) !important; }

    /* Tables / charts */
    div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; box-shadow:0 1px 2px rgba(16,24,40,.02); }
    div[data-testid="stPlotlyChart"] { background:#FFF; border:1px solid var(--line); border-radius:9px; padding:2px; box-shadow:0 1px 2px rgba(16,24,40,.025); }

    /* Buttons */
    .stButton > button { border:1px solid #D0D5DD; background:#FFF; color:var(--ink); border-radius:7px; font-size:11px; font-weight:700; min-height:35px; }
    .stButton > button:hover { border-color:var(--blue); color:var(--blue); background:#F8FAFF; }
    button[kind="primary"] { background:var(--blue) !important; border-color:var(--blue) !important; color:#FFF !important; box-shadow:0 3px 10px rgba(47,91,234,.18); }
    button[kind="primary"]:hover { background:#2448C5 !important; border-color:#2448C5 !important; color:#FFF !important; }

    /* Inputs */
    div[data-baseweb="select"] > div { border-color:#D0D5DD; border-radius:7px; background:#FFF; }
    div[data-testid="stTextInput"] input { border-color:#D0D5DD; border-radius:7px; }
    div[data-testid="stAlert"] { border-radius:8px; font-size:10px; }
    div[data-testid="stExpander"] { border:1px solid var(--line); border-radius:8px; background:#FFF; }

    /* Lifecycle */
    .lifecycle-row { display:grid; grid-template-columns:1.25fr 1.4fr 110px; align-items:center; padding:11px 0; border-bottom:1px solid #EEF0F3; }
    .lifecycle-row:last-child { border-bottom:none; }
    .lifecycle-label { color:var(--ink) !important; font-size:10px; font-weight:650; }
    .lifecycle-value { color:var(--muted) !important; font-size:10px; }

    /* Architecture */
    .architecture-flow { display:flex; align-items:center; flex-wrap:wrap; gap:0; font-size:10px; color:var(--ink); font-weight:650; }
    .architecture-node { padding:6px 8px; color:var(--ink) !important; background:#F9FAFB; border:1px solid var(--line); border-radius:5px; }
    .architecture-arrow { color:var(--subtle) !important; padding:0 5px; }

    /* ================= INVESTOR DEMO ================= */
    .demo-hero {
        position:relative; overflow:hidden; background:linear-gradient(135deg,#101B31 0%,#182A52 55%,#203C82 100%);
        border-radius:14px; padding:30px 32px; margin-top:4px; color:#FFF;
        box-shadow:0 10px 28px rgba(15,31,61,.16);
    }
    .demo-hero:after { content:""; position:absolute; width:230px; height:230px; border:1px solid rgba(255,255,255,.08); border-radius:50%; right:-70px; top:-100px; box-shadow:0 0 0 35px rgba(255,255,255,.025),0 0 0 70px rgba(255,255,255,.018); }
    .demo-kicker { position:relative; z-index:1; color:#9FB5FF; font-size:9px; font-weight:800; text-transform:uppercase; letter-spacing:.14em; margin-bottom:8px; }
    .demo-title { position:relative; z-index:1; color:#FFF; font-size:29px; line-height:1.12; font-weight:800; letter-spacing:-.045em; max-width:850px; }
    .demo-description { position:relative; z-index:1; color:#C6D0E3; font-size:11px; line-height:1.65; max-width:760px; margin-top:10px; }

    .demo-explanation { display:grid; grid-template-columns:repeat(5,1fr); gap:7px; margin:12px 0 17px; }
    .demo-explanation-item { background:#FFF; border:1px solid var(--line); border-radius:8px; padding:12px; }
    .demo-explanation-number { color:var(--blue); font-size:8px; font-weight:800; margin-bottom:6px; }
    .demo-explanation-title { color:var(--ink); font-size:10px; font-weight:750; }
    .demo-explanation-text { color:var(--muted); font-size:9px; line-height:1.45; margin-top:3px; }

    .demo-start-card { background:#FFF; border:1px solid var(--line); border-radius:10px; padding:15px 17px; margin-bottom:15px; display:flex; align-items:center; justify-content:space-between; gap:18px; }
    .demo-start-left { display:flex; align-items:center; gap:12px; }
    .demo-start-icon { width:36px; height:36px; border-radius:9px; background:var(--blue-light); color:var(--blue); display:flex; align-items:center; justify-content:center; font-weight:850; }
    .demo-start-title { color:var(--ink); font-size:12px; font-weight:750; }
    .demo-start-text { color:var(--muted); font-size:9px; line-height:1.5; margin-top:3px; }

    .demo-status { display:flex; align-items:center; justify-content:space-between; background:#FFF; border:1px solid var(--line); border-radius:8px; padding:9px 12px; margin-bottom:10px; }
    .demo-status-left { display:flex; align-items:center; gap:7px; }
    .demo-status-dot { width:7px; height:7px; border-radius:50%; background:#12B76A; box-shadow:0 0 0 3px #ECFDF3; }
    .demo-status-text { color:var(--green); font-size:8px; font-weight:800; letter-spacing:.07em; }
    .demo-status-meta { color:var(--subtle); font-size:9px; }

    .demo-scenario { background:#FFF; border:1px solid var(--line); border-radius:10px; padding:16px; margin-bottom:9px; box-shadow:0 1px 2px rgba(16,24,40,.025); }
    .demo-scenario.recovered { border-left:4px solid #12B76A; }
    .demo-scenario.no-action { border-left:4px solid #F79009; }
    .demo-scenario-top { display:flex; align-items:flex-start; justify-content:space-between; gap:15px; margin-bottom:12px; }
    .demo-scenario-number { color:var(--subtle); font-size:8px; font-weight:800; text-transform:uppercase; letter-spacing:.09em; }
    .demo-scenario-title { color:var(--ink); font-size:14px; font-weight:780; margin-top:3px; }
    .demo-scenario-failure { color:var(--muted); font-size:9px; margin-top:3px; }
    .demo-amount { color:var(--ink); font-size:19px; font-weight:820; white-space:nowrap; }

    .demo-decision-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:7px; overflow:hidden; }
    .demo-decision-cell { background:#FAFBFC; padding:10px; min-height:60px; }
    .demo-cell-label { color:var(--muted); font-size:7px; text-transform:uppercase; letter-spacing:.07em; font-weight:800; margin-bottom:5px; }
    .demo-cell-value { color:var(--ink); font-size:11px; font-weight:760; }
    .demo-action { color:var(--blue); }
    .demo-action.no-action { color:var(--amber); }
    .demo-reason { margin-top:9px; padding:9px 10px; background:#F9FAFB; border-radius:6px; font-size:9px; line-height:1.5; color:#475467; }
    .demo-recovered { margin-top:8px; font-size:10px; font-weight:750; color:var(--green); }

    .killer-card { background:#FFFBEB; border:1px solid #F4DFA1; border-radius:10px; padding:19px; margin:15px 0; box-shadow:0 2px 5px rgba(181,119,31,.04); }
    .killer-label { color:var(--amber); font-size:8px; text-transform:uppercase; letter-spacing:.12em; font-weight:850; }
    .killer-title { color:var(--ink); font-size:19px; font-weight:820; letter-spacing:-.025em; margin-top:4px; }
    .killer-text { color:#6B5A2E; font-size:10px; line-height:1.55; margin-top:6px; max-width:760px; }
    .killer-reason { display:inline-block; margin-top:9px; background:#FFF; border:1px solid #EADDAF; border-radius:5px; padding:6px 8px; font-size:9px; color:#594B28; font-family:monospace; }
    .killer-line { margin-top:10px; padding-top:10px; border-top:1px solid #EADDAF; font-size:10px; font-weight:750; color:#5C4D22; }

    .revenue-impact { background:#FFF; border:1px solid var(--line); border-radius:10px; padding:15px; margin-top:13px; }
    .revenue-impact-title { color:var(--ink); font-size:12px; font-weight:780; margin-bottom:10px; }
    .revenue-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
    .revenue-cell { background:#F9FAFB; border-radius:7px; padding:11px; }
    .revenue-label { color:var(--muted); font-size:7px; text-transform:uppercase; letter-spacing:.07em; font-weight:800; }
    .revenue-value { color:var(--ink); font-size:18px; font-weight:820; margin-top:5px; }
    .demo-disclosure { margin-top:12px; padding:9px 11px; border:1px solid var(--line); border-radius:6px; background:#FAFBFC; font-size:8px; line-height:1.55; color:var(--muted); }

    @media (max-width:1000px) {
        .demo-explanation { grid-template-columns:repeat(2,1fr); }
        .demo-decision-grid { grid-template-columns:repeat(2,1fr); }
        .revenue-grid { grid-template-columns:repeat(2,1fr); }
    }
    @media (max-width:700px) {
        .main .block-container { padding-left:1rem; padding-right:1rem; }
        .page-header { flex-direction:column; gap:10px; }
        .environment-label { text-align:left; }
        .demo-title { font-size:23px; }
        .demo-explanation,.demo-decision-grid,.revenue-grid { grid-template-columns:1fr; }
        .demo-start-card,.demo-scenario-top { flex-direction:column; align-items:flex-start; }
        .decision-row { grid-template-columns:1fr 1fr; }
    }
    </style>
    """))


def render_brand():
    st.html(dedent("""
    <div class="sidebar-brand">
        <div class="brand-row">
            <div class="brand-mark">R</div>
            <div class="sidebar-brand-name">RECLAIM</div>
        </div>
        <div class="sidebar-brand-sub">Autonomous Revenue Recovery</div>
    </div>
    """))
