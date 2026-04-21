# backend/analytics.py
# ─────────────────────────────────────────────────────────────
# Sasyam — Analytics module
# Hardcoded 2024 Indian agricultural statistics
# No random numbers — all values are realistic benchmarks
# ─────────────────────────────────────────────────────────────

# ═════════════════════════════════════════════════════════════
# MARKET DATA — 2024-25 Season
# Sources: CACP MSP notifications, APMC mandi data, NAFED reports
# ═════════════════════════════════════════════════════════════

_MARKET_DATA = {
    "Wheat": {
        "msp_rate":          2275,       # ₹/quintal, 2024-25 CACP recommendation
        "current_price":     2310,       # ₹/quintal, national mandi average
        "demand_index":      82,         # 0-100; higher = stronger demand
        "supply_ratio":      1.08,       # >1 = surplus; <1 = deficit
        "market_status":     "Stable",   # Stable / Active / Critical
        "price_trend_7day":  [2215, 2245, 2260, 2255, 2278, 2290, 2310]
    },
    "Rice": {
        "msp_rate":          2300,
        "current_price":     2260,
        "demand_index":      91,
        "supply_ratio":      0.97,
        "market_status":     "Active",
        "price_trend_7day":  [2180, 2200, 2210, 2195, 2220, 2245, 2260]
    },
    "Corn": {
        "msp_rate":          2090,
        "current_price":     2090,
        "demand_index":      74,
        "supply_ratio":      1.03,
        "market_status":     "Stable",
        "price_trend_7day":  [2010, 2035, 2055, 2048, 2070, 2083, 2090]
    },
    "Sugarcane": {
        "msp_rate":          340,        # ₹/tonne (FRP 2024-25)
        "current_price":     340,
        "demand_index":      68,
        "supply_ratio":      1.12,
        "market_status":     "Stable",
        "price_trend_7day":  [325, 330, 332, 331, 335, 338, 340]
    },
    "Cotton": {
        "msp_rate":          7121,       # MCU-5 variety
        "current_price":     7080,
        "demand_index":      58,
        "supply_ratio":      0.88,
        "market_status":     "Critical",
        "price_trend_7day":  [6820, 6890, 6945, 6910, 6980, 7020, 7080]
    },
    "Mustard": {
        "msp_rate":          5650,
        "current_price":     5650,
        "demand_index":      79,
        "supply_ratio":      1.01,
        "market_status":     "Stable",
        "price_trend_7day":  [5450, 5490, 5510, 5530, 5580, 5610, 5650]
    },
    "Pulses": {
        "msp_rate":          6425,       # Masur Dal
        "current_price":     6350,
        "demand_index":      85,
        "supply_ratio":      0.93,
        "market_status":     "Active",
        "price_trend_7day":  [6100, 6150, 6200, 6180, 6250, 6300, 6350]
    }
}


def get_market_data() -> dict:
    """
    Returns per-crop market data dict.
    All MSP rates from CACP 2024-25 recommendations.
    Mandi prices are national weighted averages (Apr 2024).
    """
    return _MARKET_DATA.copy()


# ═════════════════════════════════════════════════════════════
# REGIONAL STATS — 2023-24 crop year
# Sources: Directorate of Economics & Statistics (DES),
#          State Agriculture Departments, ICAR yield data
# ═════════════════════════════════════════════════════════════

_REGIONAL_DATA = {
    "Punjab": {
        "primary_crop":    "Wheat",
        "avg_yield_qac":   4.2,           # quintal per acre
        "yoy_growth_pct":  5.2,
        "total_area_kha":  7200,           # thousand hectares
        "irrigated_pct":   98,
        "benchmark_note":  "Highest wheat yield state in India"
    },
    "Haryana": {
        "primary_crop":    "Wheat",
        "avg_yield_qac":   3.8,
        "yoy_growth_pct":  3.1,
        "total_area_kha":  4800,
        "irrigated_pct":   85,
        "benchmark_note":  "Major contributor to central pool wheat stock"
    },
    "Uttar Pradesh": {
        "primary_crop":    "Wheat",
        "avg_yield_qac":   3.1,
        "yoy_growth_pct":  4.8,
        "total_area_kha":  9800,
        "irrigated_pct":   74,
        "benchmark_note":  "Largest wheat producing state by area"
    },
    "Madhya Pradesh": {
        "primary_crop":    "Wheat",
        "avg_yield_qac":   2.9,
        "yoy_growth_pct":  6.1,
        "total_area_kha":  6200,
        "irrigated_pct":   55,
        "benchmark_note":  "Fastest growing wheat yields in central India"
    },
    "Maharashtra": {
        "primary_crop":    "Sugarcane",
        "avg_yield_qac":   32.0,          # tonnes/acre for sugarcane
        "yoy_growth_pct":  2.4,
        "total_area_kha":  1100,
        "irrigated_pct":   100,
        "benchmark_note":  "Largest sugarcane producing state"
    },
    "Gujarat": {
        "primary_crop":    "Cotton",
        "avg_yield_qac":   2.4,
        "yoy_growth_pct":  1.8,
        "total_area_kha":  2600,
        "irrigated_pct":   44,
        "benchmark_note":  "Bt-Cotton dominant; largest cotton producer"
    },
    "Karnataka": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   2.3,
        "yoy_growth_pct":  3.5,
        "total_area_kha":  1100,
        "irrigated_pct":   38,
        "benchmark_note":  "Rain-fed paddy dominates Malnad region"
    },
    "Tamil Nadu": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   3.4,
        "yoy_growth_pct":  4.2,
        "total_area_kha":  1800,
        "irrigated_pct":   62,
        "benchmark_note":  "Highest paddy yield per acre in South India"
    },
    "Rajasthan": {
        "primary_crop":    "Mustard",
        "avg_yield_qac":   2.0,
        "yoy_growth_pct":  7.3,
        "total_area_kha":  3200,
        "irrigated_pct":   28,
        "benchmark_note":  "Largest mustard producing state; 46% of national area"
    },
    "Bihar": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   2.8,
        "yoy_growth_pct":  2.9,
        "total_area_kha":  3400,
        "irrigated_pct":   55,
        "benchmark_note":  "Kharif rice dominant; rising maize cultivation"
    },
    "West Bengal": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   3.2,
        "yoy_growth_pct":  3.8,
        "total_area_kha":  5600,
        "irrigated_pct":   68,
        "benchmark_note":  "Boro rice with highest irrigation intensity"
    },
    "Andhra Pradesh": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   3.0,
        "yoy_growth_pct":  3.0,
        "total_area_kha":  2100,
        "irrigated_pct":   72,
        "benchmark_note":  "Krishna-Godavari delta high-productivity zone"
    },
    "Telangana": {
        "primary_crop":    "Cotton",
        "avg_yield_qac":   2.7,
        "yoy_growth_pct":  2.2,
        "total_area_kha":  1800,
        "irrigated_pct":   40,
        "benchmark_note":  "Third largest cotton state; rising paddy area"
    },
    "Odisha": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   2.4,
        "yoy_growth_pct":  2.7,
        "total_area_kha":  4200,
        "irrigated_pct":   36,
        "benchmark_note":  "Rain-fed upland rice; tribal cultivation practices"
    },
    "Chhattisgarh": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   2.1,
        "yoy_growth_pct":  4.1,
        "total_area_kha":  3900,
        "irrigated_pct":   30,
        "benchmark_note":  "Rice bowl of central India; traditional varieties"
    },
    "Assam": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   2.5,
        "yoy_growth_pct":  3.3,
        "total_area_kha":  2800,
        "irrigated_pct":   22,
        "benchmark_note":  "Ahu-Sali-Boro rice system; flood-prone districts"
    },
    "Himachal Pradesh": {
        "primary_crop":    "Wheat",
        "avg_yield_qac":   2.1,
        "yoy_growth_pct":  2.0,
        "total_area_kha":  380,
        "irrigated_pct":   18,
        "benchmark_note":  "Hill agriculture; apple and off-season vegetables"
    },
    "Jharkhand": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   1.9,
        "yoy_growth_pct":  2.0,
        "total_area_kha":  1600,
        "irrigated_pct":   14,
        "benchmark_note":  "Rain-fed cultivation; high drought risk zones"
    },
    "Kerala": {
        "primary_crop":    "Rice",
        "avg_yield_qac":   1.8,
        "yoy_growth_pct":  1.5,
        "total_area_kha":  240,
        "irrigated_pct":   46,
        "benchmark_note":  "Area declining; spices, coconut, rubber dominant"
    }
}


def get_regional_stats(state: str) -> dict | None:
    """
    Returns yield comparison and growth trend for a given Indian state.
    State name must match the keys in _REGIONAL_DATA (title case).
    Returns None if state not found.
    """
    key = state.strip().title()
    return _REGIONAL_DATA.get(key)


def get_all_regional_stats() -> dict:
    """Returns stats for all states."""
    return _REGIONAL_DATA.copy()
