import azure.functions as func
import logging
import os
import time
from openai import AzureOpenAI

AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT= os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name("function-completion")
@app.route(route="chat")
def http_trigger(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    start_time = time.time()

    client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,  
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint = AZURE_OPENAI_ENDPOINT
    )

    user_prompt = req.params.get('prompt')
    if not user_prompt:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_prompt = req_body.get('prompt')

    if user_prompt:
        logging.info(f'Prompt: {user_prompt}')
        completion = client.chat.completions.create(model=AZURE_OPENAI_CHAT_DEPLOYMENT, messages=[{"role":"user", "content":user_prompt}])
        
        response = user_prompt +"\n"+ completion.choices[0].message.content
        logging.info(f'Completeion: {completion.choices[0].message.content}')
        logging.info(f'Total tokens: {completion.usage.total_tokens} - Completion tokens: {completion.usage.completion_tokens} - Prompt tokens: {completion.usage.prompt_tokens}')
        
        end_time = time.time()
        logging.info(f'Time taken for invocation id #{context.invocation_id}: {end_time - start_time}')
        
        return func.HttpResponse(response)
    else:
        end_time = time.time()
        logging.info(f'Time taken for invocation id #{context.invocation_id}: {end_time - start_time}')
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a prompt in the query string or in the request body for a personalized response.",
             status_code=200
        )