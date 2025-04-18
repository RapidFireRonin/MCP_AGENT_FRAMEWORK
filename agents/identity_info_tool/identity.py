from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

server = FastMCP("Identity MCP Server")
agent = Agent("openai:gpt-4o", system_prompt="Be friendly and factual.")

@server.tool()
async def who_am_i() -> str:
    return (
        "I am a cook. "
        "My favorite garnishes are radish and huckley. "
        "My dog's name is Bookley. "
        "My cat hates my dog."
    )

if __name__ == "__main__":
    print(" Identity server running...")
    server.run()
