"""
MindScope AI — Face Emotion Detector
File: models/face_detector.py

After running inspect_face_model.py, update the 3 config values below.
"""

import cv2
import numpy as np

# ─────────────────────────────────────────────
# ✏️  UPDATE THESE 3 VALUES after running inspect_face_model.py
# ─────────────────────────────────────────────
IMG_SIZE    = (64, 64)           # e.g. (48,48) or (64,64)
CHANNELS    = 3                  # 1 = grayscale, 3 = RGB
FACE_LABELS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
# ─────────────────────────────────────────────

# Map face emotions → mental states (for fusion)
FACE_TO_MENTAL = {
    "Happy"    : "Positive",
    "Surprise" : "Positive",
    "Neutral"  : "Neutral",
    "Sad"      : "Stress",
    "Angry"    : "Stress",
    "Fear"     : "Stress",
    "Disgust"  : "Stress",
}

_model = None  # lazy-loaded

def _load_model():
    global _model
    if _model is None:
        from tensorflow.keras.models import load_model
        import os
        path = os.path.join(os.path.dirname(__file__), "face_emotion_model.keras")
        _model = load_model(path)
    return _model


def _preprocess_face(face_img: np.ndarray) -> np.ndarray:
    """Resize and normalise a cropped face for model input."""
    face = cv2.resize(face_img, IMG_SIZE)
    if CHANNELS == 1:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face = face.reshape(1, IMG_SIZE[0], IMG_SIZE[1], 1)
    else:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = face.reshape(1, IMG_SIZE[0], IMG_SIZE[1], 3)
    face = face.astype("float32") / 255.0
    return face


def predict_face_emotion(face_img: np.ndarray):
    """
    Given a cropped face (BGR numpy array), return:
        emotion   : str   — predicted label
        confidence: float — probability (0-1)
        mental    : str   — mapped mental state
        all_probs : dict  — {label: prob} for all classes
    """
    model = _load_model()
    processed = _preprocess_face(face_img)
    preds = model.predict(processed, verbose=0)[0]

    idx        = int(np.argmax(preds))
    emotion    = FACE_LABELS[idx]
    confidence = float(preds[idx])
    mental     = FACE_TO_MENTAL.get(emotion, "Neutral")
    all_probs  = {FACE_LABELS[i]: float(preds[i]) for i in range(len(FACE_LABELS))}

    return emotion, confidence, mental, all_probs


# ── Haar cascade (ships with OpenCV, no download needed) ──────────────────────
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(frame: np.ndarray):
    """Return list of (x, y, w, h) bounding boxes in frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48)
    )
    return faces if len(faces) else []


def annotate_frame(frame: np.ndarray, faces, results: list) -> np.ndarray:
    """
    Draw bounding boxes + labels on frame.
    results: list of (emotion, confidence) per face.
    """
    annotated = frame.copy()
    for i, (x, y, w, h) in enumerate(faces):
        if i < len(results):
            emotion, conf = results[i]
            label = f"{emotion} {conf*100:.1f}%"
        else:
            label = "Detecting..."

        color = (0, 200, 100) if emotion in ("Happy", "Surprise") else \
                (0, 100, 255) if emotion == "Neutral" else (0, 60, 220)

        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.rectangle(annotated, (x, y - 28), (x + w, y), color, -1)
        cv2.putText(
            annotated, label, (x + 4, y - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
    return annotated