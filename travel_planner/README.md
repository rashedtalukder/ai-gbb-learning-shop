# AI-Powered Travel Planner

An agent via AI Agent Service is used to generate daily activity plan recommendations based on the user's travel itinerary that's located in a file.

## Prerequisites

Before setting up the project, ensure you have the following:
- **Azure subscription**: Required to set up services
- **miniconda**: Installed and the command "conda" works because it's been added to your PATH
- **Python 3.11 conda environment**: There should be an existing Python 3.11 environment called `ai-gbb-workshop`.
- **Azure CLI**: Installed and configured

## 1. Azure Portal Setup

### 1.1 Create an Azure AI Services Resource
You'll be using an Azure AI services deployment, which includes Content Understanding service, which you'll be using in order to parse travel itinerary documentation. 
1. Go to the Azure Portal.
2. Search for Azure AI Services and create a new resource.
3. Select the lowest pricing tier.
4. Copy the endpoint and API Key after deployment.

### 1.2 Set Up Azure Blob Storage for PDF Templates
1. In the Azure Portal, search for Storage Accounts.
2. Click Create and set up the storage account.
3. In Containers, create a new container named `travel-itineraries`.
4. Upload the PDF template (`travel_itinerary.pdf`).
5. Copy the Storage Account Connection String.

## 2. Environment Setup

### 2.1 Clone the Repository
```bash
git clone https://github.com//rashedtalukder/ai-gbb-learning-shop.git
cd travel_planner
```

### 2.2 Load Conda Environment and Install Required Python Packages
```bash
conda activate ai-gbb-workshop
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables
Create a `.env` file in the root of your project and add the parameters below, filling out individual fields accordingly:
```env
AZURE_AI_ENDPOINT="https://{{YOUR_AI_PROJECT_RESOURCE_NAME}}.services.ai.azure.com"
AZURE_AI_API_VERSION="2024-12-01-preview"
AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS="{{YOUR_AZURE_FOUNDRY_CONNECTION_STRINGS}}"
AZ_MODEL_DEPLOYMENT_NAME="{{YOUR_AOAI_DEPLOYMENT_NAME}}"
BING_CONNECTION_NAME="{{YOUR_BING_CONNECTION_NAME}}"
ITINERARY_FILE_URL="https://{{YOUR_STORAGE_SUBDOMAIN}}.blob.core.windows.net/travel_itineraries/travel_Itinerary.pdf"
```

## 3. Running the AI Pipeline
In this application, we are using the Azure AI Agent service and utilizing a few of it's capabilities (e.g., function calling, Grounding with Bing, and message state storage) to autonomously handle different customer requests and recommend a rich travel experience based on their existing travel plans.

The Agent is able to ingest itinerary that's either pasted in, or using function calling of custom code, ingest a document from a URL. That data ingestion triggers a job in Content Understanding to parse the data and send it back to the LLM.

Additionally, the AI Agent has the capability to perform a Bing search and gather additional/current recommendations to satisfy the user query.

The final functionality is the ability to export the updated travel plan to a local file so that it can be viewed offline while traveling. This is done via another function call that we've defined.

### 3.1 Run Automated AI Execution
Run the following command to start the agent:
```bash
python src/app.py
```

### 3.2 Review the Code
Dive in to the `app.py` file and `tool_functions.py` to see how this application works, the prompts provided, and the SDKs used.

## 4. Automating with Azure Functions (Optional)
To automate itinerary processing with Azure Functions:
1. Deploy the project to Azure Functions.
2. Configure it to trigger when a new PDF is uploaded to Azure Blob Storage.
3. Connect it with the AI Services API to generate the itinerary automatically.

## 5. Conclusion
Your AI-powered travel itinerary is now set up! You can now generate AI-enhanced itineraries,
complete with recommendations and a professional PDF format.
Run the pipeline anytime using:
```bash
python app.py
```