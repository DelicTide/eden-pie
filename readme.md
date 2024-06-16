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
├── txt2img.py
├── cv.py
├── vid.py
├── main.py
├── requirements.txt
└── README.md


## Installation

1. Clone the repository: (i prefer ssh connections to giuthub. It's much more convient once setup)
    ```sh
    git clone git@github.com:DelicTide/eden-pie.git
    cd eden-pie
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
    - Creates necessary folders and clear previous images.
    - Generates images using the Eden API.
    - Downloads and save the images in the `assets/images` folder.
    - Selects two random style images and save their URLs in `assets/inputs/style_images.txt`.
    - Runs the `cv.py` script to compile images into a video.
    - Runs the `vid.py` script to process the video with Eden's vid2vid functionality and download the processed video to `assets/outputs/v2v.mp4`.

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

notes: 
    how i run the sequence... 

    1st I will find or generate an intersteing Control image. 
        Place that image in ./assets/inputs/ (delete any existing img when adding new images,
            the file will read the 1st image it finds in the ./dir)
    I then use context from my control img (such as its prompt) to define the intial prompt.
        So, 2nd I will define the txt2img prompt in main.py as well as the number images to geerate (main.py line:52&53)
    3rd I will select an appropriate model based on our control image and set the control and lora strengths in the txt2img.py config (txt2img.py line:125-148)
    having selected our number of images to be generated, or in our case frames, we need to be sure that the compiled video and vid2vid share some comminalty in fps. 
    A good starting point or the sweet spot seems to be 64/8/32
    Thats 64 generated images using txt2img, compiled at 8fps using opencv, and passed to vid2vid for a total of 32 frames. 
    This has generated smooth smokes of clouds and belivable limb movments. 
     Lowering the fps in opencv will slow the video generation while increaasing the frames will produce seizure casuing vizuals. 
     And generating less input frames than vid2vid frames produces choppy video. 
