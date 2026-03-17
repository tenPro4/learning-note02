import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio


async def main():
    load_dotenv()

    # ---------------- fetch MCP ----------------
    fetch_params = {
        "command": "uvx",
        "args": ["mcp-server-fetch"]
    }

    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.session.list_tools()

    print("Fetch tools:")
    print(fetch_tools.tools)
    print()

    # ---------------- playwright MCP ----------------
    # Ensure you have node install and the version must > 22
    playwright_params = {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
    }

    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as server:
        playwright_tools = await server.session.list_tools()

    print("Playwright tools:")
    print(playwright_tools.tools)
    print()

    # ---------------- filesystem MCP ----------------
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))

    files_params = {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]
    }

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as server:
        file_tools = await server.session.list_tools()

    print("Filesystem tools:")
    print(file_tools.tools)
    print()


if __name__ == "__main__":
    # Windows async subprocess fix
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())