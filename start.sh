#!/bin/bash
echo "=================================================================="
echo "  PRECISION SERICULTURE ROVER PLATFORM STARTUP SCRIPT            "
echo "=================================================================="

# Detect Python interpreter (prefer local .venv)
if [ -d ".venv" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python interpreter: $PYTHON_CMD"

# Run ML Data Pipeline & Model Training
echo "Running ML Pipeline and Populating Database..."
$PYTHON_CMD ml/pipeline.py

# Launch Demonstration Launcher
echo "Starting Demo Pipeline..."
$PYTHON_CMD demo.py
