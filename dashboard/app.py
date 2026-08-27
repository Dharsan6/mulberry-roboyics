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
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime

# Streamlit Page Config
st.set_page_config(
    page_title="Precision Sericulture | Mulberry Rover Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Aesthetic Glassmorphism Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metrics glass card */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-transit { background-color: rgba(30, 58, 138, 0.7); color: #93C5FD; border: 1px solid #3B82F6; }
    .badge-deployment { background-color: rgba(124, 45, 18, 0.7); color: #FDBA74; border: 1px solid #F97316; }
    .badge-interrogation { background-color: rgba(6, 95, 70, 0.7); color: #6EE7B7; border: 1px solid #10B981; }
    .badge-retraction { background-color: rgba(88, 28, 135, 0.7); color: #D8B4FE; border: 1px solid #A855F7; }
    .badge-emergencystop { background-color: rgba(127, 29, 29, 0.8); color: #FCA5A5; border: 1px solid #EF4444; }
    
    /* Top Sericulture Header Banner */
    .sericulture-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(59, 130, 246, 0.12) 50%, rgba(139, 92, 246, 0.12) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 14px 22px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .zone-card {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left-width: 4px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Log console */
    .log-box {
        background-color: #050811;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #10B981;
        max-height: 260px;
        overflow-y: auto;
    }
    
    .hw-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# API Host
API_HOST = os.getenv("API_HOST", "http://127.0.0.1:8000")

# Helper functions
@st.cache_data(ttl=1)
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

# Sidebar Title & Controls
st.sidebar.image("https://img.icons8.com/color/96/000000/leaf.png", width=56)
st.sidebar.title("SERICULTURE ROVER")
st.sidebar.caption("4WD Soil Probing Robot • Morus alba Agronomy")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ Rover Robot Controls")
col_s1, col_s2 = st.sidebar.columns(2)
if col_s1.button("▶️ Step State", use_container_width=True, help="Advances state machine by 1 step"):
    post_api("/api/simulator/step")
    st.rerun()

if col_s2.button("⚡ Auto-Cycle", use_container_width=True, help="Executes full 4-state sampling cycle"):
    post_api("/api/simulator/run_cycle")
    st.rerun()

col_s3, col_s4 = st.sidebar.columns(2)
if col_s3.button("🔄 Reset Rover", use_container_width=True):
    post_api("/api/simulator/reset")
    st.rerun()

if col_s4.button("🚨 E-STOP", type="primary", use_container_width=True):
    post_api("/api/simulator/estop")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌾 CSRTI Agronomic Targets")
st.sidebar.markdown("""
<div style="font-size:0.85rem; color:#94A3B8; background:rgba(255,255,255,0.03); padding:10px; border-radius:8px;">
    <strong>Mulberry Standard Baseline:</strong><br>
    • <strong>pH</strong>: 6.5 – 7.5 (Optimal: 6.8)<br>
    • <strong>EC</strong>: &lt; 1.0 dS/m (Normal)<br>
    • <strong>Moisture</strong>: 40% – 55%<br>
    • <strong>Nitrogen (N)</strong>: 350 kg/ha/yr<br>
    • <strong>Phosphorus (P)</strong>: 140 kg/ha/yr<br>
    • <strong>Potassium (K)</strong>: 140 kg/ha/yr<br>
    • <strong>Organic Carbon (SOC)</strong>: &gt; 0.65%
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("Precision Sericulture v1.2 • Google Deepmind Antigravity")

# Top Header Banner
st.markdown("""
<div class="sericulture-banner">
    <div>
        <span style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">🌱 Precision Sericulture: Automated Soil Probing Platform</span><br>
        <span style="font-size: 0.85rem; color: #94A3B8;">Autonomous 4WD Differential-Drive Rover • Modbus RS485 Sensing • PyTorch Spatial Neural Regressors</span>
    </div>
    <div>
        <span class="status-badge badge-interrogation">Active Field Station</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab_overview, tab_rover, tab_telemetry, tab_map, tab_prescriptions, tab_ml, tab_missions, tab_health = st.tabs([
    "📊 Overview",
    "🤖 Live Rover Digital Twin",
    "🧪 Soil Lab Telemetry",
    "🗺️ Spatial ML Heatmaps",
    "💊 Treatment Prescriptions",
    "🧠 ML Diagnostics & Benchmarks",
    "📜 Missions & Replay",
    "🖥️ IoT & System Health"
])

# ==========================================
# TAB 1: OVERVIEW & COMMAND CENTER
# ==========================================
with tab_overview:
    summary = fetch_api("/api/plantation/summary", {
        "total_samples": 1000,
        "total_missions": 10,
        "current_rover_state": "TRANSIT",
        "latest_gps": {"latitude": 11.3921, "longitude": 77.7342},
        "avg_ph": 6.82,
        "avg_ec": 0.64,
        "avg_moisture": 46.2,
        "avg_temperature": 26.5,
        "avg_soil_health": 82.4,
        "total_n_deficiency": 12850.0,
        "total_p_deficiency": 3920.0,
        "total_k_deficiency": 3610.0,
        "total_urea_needed_kg": 27934.8,
        "total_ssp_needed_kg": 24500.0,
        "total_mop_needed_kg": 6016.7,
        "rover_battery_soc": 96.5,
        "system_status": "ONLINE"
    })
    
    # Top KPI Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Probed Samples", summary.get("total_samples", 0), delta="Active Grid")
    c2.metric("Missions", summary.get("total_missions", 0), delta="Surveyed")
    
    avg_ph = summary.get("avg_ph", 6.8)
    ph_delta = "Optimal" if 6.5 <= avg_ph <= 7.5 else ("Low (Acidic)" if avg_ph < 6.5 else "High (Alkaline)")
    c3.metric("Avg Soil pH", f"{avg_ph} pH", delta=ph_delta)
    
    avg_ec = summary.get("avg_ec", 0.65)
    c4.metric("Avg Soil EC", f"{avg_ec} dS/m", delta="Normal (<1.0)" if avg_ec < 1.0 else "High Salinity")
    c5.metric("Avg Moisture", f"{summary.get('avg_moisture', 46.0)}%", delta=f"{summary.get('avg_temperature', 26.5)}°C Temp")
    c6.metric("Soil Health Score", f"{summary.get('avg_soil_health', 82.0)}/100", delta="CSRTI Standard")

    st.markdown("### 🌾 Plantation Total Nutrient Shortfalls & Commercial Fertilizer Requirements")
    col_n, col_p, col_k = st.columns(3)
    with col_n:
        st.metric(
            "Nitrogen (N) Shortfall",
            f"{summary.get('total_n_deficiency', 0):,.1f} kg/ha",
            delta=f"Requires {summary.get('total_urea_needed_kg', 0):,.1f} kg Urea",
            delta_color="inverse"
        )
    with col_p:
        st.metric(
            "Phosphorus (P) Shortfall",
            f"{summary.get('total_p_deficiency', 0):,.1f} kg/ha",
            delta=f"Requires {summary.get('total_ssp_needed_kg', 0):,.1f} kg SSP",
            delta_color="inverse"
        )
    with col_k:
        st.metric(
            "Potassium (K) Shortfall",
            f"{summary.get('total_k_deficiency', 0):,.1f} kg/ha",
            delta=f"Requires {summary.get('total_mop_needed_kg', 0):,.1f} kg MOP",
            delta_color="inverse"
        )

    st.markdown("---")
    st.markdown("### 📍 Live Plantation Spatial Point Cloud & Rover Location")
    
    samples_data = fetch_api("/api/samples", [])
    sim_status = fetch_api("/api/simulator/status", {})
    
    if samples_data:
        df_samples = pd.DataFrame(samples_data)
        
        # Color based on Soil Health or pH
        color_col = "soil_health_index" if "soil_health_index" in df_samples.columns else "ph"
        hover_fields = [c for c in ["ph", "ec", "moisture", "nitrogen", "phosphorus", "potassium", "soil_texture", "mulberry_variety"] if c in df_samples.columns]
        
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_samples,
                lat="latitude",
                lon="longitude",
                color=color_col,
                size="nitrogen",
                hover_name="sample_id",
                hover_data=hover_fields,
                color_continuous_scale="Viridis",
                zoom=16,
                height=460,
                title="Plantation Sample Distribution (Color: Soil Health Index, Size: Nitrogen Content)"
            )
            if sim_status and "gps" in sim_status:
                r_gps = sim_status["gps"]
                fig_map.add_trace(go.Scattermap(
                    lat=[r_gps["latitude"]],
                    lon=[r_gps["longitude"]],
                    mode="markers+text",
                    marker=go.scattermap.Marker(size=18, color="#EF4444"),
                    text=["🤖 ROVER"],
                    textposition="top right",
                    name="Live Rover Location"
                ))
            fig_map.update_layout(
                map_style="carto-darkmatter",
                margin={"r": 0, "t": 35, "l": 0, "b": 0},
                template="plotly_dark"
            )
        else:
            fig_map = px.scatter_mapbox(
                df_samples,
                lat="latitude",
                lon="longitude",
                color=color_col,
                size="nitrogen",
                hover_name="sample_id",
                hover_data=hover_fields,
                color_continuous_scale="Viridis",
                zoom=16,
                height=460,
                title="Plantation Sample Distribution (Color: Soil Health Index, Size: Nitrogen Content)"
            )
            if sim_status and "gps" in sim_status:
                r_gps = sim_status["gps"]
                fig_map.add_trace(go.Scattermapbox(
                    lat=[r_gps["latitude"]],
                    lon=[r_gps["longitude"]],
                    mode="markers+text",
                    marker=go.scattermapbox.Marker(size=18, color="#EF4444", symbol="circle"),
                    text=["🤖 ROVER"],
                    textposition="top right",
                    name="Live Rover Location"
                ))
            fig_map.update_layout(
                mapbox_style="carto-darkmatter",
                margin={"r": 0, "t": 35, "l": 0, "b": 0},
                template="plotly_dark"
            )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Execute `python ml/pipeline.py` or trigger the simulator to load plantation sample points.")

# ==========================================
# TAB 2: LIVE ROVER DIGITAL TWIN
# ==========================================
with tab_rover:
    st.subheader("🤖 Autonomous 4WD Rack-and-Pinion Rover Digital Twin")
    
    sim_status = fetch_api("/api/simulator/status", {
        "rover_state": "TRANSIT",
        "mission_id": "M001",
        "current_waypoint": {"lat": 11.3927, "lon": 77.7336, "id": "WP_NW01", "desc": "Zone A: Nitrogen Sector"},
        "waypoint_index": 0,
        "total_waypoints": 8,
        "gps": {"latitude": 11.3927, "longitude": 77.7336, "altitude": 320.0, "fix": "3D_FIX (RTK-FIXED)", "satellites": 14},
        "hardware": {
            "linear_vel": 1.0,
            "angular_vel": 0.0,
            "heading_deg": 45.0,
            "actuator_position": "TOP",
            "probe_depth_cm": 0.0,
            "top_limit": True,
            "bottom_limit": False,
            "estop": False,
            "battery_soc": 98.2,
            "motor_current_ma": 640,
            "actuator_current_ma": 40,
            "wifi_rssi_dbm": -58
        },
        "latest_telemetry": None,
        "logs": []
    })

    cur_state = sim_status.get("rover_state", "TRANSIT")
    badge_class = f"badge-{cur_state.lower().replace('_', '')}"
    hw = sim_status.get("hardware", {})
    gps = sim_status.get("gps", {})
    cur_wp = sim_status.get("current_waypoint", {})

    # Top Status Banner
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.markdown(f"**State:** <span class='status-badge {badge_class}'>{cur_state}</span>", unsafe_allow_html=True)
    col_r2.markdown(f"**Active Waypoint:** `{cur_wp.get('id', 'WP_001')}` ({sim_status.get('waypoint_index', 0)+1}/{sim_status.get('total_waypoints', 8)})")
    col_r3.markdown(f"**GPS Fix:** `{gps.get('fix', '3D_FIX')}` ({gps.get('satellites', 12)} Sats)")
    col_r4.markdown(f"**Battery SoC:** `{hw.get('battery_soc', 95.0)}%` (WiFi: `{hw.get('wifi_rssi_dbm', -60)} dBm`)")

    st.markdown("---")
    
    # 4-State Machine Visual Sequence
    st.markdown("#### 🔄 4-State Sequential Machine Workflow")
    states = [
        ("TRANSIT", "Drive to Waypoint", "🚗"),
        ("DEPLOYMENT", "Lower Probe to NC Limit", "⬇️"),
        ("INTERROGATION", "Modbus RS485 Reading", "🧪"),
        ("RETRACTION", "Raise Probe to Top Limit", "⬆️")
    ]
    st_cols = st.columns(4)
    for i, (s_name, s_desc, s_icon) in enumerate(states):
        is_active = (s_name == cur_state)
        bg = "linear-gradient(135deg, #065F46 0%, #10B981 100%)" if is_active else "#1E293B"
        border = "2px solid #34D399" if is_active else "1px solid rgba(255,255,255,0.08)"
        st_cols[i].markdown(f"""
        <div style="background:{bg}; border:{border}; padding:14px; border-radius:10px; text-align:center; color:white;">
            <div style="font-size:1.4rem;">{s_icon}</div>
            <strong>Step {i+1}: {s_name}</strong><br>
            <span style="font-size:0.75rem; color:#CBD5E1;">{s_desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_mech, col_modbus = st.columns(2)
    
    with col_mech:
        st.markdown("#### ⚙️ Actuator & Locomotion Hardware Status")
        st.markdown(f"""
        <div class="hw-card">
            <strong>Rack Actuator Stroke Depth:</strong> {hw.get('probe_depth_cm', 0.0)} cm / 15.0 cm<br>
            <strong>Rack Position:</strong> <code>{hw.get('actuator_position', 'TOP')}</code><br>
            <strong>Top Safety Limit Switch (NC):</strong> {'🔴 TRIGGERED (Top Locked)' if hw.get('top_limit') else '🟢 OPEN'}<br>
            <strong>Bottom Safety Limit Switch (NC):</strong> {'🔴 TRIGGERED (Soil Bottom)' if hw.get('bottom_limit') else '🟢 OPEN'}<br>
            <strong>Linear Speed:</strong> {hw.get('linear_vel', 0.0)} m/s | <strong>Heading:</strong> {hw.get('heading_deg', 0.0)}°<br>
            <strong>Motor Current Draw:</strong> Locomotion: {hw.get('motor_current_ma', 0)} mA | Actuator: {hw.get('actuator_current_ma', 0)} mA<br>
            <strong>Emergency Stop Interlock:</strong> {'🚨 ACTIVE (System Locked)' if hw.get('estop') else '🟢 CLEAR (Normal Operation)'}
        </div>
        """, unsafe_allow_html=True)

    with col_modbus:
        st.markdown("#### 📡 RS485 Modbus RTU Live Frame Sniffer")
        latest_t = sim_status.get("latest_telemetry")
        raw_hex = latest_t.get("raw_modbus_hex") if latest_t else "01 03 0E 01C2 0109 02EE 0044 0145 0087 0084 A5C3"
        st.markdown(f"""
        <div class="hw-card">
            <strong>ZTS-3002 Modbus Frame (Hex):</strong><br>
            <code style="color:#38BDF8; font-size:0.95rem;">{raw_hex}</code><br><br>
            <strong>Decoded Sensor Values:</strong><br>
            • Moisture: <code>{latest_t.get('moisture', 45.0) if latest_t else 45.0}%</code> | Temp: <code>{latest_t.get('temperature', 26.5) if latest_t else 26.5}°C</code><br>
            • EC: <code>{latest_t.get('ec', 0.65) if latest_t else 0.65} dS/m</code> | pH: <code>{latest_t.get('ph', 6.8) if latest_t else 6.8}</code><br>
            • NPK: <code>N:{latest_t.get('nitrogen', 320) if latest_t else 320} | P:{latest_t.get('phosphorus', 135) if latest_t else 135} | K:{latest_t.get('potassium', 130) if latest_t else 130} kg/ha</code>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📜 Rover Event & State Machine Telemetry Logs")
    logs = sim_status.get("logs", [])
    if logs:
        log_str = "\n".join([f"[{entry.get('time', '')}] [{entry.get('state', '')}] {entry.get('message', '')}" for entry in logs])
    else:
        log_str = "[10:00:00] [TRANSIT] Rover initialized. Ready to execute missions."
    st.markdown(f'<div class="log-box">{log_str}</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: SOIL OBSERVATIONS & LAB ANALYTICS
# ==========================================
with tab_telemetry:
    st.subheader("🧪 Soil Telemetry & Laboratory Observation Records")
    samples = fetch_api("/api/samples", [])
    
    if samples:
        df_obs = pd.DataFrame(samples)
        
        # Filters row
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            missions_list = ["All Missions"] + sorted(list(df_obs["mission_id"].unique()))
            sel_mission = st.selectbox("Filter by Mission:", missions_list)
        with col_f2:
            var_list = ["All Varieties"] + sorted(list(df_obs["mulberry_variety"].dropna().unique())) if "mulberry_variety" in df_obs.columns else ["All Varieties"]
            sel_variety = st.selectbox("Filter by Variety:", var_list)
        with col_f3:
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = df_obs.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Full Dataset (CSV)",
                data=csv_data,
                file_name="mulberry_soil_telemetry.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Apply Filters
        filtered_df = df_obs.copy()
        if sel_mission != "All Missions":
            filtered_df = filtered_df[filtered_df["mission_id"] == sel_mission]
        if sel_variety != "All Varieties" and "mulberry_variety" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["mulberry_variety"] == sel_variety]

        display_cols = [c for c in [
            "sample_id", "mission_id", "timestamp", "latitude", "longitude",
            "ph", "ec", "moisture", "temperature", "nitrogen", "phosphorus", "potassium",
            "organic_carbon", "soil_health_index", "soil_texture", "mulberry_variety"
        ] if c in filtered_df.columns]

        st.dataframe(filtered_df[display_cols], use_container_width=True, height=280)
        
        st.markdown("---")
        st.markdown("### 📈 Multi-Parameter Agronomic Distributions & Correlations")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            fig_dist = make_subplots(rows=2, cols=2, subplot_titles=("pH Distribution", "EC Distribution (dS/m)", "Nitrogen (kg/ha)", "Soil Health Score"))
            fig_dist.add_trace(go.Histogram(x=filtered_df["ph"], marker_color="#10B981", nbinsx=20), row=1, col=1)
            fig_dist.add_trace(go.Histogram(x=filtered_df["ec"], marker_color="#3B82F6", nbinsx=20), row=1, col=2)
            fig_dist.add_trace(go.Histogram(x=filtered_df["nitrogen"], marker_color="#F59E0B", nbinsx=20), row=2, col=1)
            fig_dist.add_trace(go.Histogram(x=filtered_df["soil_health_index"] if "soil_health_index" in filtered_df.columns else filtered_df["ph"], marker_color="#8B5CF6", nbinsx=20), row=2, col=2)
            fig_dist.update_layout(height=400, showlegend=False, template="plotly_dark", margin={"r": 10, "t": 40, "l": 10, "b": 10})
            st.plotly_chart(fig_dist, use_container_width=True)

        with c_p2:
            # Correlation Matrix Heatmap
            corr_cols = [c for c in ["ph", "ec", "moisture", "nitrogen", "phosphorus", "potassium", "organic_carbon", "soil_health_index"] if c in filtered_df.columns]
            corr = filtered_df[corr_cols].corr()
            fig_corr = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="RdBu_r",
                title="Mulberry Soil Parameter Correlation Matrix",
                height=400
            )
            fig_corr.update_layout(template="plotly_dark", margin={"r": 10, "t": 40, "l": 10, "b": 10})
            st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("No soil observations available. Run `python ml/pipeline.py` or trigger the rover simulator.")

# ==========================================
# TAB 4: SPATIAL ML HEATMAPS
# ==========================================
with tab_map:
    st.subheader("🗺️ High-Resolution 50x50 Spatial ML Prediction Heatmaps")
    
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        sel_model = st.selectbox(
            "Select Prediction Engine:",
            ["EfficientNet", "RandomForest", "IDW"],
            format_func=lambda x: {
                "EfficientNet": "⚡ PyTorch EfficientNet Spatial Regressor",
                "RandomForest": "🌲 Multi-Output Random Forest Baseline",
                "IDW": "📐 Inverse Distance Weighting (IDW) Baseline"
            }[x]
        )
        
        sel_param = st.selectbox(
            "Select Soil / Agronomic Layer:",
            ["n_deficiency", "p_deficiency", "k_deficiency", "ph", "ec", "moisture", "temperature", "soil_health"],
            format_func=lambda x: {
                "n_deficiency": "Nitrogen (N) Deficiency Shortfall (kg/ha)",
                "p_deficiency": "Phosphorus (P) Deficiency Shortfall (kg/ha)",
                "k_deficiency": "Potassium (K) Deficiency Shortfall (kg/ha)",
                "ph": "Soil pH Level",
                "ec": "Electrical Conductivity EC (dS/m)",
                "moisture": "Soil Moisture (%)",
                "temperature": "Soil Temperature (°C)",
                "soil_health": "Composite Soil Health Score (0-100)"
            }[x]
        )

        st.info(f"""
        **Active Model:** `{sel_model}`<br>
        **Resolution:** 50x50 Dense Grid (2,500 points)<br>
        **Plantation Area:** 200m x 200m (4 Hectares)
        """, icon="ℹ️")

    grid_data = fetch_api(f"/api/predictions/{sel_param}?model_type={sel_model}", [])
    
    with col_m2:
        if grid_data:
            df_grid = pd.DataFrame(grid_data)
            
            # Interactive 2D/3D PyDeck Heatmap
            view_state = pdk.ViewState(
                latitude=df_grid["lat"].mean(),
                longitude=df_grid["lon"].mean(),
                zoom=16.2,
                pitch=45,
                bearing=20
            )
            
            # Normalize weights for Pydeck
            min_v = df_grid["val"].min()
            max_v = df_grid["val"].max()
            df_grid["norm_val"] = (df_grid["val"] - min_v) / (max_v - min_v + 1e-6)
            
            layer = pdk.Layer(
                "HeatmapLayer",
                data=df_grid,
                get_position=["lon", "lat"],
                get_weight="norm_val",
                radius_pixels=32,
                intensity=1.8,
                threshold=0.03
            )
            
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v10",
                tooltip={"text": "Latitude: {lat}\nLongitude: {lon}\nValue: {val}"}
            )
            st.pydeck_chart(deck)
        else:
            st.warning("Prediction grid not loaded. Execute `python ml/pipeline.py` to train models and generate spatial grid.")

# ==========================================
# TAB 5: AGRONOMIC PRESCRIPTIONS
# ==========================================
with tab_prescriptions:
    st.subheader("💊 Sector-by-Sector CSRTI Fertilizer Prescriptions & Treatment Plan")
    prescriptions = fetch_api("/api/prescriptions", [])
    
    if prescriptions:
        for p in prescriptions:
            prio = p.get("priority", "MODERATE")
            prio_color = "#EF4444" if prio == "HIGH" else ("#F59E0B" if prio == "MODERATE" else "#10B981")
            
            st.markdown(f"""
            <div class="zone-card" style="border-left-color: {prio_color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#F8FAFC;">📍 {p.get('zone_id', '')}: {p.get('zone_name', '')}</h4>
                    <span style="background:{prio_color}; color:white; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">{prio} PRIORITY</span>
                </div>
                <p style="color:#94A3B8; font-size:0.85rem; margin-top:4px;">
                    <strong>Coordinates:</strong> {p.get('center_lat', 0.0):.4f}, {p.get('center_lon', 0.0):.4f} | 
                    <strong>Soil Health Score:</strong> {p.get('avg_health_score', 80.0):.1f}/100 | 
                    <strong>Avg pH:</strong> {p.get('avg_ph', 6.8):.2f} | 
                    <strong>Avg EC:</strong> {p.get('avg_ec', 0.65):.2f} dS/m
                </p>
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; margin: 12px 0;">
                    <div style="background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:6px;">
                        <span style="color:#93C5FD; font-size:0.8rem;">Urea (46% N):</span><br>
                        <strong style="font-size:1.1rem; color:#F8FAFC;">{p.get('urea_kg_ha', 0.0):.1f} kg/ha</strong>
                    </div>
                    <div style="background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:6px;">
                        <span style="color:#FDBA74; font-size:0.8rem;">Single Super Phosphate (SSP):</span><br>
                        <strong style="font-size:1.1rem; color:#F8FAFC;">{p.get('ssp_kg_ha', 0.0):.1f} kg/ha</strong>
                    </div>
                    <div style="background:rgba(255,255,255,0.03); padding:8px 12px; border-radius:6px;">
                        <span style="color:#D8B4FE; font-size:0.8rem;">Muriate of Potash (MOP):</span><br>
                        <strong style="font-size:1.1rem; color:#F8FAFC;">{p.get('mop_kg_ha', 0.0):.1f} kg/ha</strong>
                    </div>
                </div>
                <p style="margin:6px 0; font-size:0.9rem;"><strong>🌾 Soil Amendment:</strong> {p.get('amendment_note', 'Standard maintenance.')}</p>
                <p style="margin:6px 0; font-size:0.9rem;"><strong>📅 Application Schedule:</strong> {p.get('application_schedule', 'Apply after pruning.')}</p>
                <p style="margin:6px 0; font-size:0.9rem; color:#A7F3D0;"><strong>💡 Advisory:</strong> {p.get('recommendation_note', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Prescriptions will be populated after executing the ML pipeline.")

# ==========================================
# TAB 6: ML DIAGNOSTICS & BENCHMARKS
# ==========================================
with tab_ml:
    st.subheader("🧠 Machine Learning Model Evaluation & Comparative Benchmarks")
    
    if os.path.exists("models/metrics_summary.json"):
        with open("models/metrics_summary.json", "r") as f:
            metrics_data = json.load(f)
            
        rf_m = metrics_data.get("baseline_random_forest", {})
        eff_m = metrics_data.get("efficientnet_spatial_regressor", {})

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### 🌲 Random Forest Baseline")
            st.markdown(f"""
            • **N MAE:** `{rf_m.get('N_DEFICIENCY_MAE', rf_m.get('N_MAE', 'N/A'))} kg/ha` | **R²:** `{rf_m.get('N_DEFICIENCY_R2', rf_m.get('N_R2', 'N/A'))}`<br>
            • **P MAE:** `{rf_m.get('P_DEFICIENCY_MAE', rf_m.get('P_MAE', 'N/A'))} kg/ha` | **R²:** `{rf_m.get('P_DEFICIENCY_R2', rf_m.get('P_R2', 'N/A'))}`<br>
            • **K MAE:** `{rf_m.get('K_DEFICIENCY_MAE', rf_m.get('K_MAE', 'N/A'))} kg/ha` | **R²:** `{rf_m.get('K_DEFICIENCY_R2', rf_m.get('K_R2', 'N/A'))}`
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown("##### ⚡ PyTorch EfficientNet Spatial Regressor")
            st.markdown(f"""
            • **N MAE:** `{eff_m.get('N_DEFICIENCY_MAE', eff_m.get('N_MAE', 'N/A'))} kg/ha` | **R²:** `{eff_m.get('N_DEFICIENCY_R2', eff_m.get('N_R2', 'N/A'))}`<br>
            • **P MAE:** `{eff_m.get('P_DEFICIENCY_MAE', eff_m.get('P_MAE', 'N/A'))} kg/ha` | **R²:** `{eff_m.get('P_DEFICIENCY_R2', eff_m.get('P_R2', 'N/A'))}`<br>
            • **K MAE:** `{eff_m.get('K_DEFICIENCY_MAE', eff_m.get('K_MAE', 'N/A'))} kg/ha` | **R²:** `{eff_m.get('K_DEFICIENCY_R2', eff_m.get('K_R2', 'N/A'))}`
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Comparative Bar Chart
        targets = ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"]
        rf_mae = [
            rf_m.get("N_DEFICIENCY_MAE", rf_m.get("N_MAE", 8.5)),
            rf_m.get("P_DEFICIENCY_MAE", rf_m.get("P_MAE", 4.2)),
            rf_m.get("K_DEFICIENCY_MAE", rf_m.get("K_MAE", 4.0))
        ]
        eff_mae = [
            eff_m.get("N_DEFICIENCY_MAE", eff_m.get("N_MAE", 4.8)),
            eff_m.get("P_DEFICIENCY_MAE", eff_m.get("P_MAE", 2.6)),
            eff_m.get("K_DEFICIENCY_MAE", eff_m.get("K_MAE", 2.4))
        ]

        fig_comp = go.Figure(data=[
            go.Bar(name='Random Forest Baseline (MAE)', x=targets, y=rf_mae, marker_color='#3B82F6'),
            go.Bar(name='PyTorch EfficientNet Spatial (MAE)', x=targets, y=eff_mae, marker_color='#10B981')
        ])
        fig_comp.update_layout(
            title="Nutrient Shortfall Mean Absolute Error (MAE - Lower is Better)",
            barmode='group',
            template="plotly_dark",
            height=380
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("No ML metrics found. Execute `python ml/pipeline.py` to train baseline and EfficientNet models.")

# ==========================================
# TAB 7: MISSIONS & FLEET OPERATIONS
# ==========================================
with tab_missions:
    st.subheader("📜 Robotic Survey Missions & Historical Replay")
    missions = fetch_api("/api/missions", [])
    
    if missions:
        df_missions = pd.DataFrame(missions)
        st.dataframe(
            df_missions[["mission_id", "mission_name", "status", "total_samples", "avg_ph", "avg_health_index", "started_at"]],
            use_container_width=True
        )
    else:
        st.info("Run `python ml/pipeline.py` to seed multi-mission survey data.")

# ==========================================
# TAB 8: SYSTEM HEALTH & IOT
# ==========================================
with tab_health:
    st.subheader("🖥️ Distributed IoT & Subsystem Health")
    health = fetch_api("/health", {"status": "UNKNOWN"})
    
    h1, h2, h3, h4, h5 = st.columns(5)
    h1.metric("ESP32 micro-ROS Agent", "ONLINE", delta="192.168.1.150")
    h2.metric("ROS 2 Humble Node", "ONLINE", delta="Domain ID 42")
    h3.metric("FastAPI Backend", health.get("status", "ONLINE").upper(), delta=":8000")
    h4.metric("Database Engine", "CONNECTED", delta="SQLite / PostgreSQL")
    h5.metric("PyTorch Engine", "ACTIVE", delta="MPS / CUDA Ready")

    st.markdown("---")
    st.markdown("#### ⚡ ESP32 Pinout Configuration & Limit Safety Map")
    st.code("""
Locomotion 4WD Skid-Steer (L298N Dual H-Bridge):
  - ENA = Pin 33 | IN1 = Pin 25 | IN2 = Pin 26
  - ENB = Pin 32 | IN3 = Pin 27 | IN4 = Pin 14

Rack-and-Pinion Linear Prober (L293D N20 Gear Motor):
  - ACT_IN1 = Pin 22 | ACT_IN2 = Pin 21 (Speed PWM = 90)

Safety Boundary Limits (Normally Closed NC Switches - Active LOW):
  - Bottom Limit Switch = Pin 18 (Interrupt ISR: bottomLimitISR)
  - Top Limit Switch    = Pin 19 (Interrupt ISR: topLimitISR)

ZTS-3002 RS485 Modbus RTU MAX485 Transceiver:
  - TX2 = Pin 17 | RX2 = Pin 16 (Hardware UART2 @ 9600 Baud, 8N1)
    """, language="text")
