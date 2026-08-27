#!/bin/bash
echo "=================================================================="
echo "  PRECISION SERICULTURE ROVER PLATFORM STARTUP SCRIPT            "
echo "=================================================================="

# Check Python environment
python3 -m pip install -r requirements.txt

# Run ML Data Pipeline & Model Training
echo "Running ML Pipeline and Populating Database..."
python3 ml/pipeline.py

# Launch Demonstration Launcher
echo "Starting Demo Pipeline..."
python3 demo.py
