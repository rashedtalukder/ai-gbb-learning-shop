#!/usr/bin/env python

#    Copyright 2025 Rashed Talukder
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Example usage of Rashed's Sora SDK for video generation.

This script demonstrates how to use Rashed's Sora SDK for common video generation tasks:
1. Creating a video generation job
2. Checking job status
3. Listing all jobs
4. Downloading generated videos and GIFs
5. Cleaning up completed jobs

Requirements:
- Python 3.11+
- Azure OpenAI resource with Sora enabled
- Environment variables in .env file
"""

from rashed_sora_sdk.models import CreateVideoGenerationRequest, JobStatus
from rashed_sora_sdk.client import SoraClient, SoraClientError
import os
import asyncio
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Import Rashed's Sora SDK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rashed_sora_example")

# Validate required environment variables
required_env_vars = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "AZURE_OPENAI_API_VERSION"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}. "
        f"Please add them to your .env file."
    )

# Log Rashed's Sora configuration (without exposing the full API key)
logger.info(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
logger.info(
    f"API Key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
logger.info(f"Deployment Name: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
logger.info(f"API Version: {os.getenv('AZURE_OPENAI_API_VERSION')}")


async def create_video_job(client, prompt, width, height, duration, variants=1):
    """Create a new video generation job."""
    logger.info(f"Creating new video job with prompt: '{prompt}'")

    # Create the request object
    request = CreateVideoGenerationRequest(
        prompt=prompt,
        width=width,
        height=height,
        n_seconds=duration,
        n_variants=variants
    )

    # Submit the job
    try:
        job = await client.create_video_generation_job(request)
        logger.info(f"Job created successfully! Job ID: {job.id}")
        return job
    except SoraClientError as e:
        logger.error(f"Failed to create job: {e.message}")
        if e.error_details:
            logger.error(f"Error details: {e.error_details}")
        return None


async def monitor_job(client, job_id, polling_interval=5.0):
    """Monitor a job until it completes."""
    logger.info(f"Monitoring job {job_id}...")

    try:
        job, generations = await client.poll_job_until_complete(job_id, polling_interval)

        if job.status == JobStatus.SUCCEEDED:
            logger.info(
                f"Job completed successfully with {len(generations)} generations")
            for i, gen in enumerate(generations):
                logger.info(
                    f"Generation {i+1}: ID={gen.id}, Created at: {gen.created_datetime}")
            return job, generations
        else:
            logger.info(f"Job completed with status: {job.status}")
            return job, []

    except SoraClientError as e:
        logger.error(f"Error monitoring job: {e.message}")
        return None, []
    except ValueError as e:
        # Handle case where API returns a status not in our enum
        if "is not a valid JobStatus" in str(e):
            logger.warning(f"Received unknown job status: {str(e)}")
            logger.warning(
                "This may be due to an API update. Continuing with available data.")
            return None, []
        else:
            logger.error(f"Value error in job monitoring: {e}")
            return None, []
    except TimeoutError as e:
        logger.error(f"Timeout waiting for job: {e}")
        return None, []


async def download_video(client, generation_id, output_dir):
    """Download a generated video to the specified directory."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename based on generation ID
    video_file = os.path.join(
        output_dir, f"sora_video_{generation_id}.mp4")
    gif_file = os.path.join(
        output_dir, f"sora_preview_{generation_id}.gif")

    logger.info(f"Downloading video for generation {generation_id}...")

    try:
        # Download and save the video file
        await client.save_video_content(generation_id, video_file)
        logger.info(f"Video saved to: {video_file}")

        # Download and save the GIF preview
        try:
            await client.save_gif_content(generation_id, gif_file)
            logger.info(f"GIF preview saved to: {gif_file}")
        except SoraClientError as e:
            logger.warning(f"Failed to download GIF preview: {e.message}")

        return video_file
    except SoraClientError as e:
        logger.error(f"Failed to download video: {e.message}")
        return None


async def list_all_jobs(client, limit=50):
    """List all video generation jobs."""
    logger.info(f"Listing all jobs (limit: {limit})...")

    try:
        job_list = await client.list_video_generation_jobs(limit)

        logger.info(f"Found {len(job_list.data)} jobs:")
        for i, job in enumerate(job_list.data):
            status_str = f"{job.status.value}" if hasattr(
                job.status, 'value') else f"{job.status}"
            logger.info(
                f"Job {i+1}: ID={job.id}, Status={status_str}, Prompt='{job.prompt}'")

            if job.status == JobStatus.SUCCEEDED and job.generations:
                logger.info(f"  - Contains {len(job.generations)} generations")

        if job_list.has_more:
            logger.info("More jobs available. Consider increasing the limit.")

        return job_list
    except SoraClientError as e:
        logger.error(f"Failed to list jobs: {e.message}")
        return None


async def clean_up_job(client, job_id):
    """Delete a job after processing is complete."""
    logger.info(f"Cleaning up job {job_id}...")

    try:
        success = await client.delete_video_generation_job(job_id)
        if success:
            logger.info(f"Job {job_id} deleted successfully")
        return success
    except SoraClientError as e:
        logger.error(f"Failed to delete job: {e.message}")
        return False


async def full_workflow(client, prompt, width, height, duration, variants=1, output_dir="./outputs"):
    """Run the full workflow: create, monitor, download, and clean up."""
    # Step 1: Create the job
    job = await create_video_job(client, prompt, width, height, duration, variants)
    if not job:
        logger.error("Failed to create job, workflow aborted.")
        return

    # Step 2: Monitor until completion
    job, generations = await monitor_job(client, job.id)
    if not job or job.status != JobStatus.SUCCEEDED:
        logger.error(
            f"Job did not complete successfully (Status: {job.status}), workflow continues with download attempt.")

    # Step 3: Download the videos if available
    downloaded_files = []
    for gen in generations:
        video_file = await download_video(client, gen.id, output_dir)
        if video_file:
            downloaded_files.append(video_file)

    # Step 4: Clean up the job
    if job:
        await clean_up_job(client, job.id)

    return downloaded_files


async def main():
    """Main function to run the example."""
    parser = argparse.ArgumentParser(description="Rashed Sora SDK Example")

    parser.add_argument("--prompt", type=str, help="Text prompt for video generation",
                        default="A cartoon racoon dancing in a disco")
    parser.add_argument("--width", type=int, help="Video width", default=480)
    parser.add_argument("--height", type=int,
                        help="Video height", default=480)
    parser.add_argument("--duration", type=int,
                        help="Video duration in seconds", default=5)
    parser.add_argument("--variants", type=int,
                        help="Number of video variants to generate", default=1)
    parser.add_argument("--output-dir", type=str,
                        help="Output directory for videos", default="./outputs")
    parser.add_argument("--list-only", action="store_true",
                        help="Only list existing jobs")
    parser.add_argument(
        "--job-id", type=str, help="Job ID to monitor (if provided, won't create a new job)")
    parser.add_argument(
        "--delete-job", type=str, help="Job ID to delete")

    args = parser.parse_args()

    # Create the client
    async with SoraClient() as client:
        if args.list_only:
            # Just list existing jobs
            await list_all_jobs(client)
        elif args.job_id:
            # Monitor and download an existing job
            job, generations = await monitor_job(client, args.job_id)
            if job and job.status == JobStatus.SUCCEEDED:
                for gen in generations:
                    await download_video(client, gen.id, args.output_dir)
        elif args.delete_job:
            # Delete a job by its ID
            success = await clean_up_job(client, args.delete_job)
            if success:
                logger.info(f"Successfully deleted job {args.delete_job}")
            else:
                logger.error(f"Failed to delete job {args.delete_job}")
        else:
            # Run the full workflow
            downloaded_files = await full_workflow(
                client, args.prompt, args.width, args.height,
                args.duration, args.variants, args.output_dir
            )

            if downloaded_files:
                logger.info(
                    f"Workflow completed successfully. Downloaded {len(downloaded_files)} files:")
                for file in downloaded_files:
                    logger.info(f"  - {file}")
            else:
                logger.warning(
                    "Workflow completed but no files were downloaded.")


if __name__ == "__main__":
    asyncio.run(main())
