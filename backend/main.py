# backend/main.py
# ─────────────────────────────────────────────────────────────
# Sasyam FastAPI Backend
# Routes: /health, /stats, /live-feed, /predict, /market/{crop}
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import io
import os
import glob
import random
import numpy as np
from PIL import Image

from model_loader import load_model_on_startup, predict
from analytics import get_market_data, get_regional_stats

# ── App ───────────────────────────────────────────────────── #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load ML model from HuggingFace Hub."""
    print("[Sasyam] Starting up — loading model…")
    await load_model_on_startup()
    print("[Sasyam] Model ready. API is live. 🌾")
    yield
    print("[Sasyam] Shutting down.")

app = FastAPI(
    title       = "Sasyam Agricultural Intelligence API",
    description = "AI-powered crop analytics for Indian farmers.",
    version     = "1.0.0",
    lifespan    = lifespan
)

# ── CORS ──────────────────────────────────────────────────── #
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Sample image folder (for live-feed) ───────────────────── #
SAMPLES_DIR = os.environ.get("SAMPLES_DIR", "./sample_images")


# ═════════════════════════════════════════════════════════════
# GET /health
# ═════════════════════════════════════════════════════════════
@app.get("/health", tags=["System"])
async def health_check():
    """Returns API health status."""
    return {
        "status":  "ok",
        "service": "Sasyam API",
        "version": "1.0.0"
    }


# ═════════════════════════════════════════════════════════════
# GET /stats
# ═════════════════════════════════════════════════════════════
@app.get("/stats", tags=["Analytics"])
async def get_stats():
    """
    Returns platform-wide crop distribution, farmer count,
    yield averages, and market demand with 7-day price trends.
    """
    market = get_market_data()

    crop_distribution = {
        "Wheat":     28,
        "Rice":      22,
        "Corn":      14,
        "Sugarcane": 16,
        "Cotton":    8,
        "Mustard":   7,
        "Pulses":    5
    }

    price_trends = {
        crop: data.get("price_trend_7day", [])
        for crop, data in market.items()
    }

    return {
        "totalFarmers":     124680,
        "areaCoverage":     892340,
        "avgYield":         3.1,
        "activeCrops":      7,
        "cropDistribution": crop_distribution,
        "priceTrends":      price_trends,
        "timestamp":        _now_iso()
    }


# ═════════════════════════════════════════════════════════════
# GET /live-feed
# ═════════════════════════════════════════════════════════════
@app.get("/live-feed", tags=["Inference"])
async def live_feed():
    """
    Picks a random sample image from SAMPLES_DIR, runs
    MobileNetV2 inference, and returns the prediction.
    """
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    images   = []
    for pat in patterns:
        images.extend(glob.glob(os.path.join(SAMPLES_DIR, pat)))

    if not images:
        raise HTTPException(
            status_code = 404,
            detail      = f"No sample images found in {SAMPLES_DIR}"
        )

    path = random.choice(images)
    img  = Image.open(path).convert("RGB").resize((224, 224))
    arr  = np.array(img) / 255.0

    result = predict(arr)

    return {
        "file":       os.path.basename(path),
        "prediction": result["class_name"],
        "confidence": round(result["confidence"], 4),
        "timestamp":  _now_iso()
    }


# ═════════════════════════════════════════════════════════════
# POST /predict
# ═════════════════════════════════════════════════════════════
@app.post("/predict", tags=["Inference"])
async def predict_crop(file: UploadFile = File(...)):
    """
    Accepts an image upload (jpg/png/webp), runs MobileNetV2
    inference, and returns crop class + confidence score.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    contents = await file.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB").resize((224, 224))
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to process image.")

    arr    = np.array(img) / 255.0
    result = predict(arr)

    return {
        "filename":   file.filename,
        "prediction": result["class_name"],
        "confidence": round(result["confidence"], 4),
        "timestamp":  _now_iso()
    }


# ═════════════════════════════════════════════════════════════
# GET /market/{crop}
# ═════════════════════════════════════════════════════════════
VALID_CROPS = {"Wheat", "Rice", "Corn", "Sugarcane", "Cotton", "Mustard", "Pulses"}

@app.get("/market/{crop}", tags=["Market"])
async def market_info(crop: str):
    """
    Returns price trend, demand index, supply ratio, and
    market status for the given crop.
    """
    crop_title = crop.strip().title()
    if crop_title not in VALID_CROPS:
        raise HTTPException(
            status_code = 400,
            detail      = f"Unknown crop '{crop}'. Valid: {sorted(VALID_CROPS)}"
        )

    data = get_market_data()
    crop_data = data.get(crop_title)
    if not crop_data:
        raise HTTPException(status_code=404, detail=f"No data for {crop_title}")

    return {
        "crop":             crop_title,
        **crop_data,
        "timestamp":        _now_iso()
    }


# ═════════════════════════════════════════════════════════════
# GET /regional/{state}
# ═════════════════════════════════════════════════════════════
@app.get("/regional/{state}", tags=["Analytics"])
async def regional_stats(state: str):
    """Yield comparison and growth trend for a given Indian state."""
    data = get_regional_stats(state)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for state: {state}")
    return { "state": state, **data, "timestamp": _now_iso() }


# ── Utility ───────────────────────────────────────────────── #
def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
