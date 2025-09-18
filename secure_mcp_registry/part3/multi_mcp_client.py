"""
Example async client that connects a MultiServerMCPClient to a remote MCP server
hosted on Azure Container Apps. Generic name: multi_mcp_client.py

Usage:
    python -m asyncio multi_mcp_client.py   (or run with an async runner)
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Load environment variables
load_dotenv()

async def main():

    weather_url = os.environ.get("WEATHER_MCP_URL")
    if not weather_url:
        raise RuntimeError("WEATHER_MCP_URL environment variable must be set in your .env file.")

    weather_api_key = os.environ["WEATHER_API_KEY"]
    client = MultiServerMCPClient(
        {
            "weather": {
                "url": weather_url.rstrip("/") + "/sse",
                "transport": "sse",
                "headers": {
                    "x-api-key": weather_api_key
                },
            },
        }
    )

    tools = await client.get_tools()

    # Azure OpenAI config from environment
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # Use DefaultAzureCredential for Azure AD token auth
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

    agent = create_react_agent(llm, tools)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )

    print("weather:", weather_response)


if __name__ == "__main__":
    asyncio.run(main())
