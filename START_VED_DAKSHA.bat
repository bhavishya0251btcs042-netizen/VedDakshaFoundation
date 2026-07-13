@echo off
title Ved Daksha Foundation — Local Server (Python)
color 0A

echo.
echo  ============================================================
echo    VED DAKSHA FOUNDATION — Local Development Server
echo    Vayam Rashtre Jagryam
echo  ============================================================
echo.

:: ── CHECK PYTHON ──
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Python is NOT installed on this computer.
    echo.
    echo  Please install Python 3.11+ from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo  [OK] Python found: 
python --version
echo.

:: ── LOCATE PROJECT FOLDER ──
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "ENV_FILE=%BACKEND_DIR%\.env"

echo  [INFO] Project folder : %SCRIPT_DIR%
echo  [INFO] Backend folder : %BACKEND_DIR%
echo.

:: ── CHECK BACKEND FOLDER EXISTS ──
if not exist "%BACKEND_DIR%" (
    color 0C
    echo  [ERROR] backend\ folder not found.
    echo  Make sure this .bat file is in the same folder as:
    echo    - index.html
    echo    - blog.html
    echo    - admin\
    echo    - backend\
    echo.
    pause
    exit /b 1
)

:: ── CHECK .ENV FILE ──
if not exist "%ENV_FILE%" (
    color 0E
    echo  [WARNING] .env file not found in backend\ folder.
    echo.
    echo  Copying .env.example to .env ...
    if exist "%BACKEND_DIR%\.env.example" (
        copy "%BACKEND_DIR%\.env.example" "%ENV_FILE%" >nul
        echo  [OK] .env created from .env.example
        echo.
        echo  IMPORTANT: Open backend\.env and fill in your:
        echo    - MONGODB_URI   ^<from MongoDB Atlas^>
        echo    - JWT_SECRET    ^<any long random string^>
        echo    - EMAIL_USER    ^<your Gmail^>
        echo    - EMAIL_PASS    ^<Gmail App Password^>
        echo.
        echo  Continuing in 3 seconds...
        timeout /t 3 >nul
    ) else (
        echo  [ERROR] .env.example also not found. Cannot start.
        pause
        exit /b 1
    )
)

:: ── CREATE VIRTUAL ENVIRONMENT IF NOT EXISTS ──
if not exist "%BACKEND_DIR%\.venv" (
    echo  [INFO] Creating virtual environment .venv ...
    python -m venv "%BACKEND_DIR%\.venv"
    if %errorlevel% neq 0 (
        color 0C
        echo  [ERROR] Failed to create Python virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
    echo.
)

:: ── INSTALL PYTHON DEPENDENCIES ──
echo  [INFO] Verifying/installing dependencies...
call "%BACKEND_DIR%\.venv\Scripts\pip" install -r "%BACKEND_DIR%\requirements.txt"
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo  [OK] Dependencies verified.
echo.

:: ── START BACKEND SERVER IN NEW WINDOW ──
echo  [INFO] Starting backend API server on port 5000...
start "VDF Backend API (FastAPI) — Port 5000" cmd /k "cd /d "%BACKEND_DIR%" && .venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 5000"

:: ── WAIT FOR SERVER TO START ──
echo  [INFO] Waiting for server to start...
timeout /t 4 /nobreak >nul

:: ── FIRST-TIME ADMIN SETUP ──
echo  [INFO] Running first-time admin setup (safe to ignore if already done)...
curl -s -X POST http://localhost:5000/api/auth/setup >nul 2>&1
echo  [OK] Admin setup attempted (no action if already exists).
echo.

:: ── OPEN WEBSITE IN BROWSER ──
echo  ============================================================
echo   Opening website in your browser...
echo  ============================================================
echo.
echo   Main Website  :  http://localhost:5000/
echo   Admin Portal  :  http://localhost:5000/admin/
echo   Blog Page     :  http://localhost:5000/blog/
echo   Backend API   :  http://localhost:5000/api/health
echo.

:: Open main site via server URL
start "" "http://localhost:5000/"
timeout /t 1 /nobreak >nul

:: Open admin portal via server URL
start "" "http://localhost:5000/admin/"
timeout /t 1 /nobreak >nul

echo  ============================================================
echo   SERVER IS RUNNING (Python FastAPI)
echo  ============================================================
echo.
echo   Backend API  : http://localhost:5000
echo   Health Check : http://localhost:5000/api/health
echo.
echo   Default Admin Login:
echo     Email    : (check backend\.env — ADMIN_EMAIL)
echo     Password : (check backend\.env — ADMIN_PASSWORD)
echo.
echo   To stop the server, close the "VDF Backend API" window.
echo.
echo   TIPS:
echo   - Fill in MONGODB_URI in backend\.env for full functionality
echo   - The website works without MongoDB (static content only)
echo   - Run this .bat again anytime to restart everything
echo.
echo  ============================================================
echo.
pause
