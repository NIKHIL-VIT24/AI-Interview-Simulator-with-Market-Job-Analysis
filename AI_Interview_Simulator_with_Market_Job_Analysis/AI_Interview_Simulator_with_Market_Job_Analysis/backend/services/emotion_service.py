"""
Emotion Detection Service — EfficientNet-B0
- Takes a webcam frame (image bytes or numpy array)
- Returns detected emotion and confidence
- Used to compute emotion_stability for behavioral score

GPU Memory: ~1GB VRAM (load after clearing Whisper cache)
"""
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as tv_models
import numpy as np
import cv2
import os
from PIL import Image
import io

# Emotion classes (FER dataset standard)
EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

# ── Model Setup ──────────────────────────────────────────────────────────────

_device = "cuda" if torch.cuda.is_available() else "cpu"
_emotion_model = None  # lazy load to save VRAM

MODEL_WEIGHTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "efficientnet_emotion.pth"
)

def _load_emotion_model():
    """Load EfficientNet-B0 fine-tuned for emotion detection."""
    global _emotion_model
    if _emotion_model is not None:
        return _emotion_model

    # Clear GPU cache before loading (sequential GPU strategy)
    if _device == "cuda":
        torch.cuda.empty_cache()

    model = tv_models.efficientnet_b0(weights=None)
    # Replace final classifier for 7 emotion classes
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 7)

    if os.path.exists(MODEL_WEIGHTS_PATH):
        model.load_state_dict(
            torch.load(MODEL_WEIGHTS_PATH, map_location=_device)
        )
        print("[Emotion CNN] Loaded fine-tuned weights.")
    else:
        print("[Emotion CNN] WARNING: No fine-tuned weights found.")
        print("  Using random weights — train the model on FER2013 dataset.")
        print(f"  Save weights to: {MODEL_WEIGHTS_PATH}")

    model = model.to(_device)
    model.eval()
    _emotion_model = model
    return model


# Image preprocessing pipeline
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),  # FER uses grayscale
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


# ── Inference ─────────────────────────────────────────────────────────────────

def detect_emotion_from_frame(frame_bytes: bytes) -> dict:
    """
    Detect emotion from a webcam frame.

    Args:
        frame_bytes: JPEG/PNG image bytes from frontend webcam

    Returns:
        dict with 'emotion', 'confidence', 'all_scores'
    """
    model = _load_emotion_model()

    # Decode image
    img_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame     = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}

    # Detect face region using OpenCV
    face_region = extract_face(frame)
    if face_region is None:
        face_region = frame  # Use full frame if no face detected

    # Convert to PIL and preprocess
    pil_img = Image.fromarray(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))
    tensor  = _transform(pil_img).unsqueeze(0).to(_device)

    with torch.no_grad():
        outputs     = model(tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]

    probs_list = probabilities.cpu().numpy().tolist()
    pred_idx   = int(np.argmax(probs_list))
    emotion    = EMOTION_CLASSES[pred_idx]
    confidence = probs_list[pred_idx]

    all_scores = {cls: round(float(p), 4)
                  for cls, p in zip(EMOTION_CLASSES, probs_list)}

    return {
        "emotion": emotion,
        "confidence": round(confidence, 4),
        "all_scores": all_scores
    }


def extract_face(frame: np.ndarray) -> np.ndarray:
    """Extract face region using OpenCV Haar cascade."""
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return None

    # Return largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return frame[y:y+h, x:x+w]


# ── Emotion Stability Calculator ─────────────────────────────────────────────

def compute_emotion_stability(emotion_history: list) -> float:
    """
    Compute emotion stability score from a sequence of detected emotions.
    Stable = mostly neutral/happy. Unstable = lots of fear/sad/angry.

    Args:
        emotion_history: list of emotion strings over the session

    Returns:
        stability score 0.0 to 1.0
    """
    if not emotion_history:
        return 0.5

    positive_emotions = {"neutral", "happy"}
    negative_emotions = {"angry", "fear", "sad", "disgust"}

    total   = len(emotion_history)
    pos_count = sum(1 for e in emotion_history if e in positive_emotions)
    neg_count = sum(1 for e in emotion_history if e in negative_emotions)

    # Consistency score (less switching = more stable)
    switches = sum(1 for i in range(1, total)
                   if emotion_history[i] != emotion_history[i-1])
    consistency = 1.0 - (switches / total)

    # Positivity score
    positivity = pos_count / total

    # Combined stability
    stability = 0.6 * positivity + 0.4 * consistency
    return round(min(1.0, max(0.0, stability)), 4)


def unload_emotion_model():
    """
    Unload emotion model from GPU memory.
    Call this after processing a batch of frames to free VRAM.
    """
    global _emotion_model
    if _emotion_model is not None and _device == "cuda":
        _emotion_model.cpu()
        _emotion_model = None
        torch.cuda.empty_cache()
        print("[Emotion CNN] Model unloaded from GPU.")
