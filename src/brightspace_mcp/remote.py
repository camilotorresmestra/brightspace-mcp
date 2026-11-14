"""Private-token, read-only Streamable HTTP transport for a personal Codespace."""
import hmac
import os
from pathlib import Path

from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import PlainTextResponse

from .server import mcp

# Local filesystem writes and path-scanning are not suitable for remote clients.
REMOTE_TOOLS = {
    "login", "get_courses", "get_assignments", "get_calendar", "get_course_content",
    "get_assignment_attachments", "get_grades", "get_course_overview",
}


def create_app(token: str):
    if len(token) < 40:
        raise ValueError("MCP token is missing or too short")
    for name in list(mcp._tool_manager._tools):
        if name not in REMOTE_TOOLS:
            mcp.remove_tool(name)
    code = os.environ.get("CODESPACE_NAME", "")
    domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    allowed = ["localhost:8787", "127.0.0.1:8787", "testserver"]
    if code:
        allowed.append(f"{code}-8787.{domain}")
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=allowed, allowed_origins=[]
    )
    inner = mcp.streamable_http_app()

    async def app(scope, receive, send):
        if scope["type"] == "http":
            # Reject duplicate authorization headers to avoid proxy ambiguity.
            values = [v for k, v in scope.get("headers", []) if k.lower() == b"authorization"]
            expected = ("Bearer " + token).encode("ascii")
            if len(values) != 1 or not hmac.compare_digest(values[0], expected):
                await PlainTextResponse("Unauthorized", status_code=401,
                                        headers={"Cache-Control": "no-store"})(scope, receive, send)
                return
        await inner(scope, receive, send)
    return app


def main():
    import uvicorn
    path = Path(os.environ.get("BRIGHTSPACE_MCP_TOKEN_FILE", Path.home() / ".local/state/brightspace-mcp/mcp-token"))
    try:
        if path.stat().st_mode & 0o077:
            raise ValueError("Token file must only be readable by its owner")
        token = path.read_text().strip()
        app = create_app(token)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Cannot start remote MCP: {exc}") from exc
    uvicorn.run(app, host="127.0.0.1", port=8787, access_log=False)

if __name__ == "__main__":
    main()
