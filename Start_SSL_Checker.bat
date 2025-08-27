@echo off
title SSL Certificate Checker v3.0
setlocal enabledelayedexpansion

cls
echo.
echo ================================================================
echo                SSL Certificate Checker v3.0
echo              Enhanced UI with Chain Visualization
echo                   No OpenSSL Required!
echo ================================================================
echo.

echo [STEP 1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python OK!

echo.
echo [STEP 2/4] Checking cryptography library...
python -c "import cryptography" >nul 2>&1
if %errorlevel% neq 0 (
    echo cryptography library not found. Installing...
    echo This may take 1-2 minutes...
    echo.
    python -m pip install cryptography
    
    if !errorlevel! neq 0 (
        echo.
        echo Installation failed!
        echo Please run: pip install cryptography
        echo.
        pause
        exit /b 1
    )
    echo cryptography installed successfully!
) else (
    echo cryptography library OK!
)

echo.
echo [STEP 3/4] Checking tkinterdnd2 library (for drag-and-drop)...
python -c "import tkinterdnd2" >nul 2>&1
if %errorlevel% neq 0 (
    echo tkinterdnd2 library not found. Installing for drag-and-drop support...
    echo.
    python -m pip install tkinterdnd2
    
    if !errorlevel! neq 0 (
        echo.
        echo tkinterdnd2 installation failed (non-critical)
        echo App will still work without drag-and-drop from File Explorer
        echo.
    ) else (
        echo tkinterdnd2 installed successfully! Drag-and-drop enabled.
    )
) else (
    echo tkinterdnd2 library OK! Full drag-and-drop support available.
)

echo.
echo [STEP 4/4] Starting SSL Certificate Checker...
echo ================================================================
echo.

python ssl_checker_v3.py

if %errorlevel% neq 0 (
    echo.
    echo Application closed with error.
    echo Check if all files are present and try again.
    echo.
    pause
) else (
    echo.
    echo Application closed successfully.
)