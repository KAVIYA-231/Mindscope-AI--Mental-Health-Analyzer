"""
MindScope AI — Analytics Engine
File: engines/analytics_engine.py

Handles all data aggregation, trend analysis,
weekly comparisons, and pattern detection.
"""

import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict


# ── State numeric mapping (lower = better) ───────────────────────────────────
STATE_SCORE = {
    "Positive":   4,
    "Neutral":    3,
    "Stress":     2,
    "Depression": 1,
}


def build_dataframe(analyses: list) -> pd.DataFrame:
    """
    Convert list of analysis dicts to a clean DataFrame.
    Handles missing/inconsistent columns gracefully.
    """
    if not analyses:
        return pd.DataFrame()

    df = pd.DataFrame(analyses)

    # Normalise column names
    rename_map = {
        "state":      "mental_state",
        "emotion":    "mental_state",
        "created_at": "timestamp",
        "date":       "timestamp",
        "time":       "timestamp",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns},
              inplace=True)

    # Parse timestamp
    date_col = next(
        (c for c in df.columns if "time" in c.lower() or "date" in c.lower()),
        None
    )
    if date_col and date_col != "timestamp":
        df.rename(columns={date_col: "timestamp"}, inplace=True)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp")
        df["date"]  = df["timestamp"].dt.date
        df["hour"]  = df["timestamp"].dt.hour
        df["week"]  = df["timestamp"].dt.isocalendar().week
        df["month"] = df["timestamp"].dt.month

    # Add numeric score column
    if "mental_state" in df.columns:
        df["score"] = df["mental_state"].map(STATE_SCORE).fillna(3)

    return df


def get_emotion_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns daily emotion score trend for line chart.
    Aggregates by date, calculates mean score.
    """
    if df.empty or "timestamp" not in df.columns:
        return pd.DataFrame()

    trend = (
        df.groupby("date")["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "avg_score", "date": "Date"})
    )
    trend["avg_score"] = trend["avg_score"].round(2)

    # Add 3-day moving average
    trend["moving_avg"] = trend["avg_score"].rolling(window=3, min_periods=1).mean().round(2)

    return trend


def get_weekly_comparison(df: pd.DataFrame) -> dict:
    """
    Compare this week vs last week for each emotion state.
    Returns dict with increase/decrease info.
    """
    if df.empty or "timestamp" not in df.columns:
        return {}

    now        = datetime.now()
    this_week  = now - timedelta(days=7)
    last_week  = now - timedelta(days=14)

    this_df = df[df["timestamp"] >= this_week]
    last_df = df[(df["timestamp"] >= last_week) & (df["timestamp"] < this_week)]

    states  = ["Positive", "Neutral", "Stress", "Depression"]
    result  = {}

    for state in states:
        this_count = len(this_df[this_df["mental_state"] == state]) if "mental_state" in this_df.columns else 0
        last_count = len(last_df[last_df["mental_state"] == state]) if "mental_state" in last_df.columns else 0
        diff       = this_count - last_count
        result[state] = {
            "this_week":  this_count,
            "last_week":  last_count,
            "diff":       diff,
            "direction":  "up" if diff > 0 else "down" if diff < 0 else "same",
        }

    return result


def get_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns emotion intensity heatmap data: hour of day vs day of week.
    """
    if df.empty or "timestamp" not in df.columns:
        return pd.DataFrame()

    df["day_of_week"] = df["timestamp"].dt.day_name()
    heatmap = (
        df.groupby(["day_of_week", "hour"])["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "intensity"})
    )
    return heatmap


def detect_patterns(df: pd.DataFrame) -> list:
    """
    Detect behavioural patterns in user's emotion history.
    Returns list of human-readable pattern strings.
    """
    patterns = []

    if df.empty or len(df) < 5:
        return patterns

    # Pattern 1: Evening stress
    if "hour" in df.columns:
        evening = df[(df["hour"] >= 18) & (df["hour"] <= 23)]
        if len(evening) >= 3:
            eve_stress = len(evening[evening["mental_state"].isin(["Stress", "Depression"])])
            if eve_stress / len(evening) > 0.5:
                patterns.append("😟 You tend to feel more stressed in the evenings.")

        # Pattern 2: Morning positivity
        morning = df[(df["hour"] >= 6) & (df["hour"] <= 11)]
        if len(morning) >= 3:
            morn_pos = len(morning[morning["mental_state"] == "Positive"])
            if morn_pos / len(morning) > 0.6:
                patterns.append("🌅 You're usually in a positive mood in the mornings.")

    # Pattern 3: Improving trend
    if len(df) >= 6 and "score" in df.columns:
        first_half = df.iloc[:len(df)//2]["score"].mean()
        second_half = df.iloc[len(df)//2:]["score"].mean()
        if second_half > first_half + 0.3:
            patterns.append("📈 Your emotional state has been improving over time!")
        elif second_half < first_half - 0.3:
            patterns.append("📉 Your emotional state has been declining recently.")

    # Pattern 4: Dominant emotion
    if "mental_state" in df.columns:
        dominant = df["mental_state"].value_counts().idxmax()
        pct = int(df["mental_state"].value_counts(normalize=True).max() * 100)
        emoji = {"Positive":"🌟","Neutral":"😐","Stress":"😟","Depression":"💙"}.get(dominant,"🧠")
        patterns.append(f"{emoji} Your dominant emotional state is {dominant} ({pct}% of sessions).")

    return patterns


def get_state_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Returns state value counts as DataFrame for charts."""
    if df.empty or "mental_state" not in df.columns:
        return pd.DataFrame()

    counts = df["mental_state"].value_counts().reset_index()
    counts.columns = ["Mental State", "Count"]
    return counts


def get_summary_stats(df: pd.DataFrame) -> dict:
    """Returns quick summary statistics dict."""
    if df.empty:
        return {}

    total      = len(df)
    state_col  = "mental_state" if "mental_state" in df.columns else None

    return {
        "total":       total,
        "positive":    len(df[df[state_col] == "Positive"])    if state_col else 0,
        "neutral":     len(df[df[state_col] == "Neutral"])     if state_col else 0,
        "stress":      len(df[df[state_col] == "Stress"])      if state_col else 0,
        "depression":  len(df[df[state_col] == "Depression"])  if state_col else 0,
        "pos_pct":     int(len(df[df[state_col]=="Positive"])  / total * 100) if state_col else 0,
        "stress_pct":  int(len(df[df[state_col]=="Stress"])    / total * 100) if state_col else 0,
        "dep_pct":     int(len(df[df[state_col]=="Depression"])/ total * 100) if state_col else 0,
    }