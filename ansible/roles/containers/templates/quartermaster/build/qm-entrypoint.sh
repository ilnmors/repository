#!/bin/sh
# Start the OpenAI video adapter (/v1/videos for Open WebUI) next to Quartermaster when it is mounted, then run
# the upstream entrypoint. The adapter talks to this Quartermaster on loopback and keeps no state; if it stops,
# the next container start brings it back.
if [ -f /opt/quartermaster/video/adapter.py ]; then
  python3 -I /opt/quartermaster/video/adapter.py &
fi
exec /usr/local/bin/entrypoint.sh "$@"
