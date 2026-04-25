"""
MindScope AI — Face Model Inspector
Run this FIRST to understand your model's input shape and output labels.
Usage: python inspect_face_model.py
"""

import numpy as np

def inspect_model(model_path="models/face_emotion_model.keras"):
    try:
        from tensorflow.keras.models import load_model
        model = load_model(model_path)
    except Exception as e:
        print(f"❌ Could not load model from '{model_path}': {e}")
        print("👉 Try changing model_path to the correct filename.")
        return

    print("=" * 50)
    print("✅ MODEL LOADED SUCCESSFULLY")
    print("=" * 50)

    input_shape = model.input_shape
    output_shape = model.output_shape
    num_classes = output_shape[-1]

    print(f"\n📥 Input Shape  : {input_shape}")
    print(f"📤 Output Shape : {output_shape}")
    print(f"🔢 Num Classes  : {num_classes}")

    # Detect image dimensions
    if len(input_shape) == 4:
        _, h, w, c = input_shape
        print(f"\n🖼️  Image Size   : {h}x{w}")
        print(f"🎨 Channels     : {'Grayscale (1)' if c == 1 else 'RGB (3)' if c == 3 else c}")
    else:
        print(f"\n⚠️  Unexpected input shape: {input_shape}")

    # Standard FER label sets
    standard_labels = {
        7: ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"],
        6: ["Angry", "Fear", "Happy", "Sad", "Surprise", "Neutral"],
        5: ["Angry", "Happy", "Sad", "Surprise", "Neutral"],
        4: ["Happy", "Sad", "Angry", "Neutral"],
        3: ["Positive", "Neutral", "Negative"],
    }

    print(f"\n🏷️  Suggested Labels for {num_classes} classes:")
    if num_classes in standard_labels:
        print(f"   {standard_labels[num_classes]}")
        print("\n✅ Copy the label list above into your face_detector.py")
    else:
        print(f"   ⚠️ Unknown class count ({num_classes}). Check your training labels manually.")

    print("\n" + "=" * 50)
    print("📋 SUMMARY — paste this into face_detector.py:")
    print("=" * 50)
    if len(input_shape) == 4:
        _, h, w, c = input_shape
        print(f"IMG_SIZE    = ({h}, {w})")
        print(f"CHANNELS    = {c}  # 1=grayscale, 3=RGB")
        if num_classes in standard_labels:
            print(f"FACE_LABELS = {standard_labels[num_classes]}")
    print("=" * 50)

    # Model layer summary
    print("\n📐 Layer Summary:")
    model.summary()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "models/face_emotion_model.keras"
    inspect_model(path)