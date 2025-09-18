# MCP Registry Lab: End-to-End Azure API Center MCP Integration

This repository demonstrates a complete hands-on workflow for working with Model Context Protocol (MCP) servers using Azure API Center's MCP registry. You'll build, deploy, register, discover, and consume MCP tools in AI applications.

## Overview

This lab covers four main parts:

1. **Build a tiny MCP server with FastMCP** - Create a weather MCP server
2. **Containerize and deploy on Azure Container Apps (ACA)** - Deploy with consumption plan (scales to 0, generous free grant)
3. **Register the server in Azure API Center's MCP registry** - Make it discoverable
4. **Discover and use MCP tools from API Center Portal** - Connect with LangGraph and consume tools

## Prerequisites

- Azure subscription with API Center enabled
- Python 3.10+
- Azure CLI
- VS Code with MCP extension (optional)
- OpenAI or Azure OpenAI access

## Part 1: Build and Deploy MCP Server

See [`part1-aca-mcp-weather-lab.md`](./part1/part1-aca-mcp-weather-lab.md) for complete instructions on:

- Creating a weather MCP server with FastMCP
- Deploying to Azure Container Apps
- Testing the deployment

The lab shows how to deploy a server that provides weather forecast tools accessible via SSE (Server-Sent Events) with API key authentication.

## Part 2: Register in Azure API Center's MCP Registry

Follow the official Microsoft documentation to register your deployed MCP server:

📖 **[Set up API Center Portal](https://learn.microsoft.com/en-us/azure/api-center/set-up-api-center-portal)**

This step makes your MCP server discoverable through the Azure API Center Portal preview.

## Part 3: Discover and Use MCP Tools

See [`part3-consume-mcp-tools.md`](./part3/part3-consume-mcp-tools.md) for complete instructions on:

- Setting up the LangGraph application with MCP integration
- Configuring Azure OpenAI with Azure AD authentication
- Running the weather query example
- Troubleshooting common issues

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

## Key Features Demonstrated

- **Remote MCP Integration**: Connect to MCP servers over HTTPS/SSE
- **Azure AD Authentication**: Secure connection to Azure OpenAI using managed identity
- **Tool Discovery**: Automatic discovery of MCP tools and their schemas
- **Reactive Agents**: LangGraph agents that can reason about and use MCP tools
- **Environment-based Configuration**: Clean separation of secrets and config
- **Production Deployment**: Container-based deployment on Azure with scaling

## Next Steps

- Explore the Azure API Center Portal preview to discover other MCP servers
- Add additional MCP servers to your `MultiServerMCPClient` configuration
- Implement error handling and logging for production use
- Experiment with different LangGraph agent patterns
- Try different Azure OpenAI models and configurations

## Resources

- [Microsoft Learn: Set up API Center Portal](https://learn.microsoft.com/en-us/azure/api-center/set-up-api-center-portal)
- [Microsoft Learn: Register and Discover MCP Server](https://learn.microsoft.com/en-us/azure/api-center/register-discover-mcp-server)
- [Microsoft Learn: Customize API Center Portal - Semantic Search](https://learn.microsoft.com/en-us/azure/api-center/customize-api-center-portal#semantic-search)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)

---

This lab provides a complete foundation for building AI applications that leverage distributed MCP tools through Azure's cloud infrastructure and API management capabilities.
