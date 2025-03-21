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
    "ITINERARY_FILE_URL") or "https://cooking.blob.core.windows.net/travel/travel_itinerary.pdf"
SAVE_TO_PDF_FILE = Path(os.path.dirname(__file__)) / \
    "output" / "new_itinerary.pdf"


async def create_agent_and_process(project_client):
    """Create an agent with necessary tools and process a conversation."""
    logging.info("Creating GPT-4o Travel Recommender Agent...")

    # Set up tools
    toolset = AsyncToolSet()
    toolset.add(AsyncFunctionTool(functions=travel_functions))

    try:
        # Get Bing connection
        bing_connection = await project_client.connections.get(
            connection_name=os.environ.get("BING_CONNECTION_NAME"))
        toolset.add(BingGroundingTool(connection_id=bing_connection.id))
    except Exception as e:
        logging.warning("Failed to add Bing tool: %s", e)

    # Create agent
    agent = await project_client.agents.create_agent(
        model=AZ_MODEL_DEPLOYMENT_NAME,
        name="travel-recommender",
        instructions=(
            "You are an AI travel assistant. Analyze provided travel itineraries "
            "and generate engaging, personalized recommendations for destinations, "
            "activities, dining experiences, and efficient transportation methods. "
            "Only save the itinerary as a PDF when the user explicitly requests it and says where they want it saved."
            "When asked to create travel plans based on existing itinerary, "
            "Create a new, concise travel itinerary with daily schedules for the entire travel duration, "
            "beginning on the the start date and ending on the end date. "
            "Provide recommendations for morning, afternoon, and evening activities, including dining options for"
            "every day of the trip. "
            "Keep existing plans and add new activities located in areas I'll be in each day."
            "If I am not in a new city/area, assume I am at the same location as the prior day. "
            "Search with Bing for popular sites, restaurants, and activities. "
            "Always include citations for information provided."
            "Use the following markdown format for the itinerary in your response: "
            "# Travel Itinerary\n"
            "## Travel Dates\n"
            "Start Date: {{start_date}}\n"
            "End Date: {{end_date}}\n"
            "## City Name\n"
            "### June 1, 2022 (Day 1)\n"
            "- Morning: Breakfast at [Restaurant Name](Restaurant URL)\n"
            "- Afternoon: Visit [Site Name](Site URL)\n"
            "- Evening: Dinner at [Restaurant Name](Restaurant URL)\n"
            "### June 2, 2022 (Day 2)\n"
            "- Morning: Breakfast at [Restaurant Name](Restaurant URL)\n"
            "- Afternoon: Visit [Site Name](Site URL)\n"
            "- Evening: Dinner at [Restaurant Name](Restaurant URL)\n"
            "## City Name\n"
            "### June 3, 2022 (Day 3)\n"
            "- Morning: Breakfast at [Restaurant Name](Restaurant URL)\n"
            "- Afternoon: Visit [Site Name](Site URL)\n"
            "- Evening: Dinner at [Restaurant Name](Restaurant URL)\n"
            "## Additional Information\n"
            "Include any additional information here."
        ),
        toolset=toolset,
        headers={"x-ms-enable-preview": "true"},
    )
    logging.info("Created agent, ID: %s", agent.id)

    # Create thread and message
    thread = await project_client.agents.create_thread()
    logging.info("Created thread, ID: %s", thread.id)

    message = await project_client.agents.create_message(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=(
            f"Suggest additional activities based on my existing itinerary at {ITINERARY_FILE}."
            "I would like to receive the new itinerary as a PDF file."
            f"Please save the new itinerary to {SAVE_TO_PDF_FILE}."
        ),
    )
    logging.info("Created message, ID: %s", message.id)

    # Run the conversation
    run = await project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id
    )

    if run.status != "completed":
        logging.error(
            "Run failed with status: %s, error: %s", run.status, run.last_error)

    return thread.id, agent.id


async def main():
    """
    Main function to create and manage an Azure Content Understanding analyzer and an AI Agent.

    This function performs the following steps:
    1. Generates a unique analyzer ID and sets the analyzer template path.
    2. Creates Azure credentials and a token provider.
    3. Initializes the Azure Content Understanding client.
    4. Creates an analyzer using the specified template.
    5. Checks the status of the analyzer creation and logs the result.
    6. Initializes the AI project client using a connection string.
    7. Creates an agent and processes it, retrieves messages from the agent, and logs the agent's response.
    8. Cleans up by deleting the thread and agent, and closing the project client.
    9. Deletes the analyzer and closes the Azure credentials.

    Logging is used extensively to provide information about the progress and status of each step.

    Raises:
        SystemExit: If the analyzer creation fails.
    """
    config.ANALYZER_ID = "itinerary_analyzer-" + str(uuid.uuid4().hex[:8])
    ANALYZER_TEMPLATE_PATH = Path(os.path.dirname(
        __file__)) / "analyzer_templates" / "itinerary_template.json"

    # Create our credentials - these need to be properly closed
    credential = DefaultAzureCredential()

    try:
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default")

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

        # Create the project client
        project_client = AIProjectClient.from_connection_string(
            credential=credential, conn_str=AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS
        )

        try:
            thread_id, agent_id = await create_agent_and_process(project_client)

            # Get messages from the thread
            messages = await project_client.agents.list_messages(thread_id=thread_id)

            # Get the last message from the agent
            last_msg = messages.get_last_text_message_by_role(
                MessageRole.AGENT)
            if last_msg:
                print(f"Agent response: {last_msg.text.value}")
            else:
                logging.warning("No agent messages found in thread.")

            # Cleanup
            await project_client.agents.delete_thread(thread_id)
            logging.info("Thread deleted.")
            await project_client.agents.delete_agent(agent_id)
            logging.info("Agent deleted.")
        finally:
            # Ensure project_client gets closed
            await project_client.close()
            logging.info("Project client closed.")

        config.CU_CLIENT.delete_analyzer(analyzer_id=config.ANALYZER_ID)
        logging.info("Analyzer deleted.")
    finally:
        # Properly close the credential
        await credential.close()
        logging.info("DefaultAzureCredential closed.")

    logging.info("✅ All processes completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
