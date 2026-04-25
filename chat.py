"""
MindScope AI — Chat Page
File: pages/chat.py

Gemini-powered mental wellness chatbot.
Remembers conversation history + aware of user's emotion history.
"""

import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_theme import apply_theme, page_header, section_header, divider
from database.db_service      import get_all_analyses
from engines.analytics_engine import build_dataframe, get_summary_stats


# ── Gemini chat call ──────────────────────────────────────────────────────────
def call_gemini_chat(messages: list, system_prompt: str) -> str:
    """
    Send conversation history to Gemini and get a response.
    messages: list of {"role": "user"|"assistant", "content": str}
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ Gemini API key not found. Please check your .env file."

        from google import genai

        client = genai.Client(api_key=api_key)

        # Build full conversation as single prompt with history
        history_text = ""
        for msg in messages[:-1]:  # all except latest user message
            role    = "User" if msg["role"] == "user" else "MindScope AI"
            history_text += f"{role}: {msg['content']}\n"

        latest = messages[-1]["content"]

        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{history_text}
User: {latest}
MindScope AI:"""

        response = client.models.generate_content(
            model    = "gemini-2.0-flash",
            contents = full_prompt,
        )
        return response.text.strip()

    except Exception as e:
        return f"⚠️ Could not reach Gemini: {str(e)[:120]}. Please check your API key."


def build_system_prompt(stats: dict, patterns: list) -> str:
    """Build a context-aware system prompt using user's emotion history."""
    total      = stats.get("total", 0)
    pos_pct    = stats.get("pos_pct", 0)
    stress_pct = stats.get("stress_pct", 0)
    dep_pct    = stats.get("dep_pct", 0)
    pattern_text = "\n".join(f"- {p}" for p in patterns) if patterns else "- No patterns detected yet."

    return f"""You are MindScope AI — a warm, empathetic, and professional mental wellness companion.

You have access to this user's emotional history:
- Total sessions: {total}
- Positive: {pos_pct}%
- Stress: {stress_pct}%
- Depression: {dep_pct}%
- Detected patterns:
{pattern_text}

Your role:
1. Listen actively and respond with genuine empathy.
2. Give personalised advice based on their emotional history.
3. Suggest practical, science-backed wellness techniques.
4. If the user shows signs of crisis, gently suggest iCall India: 9152987821.
5. Keep responses concise (3-5 sentences max unless asked for more).
6. Never diagnose. You are a supportive companion, not a doctor.
7. Use the user's history naturally — don't repeat it robotically.
8. Always end with an open question to keep the conversation going.

Respond in a warm, conversational tone. No bullet points unless asked."""


# ── Chat bubble HTML ──────────────────────────────────────────────────────────
def user_bubble(text: str) -> str:
    return f"""
    <div style="display:flex;justify-content:flex-end;margin-bottom:12px">
        <div style="max-width:75%;background:linear-gradient(135deg,#0ea5e9,#6366f1);
                    border-radius:18px 18px 4px 18px;padding:12px 16px;
                    font-size:14px;color:white;line-height:1.6">
            {text}
        </div>
        <div style="width:32px;height:32px;border-radius:50%;background:#1e2d45;
                    display:flex;align-items:center;justify-content:center;
                    margin-left:8px;flex-shrink:0;font-size:14px">👤</div>
    </div>
    """


def bot_bubble(text: str) -> str:
    # Convert newlines to <br> for HTML
    text_html = text.replace("\n", "<br>")
    return f"""
    <div style="display:flex;justify-content:flex-start;margin-bottom:12px">
        <div style="width:32px;height:32px;border-radius:50%;
                    background:linear-gradient(135deg,#0ea5e9,#6366f1);
                    display:flex;align-items:center;justify-content:center;
                    margin-right:8px;flex-shrink:0;font-size:14px">🧠</div>
        <div style="max-width:75%;background:#111827;border:1px solid #1e2d45;
                    border-radius:18px 18px 18px 4px;padding:12px 16px;
                    font-size:14px;color:#e2e8f0;line-height:1.7">
            {text_html}
        </div>
    </div>
    """


# ════════════════════════════════════════════════════════════════════════════
def chat_page():
    apply_theme()

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">Mind<span>Scope</span> AI</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:1.5rem">
            Emotion Intelligence System
        </div>
        """, unsafe_allow_html=True)

        # Clear chat button
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

        st.markdown("""
        <div style="font-size:12px;color:#64748b;margin-top:1rem;line-height:1.6">
            💡 <b>Tips:</b><br>
            • Share how you're feeling<br>
            • Ask for coping strategies<br>
            • Talk about your day<br>
            • Ask about your patterns
        </div>
        """, unsafe_allow_html=True)

    page_header("MindScope", "Chat",
                "Your personal AI wellness companion")

    # ── Load user context ─────────────────────────────────────────────────────
    user_id = st.session_state.get("user_id")
    try:
        analyses = get_all_analyses(user_id)
    except Exception:
        analyses = []

    from engines.analytics_engine import detect_patterns
    df       = build_dataframe(analyses)
    stats    = get_summary_stats(df)
    patterns = detect_patterns(df)

    # ── Session state ─────────────────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # ── User context card ─────────────────────────────────────────────────────
    total      = stats.get("total", 0)
    pos_pct    = stats.get("pos_pct", 0)
    stress_pct = stats.get("stress_pct", 0)

    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1e2d45;border-radius:14px;
                padding:14px 18px;margin-bottom:1rem;
                display:flex;gap:24px;align-items:center;flex-wrap:wrap">
        <div style="font-size:11px;color:#64748b;letter-spacing:1px;
                    text-transform:uppercase;margin-right:4px">Your context</div>
        <div style="font-size:13px;color:#e2e8f0">
            🧠 <b>{total}</b> sessions
        </div>
        <div style="font-size:13px;color:#34d399">
            🌟 <b>{pos_pct}%</b> positive
        </div>
        <div style="font-size:13px;color:#fb923c">
            ⚠️ <b>{stress_pct}%</b> stress
        </div>
        <div style="font-size:11px;color:#475569;margin-left:auto">
            ✦ Powered by Gemini
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Welcome message ───────────────────────────────────────────────────────
    if not st.session_state.chat_messages:
        welcome = "Hey there! 👋 I'm MindScope AI, your personal wellness companion. I've been following your emotional journey and I'm here to chat, support, and guide you. How are you feeling right now?"
        st.session_state.chat_messages.append({
            "role": "assistant", "content": welcome
        })

    # ── Chat display area ─────────────────────────────────────────────────────
    chat_html = '<div style="min-height:400px;max-height:500px;overflow-y:auto;padding:4px 0">'
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            chat_html += user_bubble(msg["content"])
        else:
            chat_html += bot_bubble(msg["content"])
    chat_html += "</div>"

    st.markdown(f"""
    <div style="background:#0d1220;border:1px solid #1e2d45;border-radius:16px;
                padding:20px;margin-bottom:1rem">
        {chat_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Input area ────────────────────────────────────────────────────────────
    divider()

    # Quick prompt suggestions
    section_header("💬", "Quick Prompts")
    qp_cols = st.columns(4)
    quick_prompts = [
        "I'm feeling stressed today",
        "Give me a breathing exercise",
        "What do my patterns say?",
        "I need some motivation",
    ]
    selected_quick = None
    for i, prompt in enumerate(quick_prompts):
        with qp_cols[i]:
            if st.button(prompt, use_container_width=True, key=f"qp_{i}"):
                selected_quick = prompt

    # Text input
    user_input = st.chat_input("Type your message here...")

    # Use quick prompt if selected
    final_input = selected_quick or user_input

    if final_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user", "content": final_input
        })

        # Build system prompt with user context
        system_prompt = build_system_prompt(stats, patterns)

        # Get Gemini response
        with st.spinner("🧠 MindScope is thinking..."):
            response = call_gemini_chat(
                messages      = st.session_state.chat_messages,
                system_prompt = system_prompt,
            )

        # Add bot response
        st.session_state.chat_messages.append({
            "role": "assistant", "content": response
        })

        st.rerun()

    # ── Crisis resource (always visible at bottom) ────────────────────────────
    st.markdown("""
    <div style="background:rgba(248,113,113,0.05);border:1px solid rgba(248,113,113,0.15);
                border-radius:10px;padding:10px 16px;margin-top:1rem;
                font-size:12px;color:#64748b;text-align:center">
        🆘 If you're in crisis, please reach out:
        <b style="color:#f87171">iCall India: 9152987821</b> &nbsp;|&nbsp;
        Vandrevala Foundation: <b style="color:#f87171">1860-2662-345</b>
    </div>
    """, unsafe_allow_html=True)


chat_page()