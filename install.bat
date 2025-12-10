@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo Retro Snake Screensaver - Installation
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM [1/4] Verify Python Installation
echo [1/4] Verifying Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later and add it to your PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: !PYTHON_VERSION!
echo.

REM [2/4] Create Virtual Environment
echo [2/4] Creating virtual environment...
if exist "venv" (
    echo WARNING: Virtual environment already exists
    echo Reusing existing venv...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Verify venv
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment is incomplete
    echo Removing incomplete venv...
    rmdir /s /q venv
    pause
    exit /b 1
)

if not exist "venv\Scripts\pip.exe" (
    echo ERROR: pip not found in virtual environment
    pause
    exit /b 1
)

echo Virtual environment verified
echo Python: venv\Scripts\python.exe
echo pip: venv\Scripts\pip.exe
echo.

REM [3/4] Upgrade pip
echo [3/4] Upgrading pip...
"venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
) else (
    echo pip upgraded successfully
)
echo.

REM [4/4] Install Dependencies
echo [4/4] Installing dependencies...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

"venv\Scripts\pip.exe" install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Verifying key dependencies...
"venv\Scripts\python.exe" -c "import pygame; print('  [OK] pygame')" 2>nul || echo "  [FAIL] pygame"
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the screensaver, use: run.bat
echo For windowed mode: run.bat -w
echo Or manually: venv\Scripts\python.exe snake_screensaver.py
echo.
pause
