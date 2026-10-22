@echo off
rem Fx Studio (local): sprite sheet of a 2D effect -> Kingdom Rush 1 frames, tuned in the browser and installed into the game.
rem Needs python with numpy, Pillow, scipy, vtracer and resvg-py (pip install -r requirements.txt). Game folder: KR1_GAME_DIR
rem (default E:\work\reverse\games\kr1).
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
start "" "http://127.0.0.1:8768/"
"%PY%" serve.py 8768
