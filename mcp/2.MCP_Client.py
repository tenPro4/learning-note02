import asyncio
import os
import sys

from agents import Agent, Runner
from tools.accounts_client import get_accounts_tools_openai, list_accounts_tools
from tools.accounts import Account
from agents.mcp import MCPServerStdio

async def main():
    account = Account.get("Ed")
    print(f"Account: {account.model_dump()}")
    # account.buy_shares("AMZN",3,"Because this bookstore website looks promising")
    print(f"Report: {account.report()}")
    print(f"Transactions: {account.list_transactions()}")
    print("="*50)

    fetch_params = {
        "command": "uv",
        "args": ["run", "python", "-m", "tools.accounts_server"]
    }

    async with MCPServerStdio(
        params=fetch_params,
        client_session_timeout_seconds=60) as server:
        fetch_tools = await server.session.list_tools()
    
    print("MCP Server Fetch tools(local):")
    print(fetch_tools.tools)
    print("="*100)
    print("MCP Client Fetch tools(local):")

    mcp_tools = await list_accounts_tools()
    print(mcp_tools)

    openai_tools = await get_accounts_tools_openai()
    print(openai_tools)

    instructions = "You are able to manage an account for a client, and answer questions about the account."
    request = "My name is Ed and my account is under the name Ed. What's my balance and my holdings?"
    model = "gpt-4.1-mini"

    agent = Agent(name="account_manager", instructions=instructions, model=model, tools=openai_tools)
    result = await Runner.run(agent, request)
    print(result.final_output)

    polygon_api_key = os.getenv("POLYGON_API_KEY")
    params = {"command": "uvx",
          "args": ["--from", "git+https://github.com/polygon-io/mcp_polygon@v0.1.0", "mcp_polygon"],
          "env": {"POLYGON_API_KEY": polygon_api_key}
    }

if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())