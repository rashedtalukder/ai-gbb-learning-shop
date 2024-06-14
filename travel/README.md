# Assistants Workshop

## Prerequisites
This demo reuses some of the part from the **pricing** workshop. Make sure you've completed that workshop before continuing.

## Background
Contoso Adventures is a travel agency specializing in vacation packages to select destinations. This simple backend system takes user questions and answers them either from available internal files (e.g., promotional brochures) or their databases (e.g., flight travel time data). They are not very tech sauvy, but they believe this will help provide quicker answers for customers especially in all hours. They want to get up and going quickly, so they decide to use the Assistants API (preview) for Azure OpenAI.

## Activate Conda
To keep things isolated from libary conflicts and other issues, you'll need to reactivate your conda virtual environment. To do so, from terminal, enter the command:
```
conda activate ai-gbb-workshop
```

## Configuration
We'll reuse the same Function App as before if you haven't deleted the resource already. If you have, follow the steps from the last workshop to create a new one using the Azure extension. By using the existing Function App, you can import the existing configuration as well. To import the configuration:
1. Go to the Azure Tools Extension.
2. From the resources drop down, select your subscription, then **Function App**, your Function App name, then *right click* **Application Settings**, **Download Remote Settings**
3. Go to the VS Code file explorer and open the newly created file in **travel\local.settings.json**
4. In terminal, enter the command `func settings decrypt`

As long as you're using a compatible Azure OpenAI model and haven't rotated keys or switched to a different region, almost everything can stay the same. Except the API version. The Assistants API is currently only compatible with Azure OpenAI API versions
- 2024-02-15-preview
- 2024-05-01-preview

So for the parameter **AZURE_OPENAI_API_VERSION**, replace the string with `2024-05-01-preview`.

Re-encrypt your local settings so you don't accidentally share it with someone and have it exposed by going back to terminal and issuing the command `func settings encrypt`. 

Reupload the change by:
1) Going to Azure Tools extension.
2) *Right click* **Application settings**.
3) Click **Upload local settings**.
4) This will then ask to overwrite the value, select yes.

## File and Code Review
Looking at the file structure contents, you can see that there is a **travel\data** folder with two files. One is a PDF that contains a brochure and a CSV that contains fake flight travel times from different airports. If you want to inspect these, feel free to _right click_ and select **Reveal in File Explorer** to then open it with other apps.

The code is self-contained in the file **function_app.py**. You can view some of the commented lines that are prefixed with a **#**. Everything on that line after that symbol in Python is an intended-for-humans comment and will not execute as code. 

## Deploying, Logging, and Testing
### Deploy
The app has everything baked in to it to work. To bundle it up, upload, and deploy the Function App, _right click_ the **pricing/function_apps** folder, select **Deploy to Function App**, select the resource group you're using.

> **_NOTE:_** You might see an error when trying to deploy complaining about "azureFunctions.deploySubpath." To remedy this, open **\.vscode\settings.json** and delete the line that says **"azureFunctions.deploySubpath": "pricing/function_app",**. Save the file and try again.

### View Logs
To view the logs, go to Azure Tools extension, and under your Function App's name, expand **Logs**. The select **Connect to Log Stream...**.

### Test
The LLM was given the user prompt "What are the highlights of going to Kyoto, Japan and are flights included in the package? What is the average travel time from Seattle?"

To test the functionality, go to the Azure Tools extension, under your Function App's name, expand **Functions** and *right click* your function name. Select **Copy Function URL** and paste that in your browser. It'll take a few seconds, but should show an output.

## Quiz
What about creating the vector store and uploading the files to the vector store in Azure Function Apps makes it a bad idea or an anti-pattern?

## Next steps
What are some other use cases for a travel agency? How do you want to build out the features of this app? Try it out! Work on it yourself, or find people to partner with. 

Some hints to remember: last workshop we also used query parameters to retrieve extra fields. You can also use dynamic paths of your function's endpoint to get more inputs from the user (see [docs](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger?tabs=python-v2%2Cisolated-process%2Cnodejs-v4%2Cfunctionsv2&pivots=programming-language-python#customize-the-http-endpoint)).