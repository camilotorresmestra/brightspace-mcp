#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb x11vnc novnc websockify openbox
python -m pip install --user 'mcp==1.26.0' -e '.[dev]'
python -m playwright install --with-deps chromium
mkdir -p "$HOME/.local/state/brightspace-mcp"
chmod 700 "$HOME/.local/state/brightspace-mcp"
python - <<'PY'
from pathlib import Path
import os, secrets
path = Path.home() / '.local/state/brightspace-mcp/mcp-token'
try:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    pass
else:
    with os.fdopen(fd, 'w') as f: f.write(secrets.token_urlsafe(48))
PY
