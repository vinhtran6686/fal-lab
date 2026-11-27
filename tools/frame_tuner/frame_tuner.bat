@echo off
rem Frame Tuner (sprite prep): double-click to open. Splits lineup clips into frames, cleans them, picks frames,
rem previews at game size and exports sheets into out\<class>\<id>\frames\. Everything stays on this computer.
rem Needs: Python 3.10+ with numpy, scipy, Pillow, and ffmpeg on PATH. Close this window to stop the tool.
setlocal
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
cd /d "%~dp0"
set "PORT=8767"

rem ---- find Python (the Microsoft Store stub is skipped when a real install exists) ----
set "PY="
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PY set "PY=python"
"%PY%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo [Frame Tuner] Python 3.10 or newer was not found.
  echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)

rem ---- packages ----
"%PY%" -c "import numpy, scipy, PIL" >nul 2>&1
if errorlevel 1 (
  echo [Frame Tuner] Missing Python packages: numpy, scipy or Pillow.
  choice /m "Install them now with pip (requirements.txt)"
  if errorlevel 2 exit /b 1
  "%PY%" -m pip install -r "%~dp0..\..\requirements.txt"
  "%PY%" -c "import numpy, scipy, PIL" >nul 2>&1
  if errorlevel 1 (
    echo [Frame Tuner] The install did not work. Run:  python -m pip install numpy scipy pillow
    pause
    exit /b 1
  )
)

rem ---- ffmpeg ----
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo [Frame Tuner] ffmpeg is not on PATH: splitting clips will fail.
  echo Install it with:  winget install Gyan.FFmpeg   then open a new window.
  echo The tool still opens; you can browse clips that are already split.
  echo.
)

rem ---- already running? just open the browser ----
"%PY%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:%PORT%/api/ping', timeout=1)" >nul 2>&1
if not errorlevel 1 (
  start "" "http://127.0.0.1:%PORT%/"
  exit /b 0
)

rem ---- start the server, open the browser once it answers ----
start "" /b "%PY%" open_when_ready.py %PORT%
echo [Frame Tuner] http://127.0.0.1:%PORT%/   (close this window to stop)
"%PY%" serve.py %PORT%
if errorlevel 1 (
  echo [Frame Tuner] The server stopped with an error ^(see above^). Is port %PORT% used by another program?
  pause
)
