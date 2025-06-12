import json
import os
from typing import Any, Dict, List
import httpx
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

# Load environment variables
load_dotenv()


class WeatherMCPClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.azure_client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    async def check_server_health(self) -> bool:
        """Check if the MCP server is running and healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from the MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.server_url}/tools")
                response.raise_for_status()
                tools_data = response.json()

                return [
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["inputSchema"]
                        }
                    }
                    for tool in tools_data["tools"]
                ]
            except Exception as e:
                raise RuntimeError(
                    f"Failed to get tools from server: {str(e)}")

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.server_url}/tools/call",
                    json={"name": tool_name, "arguments": arguments}
                )
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"] if result["content"] else "No result"
            except httpx.HTTPStatusError as e:
                error_detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                raise RuntimeError(f"Tool call failed: {error_detail}")
            except Exception as e:
                raise RuntimeError(f"Failed to call tool: {str(e)}")

    async def chat_with_weather_assistant(self, user_message: str) -> str:
        """Chat with Azure OpenAI using weather tools."""
        try:
            # Check server health first
            if not await self.check_server_health():
                return "❌ Weather server is not available. Please make sure the server is running."

            # Get available tools
            tools = await self.get_available_tools()

            # System message to help the assistant understand its role
            system_message = """You are a helpful weather assistant. You can get current weather information for any city using the available tools. 
            When a user asks about weather, use the get_weather tool to fetch the information and provide a friendly, informative response.
            Always include temperature, weather conditions, and any other relevant details from the weather data."""

            # Create messages for the conversation
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]

            # Call Azure OpenAI
            response = await self.azure_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            # Check if the model wants to call a tool
            message = response.choices[0].message

            if message.tool_calls:
                # Execute tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [tc.model_dump() for tc in message.tool_calls]
                })

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Call the MCP tool
                    tool_result = await self.call_mcp_tool(function_name, function_args)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # Get final response from the model
                final_response = await self.azure_client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages
                )

                return final_response.choices[0].message.content
            else:
                return message.content

        except Exception as e:
            return f"Error: {str(e)}"


async def main():
    """Main interactive client function."""
    client = WeatherMCPClient()

    print("🌤️  MCP Weather Client")
    print("=" * 50)

    # Check server health
    if not await client.check_server_health():
        print("❌ Cannot connect to weather server at http://localhost:8000")
        print("Please make sure the server is running with: python weather_server.py")
        return

    print("✅ Connected to weather server")
    print("Type 'quit' to exit\n")

    try:
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break

            if user_input:
                print("Assistant: ", end="", flush=True)
                response = await client.chat_with_weather_assistant(user_input)
                print(response)
                print()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
