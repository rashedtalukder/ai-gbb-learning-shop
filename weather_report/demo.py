"""Demo script to run weather server and client together."""

import asyncio
import subprocess
import time
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


async def check_server_ready(url: str, max_attempts: int = 30) -> bool:
    """Check if the server is ready to accept connections."""
    import httpx

    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient() as client:
                # Try to connect to the server health endpoint
                response = await client.get(f"{url.replace('/mcp', '')}/", timeout=1.0)
                # 404 is OK, means server is running
                if response.status_code in [200, 404]:
                    return True
        except (httpx.RequestError, httpx.TimeoutException):
            pass

        await asyncio.sleep(1)
        print(f"Waiting for server... (attempt {attempt + 1}/{max_attempts})")

    return False


async def run_sample_queries():
    """Run the sample weather queries using the client."""
    from weather_client import WeatherMCPClient

    # Check if all required environment variables are set
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "OPENWEATHER_API_KEY"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all variables are set.")
        return

    client = WeatherMCPClient()

    print("Weather Query Demo with Azure OpenAI + MCP")
    print("=" * 50)
    print("This demo uses Azure OpenAI to understand your weather questions")
    print("and then fetches real weather data using the MCP server.\n")

    # Sample queries
    sample_queries = [
        "What is the weather in London?",
        "What is the weather in Scranton, Pennsylvania?"
    ]

    print("Processing sample queries:")
    print("-" * 30)

    for query in sample_queries:
        try:
            print(f"\nProcessing: '{query}'")
            response = await client.process_weather_query(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error processing '{query}': {e}")

    # Interactive mode
    print("\nInteractive mode - Ask about the weather in any city!")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("Ask me about the weather: ").strip()

            if user_input.lower() in ['quit', 'exit', '']:
                print("Goodbye!")
                break

            response = await client.process_weather_query(user_input)
            print(f"Response: {response}\n")

        except KeyboardInterrupt:
            print("\nDemo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


async def main():
    """Run the demo: start server, wait for it to be ready, then run client."""

    # Check if API keys are set
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("WARNING: OPENWEATHER_API_KEY not set!")
        print("Please set your OpenWeatherMap API key in the .env file")
        print("Get a free key at: https://openweathermap.org/api")
        return

    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("WARNING: AZURE_OPENAI_API_KEY not set!")
        print("Please set your Azure OpenAI API key in the .env file")
        return

    server_process = None

    try:
        print("Starting Weather MCP Server...")
        print("="*50)

        # Start the server in a subprocess
        server_process = subprocess.Popen(
            [sys.executable, "weather_server.py"],
            cwd=Path(__file__).parent,
        )

        # Wait a moment for the server to start
        server_url = "http://127.0.0.1:8000"

        print(f"Checking if server is ready at {server_url}...")

        if await check_server_ready(f"{server_url}/mcp"):
            print("Server is ready!")
            print(f"Server running at: {server_url}")
            print(f"MCP endpoint: {server_url}/mcp")

            print("\nRunning Weather Client Demo...")
            print("="*50)

            # Run sample queries and interactive mode
            await run_sample_queries()

        else:
            print("Server failed to start or is not ready")

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")

    except Exception as e:
        print(f"Error running demo: {e}")

    finally:
        # Clean up server process
        if server_process:
            print("\nStopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("Server stopped cleanly")
            except subprocess.TimeoutExpired:
                print("Force killing server...")
                server_process.kill()
                server_process.wait()


if __name__ == "__main__":
    print("Weather MCP Demo")
    print("================")
    print("This demo will:")
    print("1. Start the weather MCP server")
    print("2. Wait for it to be ready")
    print("3. Run sample weather queries using Azure OpenAI and "
          "retrieve real weather data")
    print("4. Allow interactive queries")
    print("5. Clean up when done")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo cancelled by user")
