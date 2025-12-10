@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo Retro Snake Screensaver - Build
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Check if pyinstaller is installed
"venv\Scripts\python.exe" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    "venv\Scripts\pip.exe" install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Building screensaver executable...
echo.

REM Build with PyInstaller using spec file (if exists) or direct command
if exist "RetroSnake.spec" (
    echo Using RetroSnake.spec...
    "venv\Scripts\pyinstaller.exe" RetroSnake.spec
) else (
    echo Building from retro_snake\main.py...
    "venv\Scripts\pyinstaller.exe" --onefile --noconsole --name "RetroSnake" --icon=snake_icon.ico retro_snake\main.py
)

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Check if dist\RetroSnake.exe exists
if not exist "dist\RetroSnake.exe" (
    echo ERROR: Build output not found: dist\RetroSnake.exe
    pause
    exit /b 1
)

echo.
echo Renaming executable to .scr format...

REM Find next available filename
set "SCR_FILE=dist\RetroSnake.scr"
set "NUM=0"

if exist "%SCR_FILE%" (
    REM File exists, find next number
    set "NUM=1"
    :find_next
    if !NUM! LSS 10 (
        set "NUM_STR=0!NUM!"
    ) else (
        set "NUM_STR=!NUM!"
    )
    set "SCR_FILE=dist\RetroSnake!NUM_STR!.scr"
    if exist "!SCR_FILE!" (
        set /a NUM+=1
        goto find_next
    )
)

REM Rename exe to scr
move /y "dist\RetroSnake.exe" "%SCR_FILE%" >nul
if errorlevel 1 (
    echo ERROR: Failed to rename executable
    pause
    exit /b 1
)

echo Renamed to: %SCR_FILE%
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Screensaver created: %SCR_FILE%
echo.
echo To install as screensaver:
echo   1. Right-click %SCR_FILE% and select "Install"
echo   OR copy to C:\Windows\System32\
echo.
echo Test commands:
echo   %SCR_FILE% /s  - Run screensaver
echo   %SCR_FILE% /c  - Configure
echo   %SCR_FILE% /p  - Preview
echo.
pause
