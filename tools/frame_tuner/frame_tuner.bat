@echo off
rem Frame Tuner (local): builds the frame sheets from raw/ clips (skips states already built), starts a local server and opens
rem the browser. Recipes are saved straight into out\heroes\holy_commander\export_recipe.json.
rem Needs python (numpy, Pillow) and ffmpeg on PATH, like the other video tools.
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
"%PY%" build_states.py || (echo Build failed: check python, numpy, Pillow and ffmpeg. & pause & exit /b 1)
start "" "http://127.0.0.1:8767/"
"%PY%" serve.py 8767
