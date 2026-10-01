import streamlit as st
import json
import os

st.set_page_config(page_title="Crop Yield Predictor", page_icon="🌾", layout="centered")

st.title("🌾 Crop Yield Prediction Dashboard")
st.write("Adjust environmental factors using the sidebar controls to predict crop yield in real-time.")

# Load JSON directly without caching to prevent stale data issues
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

# Compute regression formula directly from JSON list order & key matching
intercept = 0.0
w_temp = 0.0
w_rain = 0.0
w_moist = 0.0

unmapped_weights = []

for key, weight in model.items():
    clean_k = key.lower()
    
    # Intercept check
    if 'intercept' in clean_k:
        intercept = float(weight)
    elif 'temp' in clean_k or clean_k == 'x1' or clean_k == 'var1':
        w_temp = float(weight)
    elif 'rain' in clean_k or 'precip' in clean_k or clean_k == 'x2' or clean_k == 'var2':
        w_rain = float(weight)
    elif 'soil' in clean_k or 'moist' in clean_k or clean_k == 'x3' or clean_k == 'var3':
        w_moist = float(weight)
    else:
        unmapped_weights.append(float(weight))

# Fallback by positional order if MATLAB exported generic names
if w_temp == 0.0 and len(unmapped_weights) > 0:
    w_temp = unmapped_weights.pop(0)
if w_rain == 0.0 and len(unmapped_weights) > 0:
    w_rain = unmapped_weights.pop(0)
if w_moist == 0.0 and len(unmapped_weights) > 0:
    w_moist = unmapped_weights.pop(0)

# Exact mathematical sum
predicted_yield = intercept + (w_temp * temp) + (w_rain * rainfall) + (w_moist * moisture)

# Display Output
st.markdown("---")
st.subheader("Predicted Harvest Output")

formatted_yield = max(0.0, predicted_yield)
st.metric(label="Estimated Crop Yield", value=f"{formatted_yield:.2f} tonnes/ha")

# Progress indicator
normalized_progress = min(1.0, max(0.0, formatted_yield / 15.0))
st.progress(normalized_progress)

# Debug Expander
with st.expander("🔍 Inspect Active Regression Formula"):
    st.write(f"**Intercept:** `{intercept:.4f}`")
    st.write(f"**Temp Weight:** `{w_temp:.4f}` × {temp}°C = `{w_temp * temp:.2f}`")
    st.write(f"**Rainfall Weight:** `{w_rain:.4f}` × {rainfall}mm = `{w_rain * rainfall:.2f}`")
    st.write(f"**Moisture Weight:** `{w_moist:.4f}` × {moisture}% = `{w_moist * moisture:.2f}`")
    st.write(f"**Total Yield:** `{predicted_yield:.4f}` tonnes/ha")
    st.json(model)
