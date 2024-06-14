import azure.functions as func
import logging
import os
import time
from openai import AzureOpenAI

AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name("function-completion")
@app.route(route="travel")
def http_trigger(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    # Create a travel agency assistant
    # Provide system prompt instructions to the assistant
    # Add file search and code interpreter tools to the assistant
    logging.info("Creating a travel agency assistant...")
    assistant = client.beta.assistants.create(
        name="Travel Agency Assistant",
        instructions="""You are a travel agency customer service representative.
          Use your knowledge base to answer questions.
          For any questions that require mathematical calculations (such as flight travel times), use the code interpreter tool and only the provided data.""",
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
    )

    # Create a vector store caled "Travel Agency Documents"
    logging.info("Creating a vector store...")
    vector_store = client.beta.vector_stores.create(
        name="Travel Agency Documents")

    # Ready the files for upload to OpenAI
    logging.info("Preparing files for upload...")
    file_paths = [f"{context.function_directory}/data/contoso-brochure.pdf",]
    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    logging.info(f"Uploading {len(file_paths)} files to the vector store...")
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # Print the status and the file counts of the batch to see the result of this operation.
    logging.info(f'File batch status: {file_batch.status}')
    logging.info(f'File batch file count: {file_batch.file_counts}')

    # Upload a file with an "assistants" purpose
    file = client.files.create(file=open(
        f"{context.function_directory}/data/flights.csv", "rb"),
        purpose='assistants'
    )

    # Update the assistant with the vector store and code interpreter with access to files
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            },
            "code_interpreter": {
                "file_ids": [file.id]
            }
        },
    )

    # Create a thread and attach the file to the message
    logging.info("Creating a thread...")
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "What are the highlights of going to Kyoto, Japan and are flights included in the package? What is the average travel time from Seattle?",
            }
        ]
    )

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.
    logging.info("Creating a run...")
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(
        thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(
            annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    return func.HttpResponse(message_content.value + "\n".join(citations), status_code=200)
