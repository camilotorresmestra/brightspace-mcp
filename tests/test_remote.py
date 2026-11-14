import pytest
from starlette.testclient import TestClient
from brightspace_mcp.remote import create_app, REMOTE_TOOLS
from brightspace_mcp.server import mcp

TOKEN = "x" * 64

def test_short_token_rejected():
    with pytest.raises(ValueError): create_app("short")

def test_transport_blocks_missing_and_wrong_auth(monkeypatch, tmp_path):
    monkeypatch.setenv("BRIGHTSPACE_URL", "https://bloqueneon.uniandes.edu.co")
    monkeypatch.setenv("BRIGHTSPACE_SESSION_DIR", str(tmp_path))
    with TestClient(create_app(TOKEN)) as client:
        assert client.post('/mcp', json={}).status_code == 401
        assert client.post('/mcp', headers={'Authorization': 'Bearer wrong'}, json={}).status_code == 401
        assert client.get('/mcp').status_code == 401
        assert client.post('/mcp', headers={'Authorization': f'Bearer {TOKEN}'}, json={}).status_code != 401
    assert set(mcp._tool_manager._tools) == REMOTE_TOOLS

def test_mcp_initialization_and_host_security(monkeypatch, tmp_path):
    # Run in a subprocess because the SDK's session manager has a single lifespan.
    import subprocess, sys
    code = '''
from starlette.testclient import TestClient
from brightspace_mcp.remote import create_app
h = {"Authorization": "Bearer " + "x" * 64, "Accept": "application/json, text/event-stream"}
request = {"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{"protocolVersion":"2025-03-26", "capabilities":{}, "clientInfo":{"name":"test", "version":"1"}}}
with TestClient(create_app("x" * 64)) as c:
    r = c.post("/mcp", headers=h, json=request)
    assert r.status_code == 200, r.text
    assert "result" in r.json(), r.text
    h["host"] = "evil.example"
    assert c.post("/mcp", headers=h, json=request).status_code == 421
'''
    monkeypatch.setenv('BRIGHTSPACE_URL','https://bloqueneon.uniandes.edu.co')
    monkeypatch.setenv('BRIGHTSPACE_SESSION_DIR', str(tmp_path))
    subprocess.run([sys.executable, '-c', code], check=True)
