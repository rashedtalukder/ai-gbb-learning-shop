import semantic_kernel as sk
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import SequentialPlanner
from dotenv import load_dotenv
import os
from plugins.QueryDb import queryDb as plugin
from semantic_kernel.planning import StepwisePlanner
import json

# Take environment variables from .env.
load_dotenv()

async def main(nlp_input):
    
    kernel = sk.Kernel()
    
    # Get AOAI settings from .env
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()

    # Set the deployment name to the value of your chat model   
    azure_text_service = AzureChatCompletion(deployment_name=deployment, endpoint=endpoint, api_key=api_key)
    kernel.add_text_completion_service("azure_text_completion", azure_text_service)

    # Immport NLP to SQL Plugin
    plugins_directory = "plugins"
    kernel.import_semantic_plugin_from_directory(plugins_directory, "nlpToSqlPlugin")
    kernel.import_plugin(plugin.QueryDbPlugin(os.getenv("CONNECTION_STRING")), plugin_name="QueryDbPlugin")
    
    # create an instance of sequential planner
    planner = SequentialPlanner(kernel)    

    # Create a plan with the NLP input (the ask for which the sequential planner is going to find a relevant function.)
    ask = f"Create a SQL query according to the following request: {nlp_input} and query the database to get the result."   

    #ask the sequential planner to identify a suitable function from the list of functions available.
    plan = await planner.create_plan(goal=ask)   
 
    # Invoke the plan and get the result
    result = await plan.invoke(kernel=kernel)   


    print('/n')
    print(f'User ASK: {nlp_input}')
    print(f'Response: {result}')    
    print('/n')
    
    # Print each step of the plan and its result
    for index, step in enumerate(plan._steps):
        print("Step:", index)
        print("Description:", step.description)
        print("Function:", step.plugin_name + "." + step._function.name)
        if len(step._outputs) > 0:
            print("  Output:\n", str.replace(result[step._outputs[0]], "\n", "\n  "))
            print("\n\n")


# Run the main function
if __name__ == "__main__":
    import asyncio

    #asyncio.run(main("I want to know how many transactions in the last 3 months"))
    asyncio.run(main("Give me the name of the best seller in terms of sales volume in the whole period"))
    #asyncio.run(main("Which product has the highest sales volume in the last month"))