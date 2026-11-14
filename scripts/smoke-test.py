"""Check the local MCP endpoint without displaying the token or course data."""
import asyncio
from pathlib import Path
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    url = 'http://127.0.0.1:8787/mcp'
    token = (Path.home() / '.local/state/brightspace-mcp/mcp-token').read_text().strip()
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={})
        print('WITHOUT_TOKEN_HTTP', response.status_code, flush=True)
    async with streamablehttp_client(url, headers={'Authorization': 'Bearer ' + token}) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print('TOOLS_DISCOVERED', len(tools.tools), flush=True)
            result = await session.call_tool('get_courses', {})
            text = ' '.join(getattr(item, 'text', '') for item in result.content).lower()
            if result.isError or 'not authenticated' in text or 'session expired' in text or 'error' in text:
                print('COURSES_TEST_FAILED', flush=True)
            else:
                print('COURSES_TEST_SUCCESS', flush=True)

if __name__ == '__main__':
    asyncio.run(main())
