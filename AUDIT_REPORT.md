# Precision Sericulture — Software Architecture & Codebase Audit

**Date:** 2026-09-14 · **Mode:** READ-ONLY (no files modified, added, or deleted by this audit)
**Scope:** ESP32 firmware, ROS 2 workspace, FastAPI backend, SQLAlchemy DB, mock/real HAL, Modbus decoder, rover state machine, agronomy engine, synthetic data generator, IDW, Random Forest, PyTorch "EfficientNet" model, ML pipeline, React/TS frontend, Streamlit dashboard, REST APIs, tests, Docker, demo/startup scripts.

**Verification performed:** full source read of every module; live SQLite inspection (`soil_observations=3001`, `soil_analysis=3001`, `missions=11`, `spatial_predictions=7500` (2500×3 models), `prescriptions=7`); pytest cache shows last run with **no failures**; confirmed test-pollution rows (`S_TEST_*`, `M_TEST_001`) live in the dev database; confirmed `ros2_ws/src/rover_interfaces/msg/` is **empty**.

Severity legend: **CRITICAL** = demo-breaking or integrity-breaking · **HIGH** = wrong/misleading results or real security/reliability risk · **MEDIUM** = quality, correctness-under-edge-cases, maintainability · **LOW** = polish, debt, style.

> **ADDENDUM (2026-09-14, Milestone 1):** The D1/E1 "missing `SoilTelemetry.msg`" finding below was an **audit tooling false negative** — the file was present, tracked at HEAD, and byte-identical to the version added in commit `80e2e38`; the audit's file-inventory command omitted `*.msg` extensions and a corroborating glob query returned a false zero that was not cross-checked with `ls`. The finding has been corrected in place and downgraded to the real (smaller) issue: the ROS 2 interface had never been verified by an actual build. Milestone 1 verification: field-by-field cross-check of `SoilTelemetry.msg` against `simulator_node.py` shows zero drift; see the Milestone 1 report for build/verification results.

---

## A. Current Architecture

```
┌────────────────────────────── ESP32 firmware (.ino) ─────────────────────────────┐
│ L298N 4WD drive · L293D N20 rack actuator · NC limit-switch ISRs · MAX485 UART2   │
│ WiFi SoftAP + embedded HTML5 web dashboard (manual drive/deploy/retract/estop)    │
│ NOTE: no GPS parsing, no Modbus read loop — sensor/GPS values are placeholders    │
└──────────────────────────────────────┬───────────────────────────────────────────┘
                                       (intended: micro-ROS / ROS 2)
┌──────────────────────────────────────▼───────────────────────────────────────────┐
│ ROS 2 ws: rover_interfaces (SoilTelemetry.msg — FILE MISSING) + rover_simulator   │
│ simulator_node.py: drives the PYTHON state machine, publishes to                  │
│ /rover/soil_telemetry (Reliable QoS) AND POSTs the same payload to FastAPI        │
└──────────────────────────────────────┬───────────────────────────────────────────┘
                                       │ HTTP POST /api/telemetry
┌──────────────────────────────────────▼───────────────────────────────────────────┐
│ FastAPI backend (backend/app)                                                     │
│  ├─ services/hardware_interface.py  Mock*/Real* HAL (Real* are stubs)             │
│  ├─ services/state_machine.py       TRANSIT→DEPLOYMENT→INTERROGATION→RETRACTION   │
│  ├─ services/modbus_decoder.py      register + hex-frame decoding (no CRC check)  │
│  ├─ services/agronomy_service.py    CSRTI baselines → shortfalls → Urea/SSP/MOP   │
│  └─ 8 routers: telemetry, samples, analysis, predictions, prescriptions,           │
│     simulator (module-level singleton), missions, dataset_api                      │
└───────────────┬───────────────────────────────────────────────────────────────────┘
                │ SQLAlchemy ORM, SQLite data/precision_sericulture.db (no Alembic;
                │ create_all at startup; FKs declared but PRAGMA foreign_keys off)
┌───────────────▼───────────────────────────────────────────────────────────────────┐
│ ML pipeline (ml/pipeline.py) — the data PRODUCER, not a consumer                   │
│  SyntheticPlantationGenerator → wipes all 5 tables → bulk-seeds observations +     │
│  analyses → IDW grid → trains RandomForest + "EfficientNet" (MLP) → stores         │
│  3×2500-grid predictions → writes metrics_summary.json → inserts 7 HARDCODED       │
│  zone prescriptions                                                                │
└───────────────┬───────────────────────────────────────────────────────────────────┘
                │ REST JSON
   ┌────────────┴─────────────────┐
   ▼                              ▼
React/TS (Vite, dual-mode         Streamlit (8 tabs; own fetch of
live-API/mock-fallback,           same API; pydeck heatmaps;
canvas heatmaps; hardcoded        reads metrics_summary.json
model metrics in SpatialMLView)   from disk)
```

Key architectural fact: **the ML pipeline is not downstream of the database — it is the database's author.** `ml/pipeline.py` deletes and repopulates all five tables from `SyntheticPlantationGenerator`, so "DB → ML" in the README is really "ML → DB". Anything the live rover/simulator writes is destroyed on the next pipeline run.

Second key fact: **all data in the system is synthetic.** There is no code path that feeds real sensor bytes into the DB: `RealGPS`/`RealModbusSoilSensor` return constants, `RealESP32Rover` does not exist, `MOCK_MODE` is never consulted anywhere, and the ESP32 firmware never reads the Modbus UART or GPS.

---

## B. Actual Data Flow Through the System

**Path 1 — synthetic seeding (dominant, populates everything you see in demos):**
1. `demo.py` / `start.sh` / `start.bat` → `ml/pipeline.run_full_ml_pipeline(1000)`.
2. Generator produces N samples (zone-correlated Gaussians + clipped noise, seeded, Modbus hex fabricated) → **deletes** all rows in 5 tables → inserts observations + agronomy analyses (commit per row) → IDW 50×50 → trains RF (100 trees) and the MLP ("EfficientNet", 35 epochs) on `latitude,longitude → 8 targets` → stores 3×2500 prediction rows → `models/metrics_summary.json` → inserts 7 hardcoded `FertilizerPrescriptionModel` rows.
3. Frontends read via `/api/plantation/summary`, `/api/samples`, `/api/predictions?model_type=…`, `/api/prescriptions`, `/api/missions`.

**Path 2 — interactive simulator (works, small footprint):**
- Streamlit button or React `RoverControlView` → `POST /api/simulator/step` → module-level `RoverStateMachine` (always Mock HAL) advances → on INTERROGATION completion builds `SoilTelemetryBase`, generates a `MockSoilSensor` reading (zone model + hex), computes health index → `simulator_api` writes observation + analysis (full field set) → status JSON returned.
- `demo.py` also runs 16 steps and POSTs each telemetry to `/api/telemetry`.
- ROS 2 `simulator_node.py` would do the same and publish to `/rover/soil_telemetry`, **but cannot run** (missing message definition).

**Path 3 — real hardware ingestion (designed, not functional):**
- ESP32 HTTP/`/api/drive` etc. exists on-device, but nothing in the firmware produces soil samples; nothing on the Python side polls the ESP32 (`RealESP32Rover` absent, `ESP32_IP` config unused by code).

**Path 4 — model inference:** none at runtime. "Predictions" are precomputed rows written at training time; `/api/predictions` only reads the DB. No model file is ever loaded at request time (`load()` methods unused).

---

## C. Current Working Functionality

| Component | Status | Notes |
|---|---|---|
| FastAPI app, lifespan table creation, 8 routers, `/health` | ✅ Works | Boots clean; OpenAPI docs at `/docs` |
| Agronomy engine (pH/EC/shortfall/Urea/SSP/MOP/lime/gypsum/FYM/economics) | ✅ Works, correct | Deterministic, matches documented CSRTI formulas; unit-tested |
| 4-state machine + E-STOP + reset (Python) | ✅ Works | Waypoint approach via MockGPS interpolation; interlocks respected (motion blocked unless probe TOP) |
| Mock HAL (`MockGPS`, `MockSoilSensor`, `MockRover`) | ✅ Works | 7-zone spatial correlation; battery/current/limit simulation; `raw_modbus_hex` generated |
| Modbus register decoder + `validate_reading` | ✅ Mostly works | Register-dict path correct; see bugs for hex/CRC/temperature issues |
| Synthetic generator (3000 samples committed) | ✅ Works | Seeded, reproducible, physically clipped ranges |
| IDW 50×50 grid | ✅ Works | Pure NumPy, correct p=2 formulation |
| Random Forest baseline + metrics | ✅ Works | Real metrics: N-MAE 5.34, R² 0.97 |
| PyTorch MLP training + 50×50 inference | ✅ Works | Runs, saves checkpoint + normalization params |
| React frontend — all 7 views + landing page | ✅ Builds/works in mock & live modes | `dist/` committed; dual-mode fallback is genuinely useful for demos |
| Streamlit dashboard — 8 tabs | ✅ Works | Graceful API-off defaults |
| pytest suite (4 files) | ✅ Passes (last run clean) | Covers state flow, estop, agronomy math, ML shapes, main API surface |
| Docker images (backend/frontend/dashboard) | ⚠️ Builds | See §M for runtime gaps |
| `demo.py` one-click | ⚠️ Works | Retrains every launch; subprocess pipe hazard (§E) |

---

## D. Broken or Incomplete Functionality

1. **MEDIUM (corrected — was wrongly reported as CRITICAL) — ROS 2 interface is complete but has never been build-verified.** `ros2_ws/src/rover_interfaces/msg/SoilTelemetry.msg` exists, is tracked at HEAD, and matches every field `simulator_node.py` assigns (`header`, `location` (NavSatFix), `ph/ec/moisture` float32, `nitrogen/phosphorus/potassium` int32, `rover_state/mission_id/sample_id` strings). However, no `colcon build` or CI has ever validated the package (and `rover_simulator/setup.py` installs no ament-index resource marker). Until a build is run, the ROS 2 story remains unverified rather than broken.
2. **HIGH — Live backend data breaks the React rover screen.** `types/telemetry.ts` models `RoverSimulatorStatus` with `actuator.{top,bottom}_limit_switch`, `step_index`, `current_waypoint.{latitude,longitude}` and state `"E_STOP"`. The backend actually returns `hardware.{top_limit,bottom_limit}`, no `step_index`, `current_waypoint.lat/lon`, and `"EMERGENCY_STOP"`. `RoverControlView` dereferences `status?.actuator.top_limit_switch` — with live data `actuator` is `undefined` → **runtime TypeError** (the optional chain guards `status` only). The E-STOP banner never appears in live mode because the string never matches.
3. **HIGH — Prescriptions are not computed from data.** All 7 zone prescriptions (N/P/K deficits, dosages, agronomy notes) are string literals inside `ml/pipeline.py`. The DB `FertilizerPrescriptionModel` rows, both dashboards, and the CSV export merely render these constants. If the synthetic generator's zone intensities change, prescriptions silently diverge from the map.
4. **HIGH — Every pipeline run wipes the database.** `run_full_ml_pipeline` deletes all 5 tables first; `POST /api/dataset/generate` triggers the same in the background. Any live rover samples collected since the last seeding are destroyed. Also wipes `M_TEST`/demo missions — a data-integrity landmine during a live demo if someone clicks "regenerate".
5. **HIGH — "Real" hardware abstraction is a façade.** `RealGPS.read_coordinates()` returns the plantation center; `RealModbusSoilSensor.read_soil_parameters()` returns a hardcoded dummy register dict (never touches a serial port); `RealESP32Rover` is advertised in the README but does not exist. `settings.MOCK_MODE` is never read by the state machine or anywhere else — the switch documented in the README does nothing.
6. **HIGH — Frontend model benchmark metrics are fabricated.** `SpatialMLView.tsx` hardcodes MAE/RMSE/R² per model ("EfficientNet 4.1 kg/ha, R² 0.96"). The real `models/metrics_summary.json` says the opposite: RF beats the "EfficientNet" MLP on every NPK target, and the MLP's health R² is 0.483. The "4.3× better than IDW" claim is invented. Any evaluator diffing UI numbers against the metrics file will catch this.
7. **MEDIUM — ESP32 firmware does not implement the sensing/autonomy it advertises.** No BN-880 NMEA parsing, no autonomous waypoint navigation, and `modbusSerial` is opened but **never read or written** — `current_ph…current_k` are constants. The "Modbus decoder on ESP32" story exists only in Python. The rover is a manually-driven demo cart with limit-switch safety, which is fine — but the README claims otherwise.
8. **MEDIUM — Streamlit "IoT & System Health" tab always shows ONLINE** for ESP32, ROS 2, DB, and PyTorch regardless of actual state. Combined with item 6, the dashboards overstate system truth.
9. **MEDIUM — Docker compose has no seeding step.** The backend container starts with an empty `data/` volume unless the host's DB is bind-mounted with data; no init job runs the pipeline. `docker-compose up` yields empty dashboards.
10. **LOW — POST /api/telemetry drops context fields.** The insert omits `organic_carbon`, `soil_health_index`, `soil_texture`, `mulberry_variety`, `probe_depth_cm`, `battery_soc`, `raw_modbus_hex`, `mission_name`, `temperature` is stored but the hex payload is not — live samples silently fall back to column defaults, skewing averages (`avg_soil_health` etc.).
11. **LOW — `/api/predictions` fallback mislabels data.** If the requested `model_type` has no rows it returns *all* rows while stamping the response `model_type=<requested>`, so a heatmap can be labeled "EfficientNet" while containing IDW points.

---

## E. Bugs and Potential Bugs

| # | Severity | Location | Bug |
|---|---|---|---|
| E1 | ~~CRITICAL~~ **RESOLVED (audit false negative)** | `ros2_ws/src/rover_interfaces/msg/` | `SoilTelemetry.msg` is present, tracked, and byte-identical to the original from commit `80e2e38`; field usage in `simulator_node.py` is fully consistent. Remaining (MEDIUM): interface never verified by `colcon build`; no CI. |
| E2 | **HIGH** | `frontend/src/views/RoverControlView.tsx` + `types/telemetry.ts` | Live-mode crash on `status?.actuator.*`; E-STOP state string mismatch (`E_STOP` vs `EMERGENCY_STOP`); waypoint field names differ (`lat/lon` vs `latitude/longitude`). |
| E3 | **HIGH** | `ml/pipeline.py` | Destructive wipe + per-row commits; combined with `dataset_api /generate` reachable from the UI. |
| E4 | **HIGH** | `demo.py` | All subprocesses use `stdout=PIPE, stderr=PIPE` and are never drained — uvicorn/vite logging will fill the OS pipe buffer (~64 KB) and **block the child process**, hanging the demo. Also `shell=True` for npm and no dependency on `npm install` having been run. |
| E5 | **MEDIUM** | `modbus_decoder.decode_hex_payload` | (a) Ignores the documented register map: indexes words from 0 instead of honoring start address, so it only works for the exact 7-register frame; (b) `temperature` register `0x0001` is decoded by neither path — temperature is silently absent from any hex decode; (c) `byte_count` is not validated against actual payload length → can read out of frame bounds; (d) CRC is never verified (the generator's "CRC" is an XOR constant, not CRC-16/MODBUS); (e) on any parse failure it **returns plausible default values** — a broken sensor frame becomes a "valid" 45 %/6.8 pH sample. |
| E6 | **MEDIUM** | `telemetry.py` | `is_valid=valid` is dead logic — `validate_reading` failure raises HTTP 400 first, so `is_valid` is always True; the invalid-sample-with-quarantine-flag path is untestable. |
| E7 | **MEDIUM** | `analysis.py` | `/api/analysis/{id}` recomputes agronomy from the observation instead of reading the stored `SoilAnalysisModel` — two sources of truth that can diverge; also `datetime.utcnow` naive timestamps everywhere (deprecated, TZ-less). |
| E8 | **MEDIUM** | `simulator_api.py` | Module-level `RoverStateMachine` singleton mutated by every request without locking — concurrent Streamlit+React stepping interleaves states nondeterministically. |
| E9 | **MEDIUM** | `state_machine.py` | Waypoint-reached threshold `0.00003°` ≈ **3.3 m**, not the documented 0.5 m (0.5 m ≈ 0.0000045°). Doc/impl mismatch; harmless with MockGPS interpolation but wrong for real GPS. |
| E10 | **MEDIUM** | firmware `.ino` | `bottomLimitISR` transitions to INTERROGATION but nothing ever exits INTERROGATION (no timeout, no Modbus read) → state deadlock; ISRs call non-trivial code with a shared `volatile` enum and no debounce; estop is unrecoverable without power-cycle (no reset endpoint in firmware). |
| E11 | **MEDIUM** | `config.py` | `DATABASE_URL` default is absolute to `BASE_DIR`, but `.env.example` ships `sqlite:///./data/...` (cwd-relative) → results differ depending on launch directory; `WIFI_PASSWORD` hardcoded in code, never read from env; many YAML-backed fields aren't overridable via env despite the naming suggesting they are. |
| E12 | **LOW** | `models.py`/`connection.py` | FKs declared but SQLite `PRAGMA foreign_keys` is off → orphan observations possible; `missions.py` does 3 queries per mission (N+1); `dataset_api /statistics` loads every row into pandas. |
| E13 | **LOW** | `predictions.py` | Response `timestamp` is `utcnow()` at request time — fabricated metadata, not the model's generation time. |
| E14 | **LOW** | `Streamlit app.py` | Pydeck `map_style="mapbox://styles/mapbox/dark-v10"` requires a Mapbox token that is nowhere configured; pydeck render may fail/fallback silently. |
| E15 | **LOW** | `SamplesView.tsx` | Timestamp shown via `toLocaleTimeString()` only — the date component is invisible. |
| E16 | **LOW** | `StatusBadge.tsx`/`RoverState` | `EMERGENCY_STOP` has no dedicated badge style (only `E_STOP` does). |

---

## F. Architecture Problems

1. **HIGH — Inverted data flow (pipeline owns the DB).** The README describes DB→ML; the code does ML→DB with a destructive seed. The cleanest incremental fix (preserve current behavior for demos) is a `--seed` flag/`SEED_DB=false` default and computing prescriptions from the stored observations.
2. **HIGH — No single source of truth for zones/geometry.** The 7-zone definition, centers, intensities, and waypoints are duplicated in `synthetic_generator.py`, `hardware_interface.MockSoilSensor`, `state_machine.py` (hardcoded waypoint list that also ignores `config.yaml` waypoints), `dataset_api.py` (a third copy of zone metadata), and `pipeline.py` (a fourth, prose copy). Any change must be made 4×.
3. **HIGH — "Dual-mode" simulation split-brain.** There are three simulators of the same rover: `MockRover`+`RoverStateMachine` (Python), the ESP32 firmware state machine, and `mockData.ts` (browser). They share no protocol definition, which is exactly why E2 exists. A single schema (even just the OpenAPI JSON served to the TS codegen) would prevent recurrence.
4. **MEDIUM — State machine ignores configuration.** `config.yaml` `state_machine.waypoints` is loaded by Settings but never used; the state machine hardcodes 8 different waypoints. Config file is partially decorative.
5. **MEDIUM — Runtime inference path absent.** Models are trained and their grids frozen into the DB; `save()/load()` are never used by the API. Fine for the demo, but it means "predictions" can never reflect freshly collected rover data — the one thing the project narrative promises.
6. **LOW — `requirements.txt` unpinned (`>=` only), no lockfile; heavyweight deps (torch, torchvision, pandas, pydeck) in the backend image that serves JSON.**

---

## G. Security / Reliability Problems

1. **HIGH — Secrets committed to git.** `.env` is tracked (contains WiFi password), `WIFI_PASSWORD` is hardcoded in `config.py` **and** in the firmware source, and the `.env.example` contains the real password too. Rotate before any public submission.
2. **HIGH — CORS `allow_origins=["*"]` together with `allow_credentials=True`** (invalid per spec; browsers reject the combination, and if it worked it would be an injection risk). Should be an explicit localhost list.
3. **HIGH — Destructive endpoints have no auth or confirmation:** `DELETE /api/dataset/clear` (wipes everything), `POST /api/dataset/generate` (background retrain + wipe), `POST /api/simulator/estop`, `/reset`, firmware `/api/estop` and `/api/drive` (anyone on the rover's WiFi can drive it). Acceptable for a closed lab demo; must be stated in the report/viva.
4. **MEDIUM — Modbus failure masking (E5e):** decoder returns plausible defaults on parse errors — the worst possible failure mode for a sensor system (bad data looks good). Should return an error flag and set `is_valid=False`.
5. **MEDIUM — No request size/rate limits, no auth on telemetry ingestion** — anyone can flood the DB. Low real risk for the demo; note it.
6. **LOW — SQLite + `check_same_thread=False`** with no `BEGIN` discipline; concurrent Streamlit+React writes can hit `database is locked` under load.

---

## H. Backend / API Problems

1. **HIGH — Schema drift with frontend** (E2) — the API contract exists only implicitly.
2. **MEDIUM — `POST /api/telemetry` drops fields** (D10) — simulator path stores them, ROS/ESP32 path doesn't; the two ingestion paths produce differently-shaped rows.
3. **MEDIUM — `run_cycle` is "best effort":** max 5 steps then break; a full TRANSIT approach can take more than 5 steps at `step_ratio=0.35`, so a "complete cycle" can return mid-TRANSIT. Also returns the loop's internal list, not a guarantee.
4. **MEDIUM — `analysis` endpoint recomputes instead of reading stored analysis** (E7).
5. **LOW — N+1 mission queries; `raw` and `statistics` endpoints unindexed full scans; predictions fallback mislabeling (D11); no pagination on `/api/samples` (limit capped 5000 but default list views pull 3000 rows into Streamlit/React).**

---

## I. Database Problems

1. **HIGH — No migrations.** `Base.metadata.create_all` at startup; schema changes require manual DB deletion. Any column you add during improvement work will silently not exist in the committed 4.3 MB `data/precision_sericulture.db` that ships in git (which itself is a problem: a binary DB in VCS will conflict with code state).
2. **MEDIUM — Pipeline commits per row** (3000+ commits); no `bulk_save_objects`/`executemany`, no single transaction, no rollback handling — seeding is slow and non-atomic.
3. **MEDIUM — Test pollution:** tests run against the dev DB (no fixture override of `DATABASE_URL`); `S_TEST_*` and `M_TEST_001` rows are already committed. Also `/api/dataset/clear` leaves the simulator's counters/mission state inconsistent.
4. **LOW — `spatial_predictions` has no uniqueness constraint on (`model_type`,`grid_x`,`grid_y`)** — re-running partial pipeline stages can duplicate grids (currently masked because everything is deleted first).
5. **LOW — `MissionModel` upsert race:** two concurrent first-telemetry posts can both fail the lookup and double-insert (unique constraint raises → 500).

---

## J. ML / Data Problems *(the synthetic-data question)*

1. **CRITICAL (for the report/viva, not for runtime) — the ML pipeline is trained exclusively on synthetic data, and the evaluation is circular.**
   - Features are `(latitude, longitude)` only; targets include `n_deficiency = max(350 − nitrogen, 0)` where `nitrogen` is itself a deterministic function of `(lat, lon)` plus noise, generated by the same Gaussian-zone formulas the models are asked to learn. The high R² (0.94–0.97) measures *the generator's own analytic functions*, not agronomic predictive skill. There is no train/test split by space or time (random 20 % of a 200×200 m field with 1000+ points ≈ interpolation, not generalization), no cross-validation, no second plantation/seed holdout.
   - Consequences: the benchmark table is not evidence the NN beats IDW; and it doesn't — the committed metrics show RF ≥ MLP everywhere, directly contradicting the frontend claims (D6).
2. **HIGH — Misleading model naming.** `EfficientNetSpatialRegressor` is a 4-layer MLP (`Linear→BatchNorm1d→SiLU`, no convolutions, no inverted bottlenecks, no residual connections despite the docstring). In a viva, one question ("where are your MBConv blocks?") collapses the claim. Rename to e.g. `SpatialMLPRegressor`/`SiLUNet` and keep EfficientNet as future work.
3. **HIGH — Prescriptions not derived from data** (D3) — the "agronomy engine" output that users see per-zone is disconnected from the engine itself.
4. **MEDIUM — IDW has no metrics at all** — it's the baseline the other two are compared against, yet `metrics_summary.json` contains no IDW errors (easy to add: evaluate IDW on the same test split).
5. **MEDIUM — No synthetic-vs-real validation hook.** The README promises "SYNTHETIC DEMONSTRATION" labeling; neither dashboard renders any such label. This is the single cheapest honesty win available.
6. **LOW — Temperature target is a pure sine wave of sample index** (`26.5 + 2·sin(i/20)`) — it has no spatial structure, hence negative R² in the committed metrics; drop it from targets or give it spatial meaning. `MOISTURE_R2=0.683` (RF) similarly reflects clipped noise, not signal.
7. **LOW — RF/MLP `predict_grid` can emit negative pH/EC** (only deficiencies are clamped at 0); cosmetic on this data.

---

## K. Frontend / UI / UX Problems

1. **HIGH — Live-mode rover view crash + E-STOP mismatch** (E2) — the flagship interactive screen is the one most likely to break in front of an audience when the backend is on.
2. **HIGH — Fabricated benchmark numbers** (D6) — UX "success" built on false metrics.
3. **MEDIUM — No visible mock/synthetic labeling** despite README promise; the "Force Mock" toggle exists in the header (good) but data cards never say SYNTHETIC.
4. **MEDIUM — `API_BASE_URL` hardcoded to `http://localhost:8000`** in `api.ts` — works on the presenter's machine, breaks on any other device/LAN viewing, and in the Docker/nginx setup (browser still calls localhost:8000, not the nginx proxy). Needs `import.meta.env.VITE_API_URL` defaulting to localhost.
5. **MEDIUM — Polling on fixed intervals** (4–5 s) with no backoff/visibility check; three views × intervals + Header health check hammer a single-worker backend; each `OverviewView` poll also refetches when tab hidden.
6. **LOW — `HeatmapCanvas` hover tooltip shows grid values only for the 5 params; mock grid is 25×25 vs backend 50×50 (handled, but scale legend claims 50×50); no color legend normalization per model; `AgronomyView` hardcodes "92.4 % optimum / 45–50 MT/ha" marketing numbers; no loading/empty states for `/api/prescriptions` when DB empty (falls back to mock silently — can mislead).**
7. **LOW — The committed `dist/` build can drift from `src/`; 7 MB demo video tracked in `frontend/public`.**

---

## L. Testing Gaps

Covered today: state flow, estop, agronomy math, generator/IDW/RF/MLP smoke, core API happy paths, dataset zones/statistics.

Missing (ordered by value):
1. **MEDIUM — No ROS build/CI exists at all**, so interface regressions (the class of issue E1 was feared to be) would go unnoticed. There is no CI configuration in the repo; `pytest` is manual.
2. **HIGH — No DB isolation:** tests hit the dev SQLite file; need a `DATABASE_URL` override fixture (tmp file) — also fixes the committed `S_TEST_*` pollution.
3. **HIGH — Modbus decoder tests:** valid hex, wrong function code, short frame, bad CRC, byte_count mismatch, and **asserting that failures do NOT return plausible defaults** (once E5 is fixed).
4. **MEDIUM — Simulator API contract test** asserting the exact JSON shape consumed by `RoverControlView` (locks the E2 fix).
5. **MEDIUM — Prediction-grid integrity:** 2500 unique (model, x, y), no NaNs, lat/lon within plantation bounds; `/api/predictions/{parameter}` param map coverage.
6. **MEDIUM — Idempotency test:** run pipeline twice → same counts, no duplicates, and (post-fix) live rows survive.
7. **LOW — Frontend tests (none exist):** a single vitest render test per view is enough for the demo claim "tested UI".
8. **LOW — No lint/typecheck CI (`tsc -b` exists as build step only; oxlint configured but not enforced).**

---

## M. Deployment Problems

1. **HIGH — Compose stack boots empty:** no seeding job/entrypoint runs the pipeline; dashboards render fallback mock data with no indication the backend DB is empty.
2. **MEDIUM — Frontend container can't reach the backend by construction:** nginx serves static files only; browser-side `localhost:8000` only works when the host also runs the backend natively. Needs an nginx `/api` proxy or env-injected API URL.
3. **MEDIUM — No healthchecks, no `depends_on` conditions, no restart policies; compose `version` key deprecated; Streamlit `API_HOST=http://backend:8000` is correct (server-side fetch) but undocumented.**
4. **MEDIUM — Images carry the entire requirements.txt** (torch+torchvision ≈ 2 GB) into both backend and dashboard images; no `.dockerignore` (build context includes `.venv`, `.git`, `data`, `node_modules` → huge, slow, cache-busting builds).
5. **LOW — Committed DB/CSV/video/dist artifacts make fresh clones heavy (~8+ MB) and can silently diverge from code; `start.sh`/`start.bat` assume `.venv` exists and never `pip install`; demo retrains (~1–3 min CPU) on every launch — should train only if `metrics_summary.json`/models are stale.**

---

## N. Technical Debt

1. Zone/geometry constants duplicated 4× (F2). 2. Two telemetry ingestion paths with divergent field sets (H2). 3. `datetime.utcnow` naive timestamps throughout. 4. `getattr(obs, 'field', default)` defensive coding everywhere masks missing columns — it exists because the DB schema and models drifted; it hides real bugs. 5. Unpinned Python deps; unpinned transitive frontend deps with very aggressive majors. 6. Committed artifacts (DB, CSV, dist, video, `.env`). 7. Config that is read but unused (`MOCK_MODE`, waypoints, ESP32 IP) — "config theater". 8. README/`PROJECT_CONTEXT_FOR_CHATGPT.md` describe aspirations (RealESP32Rover, 0.5 m threshold, "SYNTHETIC DEMONSTRATION" labels) that the code doesn't implement — documentation debt that will be discovered live during a viva.

---

## O. Features That Should Be Added

| # | Feature | Severity (need) | Why needed | Likely files | Risk | Demo-critical? |
|---|---|---|---|---|---|---|
| O1 | Restore `SoilTelemetry.msg` (header, NavSatFix location, float32 ph/ec/moisture, int32 n/p/k, strings rover_state/mission_id/sample_id) | CRITICAL | ROS 2 is a headline claim; package currently cannot build | `ros2_ws/src/rover_interfaces/msg/SoilTelemetry.msg` | None — additive; matches `simulator_node.py` field usage exactly | **Yes** (if ROS is claimed) |
| O2 | Fix `RoverSimulatorStatus` typing + map backend fields (`hardware.*`, `lat/lon`, `EMERGENCY_STOP`) | HIGH | Prevents live-mode crash; E-STOP must visibly work on stage | `frontend/src/types/telemetry.ts`, `views/RoverControlView.tsx`, optionally normalize in `services/api.ts` | Low — additive mapping | **Yes** |
| O3 | Serve real metrics to the UI (`GET /api/ml/metrics` reading `metrics_summary.json`); render IDW row too | HIGH | Benchmark numbers must match artifacts; add IDW baseline for a 3-way comparison | `backend/app/api/` (new or analysis.py), `SpatialMLView.tsx` | Low | **Yes** (credibility) |
| O4 | Compute zone prescriptions from stored observations (group by nearest zone center; avg N/P/K/pH/EC → engine) with hardcoded prose only as fallback | HIGH | Makes the agronomy engine the actual source of the advice; survives regenerate | `ml/pipeline.py`, `backend/app/api/prescriptions.py` | Medium — must keep zone prose strings as static agronomy notes; dosages become computed | Yes (strongly recommended) |
| O5 | Non-destructive seeding: `run_full_ml_pipeline(..., reset_data=False)` default; preserve non-synthetic sample IDs; UI confirm on `/dataset/generate` | HIGH | Protects live samples; prevents accidental wipe mid-demo | `ml/pipeline.py`, `dataset_api.py`, frontend confirm dialog | Low | **Yes** |
| O6 | Synthetic-data labeling: "SYNTHETIC DEMONSTRATION" badge in Header + summary card, driven by `MOCK_MODE`/sample prefix | HIGH | README honesty promise; examiners will ask; zero functional risk | `Header.tsx`, `OverviewView.tsx`, `dashboard/app.py` | None | **Yes** |
| O7 | Secrets hygiene: stop tracking `.env`, rotate password, read `WIFI_PASSWORD` from env, fix CORS origin list | HIGH | Committed credentials + wildcard CORS | `.gitignore`, `.env`, `config.py`, `main.py`, `.ino` | Low; rotation required | For submission: yes |
| O8 | Modbus decoder hardening: honor register map incl. `0x0001` temperature, validate byte_count, verify CRC-16/MODBUS, return validity flag instead of defaults | MEDIUM | A "failure returns plausible data" decoder undermines the sensing story | `modbus_decoder.py`, `synthetic_generator.py` (emit real CRC), tests | Low; keep fallback flag-gated | Optional but cheap |
| O9 | `VITE_API_URL` + nginx `/api` proxy in Dockerfile.frontend | MEDIUM | LAN/deployed viewing works | `api.ts`, `Dockerfile.frontend`, `vite.config.ts` | Low | Nice-to-have |
| O10 | Demo robustness: drain subprocess pipes (or `stdout=None` to console), skip retraining when artifacts fresh, `npm install` guard | MEDIUM | Removes the two most likely live-demo freezes | `demo.py`, `start.sh`, `start.bat` | Low | **Yes** |
| O11 | Minimal real-HAL stubs that at least fail loudly: `RealModbusSoilSensor` using pyserial behind try/import, `MOCK_MODE` actually selecting implementations | MEDIUM | Makes the README's switch true; one command flips to hardware when the sensor arrives | `hardware_interface.py`, `state_machine.py`, `config.py` | Medium — do not let hardware errors crash the API; keep Mock default | No (post-demo) |
| O12 | DB isolation for tests + FK pragma + uniqueness on prediction grid | MEDIUM | Correct CI foundation; stops dev-DB pollution | `tests/`, `connection.py`, `models.py` | Low | No |
| O13 | Seed-on-start entrypoint for compose (`python ml/pipeline.py --seed-if-empty`) | MEDIUM | `docker-compose up` shows a full demo immediately | `Dockerfile.backend`, `docker-compose.yml` | Low | Yes (if Docker used in demo) |
| O14 | IDW metrics in `metrics_summary.json` | MEDIUM | Completes the 3-model benchmark story | `ml/pipeline.py`, `spatial_idw.py` | Low | Nice |
| O15 | Firmware: exit INTERROGATION timeout + Modbus read attempt loop (even if only wired to a simulator), estop reset endpoint | MEDIUM | Removes the deadlock state; hardware demo safe | `esp32_rover_firmware.ino` | Medium — firmware changes need bench testing | Only if hardware demo |

## P. Features That Should NOT Be Added (unnecessary for the final college demonstration)

- **Authentication/JWT/OAuth, user accounts, roles** — no threat model justifies it; a synthetic-data demo API gains nothing; skip.
- **PostgreSQL migration** — SQLite is fully sufficient for 3k rows and a single presenter; migrating adds Docker/deps risk with zero visible benefit. (Keep `DATABASE_URL` overridable as it already is.)
- **Microservices split, Kafka/RabbitMQ/Celery, Kubernetes, GraphQL** — architecture fashion; would multiply failure modes before a demo.
- **WebSocket/real-time streaming telemetry** — 4 s polling is visually identical for this data volume; WS adds connection-state bugs.
- **True convolutional/EfficientNet image model, transfer learning, satellite imagery** — there is no imagery; a real CNN on 2 features is scientifically meaningless and would burn demo-prep time. (Renaming the MLP, per J2, is the correct move.)
- **More ML models (XGBoost, GPR, kriging)** — the benchmark is already 3-way and the data is synthetic; more rows in a table prove nothing new.
- **React state management (Redux/Zustand), router, SSR/Next.js migration, i18n, PWA** — the app is 7 views; current `useState` + tabs is fine.
- **Storybook, heavy e2e (Playwright/Cypress) suites** — one vitest smoke test is the right size (L7).
- **Micro-ROS on the ESP32** — real firmware port is weeks of work; HTTP fallback + ROS 2 simulator node already demonstrates the pipeline. Don't start it for the demo.
- **Rate limiting, WAF, HTTPS termination, secrets manager** — note them in the report as future work instead of implementing.

---

## Q. Recommended Implementation Order

**Phase 0 — integrity stops (do before anything else; ~half a day total)**
1. ~~**O1** restore `SoilTelemetry.msg`~~ — **not needed; corrected finding** (message exists and is consistent). Replace with: verify `colcon build` + `ros2 interface show rover_interfaces/msg/SoilTelemetry` in a `ros:humble` container once (done in Milestone 1).
2. **O2** fix frontend simulator contract/crash (HIGH).
3. **O5** make pipeline seeding non-destructive (HIGH) — do this *before* any demo rehearsal that collects live samples.
4. **O6** SYNTHETIC labeling (HIGH, trivial).
5. **O7** secrets/CORS (HIGH).

**Phase 1 — correctness & credibility (1–2 days)**
6. **O3** real metrics endpoint + UI + IDW row; **O4** computed prescriptions; **O8** decoder hardening (+ tests per L3); **O10** demo/startup robustness.
7. **L2/L4** test-isolation + API contract tests so the E2 class of bug cannot silently return.

**Phase 2 — deployment & polish (1–2 days)**
8. **O13** compose seeding; **O9** API URL/nginx proxy; **M4** `.dockerignore` + slimmer images; **E13/E14/E15** small UI fixes; committed-artifact cleanup (DB/CSV/dist out of git, video via LFS or link).

**Phase 3 — post-demo / report enhancements**
9. **O11** real-HAL stubs with loud failures; **O12** remaining DB tests; **O15** firmware interrogation timeout + Modbus loop; **J1** methodology note in the report (spatial CV, second-seed holdout) — this is a *documentation* fix that costs an afternoon and inoculates the viva.

**Deliberately deferred:** everything in §P.

---

### Bottom line

The stack is a genuinely working demo machine: backend, state machine, agronomy math, both dashboards, and the synthetic ML pipeline all run and are covered by a passing test suite. The three things that would actually fail or embarrass in front of examiners are (1) the unverified ROS 2 toolchain (originally misreported as a missing message file — corrected above) together with the live-backend contract drift, (2) the live-backend crash on the rover control screen, and (3) the honesty gap between what the UI displays (fabricated benchmark metrics, prescriptions unconnected to data, "real" HAL that is fake) and what the code does — compounded by the pipeline's habit of wiping the database. All are fixable incrementally without replacing the architecture, in the order given in §Q.
