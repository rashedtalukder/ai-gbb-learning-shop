import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool

# Take environment variables from .env.
load_dotenv()
AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS = os.environ["AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS"]
AZ_MODEL_DEPLOYMENT_NAME = os.environ["AZ_MODEL_DEPLOYMENT_NAME"]
BING_CONNECTION_NAME = os.environ["BING_CONNECTION_NAME"]


def main():
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS,
    )
    print(project_client)

    # [START create_agent_with_bing_grounding_tool]
    bing_connection = project_client.connections.get(
        connection_name=BING_CONNECTION_NAME)
    conn_id = bing_connection.id

    print(conn_id)

    # Initialize agent bing tool and add the connection id
    bing = BingGroundingTool(connection_id=conn_id)

    # Create agent with the bing tool and process assistant run
    with project_client:
        agent_list = project_client.agents.list_agents()
        print(agent_list)

        agent = project_client.agents.create_agent(
            model=AZ_MODEL_DEPLOYMENT_NAME,
            name="tour-guide-assistant",
            instructions="You are a helpful tour guide assistant for visitors of Austin, TX.",
            tools=bing.definitions,
            headers={"x-ms-enable-preview": "true"},
        )
        # [END create_agent_with_bing_grounding_tool]

        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        thread = project_client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        # Create message to thread
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content="What are some great BBQ spots near downtown Austin?",
        )
        print(f"Created message, ID: {message.id}")

        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id, assistant_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")

        # Delete the thread
        project_client.agents.delete_thread(thread.id)
        print("Deleted thread")

        # Delete the assistant when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")


if __name__ == "__main__":
    main()
