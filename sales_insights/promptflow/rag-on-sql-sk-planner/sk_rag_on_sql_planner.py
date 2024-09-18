
from promptflow import tool
from promptflow.connections import CustomConnection
import semantic_kernel as sk
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import SequentialPlanner
from dotenv import load_dotenv
import os
from plugins.QueryDb import queryDb as plugin
import json

@staticmethod
def to_json(obj):
    return json.dumps(obj, default=lambda obj: obj.__dict__)

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
async def my_python_tool(ask: str, aoai_deployment: str, conn: CustomConnection) -> object:
    
    endpoint = conn.AZURE_OPENAI_API_BASE
    api_key = conn.AZURE_OPENAI_API_KEY
    deployment = aoai_deployment
    sql_conn_string = conn.SQL_CONNECTION_STRING

    kernel = sk.Kernel()

    # Set the deployment name to the value of your chat model   
    azure_text_service = AzureChatCompletion(deployment_name=deployment, endpoint=endpoint, api_key=api_key)
    kernel.add_text_completion_service("azure_text_completion", azure_text_service)

     # Immport NLP to SQL Plugin
    plugins_directory = "plugins"
    kernel.import_semantic_plugin_from_directory(plugins_directory, "nlpToSqlPlugin")
    kernel.import_plugin(plugin.QueryDbPlugin(sql_conn_string), plugin_name="QueryDbPlugin")

    # create an instance of sequential planner
    planner = SequentialPlanner(kernel)    

    # Create a plan with the NLP input (the ask for which the sequential planner is going to find a relevant function.)
    userask = f"Create a SQL query according to the following request: {ask} and query the database to get the result."   

    #ask the sequential planner to identify a suitable function from the list of functions available.
    plan = await planner.create_plan(goal=userask)  
 
    # Invoke the plan and get the result
    result = await plan.invoke(kernel=kernel)
    steps = [("Description:", step.description, "Function: " , step.plugin_name + "." + step._function.name) for step in plan._steps]  
    answer = to_json(result)    
    return_value = {"result": answer, "steps": steps}
  
    return return_value


