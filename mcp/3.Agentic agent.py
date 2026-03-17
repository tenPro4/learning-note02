from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, Tool
from agents.mcp import MCPServerStdio
from IPython.display import Markdown, display
from datetime import datetime
from tools.accounts_client import read_accounts_resource, read_strategy_resource
from tools.accounts import Account
from tools.mcp_params import trader_mcp_server_params,researcher_mcp_server_params
import asyncio

async def get_researcher_agent(mcp_servers) -> Agent:
    instructions = f"""
    You are a financial researcher. You are able to search the web for interesting financial news,
    look for possible trading opportunities, and help with research.
    Based on the request, you carry out necessary research and respond with your findings.
    Take time to make multiple searches to get a comprehensive overview, and then summarize your findings.
    If there isn't a specific request, then just respond with investment opportunities based on searching latest news.
    The current datetime is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    researcher = Agent(
        name="Researcher",
        instructions=instructions,
        model="gpt-4.1-mini",
        mcp_servers=mcp_servers,
    )
    return researcher

async def get_researcher_tool(mcp_servers) -> Tool:
    researcher = await get_researcher_agent(mcp_servers)
    return researcher.as_tool(
            tool_name="Researcher",
            tool_description="This tool researches online for news and opportunities, \
                either based on your specific request to look into a certain stock, \
                or generally for notable financial news and opportunities. \
                Describe what kind of research you're looking for."
        )

async def main():
    agent_name = "ed"
    account_details = await read_accounts_resource(agent_name)
    strategy = await read_strategy_resource(agent_name)

    instructions = f"""
    You are a trader that manages a portfolio of shares. Your name is {agent_name} and your account is under your name, {agent_name}.
    You have access to tools that allow you to search the internet for company news, check stock prices, and buy and sell shares.
    Your investment strategy for your portfolio is:
    {strategy}
    Your current holdings and balance is:
    {account_details}
    You have the tools to perform a websearch for relevant news and information.
    You have tools to check stock prices.
    You have tools to buy and sell shares.
    You have tools to save memory of companies, research and thinking so far.
    Please make use of these tools to manage your portfolio. Carry out trades as you see fit; do not wait for instructions or ask for confirmation.
    """

    prompt = """
    Use your tools to make decisions about your portfolio.
    Investigate the news and the market, make your decision, make the trades, and respond with a summary of your actions.
    """

    try:
        async with AsyncExitStack() as stack:
            trader_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds=120)
                )
                for params in trader_mcp_server_params
            ] # Inside stack
            researcher_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds=120)
                )
                for params in researcher_mcp_server_params("ed")
            ]
            researcher_tool = await get_researcher_tool(researcher_mcp_servers)
            trader = Agent(
                name=agent_name,
                instructions=instructions,
                tools=[researcher_tool],
                mcp_servers=trader_mcp_servers,
                model="gpt-4o-mini",
            )
            result = await Runner.run(trader, prompt, max_turns=30)
            print(f"Final result: {result.final_output}")
    except Exception as e:
        print(f"Error running trader: {e}")

if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())