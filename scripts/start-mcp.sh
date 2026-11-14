#!/usr/bin/env bash
set -euo pipefail
export BRIGHTSPACE_URL="${BRIGHTSPACE_URL:-https://bloqueneon.uniandes.edu.co}"
export BRIGHTSPACE_TZ="${BRIGHTSPACE_TZ:-America/Bogota}"
# Silent refresh needs a display. The profile itself stays on the Codespace disk.
exec xvfb-run -a python -m brightspace_mcp.remote
