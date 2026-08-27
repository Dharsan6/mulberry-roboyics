import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from datetime import datetime

# Streamlit Page Config
st.set_page_config(
    page_title="Precision Sericulture | Mulberry Rover Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Mode Glassmorphism Aesthetics
st.markdown("""
<style>
    /* Dark glassmorphism theme */
    .main {
        background-color: #0E1117;
        color: #E0E6ED;
        font-family: 'Inter', sans-serif;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    .badge-transit { background-color: #1E3A8A; color: #93C5FD; border: 1px solid #3B82F6; }
    .badge-deployment { background-color: #7C2D12; color: #FDBA74; border: 1px solid #F97316; }
    .badge-interrogation { background-color: #065F46; color: #6EE7B7; border: 1px solid #10B981; }
    .badge-retraction { background-color: #581C87; color: #D8B4FE; border: 1px solid #A855F7; }
    .badge-estop { background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #EF4444; }
    
    .synthetic-banner {
        background: linear-gradient(90deg, #1E1B4B 0%, #311042 100%);
        border: 1px solid #6366F1;
        border-radius: 8px;
        padding: 10px 18px;
        color: #C7D2FE;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    
    .zone-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# API Host
API_HOST = os.getenv("API_HOST", "http://localhost:8000")

# Helper functions
def fetch_api(endpoint: str, default=None):
    try:
        resp = requests.get(f"{API_HOST}{endpoint}", timeout=2.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return default

def post_api(endpoint: str):
    try:
        resp = requests.post(f"{API_HOST}{endpoint}", timeout=2.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

# Sidebar Title & Configuration
st.sidebar.image("https://img.icons8.com/color/96/000000/leaf.png", width=64)
st.sidebar.title("PRECISION SERICULTURE")
st.sidebar.caption("Automated Rack-and-Pinion Soil Probing Rover")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ Rover Control Panel")
col_s1, col_s2 = st.sidebar.columns(2)
if col_s1.button("▶️ Step State", use_container_width=True):
    post_api("/api/simulator/step")
    st.rerun()

if col_s2.button("🔄 Reset Machine", use_container_width=True):
    post_api("/api/simulator/reset")
    st.rerun()

if st.sidebar.button("🚨 EMERGENCY STOP", type="primary", use_container_width=True):
    post_api("/api/simulator/estop")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Agronomic Parameters")
st.sidebar.info("""
**Mulberry Target Profile:**
- **pH**: 6.5 – 7.5
- **EC**: < 1.0 dS/m
- **Nitrogen (N)**: 350 kg/ha
- **Phosphorus (P)**: 140 kg/ha
- **Potassium (K)**: 140 kg/ha
""")

# Top Header Banner
st.markdown("""
<div class="synthetic-banner">
    ⚠️ <strong>DEMONSTRATION MODE / SYNTHETIC DATA:</strong> This dashboard renders simulated telemetry and machine-learning spatial predictions derived from spatial soil sampling algorithms.
</div>
""", unsafe_allow_html=True)

st.title("🌱 Precision Sericulture Soil Intelligence Platform")
st.caption("Autonomous 4WD Rack-and-Pinion Rover • Modbus RS485 Sensing • Spatial ML Nutrient Deficiencies")

# Navigation Tabs
tab_overview, tab_rover, tab_telemetry, tab_map, tab_prescriptions, tab_ml, tab_health = st.tabs([
    "📊 Overview",
    "🤖 Live Rover & Hardware",
    "🧪 Soil Observations",
    "🗺️ Plantation Heatmaps",
    "💊 Agronomic Prescriptions",
    "🧠 ML Model Diagnostics",
    "🖥️ System Health"
])

# --- TAB 1: OVERVIEW ---
with tab_overview:
    summary = fetch_api("/api/plantation/summary", {
        "total_samples": 1000,
        "total_missions": 10,
        "current_rover_state": "INTERROGATION",
        "latest_gps": {"latitude": 11.3921, "longitude": 77.7342},
        "avg_ph": 6.8,
        "avg_ec": 0.72,
        "avg_moisture": 46.5,
        "total_n_deficiency": 14250.0,
        "total_p_deficiency": 4120.0,
        "total_k_deficiency": 3890.0,
        "system_status": "ONLINE"
    })
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Soil Samples", summary["total_samples"], delta="Active Grid")
    col2.metric("Missions Completed", summary["total_missions"], delta="Autonomous")
    col3.metric("Avg Soil pH", f"{summary['avg_ph']} pH", delta="Optimal (6.5-7.5)" if 6.5 <= summary['avg_ph'] <= 7.5 else "Warning")
    col4.metric("Avg Soil EC", f"{summary['avg_ec']} dS/m", delta="Normal (<1.0)")
    col5.metric("Avg Moisture", f"{summary['avg_moisture']}%", delta="Hydrated")

    st.markdown("### 🌾 Total Plantation Nutrient Shortfalls (kg/ha)")
    c_n, c_p, c_k = st.columns(3)
    c_n.metric("Nitrogen (N) Shortfall", f"{summary['total_n_deficiency']} kg/ha", delta="-Shortfall", delta_color="inverse")
    c_p.metric("Phosphorus (P) Shortfall", f"{summary['total_p_deficiency']} kg/ha", delta="-Shortfall", delta_color="inverse")
    c_k.metric("Potassium (K) Shortfall", f"{summary['total_k_deficiency']} kg/ha", delta="-Shortfall", delta_color="inverse")

    st.markdown("---")
    st.markdown("### 📍 Live Plantation Grid Overview")
    samples_data = fetch_api("/api/samples", [])
    if samples_data:
        df_samples = pd.DataFrame(samples_data)
        fig_overview = px.scatter_mapbox(
            df_samples,
            lat="latitude",
            lon="longitude",
            color="ph",
            size="nitrogen",
            hover_name="sample_id",
            hover_data=["ec", "moisture", "nitrogen", "phosphorus", "potassium"],
            color_continuous_scale="Viridis",
            zoom=16,
            height=450
        )
        fig_overview.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_overview, use_container_width=True)
    else:
        st.info("Run `python ml/pipeline.py` or trigger the simulator to load sample points.")

# --- TAB 2: LIVE ROVER & HARDWARE ---
with tab_rover:
    st.subheader("🤖 Autonomous Rover Real-Time State Machine")
    sim_status = fetch_api("/api/simulator/status", {
        "rover_state": "INTERROGATION",
        "mission_id": "M001",
        "current_waypoint": {"lat": 11.3925, "lon": 77.7338, "id": "WP_001"},
        "gps": {"latitude": 11.3925, "longitude": 77.7338, "altitude": 320.0, "fix": "3D_FIX"},
        "hardware": {
            "linear_vel": 0.0,
            "angular_vel": 0.0,
            "actuator_position": "BOTTOM",
            "top_limit": False,
            "bottom_limit": True,
            "estop": False
        },
        "logs": ["WAYPOINT WP_001 REACHED.", "DEPLOYMENT STARTED.", "BOTTOM LIMIT TRIGGERED.", "INTERROGATION STABILIZING..."]
    })

    cur_state = sim_status["rover_state"]
    badge_class = f"badge-{cur_state.lower().replace('_', '')}"
    
    col_st1, col_st2, col_st3 = st.columns([1, 2, 1])
    with col_st1:
        st.markdown(f"#### Current State: <span class='status-badge {badge_class}'>{cur_state}</span>", unsafe_allow_html=True)
        st.markdown(f"**Mission ID:** `{sim_status['mission_id']}`")
        st.markdown(f"**Target Waypoint:** `{sim_status['current_waypoint']['id']}`")
        st.markdown(f"**Coordinates:** {sim_status['gps']['latitude']:.6f}, {sim_status['gps']['longitude']:.6f}")
        st.markdown(f"**GPS Fix:** `{sim_status['gps']['fix']}`")

    with col_st2:
        st.markdown("#### State Sequence Progress")
        states = ["TRANSIT", "DEPLOYMENT", "INTERROGATION", "RETRACTION"]
        cols = st.columns(4)
        for i, s in enumerate(states):
            is_active = (s == cur_state)
            color = "#10B981" if is_active else "#334155"
            cols[i].markdown(f"""
            <div style="background:{color}; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold;">
                Step {i+1}<br>{s}
            </div>
            """, unsafe_allow_html=True)

    with col_st3:
        st.markdown("#### Hardware Limits & Actuator")
        hw = sim_status["hardware"]
        st.write(f"**Rack Position:** `{hw['actuator_position']}`")
        st.write(f"**Bottom Limit Switch (NC):** {'🔴 TRIGGERED' if hw['bottom_limit'] else '🟢 OPEN'}")
        st.write(f"**Top Limit Switch (NC):** {'🔴 TRIGGERED' if hw['top_limit'] else '🟢 OPEN'}")
        st.write(f"**Emergency Stop:** {'🚨 ACTIVE' if hw['estop'] else '🟢 CLEAR'}")

    st.markdown("---")
    st.markdown("#### 📜 Live Rover State Machine Event Logs")
    for log_msg in sim_status.get("logs", []):
        st.code(log_msg)

# --- TAB 3: SOIL OBSERVATIONS ---
with tab_telemetry:
    st.subheader("🧪 Soil Telemetry Readings (ZTS-3002 RS485 Modbus RTU)")
    samples = fetch_api("/api/samples", [])
    if samples:
        df_obs = pd.DataFrame(samples)
        st.dataframe(
            df_obs[["sample_id", "mission_id", "timestamp", "latitude", "longitude", "ph", "ec", "moisture", "nitrogen", "phosphorus", "potassium", "rover_state"]],
            use_container_width=True
        )
        
        st.markdown("### 📈 Soil Parameter Distributions")
        c1, c2 = st.columns(2)
        fig_ph = px.histogram(df_obs, x="ph", nbins=20, title="Soil pH Distribution", color_discrete_sequence=["#10B981"])
        c1.plotly_chart(fig_ph, use_container_width=True)
        
        fig_ec = px.histogram(df_obs, x="ec", nbins=20, title="Soil EC Distribution (dS/m)", color_discrete_sequence=["#3B82F6"])
        c2.plotly_chart(fig_ec, use_container_width=True)
    else:
        st.warning("No soil telemetry found. Run the dataset generator or ML pipeline.")

# --- TAB 4: PLANTATION HEATMAPS ---
with tab_map:
    st.subheader("🗺️ Spatial Interpolation Grid Heatmaps")
    param_select = st.selectbox(
        "Select Parameter Layer to Visualize:",
        ["n_deficiency", "p_deficiency", "k_deficiency", "ph", "ec"],
        format_func=lambda x: {
            "n_deficiency": "Nitrogen (N) Deficiency Shortfall (kg/ha)",
            "p_deficiency": "Phosphorus (P) Deficiency Shortfall (kg/ha)",
            "k_deficiency": "Potassium (K) Deficiency Shortfall (kg/ha)",
            "ph": "Soil pH Levels",
            "ec": "Soil Electrical Conductivity (dS/m)"
        }[x]
    )

    grid_data = fetch_api(f"/api/predictions/{param_select}?model_type=IDW", [])
    if grid_data:
        df_grid = pd.DataFrame(grid_data)
        
        view_state = pdk.ViewState(
            latitude=df_grid["lat"].mean(),
            longitude=df_grid["lon"].mean(),
            zoom=16,
            pitch=45
        )
        
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df_grid,
            get_position=["lon", "lat"],
            get_weight="val",
            radius_pixels=30,
            intensity=1.5,
            threshold=0.05
        )
        
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/dark-v9")
        st.pydeck_chart(r)
    else:
        st.info("Run `python ml/pipeline.py` to generate the 50x50 spatial prediction grid.")

# --- TAB 5: AGRONOMIC PRESCRIPTIONS ---
with tab_prescriptions:
    st.subheader("💊 Zone-by-Zone Agronomic Shortfall & Prescription Matrix")
    prescriptions = fetch_api("/api/prescriptions", [])
    if prescriptions:
        for p in prescriptions:
            prio_color = "#EF4444" if p["priority"] == "HIGH" else ("#F59E0B" if p["priority"] == "MODERATE" else "#10B981")
            st.markdown(f"""
            <div class="zone-card" style="border-left-color: {prio_color};">
                <h4>📍 {p['zone_id']} <span style="background:{prio_color}; color:white; padding:2px 8px; border-radius:4px; font-size:0.8rem;">{p['priority']} PRIORITY</span></h4>
                <p><strong>Coordinates:</strong> {p['center_lat']:.4f}, {p['center_lon']:.4f}</p>
                <p><strong>Nutrient Shortfalls:</strong> N: {p['n_deficiency']} kg/ha | P: {p['p_deficiency']} kg/ha | K: {p['k_deficiency']} kg/ha</p>
                <p><strong>Agronomic Recommendation:</strong> {p['recommendation_note']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Prescription data will be rendered after executing the ML pipeline.")

# --- TAB 6: ML MODEL DIAGNOSTICS ---
with tab_ml:
    st.subheader("🧠 Machine Learning Model Evaluation Diagnostics")
    
    if os.path.exists("models/metrics_summary.json"):
        with open("models/metrics_summary.json", "r") as f:
            metrics_data = json.load(f)
            
        st.markdown("#### Baseline vs. EfficientNet Spatial Model Performance")
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("##### 🌲 Random Forest Baseline Metrics")
            st.json(metrics_data.get("baseline_random_forest", {}))
            
        with col_m2:
            st.markdown("##### ⚡ EfficientNet Spatial Regressor Metrics")
            st.json(metrics_data.get("efficientnet_spatial_regressor", {}))

        # Comparison Bar Chart
        rf_m = metrics_data.get("baseline_random_forest", {})
        eff_m = metrics_data.get("efficientnet_spatial_regressor", {})
        
        targets = ["N", "P", "K"]
        rf_mae = [rf_m.get("N_MAE", 0), rf_m.get("P_MAE", 0), rf_m.get("K_MAE", 0)]
        eff_mae = [eff_m.get("N_MAE", 0), eff_m.get("P_MAE", 0), eff_m.get("K_MAE", 0)]

        fig_comp = go.Figure(data=[
            go.Bar(name='Random Forest Baseline MAE', x=targets, y=rf_mae, marker_color='#3B82F6'),
            go.Bar(name='EfficientNet Spatial MAE', x=targets, y=eff_mae, marker_color='#10B981')
        ])
        fig_comp.update_layout(title="Nutrient Shortfall Mean Absolute Error (MAE - Lower is Better)", barmode='group', template="plotly_dark")
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("No ML metrics found. Execute `python ml/pipeline.py` to train baseline and EfficientNet models.")

# --- TAB 7: SYSTEM HEALTH ---
with tab_health:
    st.subheader("🖥️ Distributed IoT & System Health Dashboard")
    health = fetch_api("/health", {"status": "UNKNOWN"})
    
    c_h1, c_h2, c_h3, c_h4, c_h5 = st.columns(5)
    c_h1.metric("ESP32 micro-ROS Agent", "ONLINE", delta="192.168.1.150")
    c_h2.metric("ROS 2 Humble Node", "ONLINE", delta="Domain 42")
    c_h3.metric("FastAPI Backend", health.get("status", "ONLINE").upper(), delta=":8000")
    c_h4.metric("SQLite Database", "CONNECTED", delta="precision_sericulture.db")
    c_h5.metric("ML Engine", "ACTIVE", delta="PyTorch / Scikit-Learn")

    st.markdown("---")
    st.markdown("#### Hardware Pinout Configuration (ESP32)")
    st.code("""
Locomotion Motors (L298N 4WD Skid-Steer):
  - ENA = Pin 33 | IN1 = Pin 25 | IN2 = Pin 26
  - ENB = Pin 32 | IN3 = Pin 27 | IN4 = Pin 14

Rack-and-Pinion Linear Actuator (L293D N20 Gear Motor):
  - ACT_IN1 = Pin 22 | ACT_IN2 = Pin 21

Safety Boundary Limit Switches (Normally Closed NC):
  - Bottom Limit Switch = Pin 18 (Active Low)
  - Top Limit Switch    = Pin 19 (Active Low)

RS485 Modbus RTU MAX485 Transceiver:
  - TX = Pin 17 | RX = Pin 16 | RO/DI Hardware UART
    """, language="text")
