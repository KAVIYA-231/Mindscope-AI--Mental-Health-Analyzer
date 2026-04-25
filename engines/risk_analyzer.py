"""
MindScope AI — Risk Analyzer
File: engines/risk_analyzer.py

Calculates risk scores, detects repeated high-risk patterns,
and triggers smart alerts.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ── Risk scoring ──────────────────────────────────────────────────────────────
RISK_SCORES = {
    "Low":      1,
    "Medium":   2,
    "High":     3,
    "Critical": 4,
    "Unknown":  1,
}

STATE_SCORES = {
    "Positive":   1,
    "Neutral":    2,
    "Stress":     3,
    "Depression": 4,
}


def get_risk_score(risk_level: str) -> int:
    """Convert risk level string to numeric score."""
    return RISK_SCORES.get(risk_level, 1)


def get_wellness_score(analyses: list) -> int:
    """
    Calculate wellness score (0-100) from recent session history.
    Higher = better mental wellness.

    Args:
        analyses: list of dicts with 'mental_state' key
    Returns:
        int score 0-100
    """
    if not analyses:
        return 50  # default neutral

    total = len(analyses)
    score_sum = sum(
        STATE_SCORES.get(a.get("mental_state", "Neutral"), 2)
        for a in analyses
    )
    avg = score_sum / total  # 1=best, 4=worst

    # Invert and scale to 0-100
    wellness = int(((4 - avg) / 3) * 100)
    return max(0, min(100, wellness))


def check_alerts(analyses: list) -> list:
    """
    Scan recent analyses for alert-worthy patterns.

    Returns list of alert dicts:
        { 'level': 'warning'|'danger', 'message': str, 'action': str }
    """
    alerts = []

    if not analyses or len(analyses) < 2:
        return alerts

    recent = analyses[:5]  # check last 5 sessions

    # ── Alert 1: Multiple high-risk sessions ──────────────────────────────────
    high_risk_count = sum(
        1 for a in recent
        if a.get("mental_state") in ("Stress", "Depression")
    )
    if high_risk_count >= 3:
        alerts.append({
            "level":   "danger",
            "message": f"⚠️ You've had {high_risk_count} high-stress sessions recently.",
            "action":  "Consider taking a proper break and talking to someone you trust.",
        })

    # ── Alert 2: Depression detected ─────────────────────────────────────────
    depression_count = sum(
        1 for a in recent
        if a.get("mental_state") == "Depression"
    )
    if depression_count >= 2:
        alerts.append({
            "level":   "danger",
            "message": "💙 Signs of persistent low mood detected across sessions.",
            "action":  "Please consider reaching out to a mental health professional. iCall India: 9152987821",
        })

    # ── Alert 3: Declining trend ──────────────────────────────────────────────
    if len(recent) >= 3:
        scores = [STATE_SCORES.get(a.get("mental_state", "Neutral"), 2) for a in recent]
        # Check if scores are consistently worsening (increasing = worse)
        if scores[0] > scores[-1] + 1:
            alerts.append({
                "level":   "warning",
                "message": "📉 Your emotional state has been declining recently.",
                "action":  "Try a 10-minute walk, deep breathing, or journaling to reset.",
            })

    # ── Alert 4: Positive streak ──────────────────────────────────────────────
    positive_count = sum(
        1 for a in recent
        if a.get("mental_state") == "Positive"
    )
    if positive_count >= 3:
        alerts.append({
            "level":   "success",
            "message": f"🌟 Amazing! {positive_count} positive sessions in a row!",
            "action":  "Keep up the great work. Your consistency is paying off!",
        })

    return alerts


def get_risk_color(risk_level: str) -> str:
    """Return hex color for a given risk level."""
    return {
        "Low":      "#34d399",
        "Medium":   "#fb923c",
        "High":     "#f87171",
        "Critical": "#ef4444",
        "Unknown":  "#64748b",
    }.get(risk_level, "#64748b")


def summarize_risk(analyses: list) -> dict:
    """
    Summarize risk distribution from session history.

    Returns dict with counts per state and dominant state.
    """
    if not analyses:
        return {"dominant": "Neutral", "counts": {}}

    counts = {}
    for a in analyses:
        state = a.get("mental_state", "Neutral")
        counts[state] = counts.get(state, 0) + 1

    dominant = max(counts, key=counts.get)
    return {"dominant": dominant, "counts": counts}