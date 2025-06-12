import asyncio
from weather_client import WeatherMCPClient


async def demo():
    """Quick demo of the weather MCP system."""
    client = WeatherMCPClient()

    try:
        print("🌤️  MCP Weather Demo")
        print("=" * 50)

        # Check if server is running
        if not await client.check_server_health():
            print("❌ Cannot connect to weather server at http://localhost:8000")
            print("Please start the server first with: python weather_server.py")
            return

        print("✅ Connected to weather server")

        # Test queries - only run first 2
        test_queries = [
            "What's the weather like in London?",
            "How's the weather in Scranton, Pennsylvania?"
        ]

        for query in test_queries:
            print(f"\n🔹 Query: {query}")
            response = await client.chat_with_weather_assistant(query)
            print(f"🤖 Response: {response}")

        # Allow user to enter their own query
        print("\n" + "=" * 50)
        print("🎯 Now it's your turn! Ask about weather in any city.")
        print("Type 'quit' to exit the demo.\n")

        while True:
            user_input = input("Your weather query: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye', '']:
                break

            if user_input:
                print(f"\n🔹 Your Query: {user_input}")
                response = await client.chat_with_weather_assistant(user_input)
                print(f"🤖 Response: {response}")
                print()

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    finally:
        print("\n✅ Demo completed")

if __name__ == "__main__":
    asyncio.run(demo())
