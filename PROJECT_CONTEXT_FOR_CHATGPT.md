# 🌿 Precision Sericulture: Project Context & Architecture Master Reference
> **Document Purpose**: This file provides comprehensive technical context, hardware pinouts, state machine rules, Modbus register maps, agronomic formulas, REST API specifications, and an exhaustive file-by-file catalog for the **Precision Sericulture** project. It is optimized for sharing directly with ChatGPT or any LLM assistant to ensure full codebase understanding without missing context.

---

## 📋 Quick Setup Prompt for ChatGPT

When starting a conversation in ChatGPT, copy and paste this intro:

```text
You are an expert full-stack AI robotics and agricultural software engineer. I am working on a project titled "Precision Sericulture: Automated Rack-and-Pinion Soil Probing Mechanism on a 4WD Autonomous Rover for Mulberry Agronomy".
I am providing you with the complete project reference document, system architecture, hardware pinouts, state machine logic, agronomic formulas, API schemas, and exhaustive file catalog.
Please read and absorb the entire project architecture and wait for my instructions on what to implement, modify, or debug.
```

---

## 📌 1. Project Overview & Problem Statement

* **Project Title**: Precision Sericulture: Automated Rack-and-Pinion Soil Probing Mechanism on a 4WD Autonomous Rover for Mulberry Agronomy
* **Target Crop**: Mulberry (*Morus alba*), the sole food plant for the domesticated silkworm (*Bombyx mori*).
* **Domain**: Autonomous Agricultural Robotics, Embedded Systems, Spatial Machine Learning & Agronomic Intelligence.
* **Core Problem**: Traditional soil sampling in sericulture plantations is manual, slow, sparse, and lab-delayed. Silkworms require strict leaf protein, moisture, and mineral balances to spin high-grade silk cocoons.
* **Solution**: An autonomous 4WD differential-drive rover equipped with a 3D-printed linear rack-and-pinion actuator. The rover drives between GPS waypoints, lowers an industrial **ZTS-3002 Modbus RS485** multi-parameter soil sensor 15 cm into the ground, measures **pH, EC, Moisture, Temperature, N, P, K**, retracts safely via limit switches, and transmits the reading via ROS 2 / REST API. The system interpolates a 50×50 plantation heatmap using an **EfficientNet Spatial Neural Network Regressor** and generates commercial fertilizer prescriptions (Urea, SSP, MOP, Lime, Gypsum).

---

## 🏗️ 2. System Architecture & Information Flow

```text
               +-------------------------------------------------------------+
               |                  ESP32 Physical Rover Hardware              |
               |  - BN-880 GPS (UART)       - ZTS-3002 Modbus Sensor (RS485) |
               |  - L298N 4WD Skid-Steer    - L293D N20 Rack-and-Pinion      |
               |  - Top & Bottom NC Limit Switches (Hardware Interrupts)     |
               +------------------------------+------------------------------+
                                              |
                   WiFi / HTTP REST / ROS 2 Reliable QoS (/rover/soil_telemetry)
                                              |
                                              v
               +-------------------------------------------------------------+
               |                 FastAPI Asynchronous Backend                |
               |  - Hardware Abstraction Layer (Mock vs Real ESP32/Modbus)   |
               |  - Strict 4-State Machine Controller                        |
               |  - Modbus RTU Hex Frame Decoder                             |
               |  - Central Sericultural Research (CSRTI) Agronomy Engine    |
               |  - SQLite / PostgreSQL Database (SQLAlchemy ORM)            |
               +------------------------------+------------------------------+
                                              |
                     Database Queries / Spatial Coordinate Extraction
                                              |
                                              v
               +-------------------------------------------------------------+
               |                Spatial Machine Learning Pipeline            |
               |  - Synthetic Plantation Generator (7 Agronomic Zones)       |
               |  - Spatial IDW Interpolator (Baseline Inverse Distance)     |
               |  - Scikit-Learn Multi-Output Random Forest Baseline         |
               |  - PyTorch EfficientNet Spatial Regressor (SiLU + BatchNorm)|
               |  - 50x50 Spatial Prediction Heatmap Grid                    |
               +------------------------------+------------------------------+
                                              |
                                    REST API JSON Endpoints
                                              |
                      +-----------------------+-----------------------+
                      |                                               |
                      v                                               v
+------------------------------------------+    +------------------------------------------+
|      Modern React TypeScript Web UI      |    |      Streamlit Soil Operations App       |
|  - Vite + Tailwind CSS + Lucide Icons    |    |  - Real-time Plotly & Pydeck Maps        |
|  - WebGL Shaders (SpecularButton, Waves) |    |  - Soil Health Metrics & Gauges          |
|  - Interactive 50x50 HTML5 Heatmaps      |    |  - State Machine Stepper & Controls      |
|  - Dual Mode: Live Backend / Mock Data   |    +------------------------------------------+
+------------------------------------------+
```

---

## ⚙️ 3. Hardware Specifications & ESP32 Pinouts

### Microcontroller: ESP32 Dev Module

| Subsystem | Hardware Component | ESP32 GPIO Pins | Function / Protocol |
| :--- | :--- | :--- | :--- |
| **Locomotion** | L298N Dual H-Bridge | `ENA`=33, `IN1`=25, `IN2`=26<br>`ENB`=32, `IN3`=27, `IN4`=14 | 4WD Skid-Steer PWM (1 kHz, 8-bit) |
| **Linear Actuator** | L293D + N20 Gear Motor | `ACT_IN1`=22, `ACT_IN2`=21 | Rack & Pinion Up/Down Drive |
| **Safety Switches** | Microswitches (Normally Closed) | `PIN_BOTTOM_LIMIT`=18<br>`PIN_TOP_LIMIT`=19 | Active LOW via `INPUT_PULLUP` & ISRs |
| **Soil Sensor** | MAX485 TTL-to-RS485 | `TX2`=17, `RX2`=16 | Hardware UART2, 9600 Baud, 8N1 |
| **GNSS Positioning** | BN-880 GPS / Compass | Default UART0/1 | NMEA sentence parsing at 9600 Baud |

---

## 🔒 4. Strict 4-State Rover State Machine Workflow

The rover strictly follows a 4-state sequential machine with hardware safety interlocks:

1. **`STATE 1 — TRANSIT`**:
   * Navigation towards target GPS coordinates (`/rover/cmd_vel`).
   * Actuator remains locked in the UP position.
   * Upon reaching waypoint distance threshold (< 0.5 m), velocity is set to ZERO (`velocity = 0`).
2. **`STATE 2 — DEPLOYMENT`**:
   * N20 motor drives rack downwards (`ACT_IN1=HIGH, ACT_IN2=LOW`).
   * Halts immediately when **Bottom Limit Switch NC (GPIO 18)** is triggered or on 15s safety timeout / E-Stop.
3. **`STATE 3 — INTERROGATION`**:
   * Pauses for electrochemical sensor stabilization (configurable 3s demo / 3 min real).
   * Reads ZTS-3002 Modbus registers, decodes raw hex values, tags reading with active GPS coordinates.
4. **`STATE 4 — RETRACTION`**:
   * N20 motor reverses to raise probe upward (`ACT_IN1=LOW, ACT_IN2=HIGH`).
   * Stops immediately when **Top Limit Switch NC (GPIO 19)** is triggered.
   * Confirms sensor is clear of ground before transitioning back to **TRANSIT**.
5. **`EMERGENCY_STOP`**:
   * Halts all locomotion and actuator power immediately (`PWM = 0`).

---

## 📡 5. Modbus Register Map & Scientific Formulas

### Modbus RTU Register Map (ZTS-3002 Sensor)

| Register Address | Parameter | Raw Resolution | Engineering Unit | Scaling Factor |
| :--- | :--- | :--- | :--- | :--- |
| `0x0000` | Soil Moisture | 0.1 % | % | `val * 0.1` |
| `0x0001` | Temperature | 0.1 °C | °C | `val * 0.1` |
| `0x0002` | Electrical Conductivity (EC) | 1 us/cm | dS/m | `val * 0.001` |
| `0x0003` | Soil pH | 0.1 pH | pH | `val * 0.1` |
| `0x0004` | Nitrogen (N) | 1 mg/kg | kg/ha | `val * 1.0` |
| `0x0005` | Phosphorus (P) | 1 mg/kg | kg/ha | `val * 1.0` |
| `0x0006` | Potassium (K) | 1 mg/kg | kg/ha | `val * 1.0` |

### Mulberry Agronomic Baseline Targets (CSRTI Standards)
* **Soil pH**: Target range `6.5 – 7.5` (`LOW` < 6.5, `OPTIMAL` 6.5-7.5, `HIGH` > 7.5)
* **Electrical Conductivity (EC)**: Target `< 1.0 dS/m` (`NORMAL` < 1.0, `HIGH` >= 1.0)
* **Nitrogen (N) Shortfall**: $\max(350 - \text{measured\_N}, 0)$ kg/ha/year
* **Phosphorus (P) Shortfall**: $\max(140 - \text{measured\_P}, 0)$ kg/ha/year
* **Potassium (K) Shortfall**: $\max(140 - \text{measured\_K}, 0)$ kg/ha/year

### Commercial Fertilizer Formulas
* **Urea (46% N)**: $\text{N\_shortfall} / 0.46\text{ kg/ha}$
* **Single Super Phosphate SSP (16% $\text{P}_2\text{O}_5$)**: $\text{P\_shortfall} / 0.16\text{ kg/ha}$
* **Muriate of Potash MOP (60% $\text{K}_2\text{O}$)**: $\text{K\_shortfall} / 0.60\text{ kg/ha}$
* **Acidic Soil Lime ($\text{CaCO}_3$)**: $\max(0.5, (6.5 - \text{pH}) \times 1.8)\text{ tons/ha}$ (when $\text{pH} < 6.5$)
* **Alkaline Soil Gypsum ($\text{CaSO}_4$)**: $\max(0.5, (\text{pH} - 7.5) \times 1.5)\text{ tons/ha}$ (when $\text{pH} > 7.5$)

---

## 🧠 6. Machine Learning & Spatial Pipeline

1. **Synthetic Generator (`ml/synthetic_generator.py`)**:
   Generates 1,000 spatial observations over a 200m × 200m plantation ($11.3921^\circ\text{N}, 77.7342^\circ\text{E}$) with 7 distinct agronomic deficiency zones:
   * *Zone A (NW)*: Severe Nitrogen Deficiency ($N < 200$).
   * *Zone B (NE)*: Phosphorus Deficiency ($P < 70$).
   * *Zone C (SE)*: Potassium Deficiency ($K < 80$).
   * *Zone D (SW)*: Saline / High EC ($\text{EC} > 1.2\text{ dS/m}, \text{pH} > 7.8$).
   * *Zone E (Center-West)*: Acidic Soil Patch ($\text{pH} < 5.8$).
   * *Zone F (Center-East)*: Optimal High-Yield Benchmark.
   * *Zone G (South Depression)*: Drainage Depression / Waterlogged ($\text{Moisture} > 65\%$).
2. **Spatial IDW Baseline (`ml/spatial_idw.py`)**:
   Inverse Distance Weighting with Euclidean power $p = 2.0$ generating a 50×50 prediction grid.
3. **Random Forest Baseline (`ml/baseline_model.py`)**:
   Multi-output Random Forest regressor with 100 trees (`scikit-learn`). Evaluates MAE, RMSE, and $R^2$.
4. **PyTorch EfficientNet Spatial Regressor (`ml/efficientnet_model.py`)**:
   * Architecture: 4-layer inverted bottleneck with `Linear`, `BatchNorm1d`, `SiLU` (Swish) activations, and `Dropout(0.1)` (64 $\to$ 128 $\to$ 128 $\to$ 64 dimensions).
   * Regression Head: Multi-output linear head predicting 8 outputs: `[n_deficiency, p_deficiency, k_deficiency, ph, ec, moisture, temperature, soil_health_index]`.
   * Optimizer: `AdamW` ($\text{lr} = 0.005$, weight decay $10^{-4}$) for 35 epochs. Outputs dense 50×50 grid (2,500 points).

---

## 🗂️ 7. Exhaustive File-by-File Catalog

### Root Files & Configuration
* `config/config.yaml`: Central YAML configuration containing plantation center coordinates ($11.3921, 77.7342$), grid resolution (50×50), agronomic targets, Modbus register mappings, pin definitions, and 8 survey waypoints.
* `.env` / `.env.example`: Environment variable definitions (`MOCK_MODE=True`, `API_HOST`, `API_PORT=8000`, `DATABASE_URL`).
* `demo.py`: Master 1-click Python demonstration runner. Executes the ML pipeline, starts the FastAPI backend, runs 16 state machine steps, launches the React frontend, and opens the browser.
* `requirements.txt`: Python dependencies (`fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `torch`, `scikit-learn`, `streamlit`, `plotly`, `pydeck`).
* `start.sh` / `start.bat`: Shell and Windows batch launcher scripts.
* `Dockerfile.backend` / `Dockerfile.frontend` / `Dockerfile.dashboard`: Container build recipes.
* `docker-compose.yml`: Multi-container orchestration for Backend, Frontend, and Dashboard.

### Firmware
* `firmware/esp32/esp32_rover_firmware.ino`: Complete Arduino C++ firmware for the ESP32. Implements L298N locomotion, L293D rack actuator, ISRs for top/bottom NC limit switches, MAX485 UART2 Modbus transceiver, a 15-second safety timeout, and an embedded HTML5 web dashboard at `http://192.168.1.150`.

### ROS 2 Workspace
* `ros2_ws/src/rover_interfaces/msg/SoilTelemetry.msg`: Custom ROS 2 message containing `Header`, `NavSatFix location`, `float32 ph`, `ec`, `moisture`, `int32 nitrogen`, `phosphorus`, `potassium`, `string rover_state`, `mission_id`, `sample_id`.
* `ros2_ws/src/rover_simulator/rover_simulator/simulator_node.py`: ROS 2 node publishing to `/rover/soil_telemetry` with `Reliable` QoS and forwarding payloads to the FastAPI REST backend via HTTP POST.

### Backend Core (`backend/app/`)
* `backend/app/main.py`: FastAPI application initialization, CORS middleware, table auto-creation lifespan, router inclusion, and `/health` route.
* `backend/app/config.py`: Pydantic-settings class loading `config/config.yaml` and `.env`.
* `backend/app/database/connection.py`: SQLAlchemy engine, `SessionLocal`, and declarative `Base` bound to `data/precision_sericulture.db`.
* `backend/app/database/models.py`:
  * `MissionModel`: Rover mission sessions and status.
  * `RoverLocationModel`: Real-time breadcrumb coordinates, heading, and battery state.
  * `SoilObservationModel`: Raw soil sensor readings, coordinates, and Modbus hex payloads.
  * `SoilAnalysisModel`: Agronomic evaluation, deficiencies, and commercial fertilizer dosages.
  * `SpatialPredictionModel`: 50×50 prediction grid points for IDW, Random Forest, and EfficientNet.
  * `FertilizerPrescriptionModel`: Zonal fertilizer prescription recommendations and application schedules.
* `backend/app/schemas/telemetry.py`: Pydantic schemas: `SoilTelemetryBase`, `SoilTelemetryResponse`, `AgronomicAnalysisResponse`, `SpatialPredictionPoint`, `SpatialGridResponse`, `FertilizerPrescriptionZone`, `MissionSummary`, `PlantationSummaryResponse`.
* `backend/app/services/agronomy_service.py`: Evaluates soil samples against CSRTI targets, calculates elemental shortfalls, converts to commercial Urea/SSP/MOP dosages, prescribes Lime/Gypsum, and evaluates economic cocoon yield impact.
* `backend/app/services/state_machine.py`: Sequential 4-state rover state machine (`TRANSIT` $\to$ `DEPLOYMENT` $\to$ `INTERROGATION` $\to$ `RETRACTION`), waypoint distance tracking, sensor reading generation, and hardware logging.
* `backend/app/services/hardware_interface.py`: Abstract base classes and implementations for GPS (`MockGPS`, `RealGPS`), Soil Sensor (`MockSoilSensor`, `RealModbusSoilSensor`), and Rover Hardware (`MockRover`, `RealESP32Rover`).
* `backend/app/services/modbus_decoder.py`: Parses 16-bit register dictionaries or raw RS485 hex byte frames into engineering units with physical range validation.

### Backend API Routers (`backend/app/api/`)
* `backend/app/api/telemetry.py`: `POST /api/telemetry` (ingests rover readings, executes agronomic evaluation), `GET /api/telemetry` (retrieves observations).
* `backend/app/api/samples.py`: `GET /api/samples` (lists soil samples), `GET /api/samples/{id}` (retrieves individual observation).
* `backend/app/api/analysis.py`: `GET /api/analysis/{sample_id}` (retrieves agronomic evaluation), `GET /api/plantation/summary` (aggregated macro stats).
* `backend/app/api/predictions.py`: `GET /api/predictions?model_type={IDW|RandomForest|EfficientNet}` (returns 50×50 spatial grid).
* `backend/app/api/prescriptions.py`: `GET /api/prescriptions` (returns zonal fertilizer prescriptions).
* `backend/app/api/simulator_api.py`: `/api/simulator/status`, `/step`, `/run_cycle`, `/reset`, `/estop`.
* `backend/app/api/missions.py`: `GET /api/missions` (mission list), `GET /api/missions/export/csv` (CSV download).
* `backend/app/api/dataset_api.py`: `/api/dataset/zones`, `/statistics`, `/raw`, `/generate`, `/clear`.

### Machine Learning (`ml/`)
* `ml/synthetic_generator.py`: Realistic synthetic generator producing 1,000 spatial samples across 7 agronomic zones with sensor noise and Modbus hex payloads.
* `ml/spatial_idw.py`: Inverse Distance Weighting spatial interpolator ($p = 2.0$) across a 50×50 grid.
* `ml/baseline_model.py`: Scikit-Learn multi-target Random Forest baseline ($R^2$, MAE, RMSE metrics).
* `ml/efficientnet_model.py`: PyTorch neural regressor using SiLU/BatchNorm bottleneck blocks and AdamW optimizer.
* `ml/pipeline.py`: End-to-end orchestrator that generates synthetic data, trains IDW, Random Forest, and EfficientNet, evaluates metrics, populates SQLite, and creates `models/metrics_summary.json`.

### Frontend Architecture (`frontend/`)
* `frontend/package.json`: Dependencies: React 19, TypeScript, Vite 8, Tailwind CSS, Lucide React, Framer Motion, Recharts, OGL (WebGL).
* `frontend/src/App.tsx`: Main entry component. Switches between `'landing'` (Landing Page) and `'app'` (Dashboard with Header and Sidebar Navbar).
* `frontend/src/services/api.ts`: API client with automatic dual-mode fallback (queries `http://localhost:8000`, seamlessly falls back to `mockData.ts` if offline).
* `frontend/src/types/telemetry.ts`: TypeScript interfaces matching the backend Pydantic models.
* `frontend/src/mock/mockData.ts`: Full mock dataset (summary, telemetry points, prescriptions, 50×50 heatmaps, rover state).

#### Frontend Views (`frontend/src/views/`)
1. `LandingPageView.tsx`: High-converting presentation landing page featuring hero video, WebGL `GradientWaves`, `SpecularButton`, interactive Mac-style `Dock`, system module showcase, and animated cards.
2. `OverviewView.tsx`: Executive dashboard with macro KPIs (Samples, Soil Health, N/P/K Deficiency, Fertilizer Required), interactive 50×50 Canvas Heatmap, and live activity feeds.
3. `RoverControlView.tsx`: Teleoperation and simulation interface. Displays rover state (`TRANSIT`, `DEPLOYMENT`, `INTERROGATION`, `RETRACTION`), limit switch indicators, step/cycle controls, and emergency stop.
4. `AgronomyView.tsx`: Deep agronomic intelligence: pH and EC status, elemental deficiency breakdowns, commercial fertilizer recommendations, and sericulture economic impact.
5. `SpatialMLView.tsx`: ML comparison laboratory. Toggle between **IDW**, **Random Forest**, and **PyTorch EfficientNet** heatmaps with MAE, RMSE, and $R^2$ model benchmarks.
6. `PrescriptionsView.tsx`: Zone-by-zone fertilizer prescriptions (Zones A–G) detailing Urea/SSP/MOP application schedules and organic amendments.
7. `SamplesView.tsx`: Searchable, filterable, and exportable data table of all rover soil observations.

#### ReactBits WebGL & Animation Components (`frontend/src/components/reactbits/`)
* `SpecularButton.tsx` & `SpecularButton.css`: WebGL-rendered metallic button with dynamic specular light reflections.
* `Dock.tsx` & `Dock.css`: macOS-style floating dock with magnification on hover.
* `GlareHover.tsx` & `GlareHover.css`: 3D perspective card hover effect with dynamic radial glare.
* `GradientWaves.tsx` & `GradientWaves.css`: OGL WebGL shader rendering fluid, animated gradient waves.
* `DotField.tsx` & `DotField.css`: Interactive canvas dot matrix with cursor attraction.

### Streamlit Dashboard (`dashboard/`)
* `dashboard/app.py`: Complete multi-page Streamlit application providing real-time telemetry tables, 3D Plotly surface charts, Pydeck GPS maps, and state machine controls.

### Automated Tests (`tests/`)
* `tests/test_state_machine.py`: Validates state machine progression (`TRANSIT` $\to$ `DEPLOYMENT` $\to$ `INTERROGATION` $\to$ `RETRACTION`), waypoint distance triggers, and E-Stop halting.
* `tests/test_agronomy.py`: Validates pH bounds, EC thresholds, NPK shortfall math, and Urea/SSP/MOP dosage formulas.
* `tests/test_spatial_ml.py`: Validates synthetic data generation, IDW grid outputs, Random Forest training, and EfficientNet inference.
* `tests/test_api.py`: Uses FastAPI `TestClient` to test `/health`, `POST /api/telemetry`, `GET /api/telemetry`, and `/api/predictions`.

---

## 🚀 8. Running & Deployment Commands

```bash
# 1. Install Dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Run the Full One-Click Demo (ML + Backend + Simulator + Frontend)
python demo.py

# 3. Or Run Services Individually:
# Start Backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Frontend
cd frontend && npm run dev

# Start Streamlit Dashboard
streamlit run dashboard/app.py

# 4. Run Automated Pytest Suite
pytest tests/ -v
```
