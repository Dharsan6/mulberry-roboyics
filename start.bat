@echo off
echo ==================================================================
echo   PRECISION SERICULTURE ROVER PLATFORM STARTUP SCRIPT (WINDOWS)   
echo ==================================================================

python -m pip install -r requirements.txt

echo Running ML Pipeline and Populating Database...
python ml/pipeline.py

echo Starting Demo Pipeline...
python demo.py
