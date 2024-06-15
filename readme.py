Eden_Pie
    A Slice 4 You
## Overview

This project uses the Eden API to generate images based on a given prompt,
 compiles these images into a video using OpenCV, 
 and processes the video further with Eden's vid2vid functionality. 
The project incorporates themes, styles, and visual effects to create unique and captivating outputs, 
 as well as uses controlnet in conjuntion with custom models/loras to create sequentailly symmetrical images, 
thereby injecting loras into the vid2vid endpoint. 
yah. 
## Project Structure
.
├── assets
│   ├── inputs
│   │   ├── input_image.jpeg
│   │   ├── opencv_video.mp4
│   │   └── style_images.txt
│   ├── outputs
│   │   └── v2v.mp4
│   └── images
│       ├── image_1.jpg
│       ├── image_2.jpg
│       └── ...
├── eden_sdk
├── src (not so:-)
│   ├── txt2img.py
│   ├── cv.py
│   ├── vid.py
├── main.py
├── requirements.txt
└── README.md


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/ai-image-video-gen.git
    cd ai-image-video-gen
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv eden_venv
    source eden_venv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory with the following content:
    ```env
    EDEN_API_KEY=your_api_key
    EDEN_API_SECRET=your_api_secret
    ```

## Usage

1. Prepare the `controlnet` image:
    - Place a `.jpg`, `.jpeg`, or `.png` image in the `assets/inputs` directory. Ensure there is only one image in this folder.

2. Generate Images:
    - Run the `main.py` script to generate images based on the specified prompt:
    ```sh
    python main.py
    ```

3. The `main.py` script will:
    - Create necessary folders and clear previous images.
    - Generate images using the Eden API.
    - Download and save the images in the `assets/images` folder.
    - Select two random style images and save their URLs in `assets/inputs/style_images.txt`.
    - Run the `cv.py` script to compile images into a video.
    - Run the `vid.py` script to process the video with Eden's vid2vid functionality and download the processed video to `assets/outputs/v2v.mp4`.

## Detailed Script Description

### `main.py`

- Sets up logging and necessary folders.
- Defines a prompt and the number of images to generate.
- Generates images using the `generate_images` function from `txt2img.py`.
- Downloads generated images and saves them locally.
- Selects two random images for style and saves their URLs.
- Calls `cv.py` to compile images into a video.
- Calls `vid.py` to process the video and download the final output.

### `txt2img.py`

- Defines functions to generate images using Eden API.
- Uploads control image from `assets/inputs/controlnet`.
    This gives you the ability to drop any image into the assets/input folder to be used 
        as your controlnet image. (adding some of the gui flavor to the terminal ;.)
- Generates images based on the given prompt and configuration.
- Downloads generated images and saves them locally.

### `cv.py`

- Compiles images from `assets/images` into a video.
- Saves the compiled video to `assets/inputs/opencv_video.mp4`.

### `vid.py`

- Uploads the compiled video to Eden.
- Processes the video with Eden's vid2vid functionality using style images.
- Downloads the processed video and saves it to `assets/outputs/v2v.mp4`.
- for our style images we have randomly selected 2 images to be used from our txt2img genrations

## Contributing

Feel free to submit issues or pull requests if you have any improvements or suggestions.

## License

This project is licensed under warm blankets, usally with coffee

~tdt