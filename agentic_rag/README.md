# Multi-agent RAG with LangGraph Workshop

This repository provides the resources and instructions for a hands-on workshop focused on using LangGraph to create and orchestrate a number of agents and respective tooling for them to utilize in order to achieve a task. The workshop is designed to guide participants through the process of building a basic agentic application.

## Prerequisites

Before you begin, ensure you have completed the [prior workshops](../README.md). In general, you should have the following already:
- **Azure OpenAI Resource**: Need to also have the endpoint URL and API get ready.
- **GPT-4o Model Deployed**: In the Azure OpenAI resource, deploy the latest GPT-4o model with standard deployment. Not the deployment name as you'll need it later.
- **VS Code**: Install Visual Studio Code.
- **GitHub Repo**: Clone the [ai-gbb-learning-shop](https://github.com/rashedtalukder/ai-gbb-learning-shop) repository from GitHub.
- **Environment**: Initiate command prompt/terminal/powershell in VS Code and set up a temporary coding environment with conda (`conda activate ai-gbb-workshop`).

### Install Python Dependencies
Install required libraries as listed in the **requirements.txt**. The libraries here provide accelerated development by reusing code.

1. With the repository open in VSCode, and from within the terminal/command prompt window in VSCode, navigate to the **agentic_rag** directory.
2. Making sure that your conda environment is active first, enter the the following to read the contents of requirements.txt and install using the pip package mangement tool for Python:
```
pip install -r requirements.txt
```

## Running the Application within Jupyter Notebooks
Go to the **agentic_rag.ipynb** file, hover over the top code block and press the _play_ button that shows up on the top-left edge of that block. It will now prompt you to paste in your Azure OpenAI API key into a pop-up in the top-middle of VS Code. The lecture will contain guidance for what the blocks do and the implemented concepts of a graph-RAG pattern as implemented with the LangGraph framework.

## Conclusion
By the end of this workshop, you now have hands-on experience building and modifying flows in prompt flow, and you know how to evaluate their performance using a testing dataset.