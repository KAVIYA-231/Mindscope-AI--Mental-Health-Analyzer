"""
MindScope AI — Dashboard Page
File: pages/dashboard.py
"""

import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_theme import (
    apply_theme, page_header, section_header,
    metric_card, divider, STATE_COLORS
)
from database.db_service         import get_all_analyses
from engines.gamification_engine import get_gamification_summary
from engines.alert_engine        import check_alerts, render_alerts
from engines.analytics_engine    import build_dataframe, detect_patterns, get_summary_stats


def dashboard_page():
    apply_theme()

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">Mind<span>Scope</span> AI</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:1.5rem">
            Emotion Intelligence System
        </div>
        """, unsafe_allow_html=True)
        username = st.session_state.get("username", "User")
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                    padding:14px 16px;margin-bottom:1rem">
            <div style="font-size:11px;color:#64748b;letter-spacing:1px;
                        text-transform:uppercase">Logged in as</div>
            <div style="font-family:'Syne',sans-serif;font-size:16px;
                        font-weight:700;margin-top:4px">👤 {username}</div>
        </div>
        """, unsafe_allow_html=True)

    page_header("Emotion", "Dashboard", "Your personal mental wellness overview")

    user_id  = st.session_state.get("user_id")
    try:
        analyses = get_all_analyses(user_id)
    except Exception:
        analyses = []

    df       = build_dataframe(analyses)
    stats    = get_summary_stats(df)
    gami     = get_gamification_summary(analyses)
    alerts   = check_alerts(analyses)
    patterns = detect_patterns(df)

    total        = stats.get("total", 0)
    positive     = stats.get("positive", 0)
    stress       = stats.get("stress", 0)
    last_emotion = analyses[0].get("mental_state", "N/A") if analyses else "N/A"

    # ── Smart Alerts ──────────────────────────────────────────────────────────
    if alerts:
        section_header("🔔", "Smart Alerts")
        st.markdown(render_alerts(alerts), unsafe_allow_html=True)
        divider()

    # ── Metric Cards ──────────────────────────────────────────────────────────
    section_header("📊", "Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Sessions", total, "all time", "🧠")
    with c2:
        metric_card("Positive", positive, f"{stats.get('pos_pct',0)}% of total", "🌟")
    with c3:
        metric_card("Stress", stress, f"{stats.get('stress_pct',0)}% of total", "⚠️")
    with c4:
        metric_card("Wellness Score", f"{gami['wellness_score']}%", "based on history", "💚")

    divider()

    # ── Wellness Index ────────────────────────────────────────────────────────
    section_header("💚", "Wellness Index")
    score     = gami["wellness_score"]
    level     = gami["level"]
    bar_color = "#34d399" if score >= 60 else "#fb923c" if score >= 35 else "#f87171"

    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;padding:20px 24px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
                <div style="font-size:13px;color:#64748b">Overall Wellness</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                            font-weight:800;color:{bar_color}">{score}%</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:18px">{level['label']}</div>
                <div style="font-size:12px;color:#64748b">{level['desc']}</div>
            </div>
        </div>
        <div style="background:#0d1220;border-radius:999px;height:12px">
            <div style="width:{score}%;background:linear-gradient(90deg,{bar_color},{bar_color}88);
                        height:12px;border-radius:999px"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if level.get("progress_to_next") is not None:
        prog = level["progress_to_next"]
        st.markdown(f"""
        <div style="margin-top:8px;font-size:12px;color:#64748b;
                    display:flex;justify-content:space-between">
            <span>Progress to next level</span><span>{prog}%</span>
        </div>
        <div style="background:#0d1220;border-radius:999px;height:6px;margin-top:4px">
            <div style="width:{prog}%;background:#818cf8;height:6px;border-radius:999px"></div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Streak + Last Session ─────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        section_header("🔥", "Streak Tracker")
        streak      = gami["streak"]
        current_str = streak["current"]
        best_str    = streak["best"]
        flame       = "🔥" * min(current_str, 5) if current_str > 0 else "💤"
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                    padding:22px;text-align:center">
            <div style="font-size:36px;margin-bottom:6px">{flame}</div>
            <div style="font-family:'Syne',sans-serif;font-size:2rem;
                        font-weight:800;color:#fb923c">{current_str}</div>
            <div style="font-size:13px;color:#64748b">current positive streak</div>
            <div style="margin-top:12px;font-size:12px;color:#475569">
                Best ever: <b style="color:#e2e8f0">{best_str}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        section_header("🎯", "Last Session")
        color = STATE_COLORS.get(last_emotion, "#64748b")
        emoji = {"Positive":"🌟","Neutral":"😐","Stress":"😟",
                 "Depression":"💙"}.get(last_emotion, "❓")
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                    padding:22px;text-align:center">
            <div style="font-size:36px;margin-bottom:6px">{emoji}</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
                        font-weight:800;color:{color}">{last_emotion}</div>
            <div style="font-size:12px;color:#64748b;margin-top:6px">most recent emotion</div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Badges ────────────────────────────────────────────────────────────────
    section_header("🏅", "Earned Badges")
    badges = gami["badges"]
    if badges:
        cols = st.columns(min(len(badges), 4))
        for i, badge in enumerate(badges):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                            padding:16px;text-align:center">
                    <div style="font-size:28px">{badge['icon']}</div>
                    <div style="font-size:13px;font-weight:700;color:#e2e8f0;
                                margin-top:6px">{badge['label']}</div>
                    <div style="font-size:11px;color:#64748b;margin-top:3px">{badge['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                    padding:18px;text-align:center;color:#64748b;font-size:13px">
            Complete more sessions to earn badges! 🎯
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Emotion Patterns ──────────────────────────────────────────────────────
    if patterns:
        section_header("🧩", "Your Emotion Patterns")
        for pattern in patterns:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e2d45;
                        border-left:3px solid #818cf8;border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;
                        font-size:14px;color:#e2e8f0">{pattern}</div>
            """, unsafe_allow_html=True)
        divider()

    # ── Recent Sessions ───────────────────────────────────────────────────────
    section_header("🕓", "Recent Sessions")
    for row in (analyses[:5] if analyses else []):
        text         = str(row.get("text", ""))
        text_short   = (text[:70] + "...") if len(text) > 70 else text
        mental_state = str(row.get("mental_state", "N/A"))
        face_emotion = str(row.get("face_emotion", "—"))
        color        = STATE_COLORS.get(mental_state, "#64748b")
        pill_cls     = {"Positive":"ms-pill-green","Neutral":"ms-pill-blue",
                        "Stress":"ms-pill-orange","Depression":"ms-pill-red"
                        }.get(mental_state, "ms-pill-blue")
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                    padding:14px 18px;margin-bottom:8px;border-left:3px solid {color};
                    display:flex;justify-content:space-between;align-items:center">
            <div style="flex:1">
                <div style="font-size:13px;color:#e2e8f0;margin-bottom:4px">"{text_short}"</div>
                <div style="font-size:11px;color:#64748b">😶 Face: {face_emotion}</div>
            </div>
            <span class="ms-pill {pill_cls}">{mental_state}</span>
        </div>
        """, unsafe_allow_html=True)

    if not analyses:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                    padding:24px;text-align:center;color:#64748b;font-size:14px">
            No sessions yet. Start your first analysis! 🚀
        </div>
        """, unsafe_allow_html=True)

    divider()
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;font-size:13px;color:#64748b">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
                     background:#34d399;box-shadow:0 0 6px #34d399"></span>
        MindScope AI is active and ready
    </div>
    """, unsafe_allow_html=True)


dashboard_page()