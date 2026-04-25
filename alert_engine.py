"""
MindScope AI — Alert Engine
File: engines/alert_engine.py

Detects high-risk patterns and generates smart UI alerts.
"""


ALERT_STYLES = {
    "danger": {
        "bg":     "rgba(248,113,113,0.08)",
        "border": "rgba(248,113,113,0.25)",
        "color":  "#f87171",
        "icon":   "🚨",
    },
    "warning": {
        "bg":     "rgba(251,146,60,0.08)",
        "border": "rgba(251,146,60,0.25)",
        "color":  "#fb923c",
        "icon":   "⚠️",
    },
    "success": {
        "bg":     "rgba(52,211,153,0.08)",
        "border": "rgba(52,211,153,0.25)",
        "color":  "#34d399",
        "icon":   "✅",
    },
    "info": {
        "bg":     "rgba(56,189,248,0.08)",
        "border": "rgba(56,189,248,0.25)",
        "color":  "#38bdf8",
        "icon":   "💡",
    },
}


def check_alerts(analyses: list) -> list:
    """
    Scan recent analyses for alert-worthy patterns.
    Returns list of alert dicts with level, message, action.
    """
    alerts = []
    if not analyses or len(analyses) < 2:
        return alerts

    recent = analyses[:5]
    states = [a.get("mental_state", "Neutral") for a in recent]

    # ── Danger: Multiple stress/depression sessions ───────────────────────────
    high_risk = sum(1 for s in states if s in ("Stress", "Depression"))
    if high_risk >= 3:
        alerts.append({
            "level":   "danger",
            "message": f"You've had {high_risk} high-stress sessions recently.",
            "action":  "Take a proper break. Try a walk, talk to someone, or do a breathing exercise.",
        })

    # ── Danger: Repeated depression ───────────────────────────────────────────
    depression = sum(1 for s in states if s == "Depression")
    if depression >= 2:
        alerts.append({
            "level":   "danger",
            "message": "Persistent low mood detected across multiple sessions.",
            "action":  "Please consider speaking to a mental health professional. iCall India: 9152987821",
        })

    # ── Warning: Declining trend ──────────────────────────────────────────────
    score_map = {"Positive": 4, "Neutral": 3, "Stress": 2, "Depression": 1}
    scores    = [score_map.get(s, 3) for s in states]
    if len(scores) >= 3 and scores[0] < scores[-1] - 0.5:
        alerts.append({
            "level":   "warning",
            "message": "Your emotional state has been gradually declining.",
            "action":  "Try journaling your thoughts or taking a 10-minute mindful break.",
        })

    # ── Warning: All neutral — possible emotional suppression ─────────────────
    all_neutral = all(s == "Neutral" for s in states)
    if all_neutral and len(states) >= 4:
        alerts.append({
            "level":   "info",
            "message": "You've been consistently neutral. Are you suppressing emotions?",
            "action":  "It's okay to feel things deeply. Try expressing yourself freely in your next entry.",
        })

    # ── Success: Positive streak ──────────────────────────────────────────────
    positive = sum(1 for s in states if s == "Positive")
    if positive >= 3:
        alerts.append({
            "level":   "success",
            "message": f"Amazing! {positive} positive sessions recently!",
            "action":  "Keep up the great work. Your positive habits are clearly working!",
        })

    return alerts


def render_alerts(alerts: list) -> str:
    """
    Render alerts as HTML string for st.markdown().
    Returns empty string if no alerts.
    """
    if not alerts:
        return ""

    html = ""
    for alert in alerts:
        style  = ALERT_STYLES.get(alert["level"], ALERT_STYLES["info"])
        html  += f"""
        <div style="background:{style['bg']};border:1px solid {style['border']};
                    border-radius:12px;padding:14px 18px;margin-bottom:10px">
            <div style="font-weight:700;color:{style['color']};margin-bottom:4px">
                {style['icon']} {alert['message']}
            </div>
            <div style="font-size:13px;color:#94a3b8">{alert['action']}</div>
        </div>
        """
    return html


def get_current_session_alert(final_state: str, risk_level: str) -> dict | None:
    """
    Returns an immediate alert for the current analysis session.
    Used in emotion_analysis_page() after prediction.
    """
    if risk_level == "Critical":
        return {
            "level":   "danger",
            "message": "Critical emotional state detected in this session.",
            "action":  "Please reach out immediately. iCall India: 9152987821",
        }
    elif risk_level == "High":
        return {
            "level":   "danger",
            "message": "High risk detected. Please take care of yourself.",
            "action":  "Step away from screens. Breathe. Talk to someone you trust.",
        }
    elif risk_level == "Medium" and final_state == "Stress":
        return {
            "level":   "warning",
            "message": "Moderate stress detected in this session.",
            "action":  "Try the 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s.",
        }
    return None