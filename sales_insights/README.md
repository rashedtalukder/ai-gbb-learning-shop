# Semantic Kernel Workshop: Natural Language (NL) to SQL Query Generation using Azure OpenAI (GPT-4 model)

## This workshop will focus on below customer use-case:

A contoso company wants to build an AI Assistant which can be used by their non technical business users to get information on their product sales data. The data resides in a SQL database and the business users wants to analyze that data using natural language queries as they might not have the technical expertise to write T-SQL queries. They also want to the results to be summarized in plain text. 

So, for the purpose of this workshop we will use an Azure SQL databse which will host some sample product sales data that we will query with natural language using Semantic Kernel Pipeline and the power of LLMs.  

## Semantic Kernel Overview and the workshop setup details
In this reworkshop we demonstrate how to use [Semantic Kernel](https://github.com/microsoft/semantic-kernel) to convert Natural Language (NL) to SQL Query using Azure OpenAI (GPT-4 model).

Semantic Kernel is an exciting framework and a powerful tool that can be used for several applications, including chatbots, virtual assistants, and more. 

This is a great way to make your data more accessible to non-technical users, and to make your applications more user-friendly.

Below are the main components of the Semantic Kernel:

![Orchestrating plugins with planner](./images/sk-kernel.png)

In the example of this repo, we developed the following plugin:

- **nlpToSqlPlugin**: This plugin is responsible for converting the Natural Language (NL) to SQL Query using Azure OpenAI (GPT-4 model).

As part of the plugin, we developed skills throught the use of [prompts](https://learn.microsoft.com/en-us/semantic-kernel/prompts/). The following skills were developed:

- **ConvertNLPToSQL**: This skill is responsible for converting the Natural Language (NL) to SQL Query using Azure OpenAI (GPT-4 model).
- **MakeSQLCompatible**: This skill is responsible for making the SQL Query compatible with the Transact-SQL syntax.
- **WriteResponse**: This skill is responsible for writing the response to the user.

We also developed a [Native Function](https://learn.microsoft.com/en-us/semantic-kernel/agents/plugins/using-the-kernelfunction-decorator?tabs=python) to be able to interact with the database:

- **QueryDb**: This function is responsible for querying the database and returning the result.

With that, we can create a "Copilot like" experience, where the user can ask questions and the system will generate the SQL Query and return the result.

As our plugin has a lot of skills, we also developed a [Sequential Planner](https://learn.microsoft.com/en-us/semantic-kernel/agents/plugins/using-the-kernelfunction-decorator?tabs=python) to orchestrate the skills:

With the planner, we can orchestrate the skills in a sequence, so the system can generate the SQL Query and return the result.

The final result is a system that can convert Natural Language (NL) to SQL Query using Azure OpenAI (GPT-4 model).

## Requirements

- You must have a Pay-As-You-Go Azure account with administrator - or contributor-level access to your subscription. If you don't have an account, you can sign up for an account following the instructions.
- Get Access to [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview)
- Once got approved create an Azure OpenAI in you Azure's subcription.
- Python 3.11
- You must have an Azure SQL Database with the tables and data you want to query. In this repo, we will use the a Sample database with some tables.

## Azure SQL DB Setup with sample data
- You can use [generate-sample-sql-data](sql-data/generate-sample-sql-data.py) script to create and populate the tables with some sample data.
- Make sure you use both SQL Authentication and Microsoft Entra suthentication for your SQL Server for the purpose of this demo. You can disable Microsoft Entra auth only option under settings --> Microsoft Entra ID. Just uncheck the "Support only Microsoft Entra authentication for this server" option. 

## Install Required Libraries (Python Dependencies)
Install required libraries as listed in the requirements.txt. The libraries here provide accelerated development by reusing code.

1. With the repository open in VSCode, and from within the terminal/command prompt window in VSCode, navigate to **your project** directory.
2. Making sure that your conda environment is active first, enter the the following to read the contents of requirements.txt and install using the pip package mangement tool for Python:
```
pip install -r requirements.txt
```


```python
semantic-kernel==0.5.1.dev0
python-dotenv==1.0.0
openai==1.12.0
Faker==23.2.1
pyodbc==5.1.0
```

## Create .env file (Rename any sample.env)

```
CONNECTION_STRING=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
```

*Make sure that the CONNECTION_STRING you pick is the one for the ODBC connection. It should start with Driver={ODBC Driver 18 for SQL Server}; You can find the connection string under your <Azure SQL Database> --> Settings --> Connection strings --> ODBC

## Quick Start

- Run `sql-data/generate-sample-sql-data.py` script to create and populate the tables with some sample data
- Run `main.py` to run the sample asks/questions detailed below.

## Sample - Questions/Asks

Below are some sample questions/asks that can be asked to the system and the responses that the system will generate.
These responses can be different based on the data in the database. If you use our generate-fake-data script, you may have different responses given the random nature of the data.

**Question/Ask 01**: I want to know how many transactions in the last 3 months

*Response*: According to the database query, the number of transactions is 26 (actual nuber will vary for your run).

---

**Question/Ask 02**: Give me the name of the best seller in terms of sales volume in the whole period

*Response*: The seller's name according to the database query is John Doe.

---

**Question/Ask 03**: Which product has the highest sales volume in the last month

*Response*: According to the database query, the total sales volume for the product 'Nike Air Force 1' is 28.

---

## Adapt to your own data

Feel free to adapt the code to your own data. You can use your own data and modify the code to fit your needs.

- Replace the connection string in the `.env` file with your own connection string.
- Replace the Azure OpenAI API key and endpoint in the `.env` file with your own API key and endpoint.
- Replace the table's structure in [ConvertNLPToSQL](plugins/nlpToSqlPlugin/ConvertNLPToSQL/skprompt.txt) Plugin with your own table's structure.


## Bonus Excersise: Create Prompt Flow to run and evaluate Semantic Kernal Planner
Once the setup is complete, you can conveniently convert your existing Semantic Kernel planner to a prompt flow by following the steps below:

- An existing promptflow is already created for you under folder "promptflow/rag-on-sql-planner"
- If you go to your VSCode left nav under PrompFlow (P), you should see an existing promptflow under Flows
- If you are not able to see that, then you can create a new flow using the below steps:
### Follow these steps if you are not able use existing flow to create new one
- Right click the folder and select new flow in this directory and create a blank or standard flow
- Select the + Python icon to create a new Python node.
- Name it "rag-on-sql-sk-planner" or the planner name of your choice
- use the sk_rag_on_sql_planner.py as the code file
- copy the "plugins" directory from the project root directory here to use the plugins as reference

### Setup custom connection to use Azure Open AI service and SQL Connection String
- create a custom connetion and name it "custom_connection"
- Add "AZURE_OPENAI_API_BASE", "AZURE_OPENAI_API_KEY" and "SQL_CONNECTION_STRING" to the custom connection and save it. 
- Define the input and output of the planner node.
- Set the flow input and output (refer flow.dag.yaml) 
- test the flow with single test run with some default input



## References

- <https://learn.microsoft.com/en-us/semantic-kernel/overview/>
- <https://techcommunity.microsoft.com/t5/analytics-on-azure-blog/revolutionizing-sql-queries-with-azure-open-ai-and-semantic/ba-p/3913513>
- <https://github.com/microsoft/semantic-kernel>
- <https://medium.com/@ranjithkumar.panjabikesanind/orchestrate-ai-and-achieve-goals-combining-semantic-kernel-sequential-planner-openai-chatgpt-d23cf5c8f98d>
