#!/usr/bin/env bash
# Run this from the Codespace; never make port 6080 public.
set -euo pipefail
export DISPLAY=:99
export BRIGHTSPACE_URL="${BRIGHTSPACE_URL:-https://bloqueneon.uniandes.edu.co}"
state="$HOME/.local/state/brightspace-mcp"
mkdir -p "$state"; chmod 700 "$state"
cleanup() { kill "${web_pid:-}" "${vnc_pid:-}" "${wm_pid:-}" "${x_pid:-}" 2>/dev/null || true; }
trap cleanup EXIT
Xvfb "$DISPLAY" -screen 0 1280x800x24 -nolisten tcp >"$state/xvfb.log" 2>&1 & x_pid=$!
sleep 2
kill -0 "$x_pid" || { echo "Display failed; stop another login session first." >&2; exit 1; }
openbox >"$state/openbox.log" 2>&1 & wm_pid=$!
x11vnc -display "$DISPLAY" -localhost -nopw -forever -shared -rfbport 5900 >"$state/vnc.log" 2>&1 & vnc_pid=$!
websockify --web=/usr/share/novnc 127.0.0.1:6080 127.0.0.1:5900 >"$state/websockify.log" 2>&1 & web_pid=$!
sleep 2
kill -0 "$vnc_pid" && kill -0 "$web_pid" || { echo "Private desktop could not start." >&2; exit 1; }
echo "Open the PRIVATE port 6080 in your browser, then open /vnc.html. Never make it public."
echo "Sign in on the remote desktop. This window closes when login completes."
python -m brightspace_mcp.login_helper
