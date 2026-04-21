# Sasyam — Agricultural Intelligence Platform for Indian Farmers

> **Mapping India's Harvest in Real Time**

Sasyam is an open-source agricultural intelligence platform that empowers India's 140 million farmers with precision AI, real-time market intelligence, and satellite-grade crop analytics — from field to market.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla JS, GSAP, Chart.js, Leaflet.js |
| Fonts | Montserrat (Optimistic VF fallback) |
| Design System | Meta Store inspired (see `DESIGN.md`) |
| AI / ML | TensorFlow 2.x, MobileNetV2 |
| LLM | Google Gemini 2.5 Flash (multi-model fallback) |
| Database | Firebase Firestore (v9 modular SDK) |
| Backend | FastAPI + Uvicorn |
| Model Hosting | Hugging Face Hub |
| Deployment | Frontend → Vercel / Netlify; Backend → Render |

---

## Project Structure

```
sasyam/
├── index.html          Landing page (GSAP + scroll canvas)
├── dashboard.html      Analytics dashboard
├── register.html       Farmer registration + registry
├── css/
│   ├── styles.css      Global design system (Meta-inspired)
│   ├── dashboard.css   Dashboard layout + animated weather icons
│   └── register.css    Form + table styles
├── js/
│   ├── config.js       Runtime config (auto-generated at deploy)
│   ├── flower.js       Scroll-driven image sequence player
│   ├── script.js       GSAP animations + nav + theme
│   ├── dashboard.js    Charts, map, AI chat, crop suggestor
│   └── register.js     Firebase CRUD + farmer registry
├── scripts/
│   └── generate-config.js  Deploy-time config generator
├── assets/
│   ├── imageSequence/  WebP frames for bloom animation
│   ├── icons/
│   └── fonts/
├── model/
│   ├── train.py        TensorFlow training script
│   ├── requirements.txt
│   └── class_indices.json
├── backend/
│   ├── main.py         FastAPI app
│   ├── model_loader.py HF Hub download + Keras inference
│   ├── analytics.py    Hardcoded 2024 Indian agri stats
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

---

## Local Setup

### 1. Frontend

No build step required — open `index.html` directly, or use a local server:

```bash
# Python
python -m http.server 3000

# Node
npx serve .
```

Then visit `http://localhost:3000`.

**Configure your API keys in `js/config.js`:**
```js
GEMINI_API_KEY: "your-key",
FIREBASE_CONFIG: { apiKey: "...", projectId: "..." }
```

---

### 2. Model Training

```bash
cd model
pip install -r requirements.txt

# Prepare dataset: ../dataset/Wheat/, ../dataset/Rice/, etc.
python train.py
```

Output: `sasyam_crop_model.h5` + `class_indices.json` + `model_card.md`

Upload the H5 file to your Hugging Face Hub repo.

---

### 3. Backend

```bash
cd backend
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env
# Edit .env: set HF_MODEL_REPO=your-username/sasyam-crop-model

# Run
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

---

### 4. Deploy-time Config (CI/CD)

Set these environment variables on your deployment platform, then run:

```bash
node scripts/generate-config.js
```

| Variable | Purpose |
|----------|---------|
| `BACKEND_URL` | FastAPI backend URL |
| `GEMINI_API_KEY` | Google Gemini API key |
| `FIREBASE_API_KEY` | Firebase project API key |
| `FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `FIREBASE_PROJECT_ID` | Firebase project ID |
| `FIREBASE_STORAGE_BUCKET` | Firebase storage bucket |
| `FIREBASE_MESSAGING_SENDER_ID` | Firebase messaging ID |
| `FIREBASE_APP_ID` | Firebase app ID |

---

## Deployment

### Frontend → Vercel / Netlify

```bash
# Vercel
vercel deploy

# Netlify
netlify deploy --prod
```

Set all `FIREBASE_*` and `GEMINI_API_KEY` env vars in the dashboard, then add a build command:
```
node scripts/generate-config.js
```

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Set **Build Command:** `pip install -r requirements.txt`
3. Set **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add env vars: `HF_MODEL_REPO`, `HF_TOKEN`, `PORT=8000`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/stats` | Platform-wide crop stats |
| GET | `/live-feed` | Random inference on sample image |
| POST | `/predict` | Upload image → crop prediction |
| GET | `/market/{crop}` | Price trend + demand for a crop |
| GET | `/regional/{state}` | Yield stats for an Indian state |

---

## Image Sequence Animation

Place 300 WebP frames named `frame_0001.webp` → `frame_0300.webp` in `assets/imageSequence/`.

The scroll-driven player (`js/flower.js`) will automatically detect and animate them on the hero canvas.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages
4. Open a pull request

---

## License

MIT © 2024 Sasyam — Built for India's farmers 🌾
