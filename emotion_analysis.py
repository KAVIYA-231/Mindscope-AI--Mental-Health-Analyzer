"""
MindScope AI — Emotion Analysis Page
File: pages/emotion_analysis.py
"""

import streamlit as st
import cv2, numpy as np, time, sys, os, pickle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from custom_theme import (
    apply_theme, page_header, section_header,
    state_card, insight_box, confidence_bar,
    risk_badge, divider, STATE_COLORS
)
from database.db_service  import save_prediction
from models.face_detector  import detect_faces, predict_face_emotion, annotate_frame
from models.gemini_insight import get_gemini_insight


@st.cache_resource
def load_text_model():
    from tensorflow.keras.models import load_model
    model      = load_model("models/text_mental_model.keras")
    vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))
    le         = pickle.load(open("models/label_encoder.pkl", "rb"))
    return model, vectorizer, le


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

def fuse_emotions(text_state, face_mental):
    if not face_mental:
        return text_state, "Unknown"
    return RISK_MATRIX.get((text_state, face_mental), (text_state, "Medium"))


def emotion_analysis_page():
    apply_theme()

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">Mind<span>Scope</span> AI</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:1.5rem">
            Emotion Intelligence System
        </div>
        """, unsafe_allow_html=True)

    page_header("Emotion", "Analysis", "Multi-modal AI — text + face fusion")

    model, vectorizer, le = load_text_model()

    for key, default in [
        ("face_emotion", None), ("face_confidence", 0.0),
        ("face_mental", None),  ("face_all_probs", {}),
        ("webcam_running", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── STEP 1: TEXT ──────────────────────────────────────────────────────────
    section_header("📝", "Step 1 — Enter Your Thoughts")
    user_text = st.text_area(
        "", height=130,
        placeholder="How are you feeling right now? Type anything...",
        label_visibility="collapsed"
    )
    divider()

    # ── STEP 2: WEBCAM ────────────────────────────────────────────────────────
    section_header("📷", "Step 2 — Real-Time Face Detection")

    c_start, c_stop, _ = st.columns([1, 1, 5])
    with c_start:
        if st.button("▶ Start", use_container_width=True,
                     disabled=st.session_state.webcam_running):
            st.session_state.webcam_running = True
    with c_stop:
        if st.button("⏹ Stop", use_container_width=True,
                     disabled=not st.session_state.webcam_running):
            st.session_state.webcam_running = False

    cam_placeholder    = st.empty()
    status_placeholder = st.empty()

    if st.session_state.webcam_running:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("❌ Webcam not accessible. Check camera permissions.")
            st.session_state.webcam_running = False
        else:
            status_placeholder.markdown("""
            <div style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2);
                        border-radius:10px;padding:10px 16px;font-size:13px;color:#38bdf8">
                📡 Camera active — detecting face emotions...
            </div>""", unsafe_allow_html=True)

            frame_count = 0
            while st.session_state.webcam_running:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % 3 == 0:
                    faces   = detect_faces(frame)
                    results = []
                    if len(faces) > 0:
                        x, y, w, h = faces[0]
                        face_crop  = frame[y:y+h, x:x+w]
                        emotion, confidence, mental, all_probs = predict_face_emotion(face_crop)
                        st.session_state.face_emotion    = emotion
                        st.session_state.face_confidence = confidence
                        st.session_state.face_mental     = mental
                        st.session_state.face_all_probs  = all_probs
                        results = [(emotion, confidence)]
                    annotated = annotate_frame(frame, faces, results)
                    cam_placeholder.image(
                        cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                        channels="RGB", use_column_width=True
                    )
                time.sleep(0.03)
            cap.release()
            cam_placeholder.empty()
            status_placeholder.markdown("""
            <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
                        border-radius:10px;padding:10px 16px;font-size:13px;color:#34d399">
                ✅ Camera stopped. Snapshot locked in.
            </div>""", unsafe_allow_html=True)

    if st.session_state.face_emotion:
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;
                    padding:14px 18px;margin-top:10px;display:flex;align-items:center;gap:14px">
            <span style="font-size:28px">😶</span>
            <div>
                <div style="font-size:11px;color:#64748b;letter-spacing:1px;text-transform:uppercase">
                    Last Face Reading
                </div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#fb923c">
                    {st.session_state.face_emotion}
                    <span style="font-size:13px;font-weight:400;color:#64748b;
                                 font-family:'DM Sans',sans-serif">
                        &nbsp;{st.session_state.face_confidence*100:.1f}% confidence
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📊 Full face emotion probability breakdown"):
            bar_colors = {
                "Happy":"#34d399","Surprise":"#38bdf8","Neutral":"#94a3b8",
                "Sad":"#fb923c","Angry":"#f87171","Fear":"#c084fc","Disgust":"#64748b"
            }
            for lbl, prob in sorted(st.session_state.face_all_probs.items(),
                                    key=lambda x: x[1], reverse=True):
                confidence_bar(lbl, prob, bar_colors.get(lbl, "#38bdf8"))

    divider()

    # ── ANALYSE BUTTON ────────────────────────────────────────────────────────
    analyse = st.button("🔍 Analyse My Emotion", use_container_width=True, type="primary")

    if analyse:
        if not user_text.strip():
            st.warning("Please enter some text before analysing.")
            return

        # Text prediction
        vec        = vectorizer.transform([user_text]).toarray()
        preds      = model.predict(vec)[0]
        idx        = int(np.argmax(preds))
        text_state = le.inverse_transform([idx])[0]
        text_conf  = float(preds[idx])
        text_probs = {le.inverse_transform([i])[0]: float(preds[i]) for i in range(len(preds))}

        # Fusion
        face_mental       = st.session_state.face_mental
        final_state, risk = fuse_emotions(text_state, face_mental)

        # ── Results ───────────────────────────────────────────────────────────
        divider()
        section_header("📊", "Results")

        c1, c2, c3 = st.columns(3)
        with c1:
            state_card("Text Mental State", text_state,
                       f"{text_conf*100:.1f}% confidence",
                       STATE_COLORS.get(text_state, "#38bdf8"))
        with c2:
            fe = st.session_state.face_emotion or "Not Detected"
            fc = st.session_state.face_confidence
            state_card("Face Emotion", fe,
                       f"{fc*100:.1f}% confidence" if fe != "Not Detected" else "Use webcam above",
                       "#fb923c" if fe != "Not Detected" else "#64748b")
        with c3:
            state_card("Final State (Fused)", final_state,
                       "multi-modal result",
                       STATE_COLORS.get(final_state, "#38bdf8"))

        st.markdown("<br>", unsafe_allow_html=True)
        risk_badge(risk)

        with st.expander("📊 Text prediction confidence breakdown"):
            text_colors = {"Positive":"#34d399","Neutral":"#38bdf8",
                           "Stress":"#fb923c","Depression":"#f87171"}
            for lbl, prob in sorted(text_probs.items(), key=lambda x: x[1], reverse=True):
                confidence_bar(lbl, prob, text_colors.get(lbl, "#38bdf8"))

        divider()

        # ── Gemini Insight ────────────────────────────────────────────────────
        section_header("🤖", "AI-Generated Insight")

        face_label = st.session_state.face_emotion or "Not Detected"

        with st.spinner("✨ Generating personalised insight with Gemini AI..."):
            insight_title, insight_body = get_gemini_insight(
                user_text    = user_text,
                text_state   = text_state,
                face_emotion = face_label,
                final_state  = final_state,
                risk_level   = risk,
            )

        insight_box(insight_title, insight_body)

        st.markdown("""
        <div style="margin-top:8px">
            <span style="background:rgba(129,140,248,0.12);color:#818cf8;
                         padding:4px 12px;border-radius:999px;font-size:11px;
                         font-weight:600;letter-spacing:0.5px">
                ✦ Powered by Gemini 1.5 Flash
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Save ──────────────────────────────────────────────────────────────
        save_prediction(
            user_id      = st.session_state.get("user_id"),
            text         = user_text,
            face_emotion = face_label,
            mental_state = final_state,
            insight      = insight_body,
        )
        st.markdown("""
        <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
                    border-radius:10px;padding:10px 16px;font-size:13px;
                    color:#34d399;margin-top:12px">
            ✅ Analysis saved to your history.
        </div>""", unsafe_allow_html=True)


emotion_analysis_page()