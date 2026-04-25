"""
MindScope AI — Gemini Insight Engine
File: models/gemini_insight.py

Uses the NEW google-genai package (google.generativeai is deprecated).
Install: pip install google-genai
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

FALLBACK_INSIGHTS = {
    ("Positive",   "Low"):      ("🌟 You're in a great headspace!",
                                 "Keep up your positive habits — journaling, exercise, and social connection sustain this state."),
    ("Positive",   "Medium"):   ("🙂 Text sounds positive but some tension detected.",
                                 "Take a short mindfulness break. There may be underlying stress worth addressing."),
    ("Neutral",    "Low"):      ("😐 You're in a calm, balanced state.",
                                 "Good time for focused work. Set one clear goal for the next 2 hours."),
    ("Neutral",    "Medium"):   ("⚠️ Mixed emotional signals detected.",
                                 "Try a 5-minute breathing exercise to realign your emotional state."),
    ("Stress",     "Medium"):   ("😟 Moderate stress detected.",
                                 "Try the 4-7-8 technique: inhale 4s, hold 7s, exhale 8s. Repeat 3 times."),
    ("Stress",     "High"):     ("🚨 High stress level detected.",
                                 "Step away from your screen. Walk for 10 minutes. Avoid caffeine. Talk to someone you trust."),
    ("Depression", "High"):     ("💙 Signs of low mood detected.",
                                 "You are not alone. Reach out to a friend, family, or counsellor. Small steps matter."),
    ("Depression", "Critical"): ("🆘 Critical emotional state detected.",
                                 "Please contact a mental health professional. iCall India: 9152987821"),
}


def _build_prompt(user_text, text_state, face_emotion, final_state, risk_level):
    return f"""
You are MindScope AI — a compassionate, professional mental wellness assistant.

A user just completed an emotion analysis. Here is their data:

USER'S TEXT: "{user_text}"
TEXT MENTAL STATE: {text_state}
FACE EMOTION: {face_emotion}
FINAL FUSED STATE: {final_state}
RISK LEVEL: {risk_level}

Generate a SHORT, PERSONALISED mental wellness insight based on this data.

Rules:
1. Be warm and empathetic — not clinical or robotic.
2. Reference the user's actual emotional state naturally.
3. Give 1 specific, actionable recommendation suited to their state.
4. If risk is High or Critical, mention professional support: iCall India: 9152987821
5. Title under 10 words. Body under 60 words.
6. Make it feel personal, not generic.

Respond in EXACTLY this format (no extra text, no markdown, no asterisks):
TITLE: <short empathetic title here>
BODY: <personalised insight and recommendation here>
""".strip()


def _parse_response(raw, final_state, risk_level):
    title = ""
    body  = ""
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("BODY:"):
            body = line.replace("BODY:", "").strip()

    if not title or not body:
        fallback_title, fallback_body = FALLBACK_INSIGHTS.get(
            (final_state, risk_level),
            ("📊 Analysis complete.", "Monitor your emotions and take regular breaks.")
        )
        return fallback_title, raw if raw else fallback_body

    emoji_map = {
        "Positive": "🌟", "Neutral": "😐",
        "Stress": "😟",   "Depression": "💙"
    }
    emoji = emoji_map.get(final_state, "🧠")
    return f"{emoji} {title}", body


def get_gemini_insight(
    user_text:    str,
    text_state:   str,
    face_emotion: str,
    final_state:  str,
    risk_level:   str,
) -> tuple:
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")

        from google import genai

        client   = genai.Client(api_key=api_key)
        prompt   = _build_prompt(user_text, text_state, face_emotion, final_state, risk_level)

        response = client.models.generate_content(
            model    = "gemini-2.0-flash",
            contents = prompt,
        )

        raw = response.text.strip()
        print(f"[Gemini] Raw response:\n{raw}")

        return _parse_response(raw, final_state, risk_level)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Gemini] Fallback triggered: {e}")
        return FALLBACK_INSIGHTS.get(
            (final_state, risk_level),
            ("📊 Analysis complete.",
             "Monitor your emotions over the next few hours and take regular breaks.")
        )