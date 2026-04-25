"""
MindScope AI — API Endpoints
File: api/endpoints.py

Demo integration-ready endpoint.
Run standalone: python api/endpoints.py
Then test: POST http://localhost:5000/analyze

Future mobile apps can call this API directly.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
import pickle
import numpy as np
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# ── Lazy load text model ──────────────────────────────────────────────────────
_model      = None
_vectorizer = None
_le         = None

def _load_models():
    global _model, _vectorizer, _le
    if _model is None:
        from tensorflow.keras.models import load_model
        _model      = load_model("models/text_mental_model.keras")
        _vectorizer = pickle.load(open("models/vectorizer.pkl", "rb"))
        _le         = pickle.load(open("models/label_encoder.pkl", "rb"))


# ── Main endpoint ─────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze_text():
    """
    Analyze text emotion and return result.

    Request JSON:
        { "text": "I feel very stressed today" }

    Response JSON:
        {
            "text":        "I feel very stressed today",
            "mental_state": "Stress",
            "confidence":   0.87,
            "risk_level":   "Medium",
            "insight":      "..."
        }
    """
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data["text"].strip()
        if not text:
            return jsonify({"error": "Empty text provided"}), 400

        _load_models()

        # Predict
        vec        = _vectorizer.transform([text]).toarray()
        preds      = _model.predict(vec)[0]
        idx        = int(np.argmax(preds))
        state      = _le.inverse_transform([idx])[0]
        confidence = float(preds[idx])

        # Risk
        from engines.fusion_engine import fuse_emotions
        final_state, risk = fuse_emotions(state, None)

        # Insight (Gemini or fallback)
        try:
            from models.gemini_insight import get_gemini_insight
            title, body = get_gemini_insight(
                user_text    = text,
                text_state   = state,
                face_emotion = "Not Detected",
                final_state  = final_state,
                risk_level   = risk,
            )
            insight = f"{title} — {body}"
        except Exception:
            insight = "Analysis complete. Monitor your emotions and take regular breaks."

        return jsonify({
            "text":         text,
            "mental_state": final_state,
            "confidence":   round(confidence, 3),
            "risk_level":   risk,
            "insight":      insight,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "MindScope AI API is running ✅"})


if __name__ == "__main__":
    print("🚀 MindScope AI API running at http://localhost:5000")
    print("📡 Endpoints: POST /analyze | GET /health")
    app.run(debug=True, port=5000)