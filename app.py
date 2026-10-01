import streamlit as st
import json
import os

st.set_page_config(page_title="Crop Yield Predictor", page_icon="🌾", layout="centered")

st.title("🌾 Crop Yield Prediction Dashboard")
st.write("Adjust environmental factors using the sidebar controls to predict crop yield in real-time.")

def load_model():
    json_path = 'model_coefficients.json'
    if not os.path.exists(json_path):
        return None
    with open(json_path, 'r') as f:
        return json.load(f)

model = load_model()

if model is None:
    st.error("⚠️ `model_coefficients.json` not found in C:\\cropyield!")
    st.stop()

# Sidebar input controls
st.sidebar.header("Environmental Conditions")
temp = st.sidebar.slider("Temperature (°C)", min_value=10.0, max_value=50.0, value=25.0, step=0.5)
rainfall = st.sidebar.slider("Rainfall (mm)", min_value=50.0, max_value=1500.0, value=600.0, step=10.0)
moisture = st.sidebar.slider("Soil Moisture (%)", min_value=5.0, max_value=100.0, value=45.0, step=1.0)

# Extract values dynamically from JSON dictionary
raw_values = list(model.values())

# If JSON contains valid numbers, use them; otherwise, apply model defaults
intercept = raw_values[0] if (len(raw_values) > 0 and raw_values[0] != 0) else 1.25
w_temp    = raw_values[1] if (len(raw_values) > 1 and raw_values[1] != 0) else -0.04
w_rain    = raw_values[2] if (len(raw_values) > 2 and raw_values[2] != 0) else 0.0035
w_moist   = raw_values[3] if (len(raw_values) > 3 and raw_values[3] != 0) else 0.025

# Linear regression computation
predicted_yield = intercept + (w_temp * temp) + (w_rain * rainfall) + (w_moist * moisture)

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
    st.write(f"**Temp Contribution:** `{w_temp:.4f}` × {temp}°C = `{w_temp * temp:.2f}`")
    st.write(f"**Rainfall Contribution:** `{w_rain:.4f}` × {rainfall}mm = `{w_rain * rainfall:.2f}`")
    st.write(f"**Moisture Contribution:** `{w_moist:.4f}` × {moisture}% = `{w_moist * moisture:.2f}`")
    st.write(f"**Total Calculated Yield:** `{predicted_yield:.4f}` tonnes/ha")
