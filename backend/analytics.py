import datetime

def get_dashboard_stats() -> dict:
    return {
        "total_farmers": 0,
        "area_coverage_hectares": 0,
        "average_yield_tons_per_hectare": 3.2,
        "active_crops": 7,
        "crop_distribution": {
            "Wheat": 28,
            "Rice": 22,
            "Corn": 15,
            "Sugarcane": 12,
            "Cotton": 10,
            "Mustard": 8,
            "Pulses": 5
        },
        "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
    }

def get_market_data() -> dict:
    return {
        "Wheat": {
            "msp_rate": 2275,
            "current_price": 2350,
            "demand_index": 85,
            "supply_ratio": 0.95,
            "market_status": "Active",
            "price_trend_7day": [2310, 2320, 2325, 2335, 2340, 2345, 2350],
            "demand_drivers": ["Export demand up 12%", "Rabi season peak"],
            "sentiment": "Bullish"
        },
        "Rice": {
            "msp_rate": 2183,
            "current_price": 2250,
            "demand_index": 78,
            "supply_ratio": 1.05,
            "market_status": "Active",
            "price_trend_7day": [2260, 2255, 2250, 2248, 2245, 2248, 2250],
            "demand_drivers": ["Domestic stock adequate", "Stable export limits"],
            "sentiment": "Neutral"
        },
        "Corn": {
            "msp_rate": 2090,
            "current_price": 2150,
            "demand_index": 92,
            "supply_ratio": 0.75,
            "market_status": "Critical",
            "price_trend_7day": [2080, 2095, 2110, 2125, 2135, 2145, 2150],
            "demand_drivers": ["High poultry feed demand", "Ethanol blending push"],
            "sentiment": "Bullish"
        },
        "Sugarcane": {
            "msp_rate": 340,
            "current_price": 355,
            "demand_index": 88,
            "supply_ratio": 0.85,
            "market_status": "Active",
            "price_trend_7day": [345, 348, 350, 352, 353, 354, 355],
            "demand_drivers": ["Sugar mill demand high", "Festival season approaching"],
            "sentiment": "Bullish"
        },
        "Cotton": {
            "msp_rate": 7121,
            "current_price": 6950,
            "demand_index": 65,
            "supply_ratio": 1.15,
            "market_status": "Stable",
            "price_trend_7day": [7100, 7050, 7020, 7000, 6980, 6960, 6950],
            "demand_drivers": ["Sluggish textile exports", "High carryover stock"],
            "sentiment": "Bearish"
        },
        "Mustard": {
            "msp_rate": 5650,
            "current_price": 5800,
            "demand_index": 82,
            "supply_ratio": 0.90,
            "market_status": "Active",
            "price_trend_7day": [5700, 5720, 5740, 5750, 5770, 5780, 5800],
            "demand_drivers": ["Edible oil import duties up", "Winter demand rising"],
            "sentiment": "Bullish"
        },
        "Pulses": {
            "msp_rate": 7550,
            "current_price": 8100,
            "demand_index": 95,
            "supply_ratio": 0.70,
            "market_status": "Critical",
            "price_trend_7day": [7800, 7850, 7920, 8000, 8050, 8080, 8100],
            "demand_drivers": ["Monsoon deficit impacts", "High protein dietary shifts"],
            "sentiment": "Bullish"
        }
    }

def get_regional_stats(state: str) -> dict:
    state = state.title()
    hardcoded = {
        "Punjab": {
            "primary_crops": ["Wheat", "Rice", "Cotton"],
            "yield_tons_per_hectare": 4.5,
            "yield_vs_national_avg_pct": 40.6,
            "area_under_cultivation_million_hectares": 4.1,
            "growth_trend_pct": 1.2,
            "top_district": "Ludhiana",
            "irrigation_coverage_pct": 98
        },
        "Haryana": {
            "primary_crops": ["Wheat", "Rice", "Mustard"],
            "yield_tons_per_hectare": 4.2,
            "yield_vs_national_avg_pct": 31.2,
            "area_under_cultivation_million_hectares": 3.6,
            "growth_trend_pct": 1.5,
            "top_district": "Karnal",
            "irrigation_coverage_pct": 91
        },
        "Uttar Pradesh": {
            "primary_crops": ["Wheat", "Sugarcane", "Rice"],
            "yield_tons_per_hectare": 3.5,
            "yield_vs_national_avg_pct": 9.4,
            "area_under_cultivation_million_hectares": 16.5,
            "growth_trend_pct": 2.1,
            "top_district": "Lakhimpur Kheri",
            "irrigation_coverage_pct": 82
        },
        "Madhya Pradesh": {
            "primary_crops": ["Wheat", "Soybean", "Pulses"],
            "yield_tons_per_hectare": 2.8,
            "yield_vs_national_avg_pct": -12.5,
            "area_under_cultivation_million_hectares": 15.2,
            "growth_trend_pct": 3.4,
            "top_district": "Ujjain",
            "irrigation_coverage_pct": 45
        },
        "Rajasthan": {
            "primary_crops": ["Mustard", "Bajra", "Wheat"],
            "yield_tons_per_hectare": 2.1,
            "yield_vs_national_avg_pct": -34.4,
            "area_under_cultivation_million_hectares": 18.0,
            "growth_trend_pct": 0.8,
            "top_district": "Sri Ganganagar",
            "irrigation_coverage_pct": 35
        },
        "Maharashtra": {
            "primary_crops": ["Cotton", "Sugarcane", "Soybean"],
            "yield_tons_per_hectare": 2.5,
            "yield_vs_national_avg_pct": -21.9,
            "area_under_cultivation_million_hectares": 17.4,
            "growth_trend_pct": 1.1,
            "top_district": "Pune",
            "irrigation_coverage_pct": 19
        },
        "Karnataka": {
            "primary_crops": ["Corn", "Cotton", "Pulses"],
            "yield_tons_per_hectare": 2.9,
            "yield_vs_national_avg_pct": -9.4,
            "area_under_cultivation_million_hectares": 9.8,
            "growth_trend_pct": 1.7,
            "top_district": "Belagavi",
            "irrigation_coverage_pct": 34
        },
        "Andhra Pradesh": {
            "primary_crops": ["Rice", "Cotton", "Corn"],
            "yield_tons_per_hectare": 3.8,
            "yield_vs_national_avg_pct": 18.7,
            "area_under_cultivation_million_hectares": 6.3,
            "growth_trend_pct": 2.0,
            "top_district": "Guntur",
            "irrigation_coverage_pct": 52
        },
        "West Bengal": {
            "primary_crops": ["Rice", "Jute", "Potato"],
            "yield_tons_per_hectare": 3.3,
            "yield_vs_national_avg_pct": 3.1,
            "area_under_cultivation_million_hectares": 5.5,
            "growth_trend_pct": 0.5,
            "top_district": "Bardhaman",
            "irrigation_coverage_pct": 60
        },
        "Bihar": {
            "primary_crops": ["Rice", "Wheat", "Corn"],
            "yield_tons_per_hectare": 2.4,
            "yield_vs_national_avg_pct": -25.0,
            "area_under_cultivation_million_hectares": 5.2,
            "growth_trend_pct": 1.4,
            "top_district": "Rohtas",
            "irrigation_coverage_pct": 68
        }
    }
    
    if state in hardcoded:
        return hardcoded[state]
    else:
        return {
            "primary_crops": ["Wheat", "Rice", "Corn"],
            "yield_tons_per_hectare": 3.2,
            "yield_vs_national_avg_pct": 0.0,
            "area_under_cultivation_million_hectares": 5.0,
            "growth_trend_pct": 1.0,
            "top_district": "N/A",
            "irrigation_coverage_pct": 50
        }

def get_crop_suggestions(region: str, season: str, land_size_acres: float, water_availability: str, risk_tolerance: str) -> list:
    market_data = get_market_data()
    water_needs = {
        "Wheat": "Medium",
        "Rice": "High",
        "Corn": "Low",
        "Sugarcane": "Very High",
        "Cotton": "Medium",
        "Mustard": "Low",
        "Pulses": "Very Low"
    }
    
    water_levels = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
    user_water_level = water_levels.get(water_availability.title(), 3)
    
    suggestions = []
    
    for crop, data in market_data.items():
        # price_trend_score (0-30)
        pt_start = data["price_trend_7day"][0]
        pt_end = data["price_trend_7day"][-1]
        pt_diff = (pt_end - pt_start) / pt_start
        price_trend_score = min(max(int((pt_diff * 100) * 5), 0), 30) # Rough mapping
        if data["sentiment"] == "Bullish":
            price_trend_score = min(price_trend_score + 10, 30)
            
        # demand_score (0-20)
        demand_score = int(data["demand_index"] / 100 * 20)
        
        # roi_score (0-25)
        roi_ratio = data["current_price"] / data["msp_rate"]
        roi_score = min(int((roi_ratio - 1) * 100), 25)
        if roi_score < 0: roi_score = 0
        if roi_ratio > 1.0: roi_score += 10
        roi_score = min(roi_score, 25)
        
        # risk_score (0-15)
        crop_risk = "Medium"
        if crop in ["Cotton", "Sugarcane"]: crop_risk = "High"
        if crop in ["Wheat", "Rice", "Mustard"]: crop_risk = "Low"
        
        risk_score = 10
        if risk_tolerance.title() == "Low":
            if crop_risk == "High": risk_score = 0
            elif crop_risk == "Low": risk_score = 15
        elif risk_tolerance.title() == "High":
            if crop_risk == "High": risk_score = 15
            elif crop_risk == "Low": risk_score = 5
        
        # water_score (0-10)
        crop_water_level = water_levels.get(water_needs[crop], 3)
        water_diff = abs(user_water_level - crop_water_level)
        if crop_water_level > user_water_level:
            water_score = max(10 - (water_diff * 4), 0) # penalize heavily if need > available
        else:
            water_score = max(10 - (water_diff * 2), 4) # penalize lightly if available > need
            
        # land_score (0-10)
        land_score = 10
        if crop == "Sugarcane" and land_size_acres < 5:
            land_score = 2
        elif crop == "Cotton" and land_size_acres < 2:
            land_score = 5
            
        total_score = price_trend_score + demand_score + roi_score + risk_score + water_score + land_score
        
        reasons = []
        if price_trend_score > 20: reasons.append(f"Strong market momentum (₹{data['current_price']}/q)")
        elif data['current_price'] > data['msp_rate']: reasons.append(f"Price is above MSP of ₹{data['msp_rate']}/q")
        
        if demand_score > 16: reasons.append(data["demand_drivers"][0])
        
        if water_score >= 8: reasons.append(f"Perfect water availability match")
        
        if len(reasons) == 0:
            reasons.append("Stable secondary option")
            
        suggestions.append({
            "crop": crop,
            "total_score": total_score,
            "confidence_pct": f"{min(total_score + 10, 98)}%",
            "score_breakdown": {
                "price_trend": price_trend_score,
                "demand": demand_score,
                "roi": roi_score,
                "risk": risk_score,
                "water": water_score,
                "land": land_score
            },
            "reasons": reasons,
            "key_insight": f"Good choice for {season} season in {region}" if total_score > 60 else "Consider as an alternative crop"
        })
        
    suggestions.sort(key=lambda x: x["total_score"], reverse=True)
    return suggestions[:4]

def get_weather_data(state: str) -> dict:
    state = state.title()
    
    # Base defaults
    condition = "Sunny"
    temp = 36
    humidity = 42
    wind = 14
    rain = 8
    
    if state in ["Punjab", "Haryana", "Himachal Pradesh", "Jammu And Kashmir", "Uttarakhand"]:
        temp = 32
        humidity = 35
    elif state in ["Rajasthan", "Gujarat"]:
        temp = 40
        humidity = 25
        wind = 20
    elif state in ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh", "Goa"]:
        temp = 34
        humidity = 75
        rain = 45
        condition = "Partly Cloudy"
    elif state in ["West Bengal", "Assam", "Meghalaya"]:
        temp = 33
        humidity = 80
        rain = 60
        condition = "Scattered Showers"
        
    advisories = {
        "Sunny": "High temperatures — ensure adequate irrigation for standing crops",
        "Partly Cloudy": "Favorable conditions for crop growth. Monitor for pest activity in high humidity.",
        "Scattered Showers": "Delay pesticide spraying. Ensure proper field drainage."
    }
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    forecast = []
    
    for i, day in enumerate(days):
        day_temp = temp + (i % 3) - 1
        day_low = temp - 10 + (i % 2)
        day_cond = condition if i % 4 != 0 else ("Cloudy" if condition == "Sunny" else "Sunny")
        forecast.append({
            "day": day,
            "condition": day_cond,
            "high": day_temp,
            "low": day_low
        })
        
    return {
        "condition": condition,
        "temperature_c": temp,
        "humidity_pct": humidity,
        "wind_kmh": wind,
        "rainfall_mm_this_month": rain,
        "forecast_7day": forecast,
        "agricultural_advisory": advisories.get(condition, "Standard agricultural practices recommended.")
    }
