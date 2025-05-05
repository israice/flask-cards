from PIL import Image, ImageDraw
import random
import os
import re
from dotenv import load_dotenv

# === LOAD ENVIRONMENT VARIABLES ===
load_dotenv()
OUTPUT_DIR = os.getenv('CARDS_BANK_FOLDER') 

# === SETTINGS ===
IMAGE_WIDTH = 768                      # Width of the generated image
IMAGE_HEIGHT = 1152                    # Height of the generated image
BACKGROUND_COLOR = (30, 30, 30)        # Background color (white)
NUM_IMAGES = 5                         # Number of images to generate
FILE_EXTENSION = '.png'                # File extension (including dot)

# Universal image generation function
def generate_image(width, height, background_color, draw_function, filename):
    # Create a blank image
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Apply the provided drawing function
    draw_function(draw, width, height)

    # Save the image
    image.save(filename)

# Example drawing function: random circles
def draw_random_circles(draw, width, height):
    for _ in range(10):
        x0 = random.randint(0, width)
        y0 = random.randint(0, height)
        x1 = x0 + random.randint(10, 100)
        y1 = y0 + random.randint(10, 100)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.ellipse([x0, y0, x1, y1], fill=color, outline=color)

# Example drawing function: random rectangles
def draw_random_rectangles(draw, width, height):
    for _ in range(10):
        x0 = random.randint(0, width)
        y0 = random.randint(0, height)
        x1 = x0 + random.randint(10, 100)
        y1 = y0 + random.randint(10, 100)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([x0, y0, x1, y1], fill=color, outline=color)

# List of available drawing functions
DRAW_FUNCTIONS = [draw_random_circles, draw_random_rectangles]

def get_next_start_index(directory, extension):
    # Regex to find numeric filenames like 001.png, 002.png
    pattern = re.compile(r'^(\d{3})' + re.escape(extension) + r'$')
    existing_numbers = []

    for fname in os.listdir(directory):
        match = pattern.match(fname)
        if match:
            num = int(match.group(1))
            existing_numbers.append(num)

    if existing_numbers:
        return max(existing_numbers) + 1
    else:
        return 1

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find the starting index
    start_index = get_next_start_index(OUTPUT_DIR, FILE_EXTENSION)

    # Generate images based on NUM_IMAGES setting
    for idx in range(start_index, start_index + NUM_IMAGES):
        # Cycle through available draw functions
        draw_func = DRAW_FUNCTIONS[(idx - 1) % len(DRAW_FUNCTIONS)]
        filename = os.path.join(OUTPUT_DIR, f"{idx:03}{FILE_EXTENSION}")
        generate_image(
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            background_color=BACKGROUND_COLOR,
            draw_function=draw_func,
            filename=filename
        )

if __name__ == '__main__':
    main()

