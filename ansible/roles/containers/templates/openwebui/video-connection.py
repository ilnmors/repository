#!/usr/bin/env python3
"""Register the video connection in a running Open WebUI.

Open WebUI 0.13 has no environment variable for video connections, and with ENABLE_PERSISTENT_CONFIG=false a
connection set in the admin UI is lost on restart. The container file runs this script inside the container
after every start: it waits for the API and posts the connection from VIDEO_CONNECTION_CONFIG with an admin
API key (OPEN_WEBUI_ADMIN_API_KEY; API_KEYS_ALLOWED_ENDPOINTS lets keys reach only this admin route besides
the model routes, and the route itself still requires an admin). Standard library only.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:%s" % os.environ.get("PORT", "8080")
KEY = os.environ["OPEN_WEBUI_ADMIN_API_KEY"]
CONFIG = json.loads(os.environ["VIDEO_CONNECTION_CONFIG"])

deadline = time.time() + 900
while True:
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=10) as response:
            if response.status == 200:
                break
    except (urllib.error.URLError, OSError):
        pass
    if time.time() > deadline:
        sys.exit("Open WebUI did not answer /health within 15 minutes")
    time.sleep(5)

request = urllib.request.Request(BASE + "/api/v1/videos/config/update", data=json.dumps(CONFIG).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        print("video connection registered:", response.status)
except urllib.error.HTTPError as error:
    sys.exit("video connection failed: %s %s" % (error.code, error.read()[:300]))
