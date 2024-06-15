import os
import httpx
import random
import requests
import logging
import shutil 
import threading
from aiofiles import open as aio_open
from eden_sdk.EdenClient import EdenClient
from dotenv import load_dotenv
import time

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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def preprocess_prompt(base_prompt):
    themes_and_styles = [
        "Cyberpunk Oasis", "Martian Sphinx", "Neo-Egyptian Metropolis", "Quantum Pyramid",
        "Steampunk Pharaoh", "Futuristic Nile", "Digital Hieroglyphics", "Holographic Tomb",
        "Eternal Cyberpunk Desert", "High-Tech Oasis", "Ancient Egyptian Cyber Temples",
        "Pyramidal Quantum Reality", "Post-apocalyptic Ankh City", "Underwater Cairo",
        "Gothic Pharaoh's Realm", "Neon Scarab", "Alien Pyramid World", "Cyber-Egyptian Renaissance",
        "Solar-Punk Sphinx", "Techno-Egyptian Enclave", "Ethereal Cyber Pyramid",
        "Astral Nile Adventure", "Arctic Cyber-Pharaoh", "Digital Dream Pyramid",
        "Surreal Cyber-Desert", "Futuristic Pyramid City", "Holographic Pharaoh's Tomb",
    ]

    visual_effects = [
        "dynamic neon holograms", "grainy futuristic hieroglyphs", "vibrant digital light patterns", "sharp cyber renderings",
        "dreamlike soft cyber glows", "high-contrast neon shadows", "glitch pyramid distortions", "3D holographic projections",
        "reflective metallic surfaces", "thermal hieroglyphic visions", "infrared pyramid imagery", "ultraviolet ankh light effects",
        "particle data streams", "cybernetic smoke overlays", "crystalline geometric textures", "futuristic metallic sheens",
        "golden laser rays", "holographic ancient hieroglyphs", "cyber-pharaonic implants", "futuristic techno armor",
    ]

    composition_techniques = [
        "dynamic geometric symmetry", "fractal pyramid composition", "kinetic holographic flow", "color isolation in neon",
        "hyper-lapse of digital hieroglyphs", "extreme close-up of cyber details", "wide panoramic view of techno landscapes", "fish-eye perspective on pyramids",
        "bokeh effects with neon lights", "tilt-shift futuristic scenes", "long exposure of light trails", "layered double exposure with hieroglyphs",
        "drone shot of techno temples", "time-lapse of digital sunrises", "multi-angle collage of futuristic Cairo", "cinematic framing with cyber elements",
    ]

    chosen_theme = random.choice(themes_and_styles)
    chosen_effect = random.choice(visual_effects)
    chosen_composition = random.choice(composition_techniques)

    # Combine all elements into a refined, detailed, and metadata-rich prompt
    enhanced_prompt = f"{base_prompt} reimagined in a {chosen_theme} setting, featuring {chosen_effect} and {chosen_composition}."

    return enhanced_prompt


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def save_style_images(selected_style_urls):
    try:
        with open('assets/inputs/style_images.txt', 'w') as file:
            for url in selected_style_urls:
                file.write(url + '\n')
        logging.info("Style image URLs successfully saved.")
    except Exception as e:
        logging.error(f"Failed to save style image URLs: {str(e)}")

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {save_path}")
    else:
        print(f"Failed to download {image_url}")

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

def generate_image(config, results, index):
    response = eden.tasks.create(generator_name='create', config=config)
    if 'taskId' in response:
        task_id = response['taskId']
        task_response = poll_for_result(task_id)
        if task_response and 'task' in task_response and 'output' in task_response['task']:
            results[index] = task_response['task']['output']['files'][0]  # Assuming 'files' is a list
        else:
            results[index] = None
    else:
        results[index] = None

def generate_images(prompt, num_requests, control_image_url):
    threads = []
    results = [None] * num_requests
    for i in range(num_requests):
        enhanced_prompt = preprocess_prompt(prompt)
        config = {
            'uc_text': "watermark, text, nude, naked, nsfw, poorly drawn face, ugly, tiling, out of frame, blurry, blurred, grainy, signature, cut off, draft",
            'control_image': control_image_url,
            'text_input': enhanced_prompt,
            'control_image_strength': 0.55,
            'controlnet_type': 'canny-edge',
            'width': 1024,
            'height': 1024,
            'n_samples': 1,
            'guidance_scale': 8,
            'sampler': 'euler',
            'steps': 32,
            'seed': random.randint(1, 1000000),
            'lora': '658d3057ec6555ba23915948',
            'lora_scale': 0.14,
            'adopt_aspect_from_init_img': True
        }
        thread = threading.Thread(target=generate_image, args=(config, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    valid_urls = [url for url in results if url]
    if len(valid_urls) >= 2:
        selected_style_images = random.sample(valid_urls, 2)
        save_style_images(selected_style_images)
    else:
        logging.error("Not enough valid images to select style images.")

    return results
