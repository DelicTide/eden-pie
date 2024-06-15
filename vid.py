import os
import time
import logging
from eden_sdk.EdenClient import EdenClient
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Eden Client with API credentials
eden = EdenClient(api_key=os.getenv('EDEN_API_KEY'), api_secret=os.getenv('EDEN_API_SECRET'))

# Ensure API keys are loaded
if not eden.api_key or not eden.api_secret:
    raise ValueError("API key and secret must be set in the environment variables.")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_video_to_eden(file_path):
    try:
        logging.debug(f"Starting upload for file: {file_path}")
        with open(file_path, 'rb') as f:
            media = f.read()
        
        headers = {"x-api-key": eden.api_key, "x-api-secret": eden.api_secret}
        files = {'media': ('media', media)}
        
        response = requests.post(f"{eden.api_url}/media/upload", headers=headers, files=files)
        response.raise_for_status()
        result = response.json()
        logging.info(f"Upload result: {result}")
        return result['url']
    except Exception as e:
        logging.error(f"Exception occurred while uploading video: {str(e)}")
        return None

def process_video_with_eden(config):
    try:
        response = eden.tasks.create(generator_name='vid2vid', config=config)
        if 'taskId' in response:
            task_id = response['taskId']
            task_response = poll_for_result(task_id)
            if task_response and 'task' in task_response and 'output' in task_response['task']:
                return task_response['task']['output']['files'][0]  # Assuming 'files' contains the video URL
        return None
    except Exception as e:
        logging.error(f"Exception occurred while processing video: {str(e)}")
        return None

def poll_for_result(task_id, interval=32, timeout=32000):
    start_time = time.time()
    while time.time() - start_time < timeout:
        task_result = eden.tasks.get(task_id)
        logging.debug(f"Polling Task {task_id}: {task_result}")  # Log the response
        if 'task' in task_result and task_result['task']['status'] == 'completed':
            logging.info(f"Task {task_id} completed successfully.")
            return task_result
        elif 'task' in task_result and task_result['task']['status'] == 'failed':
            logging.error(f"Image generation failed for task {task_id}: {task_result['task']['error']}")
        time.sleep(interval)
    logging.error(f"Polling for task {task_id} timed out after {timeout} seconds")
    return None

def download_video(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded processed video to {save_path}")
    except Exception as e:
        logging.error(f"Exception occurred while downloading video: {str(e)}")

def main():
    input_video_path = "assets/inputs/opencv_video.mp4"  # Corrected filename
    style_images_file = "assets/inputs/style_images.txt"

    # Retrieve style images from file
    try:
        with open(style_images_file, 'r') as f:
            style_text = f.read().strip()
        style_images = style_text.splitlines() if style_text else []
        if not style_images:
            raise ValueError("No style images found in file.")
    except FileNotFoundError:
        raise FileNotFoundError("Style images file not found.")

    # Upload video and get the URL
    input_video_url = upload_video_to_eden(input_video_path)
    if not input_video_url:
        logging.error("Failed to upload video.")
        return

    # Configuration for the video processing
    config = {
        "negative_prompt": "nude, naked, text, watermark, low-quality, signature, padding, margins, blurry, jpeg artifacts, poorly drawn, low-resolution, bad",
        "style_images": style_images,
        "input_video_path": input_video_url,  # Use the video URL in the configuration
        "n_frames": 64,
        "control_method": "coarse",
        "text_input": "",
        "width": 1024,
        "height": 1024,
        "denoise_strength": 0.95,
        "controlnet_strength": 0.78,
        "loop": True,
        "motion_scale": 0.95,
    }

    processed_video_url = process_video_with_eden(config)
    if processed_video_url:
        logging.info(f"Processed video URL: {processed_video_url}")
        # Download the processed video
        download_video(processed_video_url, "assets/outputs/v2v.mp4")
    else:
        logging.error("Failed to process video.")

if __name__ == "__main__":
    main()
