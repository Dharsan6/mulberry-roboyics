import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import time
import subprocess
import webbrowser
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [DEMO] - %(message)s")

def run_demo():
    logging.info("==================================================================")
    logging.info("  PRECISION SERICULTURE: AUTOMATED SOIL PROBING ROVER DEMO      ")
    logging.info("==================================================================")

    # 1. Run ML Pipeline & Data Generation
    logging.info("STEP 1: Executing ML Pipeline (Synthetic Plantation, IDW, RF Baseline & EfficientNet)...")
    from ml.pipeline import run_full_ml_pipeline
    metrics = run_full_ml_pipeline(num_samples=1000)
    logging.info("ML Pipeline completed successfully!")

    # 2. Start FastAPI Backend in background
    logging.info("STEP 2: Launching FastAPI Backend on http://localhost:8000 ...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for backend health
    backend_ready = False
    for attempt in range(15):
        try:
            resp = requests.get("http://localhost:8000/health", timeout=1.0)
            if resp.status_code == 200:
                backend_ready = True
                logging.info("FastAPI Backend is ONLINE!")
                break
        except Exception:
            pass
        time.sleep(1.0)

    if not backend_ready:
        logging.error("FastAPI Backend failed to respond within 15 seconds.")
        backend_process.terminate()
        sys.exit(1)

    # 3. Simulate Rover State Machine Waypoint Steps
    logging.info("STEP 3: Running Rover State Machine Simulation (TRANSIT -> DEPLOYMENT -> INTERROGATION -> RETRACTION)...")
    try:
        from backend.app.services.state_machine import RoverStateMachine
        sm = RoverStateMachine(stabilization_seconds=1)
        for i in range(15):
            status = sm.step()
            state = status["rover_state"]
            wp = status["current_waypoint"]["id"]
            gps = status["gps"]
            logging.info(f"Step {i+1:02d}: Rover State = [{state}] | Target = {wp} | Lat = {gps['latitude']:.6f}, Lon = {gps['longitude']:.6f}")
            
            # Post telemetry to backend if available
            if status.get("latest_telemetry"):
                try:
                    requests.post("http://localhost:8000/api/telemetry", json=status["latest_telemetry"], timeout=1.0)
                except Exception:
                    pass
            time.sleep(0.5)
    except Exception as e:
        logging.warning(f"Simulator step execution warning: {e}")

    # 4. Launch Streamlit Dashboard
    logging.info("STEP 4: Launching Streamlit Dashboard on http://localhost:8501 ...")
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port=8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(3.0)
    webbrowser.open("http://localhost:8501")

    logging.info("==================================================================")
    logging.info("  DEMO RUNNING! Press Ctrl+C in terminal to stop all services.   ")
    logging.info("==================================================================")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        logging.info("Shutting down demonstration services...")
        backend_process.terminate()
        dashboard_process.terminate()
        logging.info("Demo stopped cleanly.")

if __name__ == "__main__":
    run_demo()
