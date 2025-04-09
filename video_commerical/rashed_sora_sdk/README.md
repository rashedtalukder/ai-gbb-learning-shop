# Azure Sora SDK

A Python SDK for interacting with the Azure OpenAI Sora Video Generation API. This library provides a convenient interface for generating AI videos using OpenAI's Sora model on Azure.

## Features

- Full support for all Azure Sora API endpoints
- Asynchronous operations for improved performance
- Comprehensive error handling
- Type hints for better development experience
- Support for polling job status until completion
- Utilities for downloading and saving generated videos and GIFs

## Installation

```bash
pip install -e .
```

## Requirements

- Python 3.11 or higher
- Azure OpenAI resource with Sora enabled

## Authentication

The SDK uses the following environment variables for authentication:

```bash
# Required
AZURE_OPENAI_ENDPOINT=https://{YOUR-RESOURCE-NAME}.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-sora-deployment-name

# Optional
AZURE_AI_API_VERSION=2025-02-15-preview  # Default if not specified
```

Alternatively, you can provide these values directly when initializing the client:

```python
from azure_sora_sdk.client import SoraClient

client = SoraClient(
    endpoint="https://{YOUR-RESOURCE-NAME}.openai.azure.com",
    api_key="your-api-key",
    deployment_name="your-sora-deployment-name"
)
```

## Quick Start

```python
import asyncio
from azure_sora_sdk.client import SoraClient
from azure_sora_sdk.models import CreateVideoGenerationRequest

async def generate_video():
    async with SoraClient() as client:
        # Create a video generation request
        request = CreateVideoGenerationRequest(
            prompt="A serene mountain landscape with a flowing river",
            width=640,
            height=360,
            n_seconds=5,
            n_variants=1
        )
        
        # Submit the job
        job = await client.create_video_generation_job(request)
        print(f"Job created with ID: {job.id}")
        
        # Poll until the job completes
        job, generations = await client.poll_job_until_complete(job.id)
        
        # Download the generated video
        if generations:
            output_path = f"output_{generations[0].id}.mp4"
            await client.save_video_content(generations[0].id, output_path)
            print(f"Video saved to: {output_path}")
        
        # Clean up
        await client.delete_video_generation_job(job.id)

if __name__ == "__main__":
    asyncio.run(generate_video())
```

## Example Script

The `examples/sora_example.py` script provides a full-featured example of working with the Azure Sora SDK. It demonstrates a complete workflow from job creation to video download.

### Usage

```bash
# Set environment variables (replace with your values)
export AZURE_OPENAI_ENDPOINT="https://{YOUR-RESOURCE-NAME}.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your-sora-deployment-name"

# Run the example script
python examples/sora_example.py --prompt "A serene lake with mountains in the background" --width 640 --height 360 --duration 5
```

### Command Line Options

- `--prompt`: Text prompt for video generation (default: "A serene mountain landscape with a flowing river")
- `--width`: Video width in pixels (default: 640)
- `--height`: Video height in pixels (default: 360)
- `--duration`: Video duration in seconds (default: 5)
- `--variants`: Number of video variants to generate (default: 1)
- `--output-dir`: Output directory for videos (default: "./outputs")
- `--list-only`: Only list existing jobs without creating new ones
- `--job-id`: Job ID to monitor (if provided, won't create a new job)

## Supported Video Parameters

- **Resolutions**: 360x360, 640x360, 480x480, 854x480, 720x720, 1280x720, 1080x1080, 1920x1080
- **Duration**: Up to 20 seconds (10 seconds max for 1080p)
- **Variants**: Up to 2 (limited to 1 for 1080p)
- **Pending tasks**: Limited to 1 job at a time (may increase to 2 in future updates)

## API Reference

For detailed API reference, please see the docstrings in the code or the official Azure OpenAI Sora documentation.

## Best Practices

1. **Error Handling**: Always implement proper error handling as API calls can fail for various reasons.
2. **Clean Up**: Delete jobs after you've downloaded the content to maintain quota.
3. **Resolution Limits**: Use appropriate resolution for your use case, noting the limits on duration and variants.
4. **Polling**: Use polling intervals that are reasonable (5+ seconds) to avoid rate limiting.
5. **Security**: Never hardcode API keys; use environment variables or Azure Key Vault.

## Security Recommendations

1. Use Managed Identity where possible for Azure-hosted applications
2. Implement least-privilege access principles
3. Store API keys securely (Azure Key Vault, environment variables, etc.)
4. Implement API key rotation mechanisms
5. Monitor usage for unusual patterns

## License

[MIT License](LICENSE)