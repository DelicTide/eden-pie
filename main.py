import os
import logging
import random
import subprocess
import asyncio
from txt2img import generate_images, download_image, create_folder, clear_folder
from eden_sdk.EdenClient import EdenClient
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize the Eden Client with API credentials from environment variables
eden = EdenClient(
    api_key=os.getenv('EDEN_API_KEY'),
    api_secret=os.getenv('EDEN_API_SECRET')
)

# Ensure API keys are loaded
if not eden.api_key or not eden.api_secret:
    raise ValueError("API key and secret must be set in the environment variables.")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

def find_control_image(directory):
    for file_name in os.listdir(directory):
        if file_name.lower().endswith(('.jpeg', '.jpg', '.png')):
            return os.path.join(directory, file_name)
    return None

def upload_control_image(file_path):
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
        logging.error(f"Exception occurred while uploading image: {str(e)}")
        return None

async def main():
    prompt = "A 'Time Traveler' visits the same place over thousands of years"
    num_requests = 64  # Number of image generation requests

    # Create necessary folders
    create_folder('assets')
    create_folder('assets/outputs')
    images_subfolder_path = 'assets/images'
    clear_folder(images_subfolder_path)

    # Find control image in the directory
    control_image_path = find_control_image('assets/inputs')
    if not control_image_path:
        logging.error("No control image found in the directory.")
        return

    # Upload control image and get the URL
    control_image_url = upload_control_image(control_image_path)
    if not control_image_url:
        logging.error("Failed to upload control image.")
        return

    # Generate images and get the URLs
    generated_images = generate_images(prompt, num_requests, control_image_url)
    if generated_images:
        logging.info("Generated image URLs:")
        for idx, url in enumerate(generated_images):
            if url:
                logging.info(f"{idx + 1}: {url}")
                # Download and save the image in the images sub-folder
                download_image(url, os.path.join(images_subfolder_path, f'image_{idx + 1}.jpg'))

        # Select two random style images from generated images
        valid_images = [url for url in generated_images if url]
        if len(valid_images) < 2:
            logging.error("Not enough valid images to sample style images.")
            return

        style_images = random.sample(valid_images, 2)
        os.environ["STYLE_IMAGES"] = ','.join(style_images)

        # Call OpenCV script to create video from images
        subprocess.run(['python', 'cv.py'])

        # Call the vid.py script to process the video with Eden
        process = subprocess.Popen(['python', 'vid.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await asyncio.get_running_loop().run_in_executor(None, process.communicate)
        if process.returncode == 0:
            logging.info("vid.py script executed successfully")
        else:
            logging.error(f"vid.py script execution failed with error: {stderr.decode()}")
    else:
        logging.error("Failed to generate images.")

if __name__ == "__main__":
    asyncio.run(main())
