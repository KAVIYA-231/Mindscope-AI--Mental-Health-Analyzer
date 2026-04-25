"""
MindScope AI — Analytics Page
File: pages/analytics.py
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_theme import apply_theme, page_header, section_header, divider, STATE_COLORS
from database.db_service      import get_all_analyses
from engines.analytics_engine import (
    build_dataframe, get_emotion_trend, get_weekly_comparison,
    get_heatmap_data, detect_patterns, get_state_distribution, get_summary_stats
)

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#94a3b8", size=12),
    margin=dict(t=40, b=20, l=10, r=10),
    legend=dict(bgcolor="rgba(13,18,32,0.8)", bordercolor="#1e2d45", borderwidth=1),
)

COLOR_MAP = {
    "Positive":"#34d399","Neutral":"#38bdf8",
    "Stress":"#fb923c","Depression":"#f87171"
}


def analytics_page():
    apply_theme()

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">Mind<span>Scope</span> AI</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:1.5rem">
            Emotion Intelligence System
        </div>
        """, unsafe_allow_html=True)

    page_header("Analytics", "Dashboard", "Deep insights into your emotional patterns")

    user_id = st.session_state.get("user_id")
    try:
        analyses = get_all_analyses(user_id)
    except Exception:
        analyses = []

    df = build_dataframe(analyses)

    if df.empty:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                    padding:40px;text-align:center;color:#64748b;font-size:15px;margin-top:2rem">
            📭 No data yet. Complete your first emotion analysis to see charts here.
        </div>
        """, unsafe_allow_html=True)
        return

    stats = get_summary_stats(df)

    # ── Quick Stats Row ───────────────────────────────────────────────────────
    section_header("📋", "Quick Stats")
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color in [
        (c1, "Total Sessions",  stats.get("total", 0),               "#38bdf8"),
        (c2, "Positive Rate",   f"{stats.get('pos_pct', 0)}%",       "#34d399"),
        (c3, "Stress Rate",     f"{stats.get('stress_pct', 0)}%",    "#fb923c"),
        (c4, "Depression Rate", f"{stats.get('dep_pct', 0)}%",       "#f87171"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                        padding:16px 20px;text-align:center">
                <div style="font-size:11px;color:#64748b;letter-spacing:1.5px;
                            text-transform:uppercase;margin-bottom:8px">{label}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.8rem;
                            font-weight:800;color:{color}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    divider()

    # ── Distribution Charts ───────────────────────────────────────────────────
    section_header("🧩", "Emotion Distribution")
    dist = get_state_distribution(df)
    col1, col2 = st.columns(2)

    colors = [COLOR_MAP.get(s, "#64748b") for s in dist["Mental State"]]

    with col1:
        fig_pie = go.Figure(go.Pie(
            labels=dist["Mental State"], values=dist["Count"],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#080c14", width=2)),
            textfont=dict(size=13, color="white"),
        ))
        fig_pie.update_layout(
            **PLOTLY_BASE,
            title=dict(text="Emotion Share", font=dict(size=14, color="#e2e8f0")),
            annotations=[dict(
                text=f"<b>{stats.get('total',0)}</b><br>sessions",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=15, color="#e2e8f0")
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = go.Figure(go.Bar(
            x=dist["Mental State"], y=dist["Count"],
            marker=dict(color=colors, line=dict(color="#080c14", width=1)),
            text=dist["Count"], textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig_bar.update_layout(
            **PLOTLY_BASE,
            title=dict(text="Session Count by State", font=dict(size=14, color="#e2e8f0")),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    divider()

    # ── Emotion Trend Line ────────────────────────────────────────────────────
    trend = get_emotion_trend(df)
    if not trend.empty:
        section_header("📈", "Emotion Trend Over Time")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["Date"], y=trend["avg_score"],
            mode="lines+markers",
            name="Daily Score",
            line=dict(color="#38bdf8", width=2),
            marker=dict(size=6, color="#38bdf8"),
            hovertemplate="Date: %{x}<br>Score: %{y}<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend["Date"], y=trend["moving_avg"],
            mode="lines",
            name="3-Day Average",
            line=dict(color="#818cf8", width=2, dash="dot"),
            hovertemplate="Moving Avg: %{y}<extra></extra>",
        ))
        fig_trend.update_layout(
            **PLOTLY_BASE,
            title=dict(text="Wellness Score Over Time (1=Depression → 4=Positive)",
                       font=dict(size=14, color="#e2e8f0")),
            yaxis=dict(
                tickvals=[1, 2, 3, 4],
                ticktext=["Depression", "Stress", "Neutral", "Positive"],
                showgrid=True, gridcolor="#1e2d45",
            ),
            xaxis=dict(showgrid=False),
            height=320,
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        divider()

    # ── Weekly Comparison ─────────────────────────────────────────────────────
    weekly = get_weekly_comparison(df)
    if weekly:
        section_header("📅", "This Week vs Last Week")
        cols = st.columns(4)
        dir_icons = {"up": "↑", "down": "↓", "same": "→"}
        dir_colors = {"up": "#34d399", "down": "#f87171", "same": "#64748b"}

        for i, (state, data) in enumerate(weekly.items()):
            with cols[i % 4]:
                direction = data["direction"]
                # For stress/depression, up is bad; for positive, up is good
                if state in ("Stress", "Depression"):
                    color = dir_colors.get(
                        "down" if direction == "up" else
                        "up"   if direction == "down" else "same"
                    )
                else:
                    color = dir_colors.get(direction, "#64748b")

                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                            padding:16px;text-align:center">
                    <div style="font-size:11px;color:#64748b;text-transform:uppercase;
                                letter-spacing:1px;margin-bottom:8px">{state}</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
                                font-weight:800;color:{COLOR_MAP.get(state,'#64748b')}">
                        {data['this_week']}
                    </div>
                    <div style="font-size:12px;color:{color};margin-top:4px">
                        {dir_icons[direction]} {abs(data['diff'])} vs last week
                    </div>
                </div>
                """, unsafe_allow_html=True)
        divider()

    # ── Heatmap ───────────────────────────────────────────────────────────────
    heatmap_df = get_heatmap_data(df)
    if not heatmap_df.empty:
        section_header("🌡️", "Emotion Intensity Heatmap")

        pivot = heatmap_df.pivot_table(
            index="day_of_week", columns="hour",
            values="intensity", aggfunc="mean"
        ).fillna(0)

        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        pivot     = pivot.reindex([d for d in day_order if d in pivot.index])

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{h}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, "#f87171"],
                [0.5, "#fb923c"],
                [1.0, "#34d399"],
            ],
            hoverongaps=False,
            hovertemplate="Day: %{y}<br>Hour: %{x}<br>Score: %{z:.2f}<extra></extra>",
        ))
        fig_heat.update_layout(
            **PLOTLY_BASE,
            title=dict(text="Wellness by Day & Hour (Green=Positive, Red=Stress)",
                       font=dict(size=14, color="#e2e8f0")),
            height=300,
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        divider()

    # ── Face Emotion Distribution ─────────────────────────────────────────────
    if "face_emotion" in df.columns:
        face_df = df[~df["face_emotion"].isin(["Not Detected Yet", "Not Detected", ""])]
        if not face_df.empty:
            section_header("😶", "Face Emotion Distribution")
            face_counts = face_df["face_emotion"].value_counts().reset_index()
            face_counts.columns = ["Face Emotion", "Count"]
            face_colors_map = {
                "Happy":"#34d399","Surprise":"#38bdf8","Neutral":"#94a3b8",
                "Sad":"#fb923c","Angry":"#f87171","Fear":"#c084fc","Disgust":"#64748b"
            }
            fc = [face_colors_map.get(f, "#64748b") for f in face_counts["Face Emotion"]]
            fig_face = go.Figure(go.Bar(
                x=face_counts["Face Emotion"], y=face_counts["Count"],
                marker=dict(color=fc),
                text=face_counts["Count"], textposition="outside",
                textfont=dict(color="#e2e8f0"),
            ))
            fig_face.update_layout(
                **PLOTLY_BASE,
                title=dict(text="Detected Face Emotions", font=dict(size=14, color="#e2e8f0")),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
            )
            st.plotly_chart(fig_face, use_container_width=True)
            divider()

    # ── Detected Patterns ─────────────────────────────────────────────────────
    patterns = detect_patterns(df)
    if patterns:
        section_header("🧩", "Detected Patterns")
        for pattern in patterns:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e2d45;
                        border-left:3px solid #818cf8;border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;
                        font-size:14px;color:#e2e8f0">{pattern}</div>
            """, unsafe_allow_html=True)


analytics_page()