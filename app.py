import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib

# 1. Page Configuration and Styling
st.set_page_config(page_title="Metformin Tablet Optimization Platform", layout="centered")
st.title("💊 Metformin HCl Tablet Optimization Platform")
st.markdown("### Quality by Design (QbD) Multi-Output Neural Network App")
st.write("Adjust the functional ingredient mass parameters using the sliders below to dynamically check core tablet attributes.")

# 2. Loading the Model Assets Cache
@st.cache_resource
def load_assets():
    model = tf.keras.models.load_model("ANN_Formulation_Model.keras")
    scaler_X = joblib.load("scaler_X.pkl")
    scaler_y = joblib.load("scaler_Y.pkl")
    return model, scaler_X, scaler_y

try:
    model, scaler_X, scaler_y = load_assets()
except Exception as e:
    st.error(f"Error loading model assets. Please check file names. Details: {e}")
    st.stop()

# 3. Setting Up Slide Interface Bars
st.sidebar.header("Formulation Excipients (mg)")
mcc = st.sidebar.slider("MCC (Filler / Binder Amount)", 60, 120, 90)
lactose = st.sidebar.slider("Lactose Monohydrate (Diluent Amount)", 0, 120, 60)
starch = st.sidebar.slider("Maize Starch (Disintegrant Base)", 0, 180, 30)
pvp = st.sidebar.slider("PVP K30 (Synthetic Binder)", 0, 50, 15)
hpmc = st.sidebar.slider("HPMC E5 (Matrix Polymer)", 0, 40, 10)
am_gum = st.sidebar.slider("Acacia Gum Powder (Natural Binder)", 0, 80, 10)
croscarmellose = st.sidebar.slider("Croscarmellose Sodium (Superdisintegrant)", 5, 40, 20)
mag_stearate = st.sidebar.slider("Magnesium Stearate (Lubricant)", 3, 8, 5)
talc = st.sidebar.slider("Talc & Aerosil (Glidant Mixture)", 3, 8, 5)

# Calculate dynamic core formulation total mass
metformin_base = 500.0
total_weight = metformin_base + mcc + lactose + starch + pvp + hpmc + am_gum + croscarmellose + mag_stearate + talc

# 4. Processing Calculations Through the Model
input_df = pd.DataFrame({
    'Metformin_HCl_mg': [metformin_base], 'MCC_mg': [mcc], 'Lactose_mg': [lactose],
    'Starch_mg': [starch], 'PVP_K30_mg': [pvp], 'HPMC_E5_mg': [hpmc],
    'AM_Gum_mg': [am_gum], 'Croscarmellose_Na_mg': [croscarmellose],
    'Magnesium_Stearate_mg': [mag_stearate], 'Talc_Aerosil_mg': [talc],
    'Total_Tablet_Weight_mg': [total_weight]
})

scaled_inputs = scaler_X.transform(input_df)
scaled_predictions = model.predict(scaled_inputs)
predictions = scaler_y.inverse_transform(scaled_predictions)

# Bound checking continuous mathematical predictions with standard caps
hardness = max(0.0, float(predictions[0][0]))
friability = min(1.0, max(0.0, float(predictions[0][1])))
disintegration = max(0.0, float(predictions[0][2]))
dissolution = min(100.0, max(0.0, float(predictions[0][3])))

# 5. Rendering Dynamic UI Output Display Cards
st.subheader("📋 Predicted Critical Quality Attributes (CQAs)")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Total Tablet Weight", value=f"{total_weight:.1f} mg")
    st.metric(label="Mechanical Hardness", value=f"{hardness:.2f} kg/cm²")
    st.metric(label="Surface Friability", value=f"{friability:.3f} %")

with col2:
    st.metric(label="Matrix Disintegration Time", value=f"{disintegration:.2f} min")
    st.metric(label="Drug Dissolution Rate (t=45 min)", value=f"{dissolution:.2f} %")

st.info("This interface runs your multi-output artificial neural network live to calculate pharmacopeial targets simultaneously.")

