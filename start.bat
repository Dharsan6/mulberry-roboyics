@echo off
echo ==================================================================
echo   PRECISION SERICULTURE ROVER PLATFORM STARTUP SCRIPT (WINDOWS)   
echo ==================================================================

if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

echo Using Python interpreter: %PYTHON_CMD%

echo Running ML Pipeline and Populating Database...
%PYTHON_CMD% ml/pipeline.py

echo Starting Demo Pipeline...
%PYTHON_CMD% demo.py
