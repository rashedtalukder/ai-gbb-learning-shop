# MCP Weather Workshop

This workshop shows how to create an MCP (Model Context Protocol) client and server setup where:

- **MCP Server**: Provides weather data tools using OpenWeatherMap API
- **MCP Client**: Uses Azure OpenAI to process natural language queries and call weather tools

This server has an endpoint that the client can call to get a list of available MCP tools that the server provides. The client LLM will using function calling to pick from the available set of server tools to best resolve the user question if applicable. This server currently only has 1 tool `get_weather` -- which provides current weather for a specified city -- but the pattern in the _weather_server.py_ file allows for any-number of available tools and endpoints for the LLM to use.

## Setup
0. **Create Conda Environment**
If you have and are happy with your existing conda environment, skip this step. If you don't have an environment already for the workshops, or want to create a new one, use the command below. If the name exists already and you want a different one, simply change the name of the environment.
    ```bash
    conda create env -n "ai-gbb-workshop"
    ```

1. **Install dependencies:**
   ```bash
   conda activate ai-gbb-workshop
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required API Keys:**
   - OpenWeatherMap API key from [openweathermap.org](https://openweathermap.org/api)
   - Azure OpenAI API key and endpoint from your Azure subscription

## Usage

### Start weather MCP server
This will need to be run in it's own terminal session. We'll call it "terminal session A."
```bash
python server.py
```

### Run the client demo
In a separate terminal session (call it terminal session B), run the command below to run the provided demo of the client code and library. The demo will run through two preset example queries for weather in a particular city and then take your input.
```bash
python demo.py
```

## Example Queries

- "What's the weather like in London?"
- "How's the weather in Scranton, Pennsylvania?"

## Architecture

```
User Query → Azure OpenAI → MCP Client → MCP Server → OpenWeatherMap API
                ↓                          ↓
            Tool Selection              Weather Data
                ↓                          ↓
            Natural Response ← ← ← ← ← Weather JSON
```

## Extend the code
Using the Open Weather Map API's, add additional functionality to the server so that it can not only provide current weather, but the [5-day forecast for a major city](https://openweathermap.org/forecast5#name5). Should the client need any changing?