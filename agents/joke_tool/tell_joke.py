from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

server = FastMCP("Joke MCP Server")
agent = Agent("openai:gpt-4o", system_prompt="Tell short, funny jokes.")

@server.tool()
async def tell_joke() -> str:
    return "Why did the developer go broke? Because they used up all their cache."

if __name__ == "__main__":
    print(" Joke server is launching...")
    server.run()
