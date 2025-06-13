"""Weather MCP Server - A stateless MCP server that provides weather information."""

import os
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

load_dotenv()

# Initialize the FastMCP server with stateless HTTP configuration
server = FastMCP(
    name="Weather Server",
    instructions="A server that provides current weather information for cities using OpenWeatherMap API.",
    stateless_http=True,  # Enable stateless mode
    json_response=True,   # Return JSON responses
    streamable_http_path="/mcp/",  # Explicitly set with trailing slash
)


@server.tool(
    name="get_weather",
    description="Get current weather information for a city using OpenWeatherMap API"
)
async def get_weather(city: str, country_code: str = "", ctx: Optional[Context] = None) -> Dict[str, Any]:
    """
    Get current weather for a city.

    Args:
        city: The name of the city to get weather for
        country_code: Optional ISO 3166 country code (e.g., 'us', 'uk')
        ctx: Context for logging and progress reporting

    Returns:
        Dictionary containing weather information
    """
    # Get API key from environment
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        error_msg = "OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY environment variable."
        if ctx:
            await ctx.error(error_msg)
        raise ValueError("OpenWeatherMap API key not configured")

    # Build query string
    if country_code:
        query = f"{city},{country_code}"
    else:
        query = city

    # API endpoint
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": query,
        "appid": api_key,
        "units": "metric"  # Use metric units for temperature
    }

    if ctx:
        await ctx.info(f"Fetching weather data for {query}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            weather_data = response.json()

            # Validate response structure
            if "main" not in weather_data or "weather" not in weather_data or not weather_data["weather"]:
                raise ValueError(
                    "Invalid response structure from OpenWeatherMap API")

            # Extract and format key information with safe access
            result = {
                "city": weather_data.get("name", "Unknown"),
                "country": weather_data.get("sys", {}).get("country", "Unknown"),
                "temperature": {
                    "current": weather_data["main"]["temp"],
                    "feels_like": weather_data["main"]["feels_like"],
                    "min": weather_data["main"]["temp_min"],
                    "max": weather_data["main"]["temp_max"],
                    "unit": "°C"
                },
                "weather": {
                    "main": weather_data["weather"][0]["main"],
                    "description": weather_data["weather"][0]["description"]
                },
                "humidity": weather_data["main"]["humidity"],
                "pressure": weather_data["main"]["pressure"],
                "visibility": weather_data.get("visibility", "N/A"),
                "wind": {
                    "speed": weather_data.get("wind", {}).get("speed", 0),
                    "direction": weather_data.get("wind", {}).get("deg", "N/A")
                },
                "clouds": weather_data.get("clouds", {}).get("all", 0),
                "coordinates": {
                    "latitude": weather_data.get("coord", {}).get("lat", 0),
                    "longitude": weather_data.get("coord", {}).get("lon", 0)
                }
            }

            if ctx:
                await ctx.info(f"Successfully retrieved weather data for {result['city']}, {result['country']}")

            return result

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code} when fetching weather data"
        if e.response.status_code == 404:
            error_msg = f"City '{query}' not found"
        elif e.response.status_code == 401:
            error_msg = "Invalid API key"

        if ctx:
            await ctx.error(error_msg)
        raise ValueError(error_msg)

    except httpx.RequestError as e:
        error_msg = f"Network error when fetching weather data: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ValueError(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ValueError(error_msg)


if __name__ == "__main__":
    server.run(transport="streamable-http")
