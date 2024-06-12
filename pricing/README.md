# Pricing Workshop

## Prerequisites
- Visual Studio Code
- Git
- Python (version 3.11.x) OR miniconda
- [Azure Tools VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)
- Azure CLI (version X.X.X)
- Azure Functions Core Tools

### Miniconda install & usage (highly recommended)
Miniconda is a great way to manage your python virtual environments and the dependencies for your application. These virtual environments help isolate one application from another as you develop them. Imagine a scenario where you have two packages named "OpenAI" but you needed one version for one app, and another for this one. How would you or the apps know? If they got mixed up for some reason, you could get unintended consequences.

To install miniconda and start up an environment with the necessary version of Python and required dependencies:
1. Download and install from: https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe.
2. Restart your computer.
3. Open Visual Studio Code, press **Control**+**Shift**+**P**, and select **Python: Select Interpreter**, then select the item in the list that has "miniconda" in the path.
4. Open a new terminal window by going to the top navigation bar, selecting **Terminal** and then **New Terminal**.
5. Create a new conda virtual environment using `conda env create -f environment.yml` into terminal window.
6. After it's created and everything has been installed, activate the environment `conda activate ai-gbb-workshop`.

### Azure CLI install & configuration
The Command Line Interface (CLI) simplifies managing your Azure services and makes it possible to be systematic. Most all developers will use these types of tools instead of the UI.

Install by following the official guide [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?tabs=azure-cli)

Then sign in to Azure in Terminal with the command `az login`.

Add your subscription configuration using the command below and replacing your subsciption id or name:
```
az account set --subscription <name or id>
```

### Azure Core Tools install
Follow the instructions in the [official docs](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python)

### Configure VS Code Azure Tools Extension
After installing [Azure Tools VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack), look for the new Azure logo on the left navigation in VS Code. Once you click it, it will have an option to sign in to Azure in the left browsing pane.

### Creating an Azure Functions App
It's easiest to do this via the Azure Tools extension.

1. From the **RESOURCES** section, find your subscription and expand it, then *right* click on **Function App**, click **Create Function App in Azure**.
2. Enter a unique but memorable name for your new function app in the text bar that opens.
3. Consumption hosting plan.
4. Python 3.11
5. Select either a new or add this to an existing resource group. It's recommended you create a new one since it's easier to delete later if it's under one resource group since you can delete everything in the resource group instead of deleting each individual resource to preserve your configuration.
6. Create a new storage account.
7. Create a new app insights resource. This is what we'll use to get logs and metrics later.

### Add Your Local App to the Deployment 


### Get Existing Environmental Variables
From the Azure Tools extension, under **RESOURCES**, open your subscription, open **Function App**, open your function app's name, then *right* click **Application Settings**, **Download Remote Settings**.

### Add Your OpenAI Configs to Env Variables
The app currently doesn't know how to access Azure OpenAI service without the configuration details. You can add each of the neccessary details:

Add your Azure OpenAI API Key by pasting the following, pressing enter and then it'll ask you to paste in the key itself.
```
func settings add AZURE_OPENAI_API_KEY
```

Add your Azure OpenAI endpoint URL by pasting the following, pressing enter and then it'll ask you to paste in the endpoint URL.
```
func settings add AZURE_OPENAI_ENDPOINT
```
Add your Azure OpenAI chat model name by pasting the following, pressing enter and then it'll ask you to paste in the deployment model name.
```
func settings add AZURE_OPENAI_CHAT_DEPLOYMENT
```

Lastly, add the API version which should be **2024-02-01** after pasting the command into terminal
```
func settings add AZURE_OPENAI_API_VERSION 2024-02-01
```
Go to the **pricing\function_completion** directory.
Encrypt these before sending over the internet using `func settings encrypt`. Note that this doesn't keep them encrypted in Azure. You'll need to use key vault for that instead. This just encrypts it locally and in flight.

### Publish Function App and Environmental Variables
In terminal, paste the following and replace `<function app name>` with your function app's name and no brackets:
`func azure functionapp publish <function app name> --python --publish-local-settings -i`

### Test the Deployed Function
From the Azure Tool's **RESOURCES** pane, go to the **Function App**, your function name, expand **Functions**, and then right click the name of the function that gets invoked called **function-completion**. Select **Copy function URL**. Paste this URL into the browser.

You should see a few things the the URL path. The endpoint **chat** is the name of route in the code. That's followed by a string with the key **code**. This is the equivalent to an access token that this type of function has. If you remove the code or change it, you'll find it doesn't work. Go ahead, press enter and see the response.

Now, let's give a quick string to test our ChatGPT completions endpoint by adding `&prompt=hello` to the very end of the URL. 
It'll look something like `https://<your function name>.azurewebsites.net/api/chat?code=<your access token>&prompt=hello`

We can send many requests using the little script in the file **prompt_ddos.py**. Go to the **pricing\tools\\** folder and run the command `python prompt_ddos.py`. Input the items the script asks for. Recommend at least 20 requests.

## Gather Metrics and Calculate Pricing

### Functions Costing
For Azure Functions and many other services, you can attach Application Insights feature of Azure Monitor. This was done when you first set up the Function App (remember?). Application Insights lets you run a number of rich queries that isn't readily available in the standard metrics set for Azure Monitor.

You'll be looking at pricing based on the [Azure Function Apps consumption plan pricing table](https://azure.microsoft.com/en-us/pricing/details/functions/#pricing). Be sure the correct region is selected to match where you are deployed.

To view the application insights,
1) From Azure Tools **RESOURCES** pane, select your function name and *right* click it. Then click **Open in Portal*.
2) Under the **Functions** tab on the main pane, click the link to your function's name.
3) Click **Invocations**
4) Click **Open in Application Insights**
5) In the query textbox, remove the line that says `Take 20`. That will truncate to just the most recent 20 recents.

This query will give you all the requests over the past 30 days. You can export this and calculate the total duration and number of invocations.

#### Challenge
Write the query that provides the count and the total execution time.

### Azure OpenAI Cost Insights
[Azure OpenAI's (AOAI) pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/#pricing) is based on model, input tokens, and output tokens. We can go to the Azure Portal dashboard for your AOAI service and select the **Metrics** menu item. From there, we need to select the sum of **Generated Completion Tokens** and then add another metric for **Processed Prompt Tokens**.

### Calculating Azure OpenAI Invocations in Function App Costs
Since the Function App logs include the token counts for each invocation, you can retrieve the logs to then calculate the actual cost of each chat session and compare that to what gets billed. There is an example in  **pricing\app_insights.py**. It has two methods demonstrating querying available metrics and also logs in App Insights. To retrieve your data, you need your App Insights resource Id:

1) Go to the Azure Tools extension and go to your Function App in the **RESOURCES** pane.
2) *Right* click on the name of your function and select **View Properties**.
3) Copy the value under `Site.tags.["hidden-link: /app-insights-resource-id"]`.
4) Paste that in the file **app_insights.py** for the variable **APP_INSIGHTS_RESOURCE_ID**
5) Run the app by going to the terminal window and the **pricing** folder and entering the command `python app_insights.py`

## Hack Away!
With the remaining time, scope a possible use case with what you've learned so far. You could, for example, use the Assistants API to generate code to graph the data and take user inputs to manipulate the data.

## Further Reading
https://techcommunity.microsoft.com/t5/fasttrack-for-azure/azure-openai-insights-monitoring-ai-with-confidence/ba-p/4026850
https://learn.microsoft.com/en-us/azure/architecture/ai-ml/openai/architecture/log-monitor-azure-openai