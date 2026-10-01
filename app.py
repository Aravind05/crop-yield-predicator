import json
import os
import streamlit as st

# Set page layout and title
st.set_page_config(
    page_title="Crop Yield Predictor", page_icon="🌾", layout="wide"
)

st.title("🌾 Crop Yield Prediction Dashboard")
st.write(
    "Adjust environmental, soil nutrient, and management parameters in the sidebar to estimate crop yield."
)

# ---------------------------------------------------------
# Sidebar Controls (All Inputs)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Input Parameters")

# 1. General & Crop Selection
st.sidebar.subheader("🌱 Crop Selection")
crop_type = st.sidebar.selectbox(
    "Crop Type",
    [
        "Rice",
        "Wheat",
        "Maize",
        "Cotton",
        "Sugarcane",
        "Pulses",
        "Groundnut",
        "Soybean",
    ],
)

# 2. Environmental Conditions (Original Parameters)
st.sidebar.subheader("🌡️ Environmental Conditions")
temperature = st.sidebar.slider("Temperature (°C)", 10.0, 50.0, 25.0, step=0.5)
rainfall = st.sidebar.slider("Rainfall (mm)", 100.0, 1000.0, 500.0, step=10.0)
soil_moisture = st.sidebar.slider(
    "Soil Moisture (%)", 10.0, 90.0, 45.0, step=1.0
)

# 3. Soil Health & Nutrients
st.sidebar.subheader("🧪 Soil Health & Nutrients")
soil_ph = st.sidebar.slider("Soil pH", 4.0, 9.0, 6.5, step=0.1)
nitrogen = st.sidebar.number_input(
    "Soil Nitrogen (N - kg/ha)", 0.0, 300.0, 120.0, step=5.0
)
phosphorus = st.sidebar.number_input(
    "Soil Phosphorus (P - kg/ha)", 0.0, 150.0, 40.0, step=2.0
)
potassium = st.sidebar.number_input(
    "Soil Potassium (K - kg/ha)", 0.0, 200.0, 50.0, step=2.0
)

# 4. Agricultural Inputs / Management
st.sidebar.subheader("🚜 Farm Inputs")
fertilizer = st.sidebar.number_input(
    "Fertilizer Usage (kg/ha)", 0.0, 500.0, 150.0, step=10.0
)
pesticide = st.sidebar.number_input(
    "Pesticide Usage (kg/ha)", 0.0, 20.0, 2.5, step=0.5
)


# ---------------------------------------------------------
# Model Load & Prediction Logic
# ---------------------------------------------------------
def load_coefficients():
    json_path = "model_coefficients.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    else:
        # Fallback coefficients matching MATLAB export
        return {
            "Intercept": 0,
            "Temp": -0.12980241492864633,
            "Rainfall": 0.015751920965971358,
            "Moisture": -0.054637760702525486,
        }


coeffs = load_coefficients()

# Base yield from regression model
base_yield = (
    coeffs.get("Intercept", 0)
    + (coeffs.get("Temp", 0) * temperature)
    + (coeffs.get("Rainfall", 0) * rainfall)
    + (coeffs.get("Moisture", 0) * soil_moisture)
)

# Crop-specific factor
crop_factors = {
    "Rice": 1.2,
    "Wheat": 1.1,
    "Maize": 1.4,
    "Cotton": 0.8,
    "Sugarcane": 2.5,
    "Pulses": 0.7,
    "Groundnut": 0.9,
    "Soybean": 1.0,
}

# Soil pH penalty/bonus (optimal pH: 6.0 - 7.5)
ph_factor = 1.0 if 6.0 <= soil_ph <= 7.5 else 0.85

# NPK and Fertilizer adjustment multiplier
npk_total = nitrogen + phosphorus + potassium
nutrient_factor = 0.9 + (npk_total / 1000.0) + (fertilizer / 2000.0)

# Calculate final crop yield (ensuring non-negative yield)
final_yield = max(
    0.0,
    base_yield * crop_factors.get(crop_type, 1.0) * ph_factor * nutrient_factor,
)

# ---------------------------------------------------------
# UI Display Results
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Prediction Results")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label=f"Predicted Yield for {crop_type}",
        value=f"{final_yield:.2f} tonnes/ha",
    )

with col2:
    st.info(f"**Selected Crop:** {crop_type}")
    st.write(f"**Soil pH Level:** {soil_ph}")
    st.write(f"**NPK Balance:** {nitrogen} N | {phosphorus} P | {potassium} K")

st.markdown("---")

# Tabbed detailed parameter view
tab1, tab2 = st.tabs(["📋 Summary of Input Parameters", "📐 Model Details"])

with tab1:
    data_summary = {
        "Parameter": [
            "Crop Type",
            "Temperature",
            "Rainfall",
            "Soil Moisture",
            "Soil pH",
            "Nitrogen (N)",
            "Phosphorus (P)",
            "Potassium (K)",
            "Fertilizer Usage",
            "Pesticide Usage",
        ],
        "Value": [
            crop_type,
            f"{temperature} °C",
            f"{rainfall} mm",
            f"{soil_moisture} %",
            f"{soil_ph}",
            f"{nitrogen} kg/ha",
            f"{phosphorus} kg/ha",
            f"{potassium} kg/ha",
            f"{fertilizer} kg/ha",
            f"{pesticide} kg/ha",
        ],
    }
    st.table(data_summary)

with tab2:
    st.write("**Model Coefficients (`model_coefficients.json`):**")
    st.json(coeffs)
