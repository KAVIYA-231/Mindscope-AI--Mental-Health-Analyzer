"""
MindScope AI — Custom Theme
File: custom_theme.py

Import and call apply_theme() at the top of every page.
Usage:
    from custom_theme import apply_theme, card, metric_card, section_header, badge
    apply_theme()
"""

import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    /* ── Google Fonts ─────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Root Variables ───────────────────────────────── */
    :root {
        --bg:         #080c14;
        --bg2:        #0d1220;
        --bg3:        #111827;
        --border:     #1e2d45;
        --accent:     #38bdf8;
        --accent2:    #818cf8;
        --green:      #34d399;
        --orange:     #fb923c;
        --red:        #f87171;
        --text:       #e2e8f0;
        --muted:      #64748b;
        --card-glow:  0 0 0 1px #1e2d45, 0 8px 32px rgba(0,0,0,0.5);
    }

    /* ── Global reset ─────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 2rem 2.5rem 4rem !important;
        max-width: 1100px !important;
    }

    /* ── Sidebar ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg2) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }
    .sidebar-logo {
        font-family: 'Syne', sans-serif;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        padding: 1.2rem 0 0.5rem 0;
    }
    .sidebar-logo span { color: var(--accent); }
    .sidebar-nav-item {
        padding: 10px 14px;
        border-radius: 10px;
        margin: 4px 0;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: background 0.2s;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sidebar-nav-item:hover { background: var(--border); }
    .sidebar-nav-item.active {
        background: rgba(56,189,248,0.12);
        color: var(--accent) !important;
        border-left: 3px solid var(--accent);
    }

    /* ── Page title ───────────────────────────────────── */
    .ms-page-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .ms-page-title span { color: var(--accent); }
    .ms-subtitle {
        color: var(--muted);
        font-size: 14px;
        margin-bottom: 2rem;
    }

    /* ── Divider ──────────────────────────────────────── */
    .ms-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }

    /* ── Metric card ──────────────────────────────────── */
    .ms-metric {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: var(--card-glow);
        position: relative;
        overflow: hidden;
    }
    .ms-metric::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
    }
    .ms-metric-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 8px;
    }
    .ms-metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--text);
        line-height: 1;
    }
    .ms-metric-sub {
        font-size: 12px;
        color: var(--muted);
        margin-top: 6px;
    }
    .ms-metric-icon {
        position: absolute;
        top: 18px; right: 18px;
        font-size: 28px;
        opacity: 0.25;
    }

    /* ── Generic card ─────────────────────────────────── */
    .ms-card {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 24px;
        box-shadow: var(--card-glow);
        margin-bottom: 1rem;
    }

    /* ── Section header ───────────────────────────────── */
    .ms-section {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text);
        margin: 1.6rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Result state cards ───────────────────────────── */
    .ms-state-card {
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        border: 1px solid var(--border);
        background: var(--bg3);
    }
    .ms-state-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 6px;
    }
    .ms-state-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
    }
    .ms-state-conf {
        font-size: 12px;
        color: var(--muted);
        margin-top: 4px;
    }

    /* ── Insight box ──────────────────────────────────── */
    .ms-insight {
        background: linear-gradient(135deg, #0f172a 0%, #0d1f35 100%);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 14px;
        padding: 20px 22px;
    }
    .ms-insight-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .ms-insight-body {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.7;
    }

    /* ── Risk badge ───────────────────────────────────── */
    .ms-badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ── Confidence bar ───────────────────────────────── */
    .ms-bar-wrap { margin-bottom: 10px; }
    .ms-bar-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 4px;
    }
    .ms-bar-bg {
        background: var(--bg3);
        border-radius: 999px;
        height: 8px;
    }
    .ms-bar-fill {
        height: 8px;
        border-radius: 999px;
        transition: width 0.5s ease;
    }

    /* ── Status pills ─────────────────────────────────── */
    .ms-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }
    .ms-pill-green  { background: rgba(52,211,153,0.12); color: #34d399; }
    .ms-pill-blue   { background: rgba(56,189,248,0.12); color: #38bdf8; }
    .ms-pill-orange { background: rgba(251,146,60,0.12);  color: #fb923c; }
    .ms-pill-red    { background: rgba(248,113,113,0.12); color: #f87171; }

    /* ── Streamlit widget overrides ───────────────────── */
    .stTextArea textarea {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.15) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px 24px !important;
        transition: opacity 0.2s, transform 0.15s !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active { transform: translateY(0px) !important; }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 12px !important; overflow: hidden; }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        color: var(--muted) !important;
    }

    /* Info / success / warning boxes */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }

    /* Plotly chart bg */
    .js-plotly-plot .plotly { background: transparent !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


# ── Helper components ─────────────────────────────────────────────────────────

def page_header(title: str, highlight: str, subtitle: str = ""):
    """Renders the styled page title."""
    st.markdown(f"""
    <div class="ms-page-title">{title} <span>{highlight}</span></div>
    <div class="ms-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def section_header(icon: str, label: str):
    st.markdown(f'<div class="ms-section">{icon} {label}</div>', unsafe_allow_html=True)


def metric_card(label: str, value, sub: str = "", icon: str = ""):
    st.markdown(f"""
    <div class="ms-metric">
        <div class="ms-metric-icon">{icon}</div>
        <div class="ms-metric-label">{label}</div>
        <div class="ms-metric-value">{value}</div>
        <div class="ms-metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def state_card(label: str, value: str, conf: str = "", color: str = "#38bdf8"):
    st.markdown(f"""
    <div class="ms-state-card">
        <div class="ms-state-label">{label}</div>
        <div class="ms-state-value" style="color:{color}">{value}</div>
        <div class="ms-state-conf">{conf}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_box(title: str, body: str):
    st.markdown(f"""
    <div class="ms-insight">
        <div class="ms-insight-title">{title}</div>
        <div class="ms-insight-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def confidence_bar(label: str, value: float, color: str = "#38bdf8"):
    pct = f"{value * 100:.1f}%"
    st.markdown(f"""
    <div class="ms-bar-wrap">
        <div class="ms-bar-row"><span>{label}</span><span>{pct}</span></div>
        <div class="ms-bar-bg">
            <div class="ms-bar-fill" style="width:{pct};background:{color}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


RISK_COLORS = {
    "Low":      ("#34d399", "rgba(52,211,153,0.12)"),
    "Medium":   ("#fb923c", "rgba(251,146,60,0.12)"),
    "High":     ("#f87171", "rgba(248,113,113,0.12)"),
    "Critical": ("#ef4444", "rgba(239,68,68,0.18)"),
    "Unknown":  ("#64748b", "rgba(100,116,139,0.12)"),
}

STATE_COLORS = {
    "Positive":   "#34d399",
    "Neutral":    "#38bdf8",
    "Stress":     "#fb923c",
    "Depression": "#f87171",
}

def risk_badge(risk: str):
    color, bg = RISK_COLORS.get(risk, ("#64748b", "rgba(100,116,139,0.12)"))
    st.markdown(f"""
    <div style="margin:12px 0">
        <span class="ms-badge" style="background:{bg};color:{color}">
            ⬤ &nbsp;Risk Level: {risk}
        </span>
    </div>
    """, unsafe_allow_html=True)


def card(content_html: str):
    st.markdown(f'<div class="ms-card">{content_html}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="ms-divider">', unsafe_allow_html=True)