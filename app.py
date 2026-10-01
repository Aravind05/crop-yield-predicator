import json
import os
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Crop Yield Predictor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom CSS for Sleek Dark Theme UI
st.markdown(
    """
    <style>
    /* Dark Theme Styles */
    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
    }
    
    /* Output Header Card */
    .output-container {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    .output-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    
    .output-value {
        font-size: 3rem;
        font-weight: 800;
        color: #38BDF8;
        margin-bottom: 0px;
    }
    
    .sub-text {
        font-size: 0.9rem;
        color: #64748B;
    }

    /* Parameter Table Custom Styling */
    .stTable {
        background-color: #161B22 !important;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Controls (Sequential Single Column)
# ---------------------------------------------------------
st.sidebar.title("🌱 Input Parameters")
st.sidebar.caption("Adjust parameters to compute expected crop output.")

# Crop Selection
crop_type = st.sidebar.selectbox(
    "Target Crop",
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

st.sidebar.markdown("---")
st.sidebar.subheader("🌡️ Environmental Conditions")
temperature = st.sidebar.slider("Temperature (°C)", 10.0, 50.0, 17.0, step=0.5)
rainfall = st.sidebar.slider("Rainfall (mm)", 100.0, 1000.0, 950.0, step=10.0)
soil_moisture = st.sidebar.slider(
    "Soil Moisture (%)", 10.0, 90.0, 16.0, step=1.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🧪 Soil Health & Nutrients")
soil_ph = st.sidebar.slider("Soil pH Level", 4.0, 9.0, 7.0, step=0.1)
nitrogen = st.sidebar.number_input(
    "Soil Nitrogen (N - kg/ha)", 0.0, 300.0, 120.0, step=5.0
)
phosphorus = st.sidebar.number_input(
    "Soil Phosphorus (P - kg/ha)", 0.0, 150.0, 40.0, step=2.0
)
potassium = st.sidebar.number_input(
    "Soil Potassium (K - kg/ha)", 0.0, 200.0, 50.0, step=2.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🚜 Agricultural Management")
fertilizer = st.sidebar.number_input(
    "Fertilizer Usage (kg/ha)", 0.0, 500.0, 150.0, step=10.0
)
pesticide = st.sidebar.number_input(
    "Pesticide Usage (kg/ha)", 0.0, 20.0, 2.5, step=0.5
)


# ---------------------------------------------------------
# Mathematical Calculation
# ---------------------------------------------------------
def load_coefficients():
    json_path = "model_coefficients.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    else:
        return {
            "Intercept": 0,
            "Temp": -0.12980241492864633,
            "Rainfall": 0.015751920965971358,
            "Moisture": -0.054637760702525486,
        }


coeffs = load_coefficients()

# Contributions
c_intercept = coeffs.get("Intercept", 0)
c_temp = coeffs.get("Temp", -0.1298) * temperature
c_rain = coeffs.get("Rainfall", 0.01575) * rainfall
c_moist = coeffs.get("Moisture", -0.0546) * soil_moisture

base_yield = c_intercept + c_temp + c_rain + c_moist

# Agronomic scaling multipliers
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
ph_factor = 1.0 if 6.0 <= soil_ph <= 7.5 else 0.85
npk_total = nitrogen + phosphorus + potassium
nutrient_factor = 0.9 + (npk_total / 1000.0) + (fertilizer / 2000.0)

final_yield = max(
    0.0,
    base_yield * crop_factors.get(crop_type, 1.0) * ph_factor * nutrient_factor,
)


# ---------------------------------------------------------
# Main Interface Display
# ---------------------------------------------------------
st.write("## Predicted Harvest Output")

st.markdown(
    f"""
    <div class="output-container">
        <div class="output-title">Estimated Crop Yield ({crop_type})</div>
        <div class="output-value">{final_yield:.2f} <span style="font-size: 1.5rem; color: #94A3B8;">tonnes/ha</span></div>
    </div>
""",
    unsafe_allow_html=True,
)

# Expandable Inspection View (Matching Second Screenshot)
with st.expander("🔍 Inspect Action Regression Formula & Calculations"):
    st.markdown("#### **Parameter Step Contributions:**")
    st.write(f"• **Intercept:** `{c_intercept:.4f}`")
    st.write(
        f"• **Temp Contribution:** `{coeffs.get('Temp', -0.1298):.4f}` × `{temperature}°C` = **`{c_temp:.2f}`**"
    )
    st.write(
        f"• **Rainfall Contribution:** `{coeffs.get('Rainfall', 0.01575):.4f}` × `{rainfall}mm` = **`{c_rain:.2f}`**"
    )
    st.write(
        f"• **Moisture Contribution:** `{coeffs.get('Moisture', -0.0546):.4f}` × `{soil_moisture}%` = **`{c_moist:.2f}`**"
    )
    st.write(f"• **Crop Scaling Factor ({crop_type}):** `× {crop_factors.get(crop_type, 1.0)}`")
    st.write(f"• **Soil pH Health Factor:** `× {ph_factor}`")
    st.write(f"• **Nutrient/Fertilizer Factor:** `× {nutrient_factor:.3f}`")
    st.markdown("---")
    st.markdown(
        f"### **Total Calculated Yield:** <span style='color:#38BDF8;'>**{final_yield:.2f} tonnes/ha**</span>",
        unsafe_allow_html=True,
    )

st.write("")
st.write("### 📋 Complete Parameter Summary")

# Single Table containing all input values and final yield at the bottom
summary_table = {
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
        "TOTAL PREDICTED CROP YIELD",
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
        f"{final_yield:.2f} tonnes/ha",
    ],
}

st.table(summary_table)
