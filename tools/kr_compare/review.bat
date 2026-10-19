@echo off
rem hero_malik (KR1) vs holy_commander (fal-lab) compare viewer: rebuilds manifest.json then
rem serves this folder on localhost so the page can fetch manifest.json and the sprite PNGs
rem (opening index.html directly as file:// blocks that fetch).
setlocal
cd /d "%~dp0"
python build_manifest.py || (pause & exit /b 1)
start "" "http://127.0.0.1:8766/"
python -m http.server 8766
