"""Open the browser once the local server answers (used by frame_tuner.bat). Usage: python open_when_ready.py [port]"""
import sys
import time
import urllib.request
import webbrowser

port = sys.argv[1] if len(sys.argv) > 1 else "8767"
url = f"http://127.0.0.1:{port}/"
for _ in range(120):
    try:
        urllib.request.urlopen(url + "api/ping", timeout=1)
        break
    except Exception:
        time.sleep(0.5)
webbrowser.open(url)
