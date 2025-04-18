import asyncio
from mcp.server.fastmcp import FastMCP
from crawl4ai import AsyncWebCrawler, CrawlResult # Import the necessary parts
from crawl4ai.types import CrawlResult  # ← this is usually where it's defined

# from pydantic_ai import Agent # Assuming used elsewhere
import time
import traceback # For detailed error logging

server = FastMCP("Crawl4AI Library Tool Server")
# agent = Agent(...)

print("[crawl4ai] Registering crawl_url (Library) tool...")

# Optional: Create a single crawler instance if you want to reuse browser contexts
# Be mindful of potential state issues if reusing across different types of crawls.
# For simplicity, creating one per call is safer but less efficient.
# crawler_instance = AsyncWebCrawler()
# print("[crawl4ai] Initializing shared AsyncWebCrawler...")


@server.tool()
async def crawl_url(url: str) -> str:
    """
    Crawls a given URL using Crawl4AI's Python library (AsyncWebCrawler)
    and returns markdown output. This avoids subprocess issues.
    """
    print(f"[crawl4ai] crawl_url (Library) triggered with: {url}")
    try:
        # Create a new crawler for each request (safer)
        # Or use a shared instance: async with crawler_instance as crawler:
        async with AsyncWebCrawler() as crawler:
            print(f"[crawl4ai] Calling crawler.arun for {url}...")
            # Add a timeout directly to the crawl operation if possible,
            # or wrap the await call if the library doesn't support it natively.
            # Note: crawl4ai's arun might have its own internal timeouts, check its docs.
            # We'll add an outer asyncio timeout for safety.
            result: CrawlResult = await asyncio.wait_for(
                crawler.arun(url=url),
                timeout=120 # Increased timeout for library potentially involving browser startup
            )
            print(f"[crawl4ai] Crawl finished for {url}. Success: {result.success}")

            if result.success and result.markdown:
                print(f"[crawl4ai] Markdown generated (first 500 chars):\n{result.markdown[:500]}")
                return result.markdown.strip()
            elif result.success:
                print("[crawl4ai] Crawl successful, but no markdown generated.")
                return "✅ Crawl successful, but no markdown output was generated."
            else:
                error_msg = f"⚠️ Crawl failed. Error: {result.error_message or 'Unknown error'}"
                print(f"[crawl4ai] {error_msg}")
                # Log potentially more info if available on the result object
                # print(f"[crawl4ai] Full result object on failure: {result}")
                return error_msg

    except asyncio.TimeoutError:
        print(f"[crawl4ai] ❌ Timeout expired after 120 seconds for URL: {url}")
        # Note: Need to ensure the underlying playwright resources are cleaned up.
        # The 'async with' should handle this, but forceful cancellation might have edge cases.
        return "⏳ Timeout: Crawl exceeded 120 seconds."
    except ImportError as e:
         print(f"[crawl4ai] ❌ Import Error: {e}. Is crawl4ai installed correctly?")
         # Add traceback for debugging if needed:
         # print(traceback.format_exc())
         return "❌ Configuration Error: Could not import crawl4ai. Check installation."
    except Exception as e:
        # Catch potential errors during crawler initialization or execution
        print(f"[crawl4ai] ❌ Unexpected error during library crawl for {url}: {e}")
        print(traceback.format_exc()) # Log full traceback for unexpected errors
        return f"❌ Unexpected error during crawl: {str(e)}"

@server.tool()
async def test_ping() -> str:
    print("[crawl4ai] test_ping invoked")
    return "pong"

if __name__ == "__main__":
    # Optional: Initialize shared crawler instance here if using one
    # asyncio.run(crawler_instance.start()) # If manual start/stop needed

    print("[crawl4ai] Tool server launching...")
    server.run()

    # Optional: Cleanup shared crawler instance on shutdown if using one
    # print("[crawl4ai] Shutting down shared crawler...")
    # asyncio.run(crawler_instance.stop())