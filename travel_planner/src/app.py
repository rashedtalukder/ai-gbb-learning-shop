from tool_functions import travel_functions
import os
from pathlib import Path
import sys
import logging
import json
import uuid
import asyncio
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AsyncFunctionTool, AsyncToolSet, BingGroundingTool, MessageRole
from content_understanding.content_understanding_client import AzureContentUnderstandingClient
from dotenv import load_dotenv
import config
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS = os.getenv(
    "AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS")
AZ_MODEL_DEPLOYMENT_NAME = os.getenv("AZ_MODEL_DEPLOYMENT_NAME")

# The URL and Version for the Content Understanding API
AZURE_AI_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
AZURE_AI_API_VERSION = os.getenv("AZURE_AI_API_VERSION")
ITINERARY_FILE = os.getenv(
    "ITINERARY_FILE_URL") | "https://cooking.blob.core.windows.net/travel/travel_itinerary.pdf"
SAVE_TO_PDF_FILE = Path(os.path.dirname(__file__)) / \
    "output" / "new_itinerary.pdf"


async def main():
    config.ANALYZER_ID = "itinerary_analyzer-" + str(uuid.uuid4().hex[:8])
    ANALYZER_TEMPLATE_PATH = Path(os.path.dirname(
        __file__)) / "analyzer_templates" / "itinerary_template.json"

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

    logging.info("Analyzer template path: %s", ANALYZER_TEMPLATE_PATH)

    # Use the async create method instead of constructor
    config.CU_CLIENT = await AzureContentUnderstandingClient.create(
        endpoint=AZURE_AI_ENDPOINT,
        api_version=AZURE_AI_API_VERSION,
        token_provider=token_provider,
    )

    analyzer = config.CU_CLIENT.begin_create_analyzer(
        analyzer_id=config.ANALYZER_ID, analyzer_template_path=ANALYZER_TEMPLATE_PATH)
    result = config.CU_CLIENT.poll_result(analyzer)

    if result and "status" in result and result["status"] == "Succeeded":
        logging.info("✅ Analyzer '%s' created successfully!",
                     result['result']['analyzerId'])
        logging.info(json.dumps(result, indent=2))
    else:
        logging.error("❌ Failed to create the analyzer.")
        logging.error(json.dumps(result, indent=2))
        sys.exit(1)

    credential = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        credential=credential, conn_str=AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS
    )

    logging.info("Creating GPT-4o Travel Recommender Agent...")
    functions = AsyncFunctionTool(functions=travel_functions)
    bing_connection = await project_client.connections.get(
        connection_name=os.environ["BING_CONNECTION_NAME"])
    conn_id = bing_connection.id

    bing = BingGroundingTool(connection_id=conn_id)

    toolset = AsyncToolSet()
    toolset.add(functions)
    toolset.add(bing)

    gpt4o_agent = await project_client.agents.create_agent(
        model=AZ_MODEL_DEPLOYMENT_NAME,
        name="travel-recommender",
        instructions="You are a AI travel assistant using GPT-4o. Your task is to analyze travel "
                     "itineraries and generate engaging, personalized recommendations for destinations, activities, "
                     "dining experiences, and efficient transportation methods. Be insightful and unique!",
        toolset=toolset,
        headers={"x-ms-enable-preview": "true"},
    )

    logging.info("Created agent, ID: %s", gpt4o_agent.id)

    thread = await project_client.agents.create_thread()
    logging.info("Created thread, ID: %s", thread.id)

    message = await project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=f"""Suggest additional activities for me to do based on my existing itinerary for my upcoming travel at {ITINERARY_FILE}. 
            Create a new, concise, travel itinierary with a daily schedules and activities for the entire travel duration using the 
            itinerary start and end dates in areas I'll be in. Keep the existing plans and add new activities to the itinerary for only 
            the areas I am in for each day.
            Search with bing and provide recommendations for the most popular and sites, restaurants, and activities. 
            Always include citations for the information you provide.
            """,
    )

    logging.info("Created message, ID: %s", message.id)

    run = await project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=gpt4o_agent.id)
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = await project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")

    # Get the last message from the sender
    last_msg = messages.get_last_text_message_by_role(MessageRole.AGENT)
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    message = await project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=f"Those are great suggestions! Save that new itinerary to {SAVE_TO_PDF_FILE}.",
    )

    logging.info("Created message, ID: %s", message.id)

    run = await project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=gpt4o_agent.id)
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = await project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")

    # Get the last message from the sender
    last_msg = messages.get_last_text_message_by_role(MessageRole.AGENT)
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    # Cleanup
    await project_client.agents.delete_thread(thread.id)
    logging.info("Thread deleted.")
    await project_client.agents.delete_agent(gpt4o_agent.id)
    logging.info("Agent deleted.")
    config.CU_CLIENT.delete_analyzer(analyzer_id=config.ANALYZER_ID)
    logging.info("Analyzer deleted.")
    logging.info("✅ All processes completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
