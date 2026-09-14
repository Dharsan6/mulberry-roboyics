# 🌿 Precision Sericulture: System Documentation & Engineering Reference Manual

**Automated Rack-and-Pinion Soil Probing Mechanism on a 4WD Autonomous Rover for Mulberry Agronomy (*Morus alba*)**

---

## 📑 Table of Contents
1. [Executive Summary & Domain Context](#1-executive-summary--domain-context)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Hardware Engineering & Circuit Pinouts](#3-hardware-engineering--circuit-pinouts)
4. [Rover 4-State Machine & Safety Interlocks](#4-rover-4-state-machine--safety-interlocks)
5. [Modbus RTU Sensor Protocol & Register Mapping](#5-modbus-rtu-sensor-protocol--register-mapping)
6. [Mulberry Agronomic Engine & Dosage Mathematics](#6-mulberry-agronomic-engine--dosage-mathematics)
7. [Spatial Machine Learning & Neural Network Regression](#7-spatial-machine-learning--neural-network-regression)
8. [Backend Architecture & Database Schema](#8-backend-architecture--database-schema)
9. [REST API Endpoints Reference](#9-rest-api-endpoints-reference)
10. [Frontend Architecture & UI Design System](#10-frontend-architecture--ui-design-system)
11. [Installation, Testing & Execution Guide](#11-installation-testing--execution-guide)
12. [Git Repository & Version Control](#12-git-repository--version-control)

---

## 1. Executive Summary & Domain Context

### 1.1 The Sericulture Challenge
Sericulture is the agro-industrial process of cultivating mulberry leaves to rear domesticated silkworms (*Bombyx mori*) for raw silk filament extraction. Because mulberry (*Morus alba*) leaves constitute 100% of the silkworm diet, leaf nutritional quality—specifically leaf protein, moisture content (>70%), and balanced mineral uptake—directly dictates silkworm larval survival, cocoon shell ratio (target >22%), and silk reelability.

### 1.2 The Innovation
Traditional plantation soil management depends on sparse, manual composite soil collection with laboratory turnaround delays of 2–4 weeks. 

**Precision Sericulture** solves this with an end-to-end automated platform:
* An autonomous 4WD skid-steer rover deployed with high-precision GNSS waypoints.
* A motorized 3D-printed PETG linear rack-and-pinion prober lowering an industrial Modbus RS485 sensor 15 cm into the soil.
* Real-time measurement of **pH, Electrical Conductivity (EC), Moisture, Nitrogen (N), Phosphorus (P), and Potassium (K)**.
* Continuous spatial field interpolation across a 50×50 grid utilizing a **PyTorch EfficientNet Spatial Neural Network**.
* Deterministic prescription generation mapping exact commercial fertilizer dosages (Urea, SSP, MOP, Lime, Gypsum) based on Central Sericultural Research & Training Institute (CSRTI) standards.

---

## 2. End-to-End System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHYSICAL ROVER PLATFORM (EDGE)                        │
│                                                                             │
│  [BN-880 GPS]   [ZTS-3002 Soil Sensor]    [Limit Switches Top/Bottom NC]    │
│        │                  │                             │                   │
│    UART NMEA        MAX485 Modbus RTU           Hardware Interrupts         │
│        └──────────────┬───┴─────────────────────────────┘                   │
│                       ▼                                                     │
│               [ESP32 Microcontroller]                                      │
│         4-State Machine + Motor PWM Drivers                                 │
│        (L298N Skid-Steer + L293D Rack Actuator)                             │
└───────────────────────┬─────────────────────────────────────────────────────┘
                        │
       WiFi SoftAP / HTTP REST / ROS 2 (/rover/soil_telemetry)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI ASYNCHRONOUS BACKEND                           │
│                                                                             │
│  - Hardware Abstraction Layer (Mock vs Physical ESP32)                      │
│  - Modbus RTU Hex Decoder (CRC16 + Scaling Factors)                         │
│  - Mulberry Agronomy Engine (CSRTI Targets & Deficiency Matrices)           │
│  - Relational Database (SQLite / PostgreSQL with SQLAlchemy ORM)            │
└───────────────────────┬─────────────────────────────────────────────────────┘
                        │
           Spatial Data Extraction & Grid Queries
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 MACHINE LEARNING & SPATIAL DATA PIPELINE                    │
│                                                                             │
│  - 7-Zone Synthetic Plantation Data Generator                               │
│  - Baseline 1: Spatial Inverse Distance Weighting (IDW, power=2.0)          │
│  - Baseline 2: Scikit-Learn Multi-Output Random Forest Regressor            │
│  - Deep Learning: PyTorch EfficientNet Spatial Regressor (SiLU + BatchNorm) │
│  - 50x50 Spatial Prediction Heatmap Grid (2,500 Grid Points)                │
└───────────────────────┬─────────────────────────────────────────────────────┘
                        │
              JSON REST Endpoints & Data Feeds
                        │
         ┌──────────────┴────────────────────────┐
         ▼                                       ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────────┐
│     REACT 19 TYPESCRIPT WEB UI    │ │     STREAMLIT OPERATIONS CONSOLE      │
│  - Dark Obsidian & Emerald Theme  │ │  - 3D Plotly Surface Maps             │
│  - Interactive 50x50 Canvas Grid  │ │  - Pydeck Spatial GPS Trajectories    │
│  - Hash Router & Browser History  │ │  - Manual State Stepper Controls      │
│  - Teleoperation & Prescriptions  │ │  - Real-time Diagnostic Gauges        │
└───────────────────────────────────┘ └───────────────────────────────────────┘
```

---

## 3. Hardware Engineering & Circuit Pinouts

### 3.1 Microcontroller Unit (MCU)
* **Processor**: ESP32-WROOM-32 (Dual Core 240 MHz, 520 KB SRAM, 4 MB Flash).
* **Communication**: 802.11 b/g/n Wi-Fi (SoftAP & Station Mode), Hardware UARTs.

### 3.2 Actuation & Locomotion Pin Assignment

| Subsystem | Hardware Driver | ESP32 GPIO | Electrical Specification | Logic / Protocol |
| :--- | :--- | :--- | :--- | :--- |
| **Locomotion Left** | L298N Dual H-Bridge | `ENA`: Pin 33<br>`IN1`: Pin 25<br>`IN2`: Pin 26 | 12V DC, 8-bit PWM (Channel 0, 1000 Hz)<br>Logic 3.3V / 5V Compatible | Skid-Steer Left Drive |
| **Locomotion Right** | L298N Dual H-Bridge | `ENB`: Pin 32<br>`IN3`: Pin 27<br>`IN4`: Pin 14 | 12V DC, 8-bit PWM (Channel 1, 1000 Hz)<br>Logic 3.3V / 5V Compatible | Skid-Steer Right Drive |
| **Rack Actuator** | L293D Motor Shield | `ACT_IN1`: Pin 22<br>`ACT_IN2`: Pin 21 | Micro N20 Metal Gear Motor (6V, 60 RPM)<br>PWM speed: 90/255 | Linear Probe Down / Up |
| **Bottom Limit Switch** | Microswitch (NC) | `PIN_BOTTOM_LIMIT`: Pin 18 | `INPUT_PULLUP`, Active LOW (`FALLING` ISR) | Probing Depth Target (15 cm) |
| **Top Limit Switch** | Microswitch (NC) | `PIN_TOP_LIMIT`: Pin 19 | `INPUT_PULLUP`, Active LOW (`FALLING` ISR) | Retracted Home Position |
| **Modbus Soil Sensor** | MAX485 TTL-to-RS485 | `TX2`: Pin 17<br>`RX2`: Pin 16 | Hardware UART2, 9600 Baud, 8N1 | Industrial Modbus RTU |
| **GNSS Receiver** | BN-880 GPS Module | Default UART0/1 | 9600 Baud, NMEA-0183 | Latitude, Longitude, Altitude |

### 3.3 Electrical & Mechanical Safety
1. **Normally Closed (NC) Limit Switches**: Wired with internal pull-up resistors. A severed wire or switch trigger immediately triggers an active-low interrupt to cut actuator power.
2. **15-Second Software Watchdog**: If the bottom limit switch fails to close within 15,000 ms, the system halts and raises an **`EMERGENCY_STOP`**.
3. **Motion Interlock**: Rover skid-steer locomotion cannot be energized unless the probe is verified at the **`TOP`** limit position.

---

## 4. Rover 4-State Machine & Safety Interlocks

The autonomous rover strictly cycles through a deterministic 4-state automaton:

```text
    ┌───────────────┐
    │ 1. TRANSIT    │◄────────────────────────────────┐
    │ Drives to GPS │                                 │
    └───────┬───────┘                                 │
            │ Dist < 0.5m                             │
            ▼                                         │
    ┌───────────────┐                                 │
    │ 2. DEPLOYMENT │                                 │
    │ Lowers Rack   │                                 │
    └───────┬───────┘                                 │
            │ Bottom Limit NC Triggered               │
            ▼                                         │
    ┌──────────────────┐                              │
    │ 3. INTERROGATION │                              │
    │ Stabilize & Read │                              │
    └───────┬──────────┘                              │
            │ Stabilization Elapsed (3s mock / 3m live)
            ▼                                         │
    ┌──────────────────┐                              │
    │ 4. RETRACTION    │                              │
    │ Raises Rack      │──────────────────────────────┘
    └──────────────────┘  Top Limit NC Triggered
```

1. **`STATE 1 — TRANSIT`**:
   * Rover navigates toward waypoint coordinates using differential skid-steer drive (`/rover/cmd_vel`).
   * Rack motor is locked in the UP position (`top_limit = true`).
   * When waypoint distance threshold $< 0.5\text{ m}$ ($0.00003^\circ$ latitude/longitude), velocity is set to zero (`velocity = 0`).
2. **`STATE 2 — DEPLOYMENT`**:
   * Rack motor rotates forward (`ACT_IN1 = HIGH`, `ACT_IN2 = LOW`), driving the sensor vertically downwards into the soil profile.
   * Motion halts the moment the **Bottom Limit Switch (Pin 18)** triggers at 15 cm probe depth.
3. **`STATE 3 — INTERROGATION`**:
   * The rover rests while the sensor electrochemically stabilizes with the root zone moisture and minerals.
   * Reads 7 Modbus registers from the ZTS-3002 probe, decodes raw hex data, computes the Soil Health Index, and pairs data with GPS coordinates.
4. **`STATE 4 — RETRACTION`**:
   * Rack motor reverses (`ACT_IN1 = LOW`, `ACT_IN2 = HIGH`), raising the probe back into the chassis.
   * Motion halts upon triggering the **Top Limit Switch (Pin 19)**.
   * Increments waypoint pointer and loops back to **`TRANSIT`**.
5. **`EMERGENCY_STOP`**:
   * Triggered by manual override or safety watchdog. Instantly zeroes motor current (`PWM = 0`).

---

## 5. Modbus RTU Sensor Protocol & Register Mapping

### 5.1 ZTS-3002 Multi-Parameter Sensor Register Map
The probe measures soil electrochemical and physical parameters via RS485 Modbus RTU (Slave ID = `0x01`, Function Code = `0x03` Read Holding Registers).

| Register Address | Soil Parameter | Raw Data Format | Output Unit | Scaling Equation | Typical Range |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x0000` | Soil Moisture | 16-bit Unsigned Int | % | $\text{Moisture} = \text{Raw} \times 0.1$ | 0.0 – 100.0 % |
| `0x0001` | Temperature | 16-bit Signed Int | °C | $\text{Temp} = \text{Raw} \times 0.1$ | -10.0 – 60.0 °C |
| `0x0002` | Electrical Conductivity | 16-bit Unsigned Int | dS/m | $\text{EC} = \text{Raw} \times 0.001$ | 0.00 – 10.00 dS/m |
| `0x0003` | Soil pH | 16-bit Unsigned Int | pH | $\text{pH} = \text{Raw} \times 0.1$ | 3.0 – 10.0 pH |
| `0x0004` | Nitrogen (N) | 16-bit Unsigned Int | kg/ha | $\text{N} = \text{Raw} \times 1.0$ | 0 – 1000 kg/ha |
| `0x0005` | Phosphorus (P) | 16-bit Unsigned Int | kg/ha | $\text{P} = \text{Raw} \times 1.0$ | 0 – 1000 kg/ha |
| `0x0006` | Potassium (K) | 16-bit Unsigned Int | kg/ha | $\text{K} = \text{Raw} \times 1.0$ | 0 – 1000 kg/ha |

### 5.2 Hexadecimal Response Frame Structure
Example Modbus response packet:
```text
[01] [03] [0E] [01C2] [00F0] [02EE] [0044] [0118] [006E] [0078] [A5C3]
 │    │    │     │      │      │      │      │      │      │      │
 │    │    │     │      │      │      │      │      │      │      └─ CRC16 Checksum
 │    │    │     │      │      │      │      │      │      └─ Potassium: 0x0078 = 120 kg/ha
 │    │    │     │      │      │      │      │      └─ Phosphorus: 0x006E = 110 kg/ha
 │    │    │     │      │      │      │      └─ Nitrogen: 0x0118 = 280 kg/ha
 │    │    │     │      │      │      └─ pH: 0x0044 = 68 -> 6.8 pH
 │    │    │     │      │      └─ EC: 0x02EE = 750 uS/cm -> 0.75 dS/m
 │    │    │     │      └─ Temp: 0x00F0 = 240 -> 24.0 °C
 │    │    │     └─ Moisture: 0x01C2 = 450 -> 45.0 %
 │    │    └─ Byte count (14 bytes payload)
 │    └─ Function code 0x03 (Read Holding Registers)
 └─ Slave Address 0x01
```

---

## 6. Mulberry Agronomic Engine & Dosage Mathematics

Evaluations conform to standard agronomic baselines established by the **Central Sericultural Research & Training Institute (CSRTI)** for high-yielding *Morus alba* cultivars (e.g., Victory-1 / V1, S36, Kanva-2).

### 6.1 Baseline Scientific Targets
* **Optimal Soil pH**: $6.5 \le \text{pH} \le 7.5$
* **Critical EC Threshold**: $\text{EC} < 1.0\text{ dS/m}$
* **Target Nitrogen ($N$)**: $350.0\text{ kg/ha/year}$
* **Target Phosphorus ($P$)**: $140.0\text{ kg/ha/year}$
* **Target Potassium ($K$)**: $140.0\text{ kg/ha/year}$

### 6.2 Elemental Nutrient Deficiencies
$$\Delta N = \max(350.0 - \text{measured\_N}, 0)$$
$$\Delta P = \max(140.0 - \text{measured\_P}, 0)$$
$$\Delta K = \max(140.0 - \text{measured\_K}, 0)$$

### 6.3 Commercial Fertilizer Quantities (kg/ha)
Commercial fertilizers contain elemental nutrients at standardized concentrations:
* **Urea (46% Nitrogen)**:
  $$\text{Urea}_{\text{req}} = \frac{\Delta N}{0.46}\text{ kg/ha}$$
* **Single Super Phosphate (SSP, 16% $\text{P}_2\text{O}_5$)**:
  $$\text{SSP}_{\text{req}} = \frac{\Delta P}{0.16}\text{ kg/ha}$$
* **Muriate of Potash (MOP, 60% $\text{K}_2\text{O}$)**:
  $$\text{MOP}_{\text{req}} = \frac{\Delta K}{0.60}\text{ kg/ha}$$

### 6.4 Soil Amendments (Tons/ha)
* **Acidic Soil Remediation ($\text{pH} < 6.5$)**:
  $$\text{Agricultural Lime (}\text{CaCO}_3\text{)} = \max(0.5, (6.5 - \text{pH}) \times 1.8)\text{ tons/ha}$$
* **Alkaline Soil Remediation ($\text{pH} > 7.5$)**:
  $$\text{Mineral Gypsum (}\text{CaSO}_4\cdot 2\text{H}_2\text{O)} = \max(0.5, (\text{pH} - 7.5) \times 1.5)\text{ tons/ha}$$

### 6.5 Composite Soil Health Index (0–100)
Calculated via multi-parameter weighted scoring:
$$\text{Health Index} = S_{\text{pH}} (20) + S_{\text{EC}} (15) + S_{\text{Moist}} (15) + S_{\text{NPK}} (40) + S_{\text{SOC}} (10)$$

---

## 7. Spatial Machine Learning & Neural Network Regression

### 7.1 Synthetic Dataset Generation (`ml/synthetic_generator.py`)
To emulate realistic spatial variation across a 200m × 200m plantation ($11.3921^\circ\text{N}, 77.7342^\circ\text{E}$), the generator models 7 spatial agronomic zones:
1. **Zone A (NW)**: Nitrogen Deficiency ($N < 200\text{ kg/ha}$) — Chlorosis and stunted shoot elongation.
2. **Zone B (NE)**: Phosphorus Deficiency ($P < 70\text{ kg/ha}$) — Root restriction and purpling.
3. **Zone C (SE)**: Potassium Deficiency ($K < 80\text{ kg/ha}$) — Marginal leaf burn and reduced drought tolerance.
4. **Zone D (SW)**: Saline / High EC ($\text{EC} > 1.2\text{ dS/m}$) — Osmotic stress inhibiting water uptake.
5. **Zone E (CW)**: Soil Acidification ($\text{pH} < 5.8$) — Micronutrient toxicity risk.
6. **Zone F (CE)**: Optimal Benchmark ($6.8 \le \text{pH} \le 7.2$, high organic carbon).
7. **Zone G (SC)**: Waterlogged Depression ($\text{Moisture} > 65\%$) — Root rot risk (*Fusarium solani*).

### 7.2 Benchmark 1: Spatial Inverse Distance Weighting (IDW)
Standard spatial geostatistical baseline ($p=2.0$):
$$\hat{Z}(x_0) = \frac{\sum_{i=1}^n w_i Z(x_i)}{\sum_{i=1}^n w_i}, \quad w_i = \frac{1}{d(x_0, x_i)^p}$$

### 7.3 Benchmark 2: Multi-Output Random Forest Regressor
Ensemble regressor comprising 100 decision trees trained on spatial coordinates with standard 80/20 train/test splits.

### 7.4 PyTorch EfficientNet Spatial Regressor (`ml/efficientnet_model.py`)
Neural network regression architecture designed for spatial representation learning:
* **Input Layer**: Normalized coordinates $(\text{Latitude}, \text{Longitude})$ ($D=2$).
* **Encoder**: 4-stage inverted bottleneck block with `Linear`, `BatchNorm1d`, `SiLU` (Swish) activations, and `Dropout(0.1)`:
  $$\text{Input}(2) \to \text{Linear}(64) \to \text{Linear}(128) \to \text{Linear}(128) \to \text{Linear}(64)$$
* **Regression Head**: `Linear(64, 32)` $\to$ `SiLU` $\to$ `Linear(32, 8)` predicting:
  `[n_deficiency, p_deficiency, k_deficiency, ph, ec, moisture, temperature, soil_health_index]`.
* **Optimization**: `AdamW` ($\text{learning rate} = 0.005$, $\text{weight decay} = 10^{-4}$), 35 epochs. Outputs a continuous 50×50 spatial matrix (2,500 grid points).

---

## 8. Backend Architecture & Database Schema

The backend uses **FastAPI** with an asynchronous lifespan model, CORS middleware, and **SQLAlchemy 2.0 ORM** connected to SQLite (`data/precision_sericulture.db`) or PostgreSQL.

### 8.1 Database Entity Models (`backend/app/database/models.py`)

```text
┌─────────────────────────┐       ┌─────────────────────────┐
│      MissionModel       │       │  FertilizerPrescription │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │       │ id (PK)                 │
│ mission_id (UK, Index)  │       │ zone_id (Index)         │
│ mission_name            │       │ zone_name               │
│ status                  │       │ center_lat, center_lon  │
│ started_at, completed_at│       │ n, p, k deficiency      │
└────────────┬────────────┘       │ urea, ssp, mop kg/ha    │
             │ 1                  │ amendment_note          │
             │                    │ recommendation_note     │
             │ *                  └─────────────────────────┘
┌────────────┴────────────┐
│  SoilObservationModel   │       ┌─────────────────────────┐
├─────────────────────────┤       │ SpatialPredictionModel  │
│ id (PK)                 │       ├─────────────────────────┤
│ sample_id (UK, Index)   │       │ id (PK)                 │
│ mission_id (FK, Index)  │       │ model_type (Index)      │
│ timestamp (Index)       │       │ grid_x, grid_y (Index)  │
│ latitude, longitude     │       │ latitude, longitude     │
│ ph, ec, moisture, temp  │       │ predicted_n/p/k         │
│ nitrogen, phosphorus, k │       │ predicted_ph, ec        │
│ organic_carbon, health  │       │ predicted_moisture      │
│ rover_state, is_valid   │       │ predicted_soil_health   │
└────────────┬────────────┘       └─────────────────────────┘
             │ 1
             │
             │ 1
┌────────────┴────────────┐
│    SoilAnalysisModel    │
├─────────────────────────┤
│ id (PK)                 │
│ sample_id (FK, UK)      │
│ ph_status, ec_status    │
│ n, p, k deficiency      │
│ urea, ssp, mop req      │
│ lime_gypsum_req         │
│ fym_req, bio_fertilizer │
│ overall_soil_status     │
│ sericulture_econ_impact │
└─────────────────────────┘
```

---

## 9. REST API Endpoints Reference

Base URL: `http://localhost:8000`

| HTTP Method | Route | Description | Request Body / Query | Response Model |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health check and mock mode status | None | `JSON status` |
| `POST` | `/api/telemetry` | Ingests real-time rover telemetry reading | `SoilTelemetryCreate` | `SoilTelemetryResponse` (201) |
| `GET` | `/api/telemetry` | Lists recent telemetry observations | `?limit=100` | `List[SoilTelemetryResponse]` |
| `GET` | `/api/samples` | Retrieves paginated soil samples | `?limit=50&skip=0` | `List[SoilTelemetryResponse]` |
| `GET` | `/api/samples/{id}` | Retrieves detailed individual soil sample | `sample_id` in path | `SoilTelemetryResponse` |
| `GET` | `/api/analysis/{sample_id}` | Retrieves CSRTI agronomic analysis & dosages | `sample_id` in path | `AgronomicAnalysisResponse` |
| `GET` | `/api/plantation/summary` | Macro KPIs for entire plantation | None | `PlantationSummaryResponse` |
| `GET` | `/api/predictions` | Retrieves 50x50 spatial prediction grid | `?model_type=EfficientNet` | `SpatialGridResponse` |
| `GET` | `/api/prescriptions` | Zonal fertilizer prescription matrix | None | `List[FertilizerPrescriptionZone]` |
| `GET` | `/api/simulator/status` | Current state machine & telemetry status | None | `RoverSimulatorStatus` |
| `POST` | `/api/simulator/step` | Advances rover state machine by 1 step | None | `RoverSimulatorStatus` |
| `POST` | `/api/simulator/run_cycle`| Executes full 4-state probing cycle | None | `RoverSimulatorStatus` |
| `POST` | `/api/simulator/reset` | Resets rover to TRANSIT state | None | `RoverSimulatorStatus` |
| `POST` | `/api/simulator/estop` | Emergency stop override | None | `RoverSimulatorStatus` |
| `GET` | `/api/missions` | Summaries of all conducted survey missions | None | `List[MissionSummary]` |
| `GET` | `/api/missions/export/csv`| Exports plantation dataset to CSV | None | `text/csv download` |
| `GET` | `/api/dataset/zones` | Geographical coordinates of deficiency zones | None | `List[ZoneInfo]` |

---

## 10. Frontend Architecture & UI Design System

### 10.1 Technology Stack
* **Framework**: React 19 + TypeScript.
* **Build System**: Vite 8 (builds in ~600ms).
* **Styling**: Tailwind CSS 3.4.
* **Component Icons**: Lucide React.
* **Data Visualization**: Recharts 3.10 & HTML5 Canvas for 50×50 heatmaps.
* **WebGL Shaders**: OGL WebGL library (`GradientWaves`).

### 10.2 Sericulture Emerald Design Language
* **Background Atmosphere**: Deep Obsidian Navy (`#070b14`), dark section panels (`#090e1a`).
* **Sericulture Accent**: Neon Emerald (`#10b981`), Mint Jade (`#34d399`), and Deep Forest Green (`#042f2e`).
* **Container Glassmorphism**: Cards styled in `bg-[#0d1627]/90` with subtle border `border-slate-800/90` and emerald hover glow.
* **Header Branding**: Prominent `PRECISION SERICULTURE AI` badge.

### 10.3 Navigation & Browser History Sync
The application incorporates a **URL hash & browser history router**:
* When on Landing Page: URL is `/#/` or `/`.
* When on Dashboard: URL synchronizes to `#/dashboard?tab=overview`.
* Native browser **Back (`←`)** and **Forward (`→`)** buttons transition between Landing Page and Dashboard with zero reloads.
* In-app exit buttons (`[ ← Landing Page ]` in header and `[ 🏠 ← Back to Landing Page ]` in sidebar) ensure effortless navigation.

---

## 11. Installation, Testing & Execution Guide

### 11.1 Prerequisites
* Python 3.11+
* Node.js 18+ and npm
* ROS 2 Humble (optional for native ROS node)

### 11.2 Installation Steps
```bash
# 1. Clone the repository
git clone https://github.com/Dharsan6/precision-sericulture-rover.git
cd precision-sericulture-rover

# 2. Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 11.3 Launching the Demonstration (1-Click)
```bash
python demo.py
```
This automatically:
1. Generates 1,000 synthetic plantation soil samples across 7 zones.
2. Trains IDW, Random Forest, and PyTorch EfficientNet models.
3. Launches the FastAPI Backend on `http://localhost:8000`.
4. Executes 16 autonomous rover state machine steps.
5. Launches the React TypeScript Website on `http://localhost:5173`.

### 11.4 Running Individual Services
```bash
# Start FastAPI Backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Start React Frontend
cd frontend && npm run dev

# Start Streamlit Operations Console
streamlit run dashboard/app.py
```

### 11.5 Automated Unit Tests
```bash
pytest tests/ -v
```
Verifies state machine transitions, limit switch interrupts, CSRTI agronomic calculations, and API endpoint contracts.

---

## 12. Git Repository & Version Control

### Official Repositories
* 🌟 **Main Repository**: [https://github.com/Dharsan6/precision-sericulture-rover](https://github.com/Dharsan6/precision-sericulture-rover)
* 📁 **Secondary Sync**: [https://github.com/Dharsan6/mulberry-roboyics](https://github.com/Dharsan6/mulberry-roboyics)

Both repositories are kept strictly synchronized on the `main` branch.

---

*Authored by the Precision Sericulture Robotics & Agronomy Engineering Team.*
