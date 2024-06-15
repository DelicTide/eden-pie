from eden_sdk.EdenClient import EdenClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Eden Client with API credentials from environment variables
eden = EdenClient(api_key=os.getenv('EDEN_API_KEY'),
                  api_secret=os.getenv('EDEN_API_SECRET'))

def generate_video(config):
    """Generate a video using a given configuration and return the result."""
    try:
        response = eden.create(generator_name='img2vid', config=config)
        if response and isinstance(response, list) and len(response) > 0:
            return response[0]  # Assume the first item in the list is the URL
        else:
            return "No URL returned or invalid response structure"
    except Exception as e:
        return f"Failed to generate video: {str(e)}"

config = {
    'input_images': ["https://d14i3advvh2bvd.cloudfront.net/8e5c807223d4e80ec263b56889e166089b4405b4388237907fda23c87977cd9a.jpg"],
    'isPrivate': False,
    'n_frames': 24,
    'loop': True,
    'width': 1280,
    'height': 1280,
    'denoise_strength': 0.95,
    'motion_scale': 1.1,
    'mask_images': [],
    'negative_prompt': "nude, naked, text, watermark, low-quality, signature, padding, margins, blurry, jpeg artifacts, poorly drawn, low-resolution, bad",
    'seed': 53469120
}

video_url = generate_video(config)
print(f"Generated video URL: {video_url}")
