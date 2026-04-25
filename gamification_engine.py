"""
MindScope AI — Gamification Engine
File: engines/gamification_engine.py

Handles wellness score, streaks, badges, and progress indicators.
"""

from datetime import datetime, timedelta


# ── Badge definitions ─────────────────────────────────────────────────────────
BADGES = {
    "first_session":    {"icon": "🎯", "label": "First Step",       "desc": "Completed your first analysis"},
    "streak_3":         {"icon": "🔥", "label": "On Fire",          "desc": "3 positive sessions in a row"},
    "streak_7":         {"icon": "⚡", "label": "Weekly Warrior",   "desc": "7 positive sessions in a row"},
    "stress_survivor":  {"icon": "💪", "label": "Stress Survivor",  "desc": "Recovered from 3 stress sessions"},
    "consistent":       {"icon": "📅", "label": "Consistent",       "desc": "Used MindScope for 5+ days"},
    "self_aware":       {"icon": "🧠", "label": "Self Aware",       "desc": "Completed 10 total analyses"},
    "wellness_master":  {"icon": "🏆", "label": "Wellness Master",  "desc": "Achieved 80%+ wellness score"},
}


def get_wellness_score(analyses: list) -> int:
    """
    Calculate wellness score 0-100 from session history.
    Positive=100, Neutral=70, Stress=35, Depression=10
    """
    if not analyses:
        return 50

    state_points = {
        "Positive":   100,
        "Neutral":    70,
        "Stress":     35,
        "Depression": 10,
    }

    recent   = analyses[:10]  # last 10 sessions
    total    = sum(state_points.get(a.get("mental_state", "Neutral"), 70) for a in recent)
    score    = int(total / len(recent))
    return max(0, min(100, score))


def get_streak(analyses: list) -> dict:
    """
    Calculate current positive streak and best streak.
    Returns dict with current, best, and streak_type.
    """
    if not analyses:
        return {"current": 0, "best": 0, "type": "none"}

    # Current streak — count from latest session backwards
    current = 0
    for a in analyses:
        if a.get("mental_state") == "Positive":
            current += 1
        else:
            break

    # Best streak ever
    best    = 0
    running = 0
    for a in reversed(analyses):
        if a.get("mental_state") == "Positive":
            running += 1
            best = max(best, running)
        else:
            running = 0

    streak_type = "positive" if current > 0 else "none"
    return {"current": current, "best": best, "type": streak_type}


def get_earned_badges(analyses: list) -> list:
    """
    Determine which badges the user has earned.
    Returns list of badge dicts.
    """
    if not analyses:
        return []

    earned  = []
    total   = len(analyses)
    streak  = get_streak(analyses)
    score   = get_wellness_score(analyses)

    states  = [a.get("mental_state", "Neutral") for a in analyses]

    # First session
    if total >= 1:
        earned.append(BADGES["first_session"])

    # Streak badges
    if streak["best"] >= 3:
        earned.append(BADGES["streak_3"])
    if streak["best"] >= 7:
        earned.append(BADGES["streak_7"])

    # Stress survivor — had 3+ stress then recovered to positive
    stress_then_positive = False
    stress_count = 0
    for state in states:
        if state in ("Stress", "Depression"):
            stress_count += 1
        elif state == "Positive" and stress_count >= 3:
            stress_then_positive = True
            break
    if stress_then_positive:
        earned.append(BADGES["stress_survivor"])

    # Consistent — sessions on 5+ different days
    if total >= 10:
        earned.append(BADGES["self_aware"])

    # Wellness master
    if score >= 80:
        earned.append(BADGES["wellness_master"])

    return earned


def get_progress_level(total_sessions: int) -> dict:
    """
    Returns user level based on total sessions.
    """
    levels = [
        (0,   "🌱 Beginner",    "Just starting your wellness journey"),
        (5,   "🌿 Explorer",    "Building self-awareness"),
        (15,  "🌳 Practitioner","Developing emotional intelligence"),
        (30,  "⭐ Advanced",    "Consistent emotional tracking"),
        (60,  "🏆 Master",      "Exceptional self-awareness"),
    ]

    level_label = levels[0]
    for threshold, label, desc in levels:
        if total_sessions >= threshold:
            level_label = (threshold, label, desc)

    # Next level threshold
    current_idx = next(
        (i for i, (t, _, _) in enumerate(levels) if t == level_label[0]),
        0
    )
    next_threshold = levels[current_idx + 1][0] if current_idx + 1 < len(levels) else None
    progress_to_next = None
    if next_threshold:
        progress_to_next = int((total_sessions - level_label[0]) /
                               (next_threshold - level_label[0]) * 100)

    return {
        "label":            level_label[1],
        "desc":             level_label[2],
        "next_threshold":   next_threshold,
        "progress_to_next": progress_to_next,
        "total_sessions":   total_sessions,
    }


def get_gamification_summary(analyses: list) -> dict:
    """
    Returns complete gamification data for dashboard display.
    """
    total   = len(analyses)
    score   = get_wellness_score(analyses)
    streak  = get_streak(analyses)
    badges  = get_earned_badges(analyses)
    level   = get_progress_level(total)

    return {
        "wellness_score": score,
        "streak":         streak,
        "badges":         badges,
        "level":          level,
        "total_sessions": total,
    }