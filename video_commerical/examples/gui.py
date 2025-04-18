import chainlit as cl
from rashed_sora_sdk.models import CreateVideoGenerationRequest, JobStatus
from rashed_sora_sdk.client import SoraClient, SoraClientError
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv(override=True)

sora_client = SoraClient()
# Create the outputs directory if it doesn't exist
os.makedirs("./outputs", exist_ok=True)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Welcome! Enter a prompt to generate a video.").send()


@cl.on_message
async def on_message(message: cl.Message):
    prompt = message.content.strip()
    if not prompt:
        await cl.Message(content="Please enter a prompt.").send()
        return

    # Show progress message
    progress_image = cl.Image(path="./examples/static/images/generating.webp")
    progress_msg = cl.Message(
        elements=[progress_image],
        content="Generating video, please wait..."
    )
    await progress_msg.send()

    try:
        # Create video generation request (defaults: 640x360, 5s, 1 variant)
        req = CreateVideoGenerationRequest(
            prompt=prompt, width=640, height=360, n_seconds=5, n_variants=1)
        job = await sora_client.create_video_generation_job(req)
        job_id = job.id

        # Poll for job status
        while True:
            await asyncio.sleep(3)
            job = await sora_client.get_video_generation_job(job_id)
            status = job.status
            progress_msg.content = f"Status: {status.name}"
            await progress_msg.update()
            if status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]:
                break

        if status == JobStatus.SUCCEEDED and job.generations:
            generation_id = job.generations[0].id
            # Get the video content directly
            video_content = await sora_client.get_video_content(generation_id)

            # Save the video to a temporary file
            temp_file_path = f"./outputs/{generation_id}.mp4"
            with open(temp_file_path, "wb") as f:
                f.write(video_content)

            # Delete the progress message since the video is ready
            await progress_msg.remove()

            # Display the video using the local file path
            await cl.Message(
                content="Video generation complete!",
                elements=[cl.Video(name="Generated Video",
                                   path=temp_file_path)]
            ).send()
        else:
            await cl.Message(content="Video generation failed.").send()
    except SoraClientError as e:
        await cl.Message(content=f"Error: {str(e)}").send()
