# How to Deploy and Use the Azure Container Apps MCP Weather Server

This guide documents the exact steps taken to deploy and use the weather MCP server from <https://github.com/anthonychu/azure-container-apps-mcp-sample>.

## 1. Clone the Repository

``` sh
git clone https://github.com/anthonychu/azure-container-apps-mcp-sample.git
cd azure-container-apps-mcp-sample
```

## 2. Edit the MCP Configuration for VS Code

Edit (or create) `.vscode/mcp.json` in your project folder with the following content:

```json
{
    "inputs": [
        {
            "type": "promptString",
            "id": "weather-api-key",
            "description": "Weather API Key",
            "password": true
        }
    ],
    "servers": {
        "weather-sse": {
            "type": "sse",
            "url": "https://<your-container-app-url>/sse",
            "headers": {
                "x-api-key": "${input:weather-api-key}"
            }
        }
    }
}
```

## 3. Deploy to Azure Container Apps

Run the following command (replace resource group/environment/location as needed):

``` sh
az containerapp up \
  -g mcp-demo-rg \
  -n weather-mcp \
  --environment mcp \
  -l eastus \
  --env-vars API_KEYS=weather-001,weather-002,weather-003 \
  --source .
```

- This sets up the app with three API keys: `weather-001`, `weather-002`, `weather-003`.
- The Azure CLI will output the public URL for your app (e.g., `https://<your-app-name>.<unique-id>.<region>.azurecontainerapps.io`).

## 4. Connect from VS Code

1. Open VS Code in the project folder.
2. Make sure the MCP extension is installed.
3. When prompted, enter one of the API keys you set above (e.g., `weather-001`).
4. Open Copilot Chat or the MCP chat interface.
5. Ask a weather question, e.g.: `What's the weather in Atlanta, GA?`

## 5. Notes

- You do NOT need to export API_KEYS locally unless running the server on your own machine.
- The API key is only needed when connecting from VS Code to the remote server.
- You can add or change API keys by redeploying with a new `--env-vars` value.

---

This process lets you run a remote MCP server in Azure Container Apps and connect to it from VS Code using API key authentication.
