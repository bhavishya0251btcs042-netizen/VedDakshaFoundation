@echo off
title Ved Daksha Foundation — START
color 0A
cls

echo.
echo  ============================================================
echo    VED DAKSHA FOUNDATION  -  Starting...
echo    Vayam Rashtre Jagryam - Vayam Rashtre Jagryam
echo  ============================================================
echo.

:: ─── PATHS ──────────────────────────────────────────────────────
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "ENV_FILE=%BACKEND%\.env"
set "VENV=%BACKEND%\.venv"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"
set "UVICORN=%VENV%\Scripts\uvicorn.exe"
set "REQ=%BACKEND%\requirements.txt"

:: ─── CHECK PYTHON ────────────────────────────────────────────────
echo  Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Python NOT found.
    echo  Download from: https://www.python.org/downloads/
    echo  (Check "Add Python to PATH" during install)
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>nul') do set PYVER=%%v
echo  [OK] %PYVER%

:: ─── CHECK PROJECT STRUCTURE ─────────────────────────────────────
if not exist "%BACKEND%\app\main.py" (
    color 0C
    echo.
    echo  [ERROR] backend\app\main.py not found.
    echo  Make sure START.bat is in the same folder as:
    echo    index.html, blog.html, admin\, backend\
    echo.
    pause
    exit /b 1
)
echo  [OK] Project structure found.

:: ─── CHECK .ENV ──────────────────────────────────────────────────
if not exist "%ENV_FILE%" (
    echo.
    echo  [INFO] Creating .env from .env.example...
    if exist "%BACKEND%\.env.example" (
        copy "%BACKEND%\.env.example" "%ENV_FILE%" >nul
        echo  [OK] .env created. Edit it to add your MongoDB URI.
        timeout /t 2 /nobreak >nul
    ) else (
        echo  [WARNING] No .env file found. Server will run in demo mode.
    )
)
echo  [OK] Environment config ready.

:: ─── CREATE VIRTUAL ENVIRONMENT ──────────────────────────────────
if not exist "%VENV%\Scripts\python.exe" (
    echo.
    echo  [INFO] Creating Python virtual environment...
    python -m venv "%VENV%"
    if %errorlevel% neq 0 (
        color 0C
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
)

:: ─── INSTALL DEPENDENCIES ────────────────────────────────────────
echo.
echo  [INFO] Installing/verifying Python packages...
"%PIP%" install -r "%REQ%" -q 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  [ERROR] Package installation failed. Check internet connection.
    pause
    exit /b 1
)
echo  [OK] Packages ready.

:: ─── KILL EXISTING PROCESS ON PORT 5000 ─────────────────────────
echo.
echo  Checking port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo  [OK] Port 5000 is free.

:: ─── START FASTAPI SERVER ────────────────────────────────────────
echo.
echo  [INFO] Starting FastAPI server on http://localhost:5000
cd /d "%BACKEND%"
start "VDF FastAPI Server" cmd /k "cd /d "%BACKEND%" && .venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"

:: ─── WAIT FOR SERVER TO BE READY ─────────────────────────────────
echo  [INFO] Waiting for server to start...
set /a tries=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
set /a tries+=1
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 goto SERVER_READY
if %tries% lss 10 goto WAIT_LOOP
echo  [INFO] Server still starting, opening browser...
goto OPEN_BROWSER

:SERVER_READY
echo  [OK] Server is running!

:: ─── FIRST-TIME ADMIN SETUP ──────────────────────────────────────
echo.
echo  [INFO] Running first-time admin setup...
curl -s -X POST http://localhost:5000/api/auth/setup >nul 2>&1
echo  [OK] Admin account ready.

:: ─── OPEN BROWSER (via localhost — NOT file://) ──────────────────
:OPEN_BROWSER
echo.
echo  [INFO] Opening website in browser...
timeout /t 1 /nobreak >nul
start "" http://localhost:5000
timeout /t 2 /nobreak >nul
start "" http://localhost:5000/admin

:: ─── DONE ────────────────────────────────────────────────────────
cls
echo.
echo  ============================================================
echo    VED DAKSHA FOUNDATION  -  RUNNING!
echo  ============================================================
echo.
echo    Main Website  :  http://localhost:5000
echo    Admin Portal  :  http://localhost:5000/admin
echo    Blog          :  http://localhost:5000/blog
echo    API Docs      :  http://localhost:5000/docs
echo    Health Check  :  http://localhost:5000/api/health
echo.
echo  ============================================================
echo    ADMIN LOGIN:
echo  ============================================================
echo.
echo    Email     :  admin@veddakshafoundation.org
echo    Password  :  VedDaksha@Admin2024
echo    (Change these in backend\.env)
echo.
echo  ============================================================
echo    FEATURES:
echo  ============================================================
echo.
echo    Language Toggle  :  Click HINDI / ENGLISH button (top right)
echo    Dark Mode        :  Click DARK / LIGHT button (top right)
echo    Both work on     :  Main website AND Admin portal
echo.
echo  ============================================================
echo.
echo    Press any key to STOP server and exit.
echo.
pause >nul

:: ─── STOP SERVER ─────────────────────────────────────────────────
echo  Stopping server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo  Done. Goodbye!
timeout /t 2 /nobreak >nul
exit /b 0
