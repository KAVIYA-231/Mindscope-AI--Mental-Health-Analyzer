"""
MindScope AI — Fusion Engine
File: engines/fusion_engine.py

Combines text emotion + face emotion → final emotional state.
"""

# ── Risk matrix ───────────────────────────────────────────────────────────────
RISK_MATRIX = {
    ("Positive",   "Positive"): ("Positive",   "Low"),
    ("Positive",   "Neutral"):  ("Positive",   "Low"),
    ("Positive",   "Stress"):   ("Neutral",    "Medium"),
    ("Neutral",    "Positive"): ("Neutral",    "Low"),
    ("Neutral",    "Neutral"):  ("Neutral",    "Low"),
    ("Neutral",    "Stress"):   ("Stress",     "Medium"),
    ("Stress",     "Positive"): ("Neutral",    "Medium"),
    ("Stress",     "Neutral"):  ("Stress",     "Medium"),
    ("Stress",     "Stress"):   ("Stress",     "High"),
    ("Depression", "Positive"): ("Neutral",    "Medium"),
    ("Depression", "Neutral"):  ("Depression", "High"),
    ("Depression", "Stress"):   ("Depression", "Critical"),
}

# Face emotion → mental state mapping
FACE_TO_MENTAL = {
    "Happy":    "Positive",
    "Surprise": "Positive",
    "Neutral":  "Neutral",
    "Sad":      "Stress",
    "Angry":    "Stress",
    "Fear":     "Stress",
    "Disgust":  "Stress",
}


def fuse_emotions(text_state: str, face_emotion: str | None) -> tuple:
    """
    Combines text mental state + face emotion into final state + risk level.

    Args:
        text_state   : predicted mental state from text model
        face_emotion : detected face emotion label (or None)

    Returns:
        (final_state, risk_level) tuple
    """
    if not face_emotion or face_emotion == "Not Detected":
        return text_state, _text_only_risk(text_state)

    face_mental = FACE_TO_MENTAL.get(face_emotion, "Neutral")
    return RISK_MATRIX.get((text_state, face_mental), (text_state, "Medium"))


def _text_only_risk(text_state: str) -> str:
    """Risk level when no face detected — based on text alone."""
    return {
        "Positive":   "Low",
        "Neutral":    "Low",
        "Stress":     "Medium",
        "Depression": "High",
    }.get(text_state, "Medium")


def get_face_mental(face_emotion: str) -> str:
    """Map a face emotion label to a mental state category."""
    return FACE_TO_MENTAL.get(face_emotion, "Neutral")