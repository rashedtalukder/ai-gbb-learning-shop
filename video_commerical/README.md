# Azure OpenAI Sora Image Generator Example
This example takes command line arguments to generate videos using a Azure OpenAI Sora model and saves them to a ./outputs/ folder.

## Prerequisites
Before setting up, ensure you have the following:
* Azure subscription: Required to set up services
* miniconda: Installed and the command "conda" works because it's been added to your PATH
* Python 3.11 conda environment: There should be an existing Python 3.11 environment called ai-gbb-workshop.
* Azure CLI: Installed and configured


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
AZURE_OPENAI_ENDPOINT="https://{{YOUR_AI_PROJECT_RESOURCE_NAME}}.services.ai.azure.com"
AZURE_OPENAI_API_KEY="{{YOUR AOAI KEY}}
AZURE_OPENAI_DEPLOYMENT_NAME="{{MODEL_DEPLOYMENT_NAME}}"
AZURE_AI_API_VERSION="2025-02-15-preview"
```

## 3. Generate a video
This application simply calls the endpoint for generating a video. There are only a few available image sizes that are supported and maximum duration of 20 seconds. Read more of the constraints in the SDK's README in the **rashed_sora_sdk** folder.

### 3.1 Run the example
The example takes arguments from your terminal. To generate a video, issue the command
```bash
python examples/sora_example_cli.py --prompt="A Chihuahua eating a taco on a counter in a Taco Bell"
```

### 3.2 Open the generated and downloaded video
Go to the **outputs** folder and view the .mp4 video file. There is also a gif that's generated.

### 3.3 Other configurations
To see what are the other available configuration arguments that the example can take, use
```bash
python examples/sora_example_cli.py --help
```
