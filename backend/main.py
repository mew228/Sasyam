from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import random
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv

import model_loader
import analytics

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("Sasyam backend starting up...")
    model_loader.initialize()
    print("Model loaded and ready")
    yield
    print("Sasyam backend shutting down")

app = FastAPI(title="Sasyam API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{formatted_time}] {request.method} {request.url.path} — {response.status_code} — {process_time:.0f}ms")
    return response

@app.get("/health")
async def get_health():
    try:
        return {
            "status": "ok",
            "model_loaded": model_loader.model is not None,
            "model_classes": model_loader.CLASS_NAMES,
            "version": "1.0.0",
            "uptime_seconds": 123.4, # Just a placeholder as per spec
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Health check failed", "detail": str(e)})

@app.get("/stats")
async def get_stats(state: str = Query(None)):
    try:
        stats = analytics.get_dashboard_stats()
        if state:
            regional = analytics.get_regional_stats(state)
            stats["regional_stats"] = regional
        return stats
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch stats", "detail": str(e)})

@app.get("/market")
async def get_market():
    try:
        return analytics.get_market_data()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch market data", "detail": str(e)})

@app.get("/market/{crop}")
async def get_market_single(crop: str):
    try:
        data = analytics.get_market_data()
        for k, v in data.items():
            if k.lower() == crop.lower():
                similar_crops = []
                if k in ["Wheat", "Rice", "Corn"]: similar_crops = ["Wheat", "Rice", "Corn"]
                elif k in ["Cotton", "Jute"]: similar_crops = ["Cotton", "Sugarcane"]
                elif k in ["Pulses", "Soybean", "Mustard"]: similar_crops = ["Pulses", "Mustard"]
                
                v["similar_crops"] = [c for c in similar_crops if c != k]
                return v
        return JSONResponse(status_code=404, content={"error": "Crop not found", "detail": f"Market data for {crop} is not available."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch market data for crop", "detail": str(e)})

@app.post("/predict")
async def create_prediction(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            return JSONResponse(status_code=400, content={"error": "Invalid file type", "detail": "Uploaded file must be an image."})
        
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            return JSONResponse(status_code=400, content={"error": "File too large", "detail": "Image size must be under 10MB."})
            
        result = model_loader.predict(content)
        return result
    except RuntimeError as e:
        return JSONResponse(status_code=500, content={"error": "Model prediction failed", "detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Server error during prediction", "detail": str(e)})

@app.get("/live-feed")
async def get_live_feed():
    try:
        locations = [
            {"name": "Ludhiana, Punjab", "lat": 30.9010, "lng": 75.8573},
            {"name": "Nashik, Maharashtra", "lat": 20.0110, "lng": 73.7903},
            {"name": "Guntur, Andhra Pradesh", "lat": 16.3067, "lng": 80.4365},
            {"name": "Patna, Bihar", "lat": 25.5941, "lng": 85.1376},
            {"name": "Indore, Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
            {"name": "Jaipur, Rajasthan", "lat": 26.9124, "lng": 75.7873},
            {"name": "Coimbatore, Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
            {"name": "Varanasi, Uttar Pradesh", "lat": 25.3176, "lng": 82.9739}
        ]
        
        loc = random.choice(locations)
        
        samples_dir = os.getenv("SAMPLES_DIR", "")
        if samples_dir and os.path.exists(samples_dir) and os.path.isdir(samples_dir):
            images = [f for f in os.listdir(samples_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if images:
                img_name = random.choice(images)
                img_path = os.path.join(samples_dir, img_name)
                with open(img_path, "rb") as f:
                    content = f.read()
                prediction = model_loader.predict(content)
                return {
                    "source": "real",
                    "location": loc["name"],
                    "coordinates": {"lat": loc["lat"], "lng": loc["lng"]},
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "prediction": {
                        "class_name": prediction["class_name"],
                        "confidence": prediction["confidence"],
                        "confidence_pct": prediction["confidence_pct"]
                    },
                    "area_hectares": round(random.uniform(1.0, 5.0), 1),
                    "alert": None
                }
        
        # Simulated fallback
        simulated_class = random.choice(model_loader.CLASS_NAMES)
        confidence = random.uniform(0.85, 0.99)
        return {
            "source": "simulated",
            "location": loc["name"],
            "coordinates": {"lat": loc["lat"], "lng": loc["lng"]},
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "class_name": simulated_class,
                "confidence": round(confidence, 4),
                "confidence_pct": f"{confidence * 100:.2f}%"
            },
            "area_hectares": round(random.uniform(1.0, 5.0), 1),
            "alert": None
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Live feed failed", "detail": str(e)})

@app.get("/suggestions")
async def get_suggestions(
    region: str = Query(...), 
    season: str = Query(...), 
    land_size: float = Query(...), 
    water: str = Query(...), 
    risk: str = Query(...)
):
    try:
        suggestions = analytics.get_crop_suggestions(region, season, land_size, water, risk)
        return suggestions
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate suggestions", "detail": str(e)})

@app.get("/weather")
async def get_weather(state: str = Query(...)):
    try:
        return analytics.get_weather_data(state)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch weather data", "detail": str(e)})

@app.get("/regional/{state}")
async def get_regional_state(state: str):
    try:
        return analytics.get_regional_stats(state)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch regional stats", "detail": str(e)})
