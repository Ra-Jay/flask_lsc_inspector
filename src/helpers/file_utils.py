import io
import numpy as np
from PIL import Image

def get_image(file):
    """
    Convert a file(np.ndarray) to image(PIL).
    
    Parameters:
        `file`: The file that the user want to convert.

    Returns:
        `image`: Pillow object as an image.
    """
    try:
        image = Image.fromarray(np.uint8(file))
        return image
    except Exception as e:
        print(f"Error converting file(np.ndarray) to image(PIL): {e}")
        return None

def get_image_dimensions(file):
    """
    Get the dimensions of an image.
    
    Parameters:
        `file`: The file that the user want to get the dimensions.
        
    Returns:
        `str`: The dimensions of the image.
    """
    try:
        image = get_image(file)
        width, height = image.size
        return f"{width}x{height}"
    except Exception as e:
        print(f"Error while getting image dimensions: {e}")
        return None

def get_image_size(file):
    """
    Get the size of an image.
    
    Parameters:
        `file`: The file that the user want to get the size.
        
    Returns:
        `str`: The size of the image.
    """
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
    
# Method that converts FileStorage to bytes
def convert_file_to_bytes(file):
    """
    Convert a file to bytes.
    
    Parameters:
        `file`: The file that the user want to convert.
        
    Returns:
        `bytes`: The file as bytes.
    """
    try:
        return file.read()
    except Exception as e:
        print(f"Error while converting file to bytes: {e}")
        return None  
    
def convert_file_to_image(file):
    """
    Convert a file to image.
    
    Parameters:
        `file`: The file that the user want to convert.
        
    Returns:
        `image`: The file as image.
    """
    try:
        image = Image.open(file)
        return image
    except Exception as e:
        print(f"Error while converting file to image: {e}")
        return None

def convert_image_to_bytes(image):
    """
    Convert an image to bytes.
    
    Parameters:
        `image`: The image that the user want to convert.
        
    Returns:
        `bytes`: The image as bytes.
    """
    try:
        with io.BytesIO() as buf:
            image.save(buf, format='PNG')
            image_bytes = buf.getvalue()
            return image_bytes
    except Exception as e:
        print(f"Error while converting image to bytes: {e}")
        return None

def convert_bytes_to_image(bytes):
    """
    Convert bytes to image.
    
    Parameters:
        `bytes`: The bytes that the user want to convert.
        
    Returns:
        `image`: The bytes as image.
    """
    try:
        image = Image.open(io.BytesIO(bytes))
        return image
    except Exception as e:
        print(f"Error while converting bytes to image: {e}")
        return None
    
# This method is tested and working
def save_image(bytes, file_path):
    """
    Save an image to the local filesystem.
    
    Parameters:
        `image`: The image that the user want to save.
        
        `image_name`: The name of the image that the user want to save.
        
    Returns:
        `bool`: True if the image is saved successfully, False otherwise.
    """
    try:
        convert_bytes_to_image(bytes).save(file_path)
        return True
    except Exception as e:
        print(f"Error while saving image to the local filesystem: {e}")
        return False