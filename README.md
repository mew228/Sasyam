<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Playfair+Display&size=42&duration=3000&pause=1000&color=4ADE80&center=true&vCenter=true&width=600&lines=🌾+Sasyam;Mapping+India's+Harvest;In+Real+Time" alt="Sasyam" />

<br/>

<p align="center">
  <strong>AI-powered agricultural intelligence for India's 140 million farmers</strong><br/>
  Satellite crop classification · Real-time market data · Gemini-powered advisory
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black"/>
  <img src="https://img.shields.io/badge/MobileNetV2-91%25_acc-4ADE80?style=for-the-badge"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Model-Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black"/>
  <img src="https://img.shields.io/badge/Dataset-24k_images-8B5CF6?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/>
</p>

<br/>

---

</div>

## 🌾 What is Sasyam?

Every season, millions of Indian farmers face the same question with life-changing stakes: **what should I plant, and will I be able to sell it?** Crop overproduction costs India an estimated ₹92,000 crore annually — too many farmers planting the same crop, flooding the market, crashing prices below the cost of cultivation.

**Sasyam** is an open-source agricultural intelligence platform that gives farmers and agricultural officials a satellite-grade view of India's harvest. It combines:

- 🛰️ **AI crop classification** from satellite imagery (MobileNetV2, 91%+ accuracy)
- 📊 **Live market intelligence** — MSP rates, demand indices, price trends for 7 major crops
- 🤖 **RAG-powered AI advisor** — Gemini 2.5 Flash grounded in live market data
- 🗺️ **Interactive India choropleth map** — state-level yield benchmarks
- 🌱 **Smart crop suggestor** — 6-dimension scoring algorithm personalised to each farmer
- 👨‍🌾 **Real-time farmer registry** — Firebase Firestore with live sync

<br/>

---

## ✨ Features at a Glance

<table>
<tr>
<td width="50%">

### 🛰️ Satellite Crop Classification
Upload any satellite image → MobileNetV2 identifies Wheat, Corn, Sugarcane, or Other with confidence score and inference time. Model hosted on Hugging Face, downloaded on first cold start.

</td>
<td width="50%">

### 📈 Live Market Intelligence
Real-time supply/demand tracking for 7 crops with animated status badges (Stable / Active / Critical), 7-day price trend charts, and MSP reference lines.

</td>
</tr>
<tr>
<td width="50%">

### 🤖 Sasyam AI — RAG Advisory
Gemini 2.5 Flash loaded with live market prices, MSP rates, yield benchmarks, seasonal calendars, and government scheme details. Answers in Hindi or English. Falls back through 3 model tiers if quota is exceeded.

</td>
<td width="50%">

### 🗺️ India Choropleth Map
Interactive Leaflet.js map coloured by agricultural yield per state. Click any state → sidebar updates with yield vs national average, top district, irrigation coverage, and YoY growth.

</td>
</tr>
<tr>
<td width="50%">

### 🌱 Smart Crop Suggestor
Enter your state, land size, water source, and budget → ranked crop recommendations scored across 6 dimensions: price trend, demand, ROI potential, risk tolerance, water fit, and land size fit.

</td>
<td width="50%">

### ☁️ Weather Intelligence
CSS-only animated weather icons (no images, no libraries). Current conditions + 7-day forecast + agricultural advisory per state. Icons built purely from `div` + `@keyframes`.

</td>
</tr>
</table>

<br/>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SASYAM PLATFORM                          │
│                                                                 │
│   FRONTEND (Vanilla JS)       BACKEND (FastAPI on Render)       │
│   ┌──────────────────┐        ┌──────────────────────────┐      │
│   │  index.html      │        │  main.py  (9 endpoints)  │      │
│   │  GSAP + Scroll   │◄──────►│  model_loader.py         │      │
│   │  300-frame WebP  │        │  MobileNetV2 inference   │      │
│   ├──────────────────┤        │  analytics.py            │      │
│   │  dashboard.html  │        │  Market + Weather data   │      │
│   │  Chart.js        │        └──────────┬───────────────┘      │
│   │  Leaflet map     │                   │                      │
│   │  Gemini RAG chat │        ┌──────────▼───────────────┐      │
│   ├──────────────────┤        │  Hugging Face Hub        │      │
│   │  register.html   │        │  cropmodel.h5 (14MB)     │      │
│   │  Firestore CRUD  │        └──────────────────────────┘      │
│   └──────────────────┘                                          │
│         │ Firebase SDK          │ Gemini API                    │
│   ┌─────▼──────┐         ┌──────▼──────┐                        │
│   │ Firestore  │         │  Gemini     │                        │
│   │  Farmers   │         │  2.5→2.0→   │                        │
│   │  Registry  │         │  lite→local │                        │
│   └────────────┘         └─────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🧠 The AI/ML Stack

### Model: MobileNetV2 + Transfer Learning

| Detail | Value |
|--------|-------|
| Base architecture | MobileNetV2 (ImageNet pretrained) |
| Parameters | 3.4M total |
| Input size | 224 × 224 × 3 (RGB) |
| Output classes | 4 (Corn, Other, Sugarcane, Wheat) |
| Phase 1 accuracy | ~90% val_acc at epoch 1 |
| Final val accuracy | 91%+ |
| Inference time | ~35–45ms on CPU |
| Model file | [`cropmodel.h5`](https://huggingface.co/BeluBeluga/Bloom/resolve/main/cropmodel.h5) on Hugging Face |

### Dataset: EuroSAT Satellite Imagery (Re-labelled)

24,000 satellite images across 4 classes derived from the EuroSAT benchmark:

| Class | Images | Source Label | Why This Mapping |
|-------|--------|-------------|-----------------|
| 🌽 Corn | 2,000 | `Pasture` | Similar dense chlorophyll canopy signature |
| 🌾 Wheat | 2,500 | `PermanentCrop` | Matching golden heading-stage spectral return |
| 🎋 Sugarcane | 3,000 | `HerbaceousVegetation` | Tall reed-like structure matches spectrally |
| 🌲 Other | 16,500 | Forest, SeaLake, Residential, River, Industrial, Highway | Deliberate negative class to reduce false positives |

The **8:1 class imbalance** (Other vs Corn) is intentional — in real satellite imagery over India, the majority of any frame is non-cropland. Balanced training would make the model over-predict crops everywhere.

### Training Pipeline

```python
# Phase 1 — Feature Extraction (frozen base, 15 epochs, lr=1e-3)
MobileNetV2(frozen) → GAP → BN → Dense(256) → Dropout(0.4) → Dense(128) → Dropout(0.3) → Dense(4, softmax)

# Phase 2 — Fine-Tuning (last 30 layers unfrozen, 10 epochs, lr=1e-5)
# Teaches the model Indian crop-specific spectral signatures
```

### RAG Advisory System

```
User query
    ↓
buildSystemPrompt() injects live context:
  · Current prices for all 7 crops (from /market endpoint)
  · 2024-25 MSP rates (Wheat ₹2275, Rice ₹2183, Cotton ₹7121...)
  · Regional yield benchmarks (Punjab 4.8 t/ha, UP 3.2 t/ha...)
  · Seasonal calendar + Government schemes (PM-KISAN, PMFBY, KCC)
    ↓
Gemini 2.5 Flash → 2.0 Flash → 2.0 Flash Lite → local keyword fallback
    ↓
Response grounded in actual live prices, not hallucinated values
```

<br/>

---

## 📁 Project Structure

```
sasyam/
├── index.html                  Landing page — GSAP scroll + 300-frame bloom animation
├── dashboard.html              Main intelligence dashboard
├── register.html               Farmer registration + live registry
│
├── css/
│   ├── styles.css              Global design system (Meta Store inspired)
│   ├── dashboard.css           Dashboard layout + CSS-only animated weather icons
│   └── register.css            Form + Firestore table styles
│
├── js/
│   ├── config.js               Runtime config (API keys — generated at deploy time)
│   ├── flower.js               Scroll-driven 300-frame WebP sequence player
│   ├── script.js               GSAP ScrollTrigger animations + theme toggle
│   ├── dashboard.js            Charts, map, AI assistant, crop suggestor (~2200 lines)
│   └── register.js             Firebase Firestore CRUD + real-time onSnapshot
│
├── scripts/
│   └── generate-config.js      Writes js/config.js from environment variables at deploy
│
├── assets/
│   ├── imageSequence/          300 WebP frames for landing page bloom animation
│   ├── icons/                  Custom inline SVG icons
│   └── fonts/
│
├── model/
│   ├── train.py                Full 14-step MobileNetV2 training pipeline
│   ├── requirements.txt        tensorflow, pillow, numpy, sklearn, seaborn
│   └── class_indices.json      {"Corn":0,"Other":1,"Sugarcane":2,"Wheat":3}
│
├── backend/
│   ├── main.py                 FastAPI app — 9 endpoints + request logging middleware
│   ├── model_loader.py         HF Hub download + Keras inference engine
│   ├── analytics.py            2024-25 Indian agri stats + scoring algorithms
│   ├── requirements.txt        fastapi, uvicorn, tensorflow, pillow, httpx...
│   └── .env.example            Environment variable template
│
├── SASYAM_DEEPDIVE.md          Full technical deep-dive (dataset, ML, architecture)
└── README.md                   This file
```

<br/>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for config generator only)
- A Google Gemini API key ([get one free](https://aistudio.google.com))
- A Firebase project ([console.firebase.google.com](https://console.firebase.google.com))

---

### 1. Clone

```bash
git clone https://github.com/mew228/Sasyam.git
cd Sasyam
```

---

### 2. Frontend

No build step. Open directly or serve locally:

```bash
# Python
python -m http.server 3000

# Node
npx serve .
```

Fill in your keys in `js/config.js`:

```javascript
const CONFIG = {
  BACKEND_URL: "http://localhost:8000",      // or your Render URL
  GEMINI_API_KEY: "AIza...",
  FIREBASE_CONFIG: {
    apiKey: "...",
    authDomain: "...",
    projectId: "...",
    storageBucket: "...",
    messagingSenderId: "...",
    appId: "..."
  }
};
```

Visit `http://localhost:3000`

---

### 3. Backend

```bash
cd backend
pip install -r requirements.txt

# Copy env template
cp .env.example .env
```

Edit `.env`:
```env
HF_MODEL_REPO=BeluBeluga/Bloom
HF_TOKEN=                        # leave blank — model is public
PORT=8000
LOCAL_MODEL_PATH=sasyam_crop_model.h5
```

```bash
uvicorn main:app --reload --port 8000
```

The backend downloads the model from Hugging Face on first start (~14MB). Subsequent starts use the cached file.

Interactive API docs: **`http://localhost:8000/docs`**

---

### 4. Model Training (Optional)

The pre-trained model is already on Hugging Face. Only run this if you want to retrain:

```bash
cd model
pip install -r requirements.txt

# Dataset must be at ../dataset/ with subfolders: Corn/ Wheat/ Sugarcane/ Other/
python train.py
```

Outputs: `sasyam_crop_model.h5`, `class_indices.json`, `training_history.json`, `confusion_matrix.png`, `model_card.md`

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Model status, uptime, version |
| `GET` | `/stats` | Crop distribution, farmer count, yield averages |
| `GET` | `/market` | All 7 crops — MSP, price, demand index, 7-day trend |
| `GET` | `/market/{crop}` | Single crop deep-dive + similar crop suggestions |
| `POST` | `/predict` | Upload image → `{class_name, confidence, all_scores, inference_time_ms}` |
| `GET` | `/live-feed` | Simulated satellite scan of a random Indian farm location |
| `GET` | `/suggestions` | Ranked crop recommendations based on farmer parameters |
| `GET` | `/weather` | Current conditions + 7-day forecast for any Indian state |
| `GET` | `/regional/{state}` | Yield benchmarks and growth trends per state |

**Example — Crop Prediction:**
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@your_satellite_image.jpg"
```
```json
{
  "class_name": "Wheat",
  "confidence": 0.9234,
  "confidence_pct": "92.34%",
  "all_scores": {
    "Corn": 0.0041,
    "Other": 0.0089,
    "Sugarcane": 0.0047,
    "Wheat": 0.9234
  },
  "inference_time_ms": 38.4
}
```

<br/>

---

## ☁️ Deployment

### Backend → Render (Free Tier)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your repo, set root directory to `backend/`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:

| Variable | Value |
|----------|-------|
| `HF_MODEL_REPO` | `BeluBeluga/Bloom` |
| `HF_TOKEN` | *(leave blank)* |
| `PORT` | `8000` |

### Frontend → Vercel / Netlify

```bash
# Vercel
vercel deploy

# Netlify
netlify deploy --prod
```

Set all environment variables in the platform dashboard, then set build command to:
```bash
node scripts/generate-config.js
```

| Variable | Purpose |
|----------|---------|
| `BACKEND_URL` | Your Render backend URL |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `FIREBASE_API_KEY` | Firebase project credentials |
| `FIREBASE_AUTH_DOMAIN` | |
| `FIREBASE_PROJECT_ID` | |
| `FIREBASE_STORAGE_BUCKET` | |
| `FIREBASE_MESSAGING_SENDER_ID` | |
| `FIREBASE_APP_ID` | |

<br/>

---

## 📊 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Deep Learning | TensorFlow 2.x, MobileNetV2 | Satellite crop classification |
| Model Hosting | Hugging Face Hub | Model storage + download on cold start |
| Backend API | FastAPI + Uvicorn | 9 REST endpoints, request logging, CORS |
| LLM / RAG | Google Gemini 2.5 Flash | Contextual agricultural advisory |
| Database | Firebase Firestore v9 | Real-time farmer registration registry |
| Charts | Chart.js 4.x | Doughnut + line charts with MSP reference |
| Maps | Leaflet.js + CartoDB | India choropleth with GeoJSON state borders |
| Animations | GSAP + ScrollTrigger | Landing page scroll effects |
| Frontend | Vanilla HTML/CSS/JS | Zero build step, pure static |
| Design System | Meta Store inspired | CSS custom properties, pill CTAs, dark/light |
| Deployment | Render (backend) + Vercel | Free tier, auto-deploy from GitHub |

<br/>

---

## 🔬 Want to Go Deeper?

Read **[`SASYAM_DEEPDIVE.md`](./SASYAM_DEEPDIVE.md)** for the full technical breakdown:

- Why MobileNetV2 beats ResNet50 and EfficientNet for this use case
- How the EuroSAT class labels map to Indian crop spectral signatures
- The exact dataset composition (6 scene types inside "Other" and why)
- Phase 1 vs Phase 2 training strategy with loss curves explained
- How the RAG system grounds Gemini responses in live price data
- The 6-dimension crop scoring algorithm with full math
- Complete real-world data flow with millisecond timestamps

<br/>

---

## 🗺️ Roadmap

- [ ] Real Indian satellite data via ISRO Bhuvan API
- [ ] Hindi / regional language full UI (Gemini already supports it)
- [ ] LSTM price prediction model on AGMARKNET historical data
- [ ] Pest and disease detection (20-class classifier from farmer photos)
- [ ] District-level overplanting early warning system
- [ ] Mobile PWA with offline-capable inference
- [ ] e-NAM / PM-KISAN API integration

<br/>

---

## 🤝 Contributing

```bash
# Fork the repo, then:
git checkout -b feature/your-feature
git commit -m "feat: your feature"
git push origin feature/your-feature
# Open a Pull Request
```

<br/>

---

<div align="center">

**Built in 24 hours at a hackathon.**

*For India's farmers — who deserve better tools than intuition and word of mouth.*

<br/>

[![GitHub](https://img.shields.io/badge/github.com/mew228/Sasyam-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mew228/Sasyam)
[![Hugging Face](https://img.shields.io/badge/Model_on_HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/BeluBeluga/Bloom)

<br/>

MIT © 2025 Sasyam 🌾

</div>
