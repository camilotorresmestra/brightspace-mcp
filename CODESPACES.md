# Bloque Neón personal Codespace

This prototype connects a personal Codespace to Bloque Neón. It is not a production multi-user service. It needs a running Codespace and a working UniAndes login. The original `stdio` server remains unchanged.

## Security

- Keep the desktop port 6080 **private**. Never share its URL or session.
- Port 8787 can be public only while the token-protected MCP server runs. Never remove the bearer-token check.
- The browser profile, cookies and MCP token in `~/.local/state/brightspace-mcp` are credentials. Never commit, upload, or share them. Deleting the Codespace deletes the saved session.
- Keep the token out of chat, screenshots, shell history and logs. Revoke it by removing `mcp-token`, then create a new one with `.devcontainer/install.sh`. Reconnect clients afterward.
- The remote endpoint offers eight tools. Download and local-filesystem audit tools are disabled. This avoids exposing local file writes and arbitrary paths.
- Session persistence depends on UniAndes policies. Sign in again when required. Passkeys and managed-device-only login flows can be unavailable in a remote desktop.

## First use

1. Create a Codespace on the `codespaces-uniandes` branch. Wait for the post-create install to finish.
2. In its terminal, run `bash scripts/private-login.sh`.
3. Open the **private** forwarded port 6080 in your own browser. Add `/vnc.html` to its URL. Connect, then sign in to Bloque Neón on that desktop. Approve MFA if asked. Select “Stay signed in” if offered.
4. After sign-in succeeds, run `bash scripts/start-mcp.sh` in the terminal. Leave this process running.
5. In the Ports tab, make **only port 8787** public. Its HTTPS URL, followed by `/mcp`, is the MCP endpoint. Keep port 6080 private.
6. Connect a client that supports a bearer token. The token is in `~/.local/state/brightspace-mcp/mcp-token`. Enter it directly in the client’s secure authentication form. Never paste it into chat. Whether a particular Notion personal-agent connection supports this authentication method must be tested.
7. Ask the client to list your courses. If login expires, stop the MCP process and repeat the private login.

The Codespace stops after inactivity. Start the MCP process again after reopening it. Do not use this Codespace for unrelated work while its remote endpoint is active.
