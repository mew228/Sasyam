import os
import io
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from PIL import Image
import numpy as np

load_dotenv()

# We delay importing tensorflow until needed or just import it here.
# Importing it globally is fine, it will just take a bit at startup.
import tensorflow as tf

HF_MODEL_URL = "https://huggingface.co/BeluBeluga/Bloom/resolve/main/cropmodel.h5"
CLASS_NAMES = ["Corn", "Other", "Sugarcane", "Wheat"]
MODEL_INPUT_SIZE = (64, 64)

model = None

def download_model_from_hf():
    print(f"Downloading model from {HF_MODEL_URL}...")
    try:
        response = requests.get(HF_MODEL_URL, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024 # 1 MB
        
        with open("cropmodel.h5", "wb") as f, tqdm(
            desc="cropmodel.h5",
            total=total_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = f.write(data)
                bar.update(size)
        print("Model downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading model: {e}")
        if os.path.exists("cropmodel.h5"):
            os.remove("cropmodel.h5")
        raise RuntimeError(f"Failed to download model: {e}")

def load_model_instance():
    # 1. LOCAL_MODEL_PATH
    local_path = os.getenv("LOCAL_MODEL_PATH")
    if local_path and os.path.exists(local_path):
        print(f"Loading model from LOCAL_MODEL_PATH: {local_path}")
        return tf.keras.models.load_model(local_path)
    
    # 2. HF_MODEL_URL Download
    hf_path = "cropmodel.h5"
    if not os.path.exists(hf_path):
        try:
            download_model_from_hf()
        except Exception as e:
            print(f"HF download failed: {e}")
            
    if os.path.exists(hf_path):
        try:
            print(f"Loading model from HF path: {hf_path}")
            return tf.keras.models.load_model(hf_path)
        except Exception as e:
            print(f"Error loading {hf_path}: {e}")
    
    # 3. Fallbacks
    fallbacks = [
        "../model/sasyam_crop_model.h5",
        "../model/sasyam_best.h5",
        "../model/sasyam_crop_model.keras",
        "../model/sasyam_best.keras"
    ]
    
    for path in fallbacks:
        if os.path.exists(path):
            try:
                print(f"Loading model from fallback path: {path}")
                return tf.keras.models.load_model(path)
            except Exception as e:
                print(f"Error loading fallback {path}: {e}")

    raise RuntimeError("No model found in any priority path. Please check model paths or download manually.")

def initialize():
    global model
    try:
        model = load_model_instance()
    except Exception as e:
        print(f"Failed to initialize model: {e}")
        raise e

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")
        image = image.resize(MODEL_INPUT_SIZE)
        img_array = np.array(image, dtype=np.float32)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        raise ValueError(f"Image preprocessing failed: {e}")

def predict(image_bytes: bytes) -> dict:
    global model
    if model is None:
        raise RuntimeError("Model is not initialized.")
    
    start_time = time.time()
    try:
        processed_image = preprocess_image(image_bytes)
        predictions = model.predict(processed_image)
        scores = predictions[0]
        
        predicted_class_idx = np.argmax(scores)
        confidence = float(scores[predicted_class_idx])
        
        all_scores = {CLASS_NAMES[i]: float(scores[i]) for i in range(len(CLASS_NAMES))}
        
        inference_time_ms = (time.time() - start_time) * 1000.0
        
        return {
            "class_name": CLASS_NAMES[predicted_class_idx],
            "confidence": round(confidence, 4),
            "confidence_pct": f"{confidence * 100:.2f}%",
            "all_scores": {k: round(v, 4) for k, v in all_scores.items()},
            "inference_time_ms": round(inference_time_ms, 2)
        }
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {e}")
