# backend/model_loader.py
# ─────────────────────────────────────────────────────────────
# Sasyam — Model loader with Hugging Face Hub fallback
# Downloads model if not cached locally, then loads with Keras.
# Exposes predict(image_array) → {class_name, confidence}
# ─────────────────────────────────────────────────────────────

import os
import json
import asyncio
import numpy as np

# Lazy imports (avoid hard crash if TF not installed in dev)
_model          = None
_class_indices  = {}      # { "Wheat": 0, "Rice": 1, … }
_idx_to_class   = {}      # reverse: { 0: "Wheat", … }

LOCAL_MODEL_PATH  = os.environ.get("LOCAL_MODEL_PATH",  "sasyam_crop_model.h5")
HF_MODEL_REPO     = os.environ.get("HF_MODEL_REPO",     "")   # e.g. "your-username/sasyam-crop-model"
HF_TOKEN          = os.environ.get("HF_TOKEN",          "")
CLASS_INDICES_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "class_indices.json")

# Fallback class list (used when class_indices.json is empty / missing)
FALLBACK_CLASSES  = ["Corn", "Wheat", "Sugarcane", "Other"]


def _load_class_indices():
    global _class_indices, _idx_to_class

    if os.path.exists(CLASS_INDICES_PATH):
        with open(CLASS_INDICES_PATH, "r") as f:
            try:
                _class_indices = json.load(f)
            except json.JSONDecodeError:
                _class_indices = {}

    if not _class_indices:
        print("[model_loader] class_indices.json empty — using fallback classes.")
        _class_indices = {c: i for i, c in enumerate(FALLBACK_CLASSES)}

    _idx_to_class = {v: k for k, v in _class_indices.items()}
    print(f"[model_loader] Classes: {list(_class_indices.keys())}")


def _download_from_hf():
    """Download model file from Hugging Face Hub."""
    if not HF_MODEL_REPO:
        return None
    try:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download(
            repo_id   = HF_MODEL_REPO,
            filename  = "sasyam_crop_model.h5",
            token     = HF_TOKEN or None,
            cache_dir  = "./.hf_cache"
        )
        print(f"[model_loader] Downloaded model from HF Hub → {path}")
        return path
    except Exception as e:
        print(f"[model_loader] HF Hub download failed: {e}")
        return None


async def load_model_on_startup():
    """
    Called during FastAPI lifespan startup.
    Tries local path first, then Hugging Face Hub.
    """
    global _model
    _load_class_indices()

    model_path = None

    # 1. Local model file
    if os.path.exists(LOCAL_MODEL_PATH):
        model_path = LOCAL_MODEL_PATH
        print(f"[model_loader] Using local model: {model_path}")
    else:
        print(f"[model_loader] Local model not found at '{LOCAL_MODEL_PATH}'.")
        # 2. Download from HF Hub in a thread (avoid blocking event loop)
        loop = asyncio.get_event_loop()
        model_path = await loop.run_in_executor(None, _download_from_hf)

    if not model_path:
        print("[model_loader] ⚠ No model available. /predict will return mock data.")
        return

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(model_path)
        print(f"[model_loader] ✓ Model loaded. Input shape: {_model.input_shape}")
    except Exception as e:
        print(f"[model_loader] ✗ Failed to load model: {e}")
        _model = None


def predict(image_array: np.ndarray) -> dict:
    """
    Run inference on a preprocessed 224×224 image array (float32, 0–1).

    Returns:
        { "class_name": str, "confidence": float }
    """
    if _model is None:
        # Mock prediction for development (no model loaded)
        import random
        cls   = random.choice(list(_idx_to_class.values()) or FALLBACK_CLASSES)
        conf  = round(random.uniform(0.72, 0.98), 4)
        print(f"[model_loader] MOCK prediction: {cls} ({conf})")
        return { "class_name": cls, "confidence": conf }

    # Ensure input shape is (1, 224, 224, 3)
    arr = np.expand_dims(image_array.astype("float32"), axis=0)

    preds     = _model.predict(arr, verbose=0)
    idx       = int(np.argmax(preds[0]))
    confidence = float(preds[0][idx])
    class_name = _idx_to_class.get(idx, f"class_{idx}")

    return { "class_name": class_name, "confidence": confidence }
