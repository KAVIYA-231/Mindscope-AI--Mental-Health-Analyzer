"""
MindScope AI — Reports Page
File: pages/reports.py
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_theme import apply_theme, page_header, section_header, divider, STATE_COLORS
from database.db_service import get_all_analyses   # your existing function


def reports_page():
    apply_theme()

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">Mind<span>Scope</span> AI</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:1.5rem">Emotion Intelligence System</div>
        """, unsafe_allow_html=True)

    page_header("Session", "Reports",
                "Your complete emotional analysis history")

    user_id = st.session_state.get("user_id")

    try:
        rows = get_all_analyses(user_id)
        df   = pd.DataFrame(rows)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                    padding:40px;text-align:center;color:#64748b;font-size:15px;margin-top:2rem">
            📭 No reports yet. Complete your first analysis to see history here.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Filter bar ────────────────────────────────────────────────────────────
    section_header("🔎", "Filter")
    col_f1, col_f2, _ = st.columns([1.5, 1.5, 4])

    with col_f1:
        state_options = ["All"] + sorted(df["mental_state"].dropna().unique().tolist()) \
                        if "mental_state" in df.columns else ["All"]
        selected_state = st.selectbox("Mental State", state_options)

    with col_f2:
        face_options = ["All"] + sorted(df["face_emotion"].dropna().unique().tolist()) \
                       if "face_emotion" in df.columns else ["All"]
        selected_face = st.selectbox("Face Emotion", face_options)

    filtered = df.copy()
    if selected_state != "All" and "mental_state" in filtered.columns:
        filtered = filtered[filtered["mental_state"] == selected_state]
    if selected_face != "All" and "face_emotion" in filtered.columns:
        filtered = filtered[filtered["face_emotion"] == selected_face]

    divider()

    # ── Stats row ─────────────────────────────────────────────────────────────
    section_header("📊", f"Showing {len(filtered)} of {len(df)} sessions")

    # ── Table ─────────────────────────────────────────────────────────────────
    PILL_HTML = {
        "Positive":   '<span class="ms-pill ms-pill-green">Positive</span>',
        "Neutral":    '<span class="ms-pill ms-pill-blue">Neutral</span>',
        "Stress":     '<span class="ms-pill ms-pill-orange">Stress</span>',
        "Depression": '<span class="ms-pill ms-pill-red">Depression</span>',
    }

    # Card-style rows
    for _, row in filtered.iterrows():
        text         = str(row.get("text", ""))
        mental_state = str(row.get("mental_state", "N/A"))
        face_emotion = str(row.get("face_emotion", "—"))
        insight      = str(row.get("insight", ""))

        # truncate
        text_short    = (text[:80] + "...") if len(text) > 80 else text
        insight_short = (insight[:100] + "...") if len(insight) > 100 else insight

        pill   = PILL_HTML.get(mental_state,
                               f'<span class="ms-pill ms-pill-blue">{mental_state}</span>')
        color  = STATE_COLORS.get(mental_state, "#64748b")

        # date if present
        date_col = next((c for c in row.index if "date" in c.lower() or "time" in c.lower()), None)
        date_str = str(row[date_col])[:16] if date_col else ""

        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                    padding:16px 20px;margin-bottom:10px;
                    border-left:3px solid {color}">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:12px">
                <div style="flex:1">
                    <div style="font-size:14px;color:#e2e8f0;margin-bottom:6px">
                        "{text_short}"
                    </div>
                    <div style="font-size:12px;color:#64748b;margin-bottom:8px">
                        💡 {insight_short}
                    </div>
                    <div style="font-size:11px;color:#475569">
                        😶 Face: <b style="color:#94a3b8">{face_emotion}</b>
                        &nbsp;&nbsp;
                        🕓 {date_str}
                    </div>
                </div>
                <div style="white-space:nowrap">
                    {pill}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    divider()

    # ── Raw table toggle ──────────────────────────────────────────────────────
    with st.expander("🗂️ View as raw table"):
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

    # ── CSV download ──────────────────────────────────────────────────────────
    section_header("⬇️", "Export")
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV Report",
        data=csv,
        file_name="mindscope_report.csv",
        mime="text/csv",
        use_container_width=False,
    )


if __name__ == "__main__":
    reports_page()