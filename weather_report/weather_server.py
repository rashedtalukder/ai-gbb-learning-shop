import json
import os
from typing import Any, Dict

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(title="Weather MCP Server", version="1.0.0")


class WeatherRequest(BaseModel):
    city: str


class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Weather MCP Server is running", "status": "healthy"}


@app.get("/tools")
async def list_tools():
    """List available weather tools."""
    return {
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather information for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name (e.g., 'London' or 'New York,US')",
                        }
                    },
                    "required": ["city"],
                },
            }
        ]
    }


@app.post("/tools/call")
async def call_tool(request: ToolRequest):
    """Handle tool calls."""
    if request.name != "get_weather":
        raise HTTPException(
            status_code=400, detail=f"Unknown tool: {request.name}")

    city = request.arguments.get("city")
    if not city:
        raise HTTPException(
            status_code=400, detail="City parameter is required")

    try:
        # Get weather data
        weather_data = await get_weather_data(city)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(weather_data, indent=2),
                }
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/weather")
async def get_weather(request: WeatherRequest):
    """Direct weather endpoint for simple requests."""
    try:
        weather_data = await get_weather_data(request.city)
        return weather_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


async def get_weather_data(city: str) -> Dict[str, Any]:
    """Fetch weather data from OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENWEATHER_API_KEY not found in environment variables")

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "standard",  # Default to standard units as requested
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"City '{city}' not found")
            else:
                raise ValueError(
                    f"Weather API error: {e.response.status_code}")
        except Exception as e:
            raise ValueError(f"Error fetching weather data: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 8000))
    uvicorn.run(app, host="localhost", port=port)
