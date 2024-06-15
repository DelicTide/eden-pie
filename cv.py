import cv2
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def images_to_video(image_folder, video_name, fps=8):
    try:
        images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
        if not images:
            logging.error("No images found in the specified folder.")
            return

        images.sort()
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        if frame is None:
            logging.error("Could not read the first image.")
            return

        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        for image in images:
            img = cv2.imread(os.path.join(image_folder, image))
            if img is not None:
                video.write(img)
            else:
                logging.warning(f"Failed to read image {image}. Skipping.")

        video.release()
        logging.info(f"Video created successfully at {video_name}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    images_to_video('assets/images', 'assets/inputs/opencv_video.mp4')
