/**
 * js/dashboard.js
 * ─────────────────────────────────────────────────────────────
 * Sasyam Dashboard — Full interactive intelligence dashboard
 * ─────────────────────────────────────────────────────────────
 */

// ==============================================================
// === CONFIG & STATE ============================================
// ==============================================================
const POLL_INTERVAL_MS = 30_000;
const CROP_COLORS = {
  Wheat:      "#F7B928",
  Rice:       "#47A5FA",
  Corn:       "#FB724B",
  Sugarcane:  "#45BD62",
  Cotton:     "#E8F3FF",
  Mustard:    "#F3425F",
  Pulses:     "#9360F7"
};

let cropChart  = null;
let priceChart = null;
let leafletMap = null;
let pollTimer  = null;

const state = {
  stats:       null,
  marketData:  null,
  selectedCrop: "Wheat",
  selectedWeatherState: "Maharashtra",
  activeAiModel: "gemini-2.5-flash",
  aiHistory: []   // {role, content}
};

// ==============================================================
// === API CALLS =================================================
// ==============================================================
const API = {
  async get(path) {
    const base = (window.CONFIG?.BACKEND_URL) || "http://localhost:8000";
    const res  = await fetch(`${base}${path}`, {
      signal: AbortSignal.timeout(8000)
    });
    if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
    return res.json();
  }
};

async function fetchStats() {
  try {
    const data = await API.get("/stats");
    state.stats = data;
    renderStats(data);
    if (data.cropDistribution) updateCropChart(data.cropDistribution);
  } catch {
    renderStatsFallback();
  }
}

async function fetchMarketData(crop) {
  const el = document.getElementById("last-updated");
  try {
    const data = await API.get(`/market/${encodeURIComponent(crop)}`);
    state.marketData = data;
    updatePriceChart(data.price_trend_7day || [], crop);
    if (el) el.innerHTML = `<span class="update-dot"></span> Updated ${new Date().toLocaleTimeString()}`;
  } catch {
    // Use analytics fallback
    const ANALYTICS = getDemoMarketData(crop);
    updatePriceChart(ANALYTICS.price_trend_7day, crop);
  }
}

function startPolling() {
  fetchStats();
  fetchMarketData(state.selectedCrop);
  fetchWeather(state.selectedWeatherState);

  pollTimer = setInterval(() => {
    fetchStats();
    fetchMarketData(state.selectedCrop);
  }, POLL_INTERVAL_MS);
}

// ==============================================================
// === CHARTS ====================================================
// ==============================================================
function initCropChart() {
  const ctx = document.getElementById("crop-chart");
  if (!ctx || !window.Chart) return;

  const initialData = {
    Wheat: 28, Rice: 22, Corn: 14, Sugarcane: 16, Cotton: 8, Mustard: 7, Pulses: 5
  };

  cropChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(initialData),
      datasets: [{
        data: Object.values(initialData),
        backgroundColor: Object.keys(initialData).map(k => CROP_COLORS[k] || "#ccc"),
        borderColor: "transparent",
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "68%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed}%`
          }
        }
      },
      animation: { animateRotate: true, duration: 900, easing: "easeOutCubic" }
    }
  });

  renderChartLegend(initialData);
}

function renderChartLegend(data) {
  const legend = document.getElementById("crop-chart-legend");
  if (!legend) return;
  legend.innerHTML = "";
  Object.entries(data).forEach(([crop, pct]) => {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-dot" style="background:${CROP_COLORS[crop] || '#ccc'}"></span>
      <span>${crop} ${pct}%</span>
    `;
    legend.appendChild(item);
  });
}

function updateCropChart(dist) {
  if (!cropChart) return;
  cropChart.data.labels   = Object.keys(dist);
  cropChart.data.datasets[0].data            = Object.values(dist);
  cropChart.data.datasets[0].backgroundColor = Object.keys(dist).map(k => CROP_COLORS[k] || "#ccc");
  cropChart.update("active");
  renderChartLegend(dist);
}

function initPriceChart() {
  const ctx = document.getElementById("price-chart");
  if (!ctx || !window.Chart) return;

  const labels = getLast7Days();

  priceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Price (₹/quintal)",
        data: getDemoMarketData("Wheat").price_trend_7day,
        borderColor: "#0064E0",
        backgroundColor: "rgba(0,100,224,0.08)",
        borderWidth: 2.5,
        pointRadius: 4,
        pointHoverRadius: 7,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => ` ₹${ctx.parsed.y.toLocaleString("en-IN")}` }
        }
      },
      scales: {
        x: {
          grid:  { color: "rgba(0,0,0,0.05)" },
          ticks: { font: { size: 11 }, color: "#65676B" }
        },
        y: {
          grid:  { color: "rgba(0,0,0,0.05)" },
          ticks: {
            font: { size: 11 }, color: "#65676B",
            callback: v => "₹" + v.toLocaleString("en-IN")
          }
        }
      },
      animation: { duration: 800, easing: "easeOutCubic" }
    }
  });

  // Crop select listener
  const sel = document.getElementById("price-crop-select");
  if (sel) {
    sel.addEventListener("change", () => {
      state.selectedCrop = sel.value;
      fetchMarketData(sel.value);
    });
  }
}

function updatePriceChart(trendData, cropName) {
  if (!priceChart) return;
  priceChart.data.datasets[0].label = `${cropName} Price (₹/quintal)`;
  priceChart.data.datasets[0].data  = trendData;
  priceChart.update("active");
}

function getLast7Days() {
  const labels = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    labels.push(d.toLocaleDateString("en-IN", { month: "short", day: "numeric" }));
  }
  return labels;
}

// ==============================================================
// === MAP =======================================================
// ==============================================================
// Simplified India state centroids for markers
const STATE_CENTROIDS = {
  "Andhra Pradesh":   [15.91,  79.74],
  "Assam":            [26.24,  92.54],
  "Bihar":            [25.09,  85.31],
  "Chhattisgarh":     [21.27,  81.86],
  "Gujarat":          [22.25,  71.19],
  "Haryana":          [29.05,  76.09],
  "Himachal Pradesh": [31.10,  77.17],
  "Jharkhand":        [23.61,  85.27],
  "Karnataka":        [15.31,  75.71],
  "Kerala":           [10.85,  76.27],
  "Madhya Pradesh":   [22.97,  78.65],
  "Maharashtra":      [19.66,  75.30],
  "Manipur":          [24.66,  93.90],
  "Meghalaya":        [25.46,  91.36],
  "Mizoram":          [23.16,  92.94],
  "Nagaland":         [26.15,  94.56],
  "Odisha":           [20.94,  84.80],
  "Punjab":           [31.14,  75.34],
  "Rajasthan":        [27.02,  74.21],
  "Sikkim":           [27.53,  88.51],
  "Tamil Nadu":       [11.12,  78.65],
  "Telangana":        [17.86,  79.09],
  "Tripura":          [23.94,  91.98],
  "Uttar Pradesh":    [26.84,  80.94],
  "Uttarakhand":      [30.06,  79.55],
  "West Bengal":      [22.98,  87.85]
};

const STATE_YIELD_DATA = {
  "Punjab":           { yield: 4.2, crop: "Wheat", growth: "+5.2%" },
  "Haryana":          { yield: 3.8, crop: "Wheat", growth: "+3.1%" },
  "Uttar Pradesh":    { yield: 3.1, crop: "Wheat", growth: "+4.8%" },
  "Madhya Pradesh":   { yield: 2.9, crop: "Wheat", growth: "+6.1%" },
  "Maharashtra":      { yield: 2.1, crop: "Sugarcane", growth: "+2.4%" },
  "Gujarat":          { yield: 2.4, crop: "Cotton", growth: "+1.8%" },
  "Karnataka":        { yield: 2.3, crop: "Rice", growth: "+3.5%" },
  "Tamil Nadu":       { yield: 3.4, crop: "Rice", growth: "+4.2%" },
  "Rajasthan":        { yield: 2.0, crop: "Mustard", growth: "+7.3%" },
  "Bihar":            { yield: 2.8, crop: "Rice", growth: "+2.9%" },
  "West Bengal":      { yield: 3.2, crop: "Rice", growth: "+3.8%" },
  "Andhra Pradesh":   { yield: 3.0, crop: "Rice", growth: "+3.0%" },
  "Telangana":        { yield: 2.7, crop: "Cotton", growth: "+2.2%" },
  "Kerala":           { yield: 1.8, crop: "Rice", growth: "+1.5%" },
  "Odisha":           { yield: 2.4, crop: "Rice", growth: "+2.7%" },
  "Chhattisgarh":     { yield: 2.1, crop: "Rice", growth: "+4.1%" },
  "Jharkhand":        { yield: 1.9, crop: "Rice", growth: "+2.0%" },
  "Assam":            { yield: 2.5, crop: "Rice", growth: "+3.3%" }
};

function getYieldColor(yieldVal) {
  if (yieldVal >= 4.0) return "#007D1E";
  if (yieldVal >= 3.0) return "#31A24C";
  if (yieldVal >= 2.0) return "#F7B928";
  return "#E41E3F";
}

function initMap() {
  if (!window.L) return;
  const container = document.getElementById("india-map");
  if (!container) return;

  leafletMap = L.map("india-map", {
    center: [22.5, 82.0],
    zoom: 4.5,
    zoomControl: true,
    attributionControl: false
  });

  // Tile layer
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
    maxZoom: 10
  }).addTo(leafletMap);

  // State markers
  Object.entries(STATE_CENTROIDS).forEach(([state, coords]) => {
    const yieldData = STATE_YIELD_DATA[state];
    const yieldVal  = yieldData ? yieldData.yield : 2.0;
    const color     = getYieldColor(yieldVal);

    const marker = L.circleMarker(coords, {
      radius:      yieldVal * 3.5,
      fillColor:   color,
      color:       "#fff",
      weight:      1.5,
      opacity:     0.9,
      fillOpacity: 0.75
    }).addTo(leafletMap);

    marker.bindTooltip(`<strong>${state}</strong><br>Yield: ${yieldVal} q/acre`, {
      direction: "top",
      offset: [0, -8]
    });

    marker.on("click", () => showStateDetail(state, yieldData));
  });

  // Full attribution
  L.control.attribution({ position: "bottomright" })
    .addAttribution("© <a href='https://openstreetmap.org'>OSM</a>")
    .addTo(leafletMap);
}

function showStateDetail(stateName, data) {
  const panel = document.getElementById("map-state-info");
  const nameEl = document.getElementById("map-state-name");
  const statsEl = document.getElementById("map-state-stats");
  const subtitle = document.getElementById("map-selected-state");

  if (!panel) return;
  panel.hidden = false;
  if (subtitle) subtitle.textContent = stateName;
  if (nameEl)   nameEl.textContent   = stateName;

  const d = data || { yield: "—", crop: "—", growth: "—" };
  if (statsEl) {
    statsEl.innerHTML = `
      <div class="state-stat-item"><span class="ssi-label">Primary Crop</span><span class="ssi-value">${d.crop}</span></div>
      <div class="state-stat-item"><span class="ssi-label">Yield (q/acre)</span><span class="ssi-value">${d.yield}</span></div>
      <div class="state-stat-item"><span class="ssi-label">YoY Growth</span><span class="ssi-value" style="color:#007D1E">${d.growth}</span></div>
    `;
  }
}

// ==============================================================
// === WEATHER ===================================================
// ==============================================================
const WEATHER_DATA = {
  "Maharashtra":     { temp: 34, desc: "Sunny", humidity: 48, wind: 14, rain: 2,   advisory: "Irrigate early morning" },
  "Punjab":          { temp: 28, desc: "Partly Cloudy", humidity: 62, wind: 18, rain: 12, advisory: "Good for wheat harvesting" },
  "Uttar Pradesh":   { temp: 32, desc: "Hazy", humidity: 55, wind: 10, rain: 5,   advisory: "Monitor for aphid activity" },
  "Madhya Pradesh":  { temp: 30, desc: "Sunny", humidity: 44, wind: 12, rain: 0,   advisory: "Apply top dressing fertiliser" },
  "Rajasthan":       { temp: 41, desc: "Hot & Sunny", humidity: 22, wind: 22, rain: 0,   advisory: "Critical: increase irrigation" },
  "Gujarat":         { temp: 36, desc: "Sunny", humidity: 38, wind: 16, rain: 0,   advisory: "Check drip irrigation systems" },
  "Karnataka":       { temp: 27, desc: "Cloudy", humidity: 74, wind: 20, rain: 28, advisory: "Delay pesticide spraying" },
  "Haryana":         { temp: 29, desc: "Partly Cloudy", humidity: 58, wind: 14, rain: 8,  advisory: "Ideal sowing conditions" }
};

function getWeatherIconClass(desc) {
  const d = desc.toLowerCase();
  if (d.includes("thunder") || d.includes("storm")) return "thunder";
  if (d.includes("rain") || d.includes("shower"))   return "rainy";
  if (d.includes("cloud") || d.includes("hazy"))    return "cloudy";
  return "sunny";
}

function buildWeatherIconHTML(cls) {
  if (cls === "sunny") {
    return `<div class="weather-icon sunny">
      <div class="sun">
        <div class="sun-rays">
          <span></span><span></span><span></span><span></span>
          <span></span><span></span><span></span><span></span>
        </div>
        <div class="sun-core"></div>
      </div>
    </div>`;
  }
  if (cls === "cloudy") {
    return `<div class="weather-icon cloudy">
      <div class="cloud">
        <div class="cloud-puff2"></div>
        <div class="cloud-puff1"></div>
        <div class="cloud-body"></div>
      </div>
    </div>`;
  }
  if (cls === "rainy") {
    return `<div class="weather-icon rainy">
      <div class="rain-cloud"></div>
      <div class="rain-drops"><span></span><span></span><span></span><span></span></div>
    </div>`;
  }
  // thunder
  return `<div class="weather-icon thunder">
    <div class="storm-cloud"></div>
    <div class="bolt">⚡</div>
  </div>`;
}

function fetchWeather(stateName) {
  const w = WEATHER_DATA[stateName] || {
    temp: 30, desc: "Sunny", humidity: 50, wind: 12, rain: 5, advisory: "Normal conditions"
  };

  const iconWrapper = document.getElementById("weather-icon");
  const temp     = document.getElementById("weather-temp");
  const desc     = document.getElementById("weather-desc");
  const humidity = document.getElementById("wd-humidity");
  const wind     = document.getElementById("wd-wind");
  const rain     = document.getElementById("wd-rain");
  const advisory = document.getElementById("wd-advisory");

  if (iconWrapper) iconWrapper.innerHTML = buildWeatherIconHTML(getWeatherIconClass(w.desc));
  if (temp)     temp.textContent     = `${w.temp}°C`;
  if (desc)     desc.textContent     = w.desc;
  if (humidity) humidity.textContent = `${w.humidity}%`;
  if (wind)     wind.textContent     = `${w.wind} km/h`;
  if (rain)     rain.textContent     = `${w.rain} mm`;
  if (advisory) advisory.textContent = w.advisory;
}

// ==============================================================
// === STATS RENDER ==============================================
// ==============================================================
function renderStats(data) {
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };
  set("val-farmers", data.totalFarmers?.toLocaleString("en-IN") || "—");
  set("val-area",    data.areaCoverage?.toLocaleString("en-IN") || "—");
  set("val-yield",   data.avgYield   ? `${data.avgYield} q/ac`  : "—");
  set("val-crops",   data.activeCrops ?? "—");
}

function renderStatsFallback() {
  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) { el.textContent = val; el.classList.add("skeleton"); }
  };
  // Demo values from analytics module
  set("val-farmers", "1,24,680");
  set("val-area",    "8,92,340");
  set("val-yield",   "3.1 q/ac");
  set("val-crops",   "7");
  setTimeout(() => {
    document.querySelectorAll(".stat-card-value.skeleton").forEach(el => el.classList.remove("skeleton"));
  }, 600);
}

// ==============================================================
// === CROP SUGGESTOR ============================================
// ==============================================================
/*
 * 6-dimension scoring algorithm:
 *   price_trend   0–30  (30 = strong upward MSP + mandi trend)
 *   demand        0–20  (20 = high demand index)
 *   roi           0–25  (25 = best net return per acre)
 *   risk          0–15  (15 = lowest pest/weather risk)
 *   water         0–10  (10 = best match to stated water source)
 *   land_fit      0–0   (10 = land size optimal range)
 * Total max = 110 → normalised to 100
 */
const CROP_SCORES_BASE = {
  Wheat:     { price_trend: 26, demand: 18, roi: 22, risk: 13, water: 7,  land_fit: 8  },
  Rice:      { price_trend: 22, demand: 20, roi: 18, risk: 10, water: 5,  land_fit: 7  },
  Corn:      { price_trend: 20, demand: 15, roi: 20, risk: 14, water: 8,  land_fit: 9  },
  Sugarcane: { price_trend: 18, demand: 14, roi: 24, risk: 8,  water: 4,  land_fit: 6  },
  Cotton:    { price_trend: 16, demand: 13, roi: 21, risk: 7,  water: 6,  land_fit: 8  },
  Mustard:   { price_trend: 24, demand: 16, roi: 20, risk: 12, water: 9,  land_fit: 10 },
  Pulses:    { price_trend: 22, demand: 17, roi: 19, risk: 14, water: 10, land_fit: 9  }
};

const WATER_WEIGHTS = {
  canal: { Rice: 1.2, Sugarcane: 1.15, Wheat: 1.1 },
  borewell: { Wheat: 1.1, Mustard: 1.1 },
  rainwater: { Pulses: 1.3, Corn: 1.2, Rice: 0.8 },
  "river / tank": { Rice: 1.2, Sugarcane: 1.1 },
  drip: { Cotton: 1.3, Corn: 1.2, Mustard: 1.15 }
};

function scoresCrops(state, landSize, waterSource) {
  const waterKey = (waterSource || "").toLowerCase();
  const waterAdj = WATER_WEIGHTS[waterKey] || {};

  return Object.entries(CROP_SCORES_BASE).map(([crop, s]) => {
    let total = s.price_trend + s.demand + s.roi + s.risk + s.water + s.land_fit;
    // Apply water-source multiplier
    if (waterAdj[crop]) total *= waterAdj[crop];
    // Normalise to 100
    const score = Math.min(Math.round((total / 110) * 100), 100);
    return { crop, score };
  }).sort((a, b) => b.score - a.score);
}

function initCropSuggestor() {
  const form    = document.getElementById("suggestor-form");
  const results = document.getElementById("suggestor-results");
  if (!form) return;

  form.addEventListener("submit", e => {
    e.preventDefault();
    const state      = document.getElementById("sug-state")?.value;
    const land       = document.getElementById("sug-land")?.value;
    const water      = document.getElementById("sug-water")?.value;

    if (!state || !water) return;

    const ranked = scoresCrops(state, parseFloat(land) || 5, water);

    results.hidden = false;
    results.innerHTML = ranked.map((item, idx) => `
      <div class="sug-crop-item">
        <span class="sug-rank">#${idx + 1}</span>
        <span class="sug-crop-name">${item.crop}</span>
        <div class="sug-score-bar-wrap">
          <div class="sug-score-bar-bg">
            <div class="sug-score-bar-fill" style="width:${item.score}%"></div>
          </div>
        </div>
        <span class="sug-score-label">${item.score}</span>
      </div>
    `).join("");
  });
}

// ==============================================================
// === AI ASSISTANT ==============================================
// ==============================================================
const AI_SYSTEM_PROMPT = `You are Sasyam, an agricultural intelligence assistant for Indian farmers.
You are knowledgeable about:
- MSP (Minimum Support Price) rates 2024-25: Wheat ₹2,275/q, Rice ₹2,300/q, Corn ₹2,090/q, Sugarcane ₹340/ton, Cotton ₹7,121/q, Mustard ₹5,650/q, Masur Dal ₹6,425/q
- Regional yield benchmarks: Punjab (wheat 4.2 q/ac), UP (rice 2.8 q/ac), Maharashtra (sugarcane 32 ton/ac)
- Crop diseases, pest management, irrigation, soil health
- Market intelligence and supply chain
- Government schemes: PM-KISAN, PMFBY crop insurance, e-NAM
Respond in clear, practical language. You can switch between Hindi and English (Hinglish welcome). Keep answers brief and farmer-friendly.`;

const AI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"];

function sanitiseAiResponse(text) {
  // Strip any HTML tags
  let clean = text.replace(/<[^>]*>/g, "");
  // Normalise markdown: **bold** → bold (simple strip for chat bubbles)
  clean = clean.replace(/\*\*(.+?)\*\*/g, "$1");
  clean = clean.replace(/\*(.+?)\*/g, "$1");
  clean = clean.replace(/#{1,4}\s/g, "");
  // Trim excess whitespace
  clean = clean.replace(/\n{3,}/g, "\n\n").trim();
  return clean;
}

async function callGemini(userMessage, modelIndex = 0) {
  const model = AI_MODELS[modelIndex];
  const key   = window.CONFIG?.GEMINI_API_KEY;
  if (!key) throw new Error("GEMINI_API_KEY not configured");

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;

  const body = {
    system_instruction: { parts: [{ text: AI_SYSTEM_PROMPT }] },
    contents: [
      ...state.aiHistory.map(h => ({
        role: h.role,
        parts: [{ text: h.content }]
      })),
      { role: "user", parts: [{ text: userMessage }] }
    ],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 512,
      topP: 0.9
    }
  };

  const res  = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(12000)
  });

  if (!res.ok) {
    // Fallback to next model
    if (modelIndex < AI_MODELS.length - 1) {
      return callGemini(userMessage, modelIndex + 1);
    }
    throw new Error(`Gemini error ${res.status}`);
  }

  const data = await res.json();
  const raw  = data.candidates?.[0]?.content?.parts?.[0]?.text || "No response.";
  const clean = sanitiseAiResponse(raw);

  // Update model indicator
  state.activeAiModel = model;
  const modelEl = document.getElementById("ai-model-name");
  if (modelEl) modelEl.textContent = model;

  return clean;
}

function appendMessage(role, text) {
  const container = document.getElementById("ai-messages");
  if (!container) return;

  const div = document.createElement("div");
  div.className = `ai-msg ${role}`;
  div.innerHTML = `<div class="msg-bubble">${text.replace(/\n/g, "<br>")}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function showTyping() {
  const container = document.getElementById("ai-messages");
  if (!container) return null;
  const div = document.createElement("div");
  div.className = "ai-msg assistant msg-typing";
  div.innerHTML = `<div class="msg-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function initAiChat() {
  const toggle  = document.getElementById("ai-chat-toggle");
  const body    = document.getElementById("ai-chat-body");
  const form    = document.getElementById("ai-form");
  const input   = document.getElementById("ai-input");
  const clearBtn = document.getElementById("ai-clear");

  if (toggle && body) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      body.hidden = open;
      if (!open) setTimeout(() => input?.focus(), 200);
    });
  }

  if (form) {
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const msg = input?.value.trim();
      if (!msg) return;
      input.value = "";
      input.disabled = true;

      appendMessage("user", msg);
      state.aiHistory.push({ role: "user", content: msg });

      const typingEl = showTyping();

      try {
        const reply = await callGemini(msg);
        typingEl?.remove();
        appendMessage("assistant", reply);
        state.aiHistory.push({ role: "model", content: reply });
        // Keep history to last 10 exchanges
        if (state.aiHistory.length > 20) state.aiHistory.splice(0, 2);
      } catch (err) {
        typingEl?.remove();
        appendMessage("assistant", "Sorry, I'm having trouble connecting right now. Please check your API key in config.js. 🙏");
      } finally {
        input.disabled = false;
        input.focus();
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      state.aiHistory = [];
      const messages = document.getElementById("ai-messages");
      if (messages) messages.innerHTML = `
        <div class="ai-msg assistant">
          <div class="msg-bubble">
            Namaste! 🙏 I'm your Sasyam agricultural assistant. Ask me about MSP rates, crop recommendations, disease treatment, or any farming query in Hindi or English.
          </div>
        </div>
      `;
    });
  }
}

// ==============================================================
// === THEME =====================================================
// ==============================================================
function initTheme() {
  const btn  = document.getElementById("theme-toggle");
  const body = document.body;
  if (!btn) return;

  const saved = localStorage.getItem("sasyam-theme") || "dark";
  body.dataset.theme = saved;
  btn.querySelector(".theme-icon").textContent = saved === "dark" ? "☀" : "☾";

  btn.addEventListener("click", () => {
    const next = body.dataset.theme === "dark" ? "light" : "dark";
    if (document.startViewTransition) {
      document.startViewTransition(() => { body.dataset.theme = next; });
    } else {
      body.dataset.theme = next;
    }
    localStorage.setItem("sasyam-theme", next);
    btn.querySelector(".theme-icon").textContent = next === "dark" ? "☀" : "☾";
  });
}

// ==============================================================
// === DEMO MARKET DATA ==========================================
// ==============================================================
function getDemoMarketData(crop) {
  const trends = {
    Wheat:     [2215, 2245, 2260, 2255, 2278, 2290, 2310],
    Rice:      [2180, 2200, 2210, 2195, 2220, 2245, 2260],
    Corn:      [2010, 2035, 2055, 2048, 2070, 2083, 2090],
    Sugarcane: [325,  330,  332,  331,  335,  338,  340 ],
    Cotton:    [6820, 6890, 6945, 6910, 6980, 7020, 7080],
    Mustard:   [5450, 5490, 5510, 5530, 5580, 5610, 5650],
    Pulses:    [6100, 6150, 6200, 6180, 6250, 6300, 6350]
  };
  return { price_trend_7day: trends[crop] || trends.Wheat };
}

// ==============================================================
// === INIT ======================================================
// ==============================================================
function init() {
  initTheme();
  initCropChart();
  initPriceChart();
  initMap();
  initCropSuggestor();
  initAiChat();

  // Weather state selector
  const weatherSel = document.getElementById("weather-state-select");
  if (weatherSel) {
    fetchWeather(state.selectedWeatherState);
    weatherSel.addEventListener("change", () => {
      state.selectedWeatherState = weatherSel.value;
      fetchWeather(weatherSel.value);
    });
  }

  // Start data polling
  startPolling();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
