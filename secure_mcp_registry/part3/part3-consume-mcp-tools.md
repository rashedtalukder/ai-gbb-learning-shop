# Part 3: Discover and Use MCP Tools in AI Applications

This guide demonstrates how to discover and consume MCP tools from Azure API Center Portal in a LangGraph application using `langchain-mcp-adapters`.

## Overview

This part shows how to:

- Connect to remote MCP servers using `langchain-mcp-adapters`
- Use Azure OpenAI with Azure AD authentication
- Create reactive agents that can call MCP tools
- Handle SSE transport with API key authentication

## Files Overview

- **[`multi_mcp_client.py`](./multi_mcp_client.py)** - Main application showing MCP integration with LangGraph
- **[`pyproject.toml`](./pyproject.toml)** - Dependencies including `langchain-mcp-adapters`, `langgraph`, and Azure libraries
- **[`sample.env`](./sample.env)** - Environment variable template
- **[`.env`](./.env)** - Your actual environment variables (not committed to git)

## Setup

1. **Install dependencies:**

   ```bash
   pip install -e .
   # or with uv
   uv sync
   ```

2. **Configure environment variables:**

   ```bash
   cp sample.env .env
   # Edit .env with your actual values
   ```

3. **Required environment variables:**
   - `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
   - `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key  
   - `AZURE_OPENAI_DEPLOYMENT_NAME` - Your model deployment name
   - `WEATHER_MCP_URL` - Your deployed MCP server base URL
   - `WEATHER_API_KEY` - API key for your MCP server

## Running the Application

```bash
python multi_mcp_client.py
```

The application will:

1. Connect to your MCP server and discover available tools
2. Create a LangGraph reactive agent with Azure OpenAI
3. Process a weather query using the MCP tools
4. Return a formatted weather forecast

## Example Output

``` sh
weather: {'messages': [HumanMessage(content='what is the weather in nyc?'), ...]}
```

The agent successfully calls the MCP weather tools and returns a detailed forecast.

## Architecture

``` sh
[LangGraph Agent] 
    ↓
[langchain-mcp-adapters]
    ↓  
[MCP Server on ACA] ←→ [Azure API Center Registry]
    ↓
[Weather API/Tools]
```

## Code Walkthrough

### 1. Environment Setup

The application uses `python-dotenv` to load configuration from your `.env` file:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. MCP Client Configuration

Configure the `MultiServerMCPClient` to connect to your weather MCP server:

```python
client = MultiServerMCPClient({
    "weather": {
        "url": weather_url.rstrip("/") + "/sse",
        "transport": "sse",
        "headers": {
            "x-api-key": weather_api_key
        },
    },
})
```

### 3. Azure OpenAI with Azure AD Authentication

Set up Azure OpenAI using managed identity for secure authentication:

```python
credential = DefaultAzureCredential()
azure_ad_token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)

llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    azure_deployment=deployment_name,
    azure_ad_token_provider=azure_ad_token_provider,
    api_version=api_version,
)
```

### 4. LangGraph Agent Creation

Create a reactive agent that can use the discovered MCP tools:

```python
tools = await client.get_tools()
agent = create_react_agent(llm, tools)
```

### 5. Tool Invocation

The agent can now reason about and invoke MCP tools:

```python
weather_response = await agent.ainvoke({
    "messages": [{"role": "user", "content": "what is the weather in nyc?"}]
})
```

## Key Features Demonstrated

- **Remote MCP Integration**: Connect to MCP servers over HTTPS/SSE
- **Azure AD Authentication**: Secure connection to Azure OpenAI using managed identity
- **Tool Discovery**: Automatic discovery of MCP tools and their schemas
- **Reactive Agents**: LangGraph agents that can reason about and use MCP tools
- **Environment-based Configuration**: Clean separation of secrets and config
- **Production Deployment**: Container-based deployment on Azure with scaling

## Troubleshooting

### Import Errors

If you see import errors for `langchain_openai` or `azure-identity`:

```bash
pip install -U langchain-openai azure-identity
```

### Authentication Issues

Make sure you have the correct Azure AD permissions and that your Azure OpenAI resource allows your identity to access it.

### MCP Connection Issues

- Verify your `WEATHER_MCP_URL` is correct
- Check that your `WEATHER_API_KEY` matches what was configured during deployment
- Test the MCP server endpoint directly with curl

## Next Steps

- Add additional MCP servers to your `MultiServerMCPClient` configuration
- Implement error handling and logging for production use
- Experiment with different LangGraph agent patterns
- Try different Azure OpenAI models and configurations
- Explore conversation memory and state management

## Resources

- [LangChain MCP Adapters Documentation](https://github.com/langchain-ai/langchain-mcp-adapters)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
