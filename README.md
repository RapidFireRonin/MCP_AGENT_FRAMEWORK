# MCP_AGENT_FRAMEWORK
BASE FRAMEWORK FOR AGENTIC MCP USE**
# AGENTIC_MCP_FRAMEWORK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Add badges for build status, etc. -->

A framework demonstrating how to build a tool-augmented AI agent using `pydantic-ai` where the tools are provided by independent microservices communicating via the Model Context Protocol (MCP).

This project features a Command-Line Interface (CLI) chat application that interacts with an LLM (like GPT-4o-mini). The agent's capabilities are extended by a set of tools (filesystem access, web fetching, code execution, web crawling, etc.), each running as a separate server process managed by MCP.

## Key Features

*   **Agentic Core:** Uses `pydantic-ai` to create an intelligent agent capable of using tools.
*   **LLM Integration:** Configurable to use different LLMs (OpenAI compatible APIs).
*   **MCP for Tools:** Implements the Model Context Protocol for decoupling tools into microservices.
    *   **`mcp-client`:** Used in the main application to discover and interact with tool servers.
    *   **`FastMCP` / Other MCP Servers:** Used to build the individual tool servers.
*   **Microservice Architecture:** Each tool runs in its own process, improving modularity, isolation, and potentially scalability.
*   **Included Tools:** Comes with pre-built examples:
    *   Filesystem operations (Node.js based)
    *   Web content fetching
    *   Identity information retrieval
    *   Joke telling
    *   Code execution via Open Interpreter
    *   Web crawling using `crawl4ai`
*   **CLI Interface:** Simple and interactive command-line chat using `rich` for enhanced display.
*   **Configuration:** Easy configuration via `.env` for secrets/LLM settings and `mcp_config.json` for defining tool servers.
*   **Extensibility:** Designed to make adding new tools straightforward.

## Architecture Overview
Use code with caution.
Markdown
+---------------------+ +------------------------+ +---------------------+
| User via CLI | <--> | Main Application | <--> | Pydantic AI Agent |
| (main.py + rich) | | (main.py, mcp-client) | | (pydantic-ai, LLM) |
+---------------------+ +---------^--------------+ +----------^----------+
| | decides to use tool
| discovers/invokes tools via MCP |
v v
+--------------------------------------+---------------------------------+
| Model Context Protocol (MCP) Network Communication |
+--^-----------^------------^-----------^-------------^------------^-----+
| | | | | |
+--+--+ +--+--+ +--+--+ +--+--+ +--+--+ +--+--+
| FS | |Fetch| | ID | |Joke | | O.I.| |Crawl| <-- MCP Tool Servers
| Srv | | Srv | | Srv | | Srv | | Srv | | Srv | (Separate Processes)
+-----+ +-----+ +-----+ +-----+ +-----+ +-----+
| | | |
v v v v
Local FS The Web Code Env The Web (via crawl4ai)
1.  The user interacts with the **CLI Chat Interface** (`main.py`).
2.  Input is passed to the **Pydantic AI Agent**.
3.  The Agent, powered by an **LLM**, processes the input. It may decide a **Tool** is needed.
4.  The Agent instructs the **MCP Client** (within `main.py`) to use a specific tool.
5.  The **MCP Client** sends a request via the **MCP Protocol** to the appropriate **MCP Tool Server** (running as a separate process defined in `mcp_config.json`).
6.  The **Tool Server** executes its specific task (e.g., crawls a URL, reads a file).
7.  The result is sent back via **MCP** to the **MCP Client**.
8.  The **Client** returns the result to the **Agent**.
9.  The **Agent** uses the tool's result to formulate the final response.
10. The response is streamed back to the **CLI Chat Interface** and displayed to the user.

## Getting Started

### Prerequisites

*   **Python:** 3.8+ Recommended.
*   **Pip:** Python package installer.
*   **Virtual Environment Tool:** `venv` (recommended) or `conda`.
*   **Node.js & npm/npx:** Required *only* for the `filesystem` tool server (which uses `@modelcontextprotocol/server-filesystem`). Check with `node --version` and `npx --version`.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AGENTIC_MCP_FRAMEWORK.git
    cd AGENTIC_MCP_FRAMEWORK
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    # Using venv (recommended)
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Python dependencies:**
    *(Ensure you have a `requirements.txt` file in the root directory. If not, create one based on the imports in your scripts: `pydantic-ai`, `openai`, `python-dotenv`, `rich`, `mcp-client`, `mcp-server-fastmcp` (or `fastmcp`), `crawl4ai`, etc.)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up `crawl4ai` prerequisites (if any):**
    `crawl4ai` often uses Playwright or similar browser automation tools. These might require a one-time setup to download browser binaries. Check the `crawl4ai` documentation, but often this is needed:
    ```bash
    # Run this *inside* your activated venv
    playwright install
    ```
    *(Note: `crawl4ai` might handle this automatically on first run, but doing it explicitly can prevent issues).*

5.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your specific configurations:
        ```dotenv
        # .env
        # LLM Configuration
        LLM_API_KEY="YOUR_API_KEY_HERE" # e.g., sk-..., or your local LLM key
        MODEL_CHOICE="gpt-4o-mini"      # Or another model like gpt-3.5-turbo, llama3, etc.
        BASE_URL="https://api.openai.com/v1" # Or your local/custom LLM API endpoint

        # Other potential secrets if needed by tools
        ```

### Configuration

*   **`.env`:** Stores secrets like API keys and basic LLM configuration (model name, base URL). See installation step 5.
*   **`mcp_config.json`:** Defines the MCP tool servers to be launched.
    *   **Structure:** A JSON object where keys are unique server names and values are objects containing:
        *   `command`: The executable to run (e.g., `npx`, `python`, `./.venv/Scripts/python.exe`). **Crucially, ensure paths are correct relative to where you run `main.py`**. Using the venv's Python executable is often necessary.
        *   `args`: A list of arguments to pass to the command.
    *   **Example Entry (from your provided config):**
        ```json
        {
          "crawl4ai": {
            "command": "./.venv/Scripts/python.exe", // Path to python in venv
            "args": [
              "agents/crawl4ai_tool/web_crawler.py" // Path to the server script
            ]
          }
          // ... other server definitions
        }
        ```
    *   **Important:** Verify that all paths in `command` and `args` are correct relative to the project's root directory (where you'll likely run `main.py`).

### Running the Application

1.  **Ensure your virtual environment is activated:**
    ```bash
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

2.  **Run the main script from the project root directory:**
    ```bash
    python main.py
    ```

3.  **Expected Output:**
    *   You should see messages indicating the MCP servers are being started (the `mcp-client` library handles launching the commands from `mcp_config.json`).
    *   Messages like "TOOLS LOADED:" followed by the names of the tools discovered from the running servers.
    *   Finally, the "=== Pydantic AI MCP CLI Chat ===" header and the `[You]` prompt.

4.  **Interact:** Type your messages and press Enter. Type `exit` or `quit` to end the chat.

## How It Works (Detailed Flow)

1.  `main.py` starts.
2.  `get_pydantic_ai_agent` is called.
3.  `mcp_client.MCPClient()` is instantiated.
4.  `client.load_servers(str(CONFIG_FILE))` reads `mcp_config.json`.
5.  `await client.start()` attempts to:
    *   Launch each server defined in the config as a separate subprocess (e.g., running `.\.venv\Scripts\python.exe agents/crawl4ai_tool/web_crawler.py`).
    *   Communicate with these newly started servers via MCP to get the list of tools they offer.
6.  If successful, `client.start()` returns a list of `Tool` objects.
7.  `Agent(model=get_model(), tools=tools)` creates the `pydantic-ai` agent, providing it with the LLM configuration and the list of MCP-backed tools.
8.  The chat loop begins.
9.  User input is captured.
10. `agent.run_stream(user_input, message_history=messages)` is called.
11. `pydantic-ai` sends the conversation history and the latest input to the LLM.
12. The LLM might respond directly or determine a tool call is necessary.
13. If a tool call is needed (e.g., the LLM outputs a request to use `crawl_url`), `pydantic-ai` identifies the corresponding `Tool` object.
14. Because this `Tool` object originated from `mcp-client`, calling it triggers `mcp-client` to send an execution request (function name + arguments) to the correct MCP server (e.g., the `crawl4ai` server) over the MCP protocol.
15. The target MCP server (e.g., `web_crawler.py`) receives the request, executes its corresponding Python function (e.g., `async def crawl_url(...)`), and sends the result back via MCP.
16. `mcp-client` receives the result and passes it back to `pydantic-ai`.
17. `pydantic-ai` provides the tool's result back to the LLM to generate the final response.
18. The final response text is streamed chunk by chunk (`result.stream_text(delta=True)`).
19. `rich.live` updates the console dynamically with the formatted Markdown response.
20. The conversation history (`messages`) is updated.
21. The loop waits for the next user input.
22. `await mcp_client.cleanup()` is called when the application exits to ensure graceful shutdown of connections and potentially the subprocesses.

## Tools

### Included Tools

*   **`filesystem`**: Performs filesystem operations (details depend on `@modelcontextprotocol/server-filesystem`).
*   **`fetch`**: Fetches raw content from a URL (via `mcp_server_fetch`).
*   **`identity`**: Provides predefined identity information (via `agents/identity_info_tool/identity.py`).
*   **`joke`**: Tells a joke (via `agents/joke_tool/tell_joke.py`).
*   **`open_interpreter`**: Executes code using Open Interpreter (via `agents/open_interpreter_tool/interpreter_runner.py`).
*   **`crawl4ai`**: Crawls a web page using the `crawl4ai` library and returns clean Markdown content (via `agents/crawl4ai_tool/web_crawler.py`).

### Adding a New Tool

1.  **Create the Tool Server Script:**
    *   Create a new Python script (e.g., `agents/my_new_tool/tool_server.py`).
    *   Use an MCP server library like `FastMCP`.
    *   Define your tool's logic within an `async` function.
    *   Decorate the function with `@server.tool()` (or the equivalent for your chosen MCP server library), including type hints for arguments and the return value. Pydantic models can be used for complex inputs/outputs.
    *   Instantiate and run the server (e.g., `server = FastMCP(...)`, `server.run()`).
    ```python
    # agents/my_new_tool/tool_server.py
    from mcp.server.fastmcp import FastMCP
    import asyncio

    server = FastMCP("My New Awesome Tool Server")

    @server.tool()
    async def perform_action(param1: str, param2: int) -> str:
        """
        This is the docstring description the LLM will see.
        It should clearly explain what the tool does and what its parameters are.
        """
        print(f"[my_tool] Received request with: {param1=}, {param2=}")
        # Your tool logic here...
        await asyncio.sleep(1) # Simulate work
        result = f"Processed '{param1}' {param2} times."
        print(f"[my_tool] Sending result: {result}")
        return result

    if __name__ == "__main__":
        print("[my_tool] Tool server launching...")
        server.run()
    ```

2.  **Update `mcp_config.json`:**
    *   Add a new entry for your tool server, specifying the command and arguments to run your new script. Make sure paths are correct!
    ```json
    {
      // ... other servers
      "my_new_tool": {
        "command": "./.venv/Scripts/python.exe",
        "args": [
          "agents/my_new_tool/tool_server.py"
        ]
      }
    }
    ```

3.  **Install Dependencies:** If your new tool script requires additional Python packages, install them into your virtual environment:
    ```bash
    # Make sure venv is active
    pip install required_package_for_my_tool
    # Optional: Update requirements.txt
    pip freeze > requirements.txt
    ```

4.  **Relaunch:** Stop the main application (Ctrl+C) and restart it (`python main.py`). The `mcp-client` should now launch your new server and discover its tool(s), making them available to the `pydantic-ai` agent.

## Troubleshooting

*   **App Doesn't Launch / Hangs:**
    *   **Check Console Output:** Look carefully for any error messages when running `python main.py`.
    *   **Verify Venv:** Ensure the correct virtual environment is activated before running `pip install` or `python main.py`.
    *   **Check Dependencies:** Run `pip list` inside the activated venv to confirm all required packages (pydantic-ai, mcp-client, openai, FastMCP/mcp-server-fastmcp, crawl4ai, rich, python-dotenv etc.) are installed.
    *   **Test Servers Manually:** This is the MOST important step. Try running each `command` + `args` from `mcp_config.json` *manually* in your terminal (with the venv activated).
        *   Example: `.\.venv\Scripts\python.exe agents/crawl4ai_tool/web_crawler.py`
        *   Do they run without errors? Do they print startup messages? Does one crash immediately (ImportError, SyntaxError)? This isolates which server is failing.
    *   **Check `mcp_config.json` Paths:** Double-check all paths for `command` and `args`. Are they correct relative to the project root? Is `./.venv/Scripts/python.exe` the correct path to your venv's Python?
    *   **Check `.env` File:** Ensure it exists, is named correctly (`.env`), and the variables are set.
    *   **Check Node/`npx`:** If the `filesystem` server fails, ensure Node.js is installed and `npx` is in your PATH (`npx --version`).
    *   **`crawl4ai` / Playwright:** If the `crawl4ai` server fails, try running `playwright install` again within the venv.

*   **Tool Not Found / Agent Doesn't Use Tool:**
    *   Verify the tool server is running (check manually or look for startup logs if the server prints them).
    *   Ensure the tool function has a clear docstring explaining its purpose and parameters – `pydantic-ai` uses this to understand when to use the tool.
    *   Check the console output of the tool server itself for errors when it's called.

*   **Authentication Errors:**
    *   Verify your `LLM_API_KEY` in `.env` is correct and has appropriate permissions/credits.
    *   Ensure the `BASE_URL` points to the correct API endpoint.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

(Optional: Add more specific contribution guidelines here - e.g., coding style, testing requirements).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (You'll need to add a LICENSE file with the MIT license text).
Use code with caution.
Next Steps for You:
Save: Save this content as README.md in the root directory of your AGENTIC_MCP_FRAMEWORK project.
Create requirements.txt: If you don't have one, create it based on your imports:
# Activate your .venv
pip freeze > requirements.txt
Use code with caution.
Bash
Create .env.example: Create a file named .env.example with the structure shown in the README, but without actual secret values.
Add LICENSE File: Choose a license (MIT is common and permissive) and add the corresponding LICENSE file to your repository.
Review and Customize: Read through the generated README and adjust any details specific to your implementation (e.g., if your tool names or specific functionalities differ slightly). Add any other sections you deem necessary.
