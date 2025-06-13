"""Weather MCP Client with Azure OpenAI - Natural language weather queries using MCP server."""

import asyncio
import json
import os
import re
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

load_dotenv()


class WeatherMCPClient:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.azure_client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.mcp_server_url = "http://127.0.0.1:8000/mcp/"

    async def extract_city_from_query(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Use Azure OpenAI to extract city and country from natural language query."""
        system_prompt = """You are a helpful assistant that extracts city and country information from weather queries.
        
        Extract the city name and country/state from the user's query. Return ONLY a JSON object with:
        - "city": the city name
        - "country_code": the ISO country code (like "us", "uk", "jp") or state abbreviation for US cities
        
        Examples:
        - "What is the weather in London?" -> {"city": "London", "country_code": "uk"}
        - "Weather in Paris?" -> {"city": "Paris", "country_code": "fr"}
        - "What's the weather in Scranton, Pennsylvania?" -> {"city": "Scranton", "country_code": "us"}
        - "How's the weather in New York?" -> {"city": "New York", "country_code": "us"}
        
        If you cannot determine the city, return {"city": null, "country_code": null}."""

        try:
            response = await self.azure_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=100
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("city"), result.get("country_code")

        except Exception as e:
            print(f"Error extracting city from query: {e}")

        return None, None

    async def get_weather_from_mcp(self, city: str, country_code: str = "") -> Optional[Dict[str, Any]]:
        """Get weather data from MCP server."""
        try:
            async with streamablehttp_client(self.mcp_server_url) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Call the get_weather tool
                    tool_result = await session.call_tool("get_weather", {
                        "city": city,
                        "country_code": country_code
                    })

                    # Parse the result
                    if tool_result.content:
                        for content in tool_result.content:
                            if hasattr(content, 'text') and content.text:
                                try:
                                    return json.loads(content.text)
                                except json.JSONDecodeError:
                                    pass

        except Exception as e:
            print(f"Error getting weather from MCP: {e}")

        return None

    def celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32

    async def process_weather_query(self, query: str) -> str:
        """Process a natural language weather query and return a simple response."""
        # Extract city and country from query
        city, country_code = await self.extract_city_from_query(query)

        if not city:
            return "Sorry, I couldn't identify a city in your query."

        # Get weather data from MCP server
        weather_data = await self.get_weather_from_mcp(city, country_code or "")

        if not weather_data:
            return f"Sorry, I couldn't get weather data for {city}."

        # Extract temperature and condition
        temp_celsius = weather_data.get("temperature", {}).get("current")
        condition = weather_data.get(
            "weather", {}).get("description", "unknown")
        actual_city = weather_data.get("city", city)

        if temp_celsius is None:
            return f"Sorry, temperature data is not available for {actual_city}."

        # Convert to Fahrenheit
        temp_fahrenheit = self.celsius_to_fahrenheit(temp_celsius)

        # Format response
        return f"The weather in {actual_city} is {temp_fahrenheit:.1f}°F and {condition}."


async def test_mcp_connection():
    """Test if MCP server is available."""
    try:
        async with streamablehttp_client("http://127.0.0.1:8000/mcp/") as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                return len(tools_result.tools) > 0
    except Exception:
        return False


async def main():
    """Main function for direct client usage."""
    print("Starting Weather Demo...")

    # Test MCP server connection
    print("Checking MCP server connection...")
    if not await test_mcp_connection():
        print("Cannot connect to MCP server at http://127.0.0.1:8000/mcp/")
        print("Please make sure the weather server is running:")
        print("   python weather_server.py")
        return

    print("MCP server is ready!")

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

    # Interactive mode
    print("Interactive mode - Ask about the weather in any city!")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("Your weather query: ").strip()

            if user_input.lower() in ['quit', 'exit', '']:
                print("Goodbye!")
                break

            response = await client.process_weather_query(user_input)
            print(f"{response}\n")

        except KeyboardInterrupt:
            print("\nDemo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
