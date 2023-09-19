import io
import numpy as np
from PIL import Image

def get_image(file):
    try:
        image = Image.fromarray(np.uint8(file))
        return image
    except Exception as e:
        print(f"Error converting file(np.ndarray) to image(PIL): {e}")
        return None

def get_image_dimensions(file):
    try:
        image = get_image(file)
        width, height = image.size
        return f"{width}x{height}"
    except Exception as e:
        print(f"Error while getting image dimensions: {e}")
        return None

def get_image_size(file):
    try:
        image = get_image(file)
        with io.BytesIO() as buf:
            image.save(buf, format='PNG')
            size_in_bytes = buf.tell()
            size_in_kb = size_in_bytes / 1024
            return f"{size_in_kb:.2f} kB"
    except Exception as e:
        print(f"Error while getting image size: {e}")
        return None