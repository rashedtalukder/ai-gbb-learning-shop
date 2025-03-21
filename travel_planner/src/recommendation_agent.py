import os
import json
import logging
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()
AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS = os.getenv(
    "AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS")
AZ_MODEL_DEPLOYMENT_NAME = os.getenv("AZ_MODEL_DEPLOYMENT_NAME")

EXTRACTION_FILE = "extracted_itinerary.json"

logging.basicConfig(level=logging.INFO)


def get_recommendations(project_client, agent, extracted_content):
    """Generates creative travel recommendations using GPT-4o based on extracted itinerary details."""
    logging.info("Creating a new thread for recommendations...")

    recommendation_thread = project_client.agents.create_thread()
    logging.info(f"Created thread, ID: {recommendation_thread.id}")

    message = project_client.agents.create_message(
        thread_id=recommendation_thread.id,
        role="user",
        content=f"Here is the extracted travel itinerary:\n{json.dumps(extracted_content, indent=2)}\n\n"
                "Please analyze this and provide a list of unique, engaging, and personalized travel recommendations. "
                "Include must-visit places, dining options, and transportation tips. Be creative and detailed.",
    )
    logging.info(f"Created message, ID: {message.id}")

    run = project_client.agents.create_and_process_run(
        thread_id=recommendation_thread.id, agent_id=agent.id
    )
    logging.info(f"Run finished with status: {run.status}")

    if run.status == "failed":
        logging.error(f"Agent failed: {run.last_error}")
        return None

    # ✅ Extract the generated recommendations properly
    recommendations = project_client.agents.list_messages(
        thread_id=recommendation_thread.id).get("data", [])

    # ✅ Ensure JSON-serializable format
    recommendations_list_serializable = [
        {"content": msg["content"][0]["text"]["value"]}
        for msg in recommendations if "content" in msg and msg["content"]
    ]

    logging.info("Generated travel recommendations:")
    logging.info(json.dumps(recommendations_list_serializable, indent=2))

    # Save updated recommendations in the extracted itinerary JSON
    OUTPUT_FILE = "extracted_itinerary.json"

    # Modify the extracted_content to include AI-generated recommendations
    extracted_content["Here are your AI agentic recommendations:"] = recommendations_list_serializable

    # Save the updated extracted_content to the JSON file
    with open(OUTPUT_FILE, "w") as file:
        json.dump(extracted_content, file, indent=2)

    logging.info("Saved AI-generated recommendations to %s", OUTPUT_FILE)

    return recommendations_list_serializable


def main():
    """Runs the GPT-4o recommendation agent"""
    if not os.path.exists("./output/" + EXTRACTION_FILE):
        logging.error("No extracted itinerary found.")
        return

    with open(EXTRACTION_FILE, "r") as file:
        extracted_content = json.load(file)

    credential = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        credential=credential, conn_str=AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS
    )

    logging.info("Creating GPT-4o Travel Recommender Agent...")

    gpt4o_agent = project_client.agents.create_agent(
        model=AZ_MODEL_DEPLOYMENT_NAME,
        name="travel-recommender",
        instructions="You are a highly creative AI travel assistant using GPT-4o. Your task is to analyze travel "
                     "itineraries and generate engaging, personalized recommendations for destinations, activities, "
                     "dining experiences, and efficient transportation methods. Be insightful and unique! Scrape the web too for additional context",
        tools=[],
        headers={"x-ms-enable-preview": "true"},
    )

    logging.info(f"Created agent, ID: {gpt4o_agent.id}")

    recommendations = get_recommendations(
        project_client, gpt4o_agent, extracted_content)

    if recommendations:
        logging.info("Successfully generated recommendations!")

    project_client.agents.delete_agent(gpt4o_agent.id)
    logging.info("Agent deleted.")


if __name__ == "__main__":
    main()
