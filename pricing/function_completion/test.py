from openai import AzureOpenAI
import time

AZURE_OPENAI_API_KEY = "b19f6870ae76451a9ca8faa99438aee1"
AZURE_OPENAI_ENDPOINT = "https://aoai-swecen.openai.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT= "chatgpt-4"
AZURE_OPENAI_API_VERSION = "2024-02-01"

def main():
    client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,  
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint = AZURE_OPENAI_ENDPOINT
    )

    # user_prompt = "What is the meaning of life?"
    # response = client.chat.completions.create(model=AZURE_OPENAI_CHAT_DEPLOYMENT, messages=[{"role":"user", "content":user_prompt}])
    # print(response.to_json())
    # print(user_prompt+response.choices[0].message.content)

    # Step 1: Create an Assistant
    assistant = client.beta.assistants.create(
        name="Math Solver",
        instructions="You are a personal math tutor. Write and run code to answer math questions.",
        tools=[{"type": "code_interpreter"}],
        model=AZURE_OPENAI_CHAT_DEPLOYMENT
    )

    # Step 2: Create a Thread
    thread = client.beta.threads.create()

    # Step 3: Add a Message to a Thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
    )

    # Step 4: Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please provide the exact steps to solve the equation"
    )

    # Waits for the run to be completed. 
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, 
                                                    run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print("Run failed:", run_status.last_error)
            break
        time.sleep(2)  # wait for 2 seconds before checking again


    # Step 5: Parse the Assistant's Response and print the Results
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # Prints the messages the latest message the bottom
    number_of_messages = len(messages.data)
    print( f'Number of messages: {number_of_messages}')

    for message in reversed(messages.data):
        role = message.role  
        for content in message.content:
            if content.type == 'text':
                response = content.text.value 
                print(f'\n{role}: {response}')

if __name__ == "__main__":
    main()