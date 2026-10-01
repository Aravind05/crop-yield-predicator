import json
import os
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Crop Yield Predictor Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Custom CSS for Modern & Clean UI
st.markdown(
    """
    <style>
    /* Main Header Styling */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 25px;
    }
    
    /* Result Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    /* Info Card Styling */
    .info-card {
        background-color: #F3F4F6;
        border-left: 5px solid #3B82F6;
        padding: 18px;
        border-radius: 8px;
    }
    
    /* Table Highlights */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Controls (Organized into Accordions)
# ---------------------------------------------------------
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.write("Customize parameters to analyze crop output.")

# Accordion 1: Crop Selection
with st.sidebar.expander("🌱 Crop Selection", expanded=True):
    crop_type = st.selectbox(
        "Target Crop",
        [
            "Pulses",
            "Rice",
            "Wheat",
            "Maize",
            "Cotton",
            "Sugarcane",
            "Groundnut",
            "Soybean",
        ],
        help="Select the crop type to adjust yield factors.",
    )

# Accordion 2: Environmental Conditions (MATLAB Variables)
with st.sidebar.expander("🌡️ Climate & Weather", expanded=True):
    temperature = st.slider(
        "Temperature (°C)",
        10.0,
        50.0,
        17.0,
        step=0.5,
        help="Average seasonal ambient temperature.",
    )
    rainfall = st.slider(
        "Rainfall (mm)",
        100.0,
        1000.0,
        950.0,
        step=10.0,
        help="Total accumulated seasonal precipitation.",
    )
    soil_moisture = st.slider(
        "Soil Moisture (%)",
        10.0,
        90.0,
        16.0,
        step=1.0,
        help="Volumetric root-zone moisture percentage.",
    )

# Accordion 3: Soil Chemistry & Nutrients
with st.sidebar.expander("🧪 Soil Health & Nutrients", expanded=False):
    soil_ph = st.slider(
        "Soil pH Level",
        4.0,
        9.0,
        7.0,
        step=0.1,
        help="Soil acidity/alkalinity scale.",
    )
    nitrogen = st.number_input(
        "Nitrogen (N) - kg/ha", 0.0, 300.0, 120.0, step=5.0
    )
    phosphorus = st.number_input(
        "Phosphorus (P) - kg/ha", 0.0, 150.0, 40.0, step=2.0
    )
    potassium = st.number_input(
        "Potassium (K) - kg/ha", 0.0, 200.0, 50.0, step=2.0
    )

# Accordion 4: Farm Inputs
with st.sidebar.expander("🚜 Agricultural Management", expanded=False):
    fertilizer = st.number_input(
        "Fertilizer Usage - kg/ha", 0.0, 500.0, 150.0, step=10.0
    )
    pesticide = st.number_input(
        "Pesticide Usage - kg/ha", 0.0, 20.0, 2.5, step=0.5
    )


# ---------------------------------------------------------
# Calculation Engine
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

# MATLAB Base Linear Regression
base_yield = (
    coeffs.get("Intercept", 0)
    + (coeffs.get("Temp", 0) * temperature)
    + (coeffs.get("Rainfall", 0) * rainfall)
    + (coeffs.get("Moisture", 0) * soil_moisture)
)

# Extended Agronomic Scaling Multipliers
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
# Main Page Content
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🌾 Crop Yield Prediction Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Real-time agricultural yield forecasting using machine learning regression models.</div>',
    unsafe_allow_html=True,
)

# Top Output Hero Cards
col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Estimated Output ({crop_type})</div>
            <div class="metric-value">{final_yield:.2f} <span style="font-size:1.2rem;">tonnes/ha</span></div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="info-card">
            <h4 style="margin-top:0; color:#1E3A8A;">📌 Current Overview</h4>
            <p style="margin-bottom:6px;"><strong>Selected Crop:</strong> <span style="color:#059669; font-weight:600;">{crop_type}</span></p>
            <p style="margin-bottom:6px;"><strong>Climate Profile:</strong> {temperature}°C Temp | {rainfall} mm Rainfall | {soil_moisture}% Moisture</p>
            <p style="margin-bottom:0;"><strong>Soil & Nutrients:</strong> pH {soil_ph} | NPK Total: {npk_total:.0f} kg/ha | Fertilizer: {fertilizer} kg/ha</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")
st.write("")

# Detailed Views in Tabs
tab1, tab2, tab3 = st.tabs(
    [
        "📋 Complete Input Summary",
        "📐 MATLAB Model Analysis",
        "💡 Quick Recommendations",
    ]
)

with tab1:
    st.write("### Complete Parameter Summary & Final Yield")

    summary_data = {
        "Category": [
            "Crop Profile",
            "Weather / Climate",
            "Weather / Climate",
            "Weather / Climate",
            "Soil Health",
            "Soil Nutrients",
            "Soil Nutrients",
            "Soil Nutrients",
            "Farm Management",
            "Farm Management",
            "🎯 FINAL RESULT",
        ],
        "Parameter Name": [
            "Target Crop Type",
            "Temperature",
            "Rainfall",
            "Soil Moisture",
            "Soil pH",
            "Nitrogen (N)",
            "Phosphorus (P)",
            "Potassium (K)",
            "Fertilizer Applied",
            "Pesticide Applied",
            "PREDICTED CROP YIELD",
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

    st.table(summary_data)

with tab2:
    st.write("### Underlying Mathematics")
    st.info(
        "The baseline calculation uses linear regression parameters trained in MATLAB and exported via JSON."
    )

    st.markdown(
        r"""
    $$Y = \beta_0 + (\beta_1 \cdot \text{Temp}) + (\beta_2 \cdot \text{Rainfall}) + (\beta_3 \cdot \text{Moisture})$$
    """
    )

    st.code(
        f"Yield = ({temperature} * -0.1298) + ({rainfall} * 0.01575) + ({soil_moisture} * -0.0546) = {base_yield:.2f} tonnes/ha (Base Yield)"
    )

    st.write("**Model Coefficients (`model_coefficients.json`):**")
    st.json(coeffs)

with tab3:
    st.write("### Agricultural Insights")
    if 6.0 <= soil_ph <= 7.5:
        st.success(
            "✅ **Soil pH is Optimal:** Your soil pH is in the ideal neutral range (6.0–7.5) for optimal nutrient absorption."
        )
    else:
        st.warning(
            "⚠️ **Soil pH Alert:** Soil pH is outside the ideal range (6.0–7.5). Consider applying lime (if acidic) or gypsum (if alkaline)."
        )

    if rainfall < 300:
        st.info(
            "💧 **Water Stress Warning:** Rainfall is low. Supplemental irrigation is strongly recommended."
        )
    elif rainfall > 800:
        st.info(
            "🌧️ **High Moisture:** Sufficient rainfall detected. Ensure proper field drainage to prevent waterlogging."
        )
