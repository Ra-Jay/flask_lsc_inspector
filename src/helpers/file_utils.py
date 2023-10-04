from os import path, urandom
from io import BytesIO
import numpy as np
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image, ImageDraw, ImageFont

def generate_hex():
    """
    Generate a random hex.
    
    Returns:
        `str`: A random hex.
    """
    return urandom(4).hex()

def get_file_base_name(file_name : str):
    """
    Get the base name of a file.
    
    Parameters:
        `file_name`: The file name that the user want to get the base name.
        
    Returns:
        `str`: The base name of the file.
    """
    return path.basename(file_name)

def get_file(file_storage : FileStorage):
    """
    Get the file from the request.
    
    Parameters:
        `file_storage`: The file storage that the user want to get.
        
    Returns:
        `dict`: The file name and data.
    """
    return {
        'name': secure_filename(file_storage.filename),
        'data': convert_file_to_bytes(file_storage)
    }
    
def get_image_dimensions(file_data : bytes):
    """
    Get the dimensions of an image.

    Parameters:
        `file_data`: The file data that the user want to get the dimensions.
         
    Returns:
        `str`: The dimensions of the image.
    """
    try:
        image = convert_bytes_to_image(file_data)
        width, height = image.size
        return f"{width}x{height}"
    except Exception as e:
        print(f"Error while getting image dimensions: {e}")
        return None

def get_image_size(file_data : bytes):
    """
    Get the size of an image.
    
    Parameters:
       `file_data`: The file data that the user want to get the size.
       
    Returns:
        `str`: The size of the image.
    """
    try:
        file_size = len(file_data)
        size_in_kb = file_size / 1024
        return f"{size_in_kb:.2f} kB"
    except Exception as e:
        print(f"Error while getting image size: {e}")
        return None
    
def convert_BytesIO_to_image(bytes_io : BytesIO):
    """
    Convert BytesIO to image.
    
    Parameters:
        `bytes_io`: The BytesIO that the user want to convert.
        
    Returns:
        `image`: The BytesIO opened as image.
    """
    try:
        return Image.open(bytes_io)
    except Exception as e:
        print(f"Error while opening image: {e}")
        return None
    
def convert_bytes_to_BytesIO(bytes : bytes):
    """
    Convert bytes to BytesIO.
    
    Parameters:
        `bytes`: The bytes that the user want to convert.
        
    Returns:
        `BytesIO`: The bytes casted as BytesIO.
    """
    try:
        return BytesIO(bytes)
    except Exception as e:
        print(f"Error while getting image by bytes: {e}")
        return None

def convert_file_to_bytes(file : FileStorage):
    """
    Convert a file to bytes.
    
    Parameters:
        `file`: The file that the user want to convert.
        
    Returns:
        `bytes`: The file read as bytes.
    """
    try:
        file_bytes : bytes = file.read()
        return file_bytes
    except Exception as e:
        print(f"Error while converting file to bytes: {e}")
        return None  
    
def convert_image_to_ndarray(image : Image):
    """
    Convert an image to ndarray.
    
    Parameters:
        `image`: The image that the user want to convert.
        
    Returns:
        `ndarray`: The image as ndarray.
    """
    try:
        return np.asarray(image)
    except Exception as e:
        print(f"Error while converting image to ndarray: {e}")
        return None

def convert_image_to_bytes(image : Image):
    """
    Convert an image to bytes.
    
    Parameters:
        `image`: The image that the user want to convert.
        
    Returns:
        `bytes`: The image as bytes.
    """
    try:
        with BytesIO() as buf:
            image.save(buf, format='PNG')
            image_bytes = buf.getvalue()
            return image_bytes
    except Exception as e:
        print(f"Error while converting image to bytes: {e}")
        return None

def convert_bytes_to_image(bytes : bytes):
    """
    Convert bytes to image.
    
    Parameters:
        `bytes`: The bytes that the user want to convert.
        
    Returns:
        `image`: The bytes casted as BytesIO to be opened as image.
    """
    try:
        image = Image.open(BytesIO(bytes))
        return image
    except Exception as e:
        print(f"Error while converting bytes to image: {e}")
        return None
    
def draw_boxes_on_image(image : Image, predictions : dict[str, list]):
  """
  Takes an image and a list of predictions, and returns the image with bounding boxes and class labels drawn on it.
  
  Parameters:
    `image`: Image object.
    
    `predictions`: List of predictions.
    
  Returns:
    `image`: Image object with bounding boxes and class labels drawn on it.
  """
  draw = ImageDraw.Draw(image)
  
  for bounding_box in predictions:
    x0 = bounding_box['x'] - bounding_box['width'] / 2
    x1 = bounding_box['x'] + bounding_box['width'] / 2
    y0 = bounding_box['y'] - bounding_box['height'] / 2
    y1 = bounding_box['y'] + bounding_box['height'] / 2
    
    draw.rectangle([x0, y0, x1, y1], outline="green" if bounding_box['class'] == "Good" else "red", width=2)
    text = f"{bounding_box['class']}: {bounding_box['confidence']:.2f}"
    fontsize = 1
    img_fraction = 0.20
    
    font = ImageFont.truetype("arial.ttf", fontsize)
    while font.getsize(text)[0] < img_fraction*image.size[0]:
      fontsize += 1
      font = ImageFont.truetype("arial.ttf", fontsize)

    fontsize -= 1
    font = ImageFont.truetype("arial.ttf", fontsize)
    draw.text((x0, y0), text, fill="green" if bounding_box['class'] == "Good" else "red", spacing=5, font=font)
    
  return image

def save_image(bytes : bytes, file_path : str):
    """
    Saves an image to the local filesystem.
    
    Parameters:
        `bytes`: The bytes of the image that you want to save.
        
        `file_path`: The path where you want to save the image.
        
    Returns:
        `bool`: True if the image is saved successfully, False otherwise.
    """
    try:
        convert_bytes_to_image(bytes).save(file_path)
        return True
    except Exception as e:
        print(f"Error while saving image to the local filesystem: {e}")
        return False