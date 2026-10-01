import json
import os
import streamlit as st

st.set_page_config(
    page_title="Crop Yield Predictor", page_icon="🌾", layout="centered"
)

st.title("🌾 Crop Yield Prediction Dashboard")
st.write(
    "Adjust environmental factors using the sidebar controls to predict crop yield in real-time."
)


def load_model():
    json_path = "model_coefficients.json"
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r") as f:
        return json.load(f)


model = load_model()

if model is None:
    st.error("⚠️ `model_coefficients.json` not found in directory!")
    st.stop()

# Sidebar input controls
st.sidebar.header("Environmental & Farm Conditions")

# 1. Crop Selection
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
temp = st.sidebar.slider(
    "Temperature (°C)", min_value=10.0, max_value=50.0, value=25.0, step=0.5
)
rainfall = st.sidebar.slider(
    "Rainfall (mm)", min_value=50.0, max_value=1500.0, value=600.0, step=10.0
)
moisture = st.sidebar.slider(
    "Soil Moisture (%)", min_value=5.0, max_value=100.0, value=45.0, step=1.0
)

# 3. Soil Health & Nutrients
soil_ph = st.sidebar.slider(
    "Soil pH Level", min_value=4.0, max_value=9.0, value=7.0, step=0.1
)
nitrogen = st.sidebar.number_input(
    "Soil Nitrogen (N - kg/ha)",
    min_value=0.0,
    max_value=300.0,
    value=120.0,
    step=5.0,
)
phosphorus = st.sidebar.number_input(
    "Soil Phosphorus (P - kg/ha)",
    min_value=0.0,
    max_value=150.0,
    value=40.0,
    step=2.0,
)
potassium = st.sidebar.number_input(
    "Soil Potassium (K - kg/ha)",
    min_value=0.0,
    max_value=200.0,
    value=50.0,
    step=2.0,
)

# 4. Agricultural Inputs / Management
fertilizer = st.sidebar.number_input(
    "Fertilizer Usage (kg/ha)",
    min_value=0.0,
    max_value=500.0,
    value=150.0,
    step=10.0,
)
pesticide = st.sidebar.number_input(
    "Pesticide Usage (kg/ha)",
    min_value=0.0,
    max_value=20.0,
    value=2.5,
    step=0.5,
)

# Extract values dynamically from JSON dictionary
raw_values = list(model.values())

# JSON coefficients or defaults
intercept = (
    raw_values[0] if (len(raw_values) > 0 and raw_values[0] != 0) else 1.25
)
w_temp = raw_values[1] if (len(raw_values) > 1 and raw_values[1] != 0) else -0.04
w_rain = (
    raw_values[2] if (len(raw_values) > 2 and raw_values[2] != 0) else 0.0035
)
w_moist = (
    raw_values[3] if (len(raw_values) > 3 and raw_values[3] != 0) else 0.025
)

# Linear regression computation
base_yield = (
    intercept + (w_temp * temp) + (w_rain * rainfall) + (w_moist * moisture)
)

# Agronomic Multipliers for Display Factors
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
crop_factor = crop_factors.get(crop_type, 1.0)
ph_factor = 1.0 if 6.0 <= soil_ph <= 7.5 else 0.85
npk_total = nitrogen + phosphorus + potassium
nutrient_factor = 0.9 + (npk_total / 1000.0) + (fertilizer / 2000.0)

# Final Output Calculation
predicted_yield = max(
    0.0, base_yield * crop_factor * ph_factor * nutrient_factor
)

# Display Output
st.markdown("---")
st.subheader("Predicted Harvest Output")

formatted_yield = max(0.0, predicted_yield)
st.metric(label="Estimated Crop Yield", value=f"{formatted_yield:.2f} tonnes/ha")

# Progress indicator bar
normalized_progress = min(1.0, max(0.0, formatted_yield / 10.0))
st.progress(normalized_progress)

# Inspect Active Formula
with st.expander("🔍 Inspect Active Regression Formula"):
    st.write(f"**Intercept:** `{intercept:.4f}`")
    st.write(
        f"**Temp Contribution:** `{w_temp:.4f}` × {temp}°C = `{w_temp * temp:.2f}`"
    )
    st.write(
        f"**Rainfall Contribution:** `{w_rain:.4f}` × {rainfall}mm = `{w_rain * rainfall:.2f}`"
    )
    st.write(
        f"**Moisture Contribution:** `{w_moist:.4f}` × {moisture}% = `{w_moist * moisture:.2f}`"
    )
    st.write(f"**Crop Type Factor ({crop_type}):** `× {crop_factor}`")
    st.write(f"**Soil pH Factor ({soil_ph}):** `× {ph_factor}`")
    st.write(
        f"**NPK & Fertilizer Factor ({nitrogen}N, {phosphorus}P, {potassium}K, {fertilizer} Fert):** `× {nutrient_factor:.3f}`"
    )
    st.write(f"**Pesticide Applied:** `{pesticide} kg/ha`")
    st.write(f"**Total Calculated Yield:** `{predicted_yield:.4f}` tonnes/ha")
