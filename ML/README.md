# Azure ML + Fine-Tuning Workshop

In this workshop, we'll cover an overview of Azure Machine Learning and try our hand at fine-tuning.

### Azure Machine Learning Setup (Web)

- In your browser, go to [ml.azure.com](ml.azure.com). Click your profile picture in the top right and switch your **Directory** to *Microsoft Non-Production*.
- Next, select **Workspaces** and create a new one. This can reside in the Resource Group of your choosing, but set the Region to East US 2 (this region choice is necessary for fine-tuning Phi-3).

Once your Workspace is created, go into the Data tab and under Data Assets, click Create. Name your asset "medquad_csv" and keep the type as File (uri_file). Hit next, then choose "From Local Files". WorkspaceBlobStore should be checked - keep it that way and select Next again. Go ahead and upload the medquad.csv file here. Once created, go into the Data Asset and copy the "Datastore URI" - this will be handy for our next step.

Under the Compute Tab, go to Compute Instances and create a new Compute Instance. For our purposes, you can select the lowest-tier SKU available.

### Azure Machine Learning Extension for VSCode

In order to proceed, you'll need to download an install the AML extension for VSCode [here](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-ai). This will allow you to run the fine-tuning notebook remotely on an AzureML Compute Instance and not burden your local laptop's resources.

We'll now have to login to the proper subscription and select the right workspace for the job. Navigate to the *~1-ExploreData.ipynb~* file, click *Select Kernel* in the top right, then click *Azure ML Compute Instances* - this will ask you to sign into your Microsoft account, so allow the necessary permissions and proceed with login in your browser. Once back in VS Code, select your **MCAPS** subscription from the list, then select the **Workspace** you created in the last step. Lastly, select the **Compute Instance** that we created in the prior step.

Now you can run through the notebook without burdening your laptop!

We'll run through ~1-ExploreData.ipynb & ~2-TrainModel.ipynb while we wait for our model to fine-tune...

### Data Asset Upload

If the prior notebook won't run, go ahead and directly upload "medquadshort.jsonl" to your Datastore by selecting the Data tab under Assets, then Create, then "From Local Files", select the file, keep the default workspaceblobstore checked, then continue with the upload.

### Fine-Tuning Job

In your AML Workspace, go to Model Catalog, filter by Microsoft, and select Phi-3-mini-4k-instruct.
Select "Fine-Tune" and then "Pay-as-you-Go". Give your model a name, then for the data source, select Data in Azure AI Studio and select the data asset that we just uploaded (make sure you're picking the jsonl, not the csv). Continue with an automated split and keep all default parameters. Go ahead and submit your job! (Note: this may take some time to complete.)

# Supplemental Materials on MaaS

## Model Catalog: MaaS = Model as a Service
MaaS encompasses every model we offer natively on Azure *outside* of the OpenAI suite of models.
Some notable examples include:
- Phi-3, Mistral, Llama3, Stable Diffusion, Nemotron, etc
Some curated models are offered via a **Serverless API** in which we manage the compute infrastructure and the customer is charged on a pay-as-you-go basis.
Anything else will have to be deployed via the **Managed Compute** option, in which you pay a fixed rate for a VM capable of hosting the model, and you can call your endpoint as many times as the hardware will allow.
- Info on how to consume the endpoint can be found [here](https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints?view=azureml-api-2).

[More info on Model Catalog](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-catalog?view=azureml-api-2)

[Announcement on MaaS](https://techcommunity.microsoft.com/t5/ai-machine-learning-blog/welcoming-mistral-phi-jais-code-llama-nvidia-nemotron-and-more/ba-p/3982699)

### HuggingFace Model Example
[Tutorial](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-models-from-huggingface?view=azureml-api-2)

-----
# Supplemental Materials for Deeper Dives into Various Aspects of AML

## Notebooks
This section contains sample Notebooks that demo running code with the AzureML Python SDK v1 and v2.
[More info on Notebooks](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-run-jupyter-notebooks?view=azureml-api-2)

## Automated ML

This section allows for easy kickoff of AutoML jobs.
[More info on AutoML](https://learn.microsoft.com/en-us/azure/machine-learning/concept-automated-ml?view=azureml-api-2)

## Designer

Designer in Azure Machine Learning studio is a drag-and-drop user interface for building machine learning pipelines in Azure Machine Learning workspaces.
[More info on Designer](https://learn.microsoft.com/en-us/azure/machine-learning/concept-designer?view=azureml-api-2)