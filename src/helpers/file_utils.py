from os import path, urandom
from io import BytesIO
from numpy import asarray
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
        'data': file_storage.read()
    }
    
def get_image_dimensions(file_data : bytes):
    """
    Get the dimensions of an image.

    Parameters:
        `file_data`: The file data as bytes that the user want to get the dimensions.
         
    Returns:
        `str`: The dimensions of the image that concatenates the `width` and `height`.
    """
    try:
        image = convert_bytes_to_image(file_data)
        width, height = image.size
        return f"{width}x{height}"
    except Exception:
        return None

def get_image_size(file_data : bytes):
    """
    Get the size of an image.
    
    Parameters:
       `file_data`: The file data as bytes that the user want to get the size.
       
    Returns:
        `str`: The size of the image in kilobytes.
    """
    try:
        file_size = len(file_data)
        size_in_kb = file_size / 1024
        return f"{size_in_kb:.2f} kB"
    except Exception:
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
        return asarray(image)
    except Exception:
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
    except Exception:
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
        return Image.open(BytesIO(bytes))
    except Exception:
        return None
    
def draw_boxes_on_image(image : Image, predictions : dict[str, list]):
  """
  Takes an image and its list of predictions that uses x, y, width, and height to draw the bounding boxes 
  then adds the class labels and confidence scores.
  
  Parameters:
    `image`: PIL.Image object to be drawn on.
    
    `predictions`: List of predictions.
    
  Example:
    >>> {
    >>>   "predictions": [
    >>>     {
    >>>       "x": 172,
    >>>       "y": 113.5,
    >>>       "width": 72,
    >>>       "height": 87,
    >>>       "confidence": 0.697,
    >>>       "class": "Good",
    >>>       "class_id": 0
    >>>     }
    >>>   ]
    >>> }
    
  Returns:
    `image`: The PIL.Image that was updated with the bounding boxes and class labels.
  """
  draw = ImageDraw.Draw(image)
  for bounding_box in predictions:
    x0 = bounding_box['x'] - bounding_box['width'] / 2
    x1 = bounding_box['x'] + bounding_box['width'] / 2
    y0 = bounding_box['y'] - bounding_box['height'] / 2
    y1 = bounding_box['y'] + bounding_box['height'] / 2
    
    draw.rectangle([x0, y0, x1, y1], outline="green" if bounding_box['class'] == "Good" else "red", width=2)
    text = f"{bounding_box['class']}: {bounding_box['confidence']:.2f}"
    
    fontsize = int(0.05 * image.size[1])
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except OSError:
        # Use default font if arial.ttf is not found in Mac/Linux/Windows.
        font = ImageFont.load_default()
    text_width, _ = draw.textsize(text, font=font)
    if text_width > bounding_box['width']:
        text_position = (x1, y0)
    else:
        text_position = (x0, y0)
    
    text_width, text_height = draw.textsize(text, font=font)
    draw.rectangle([text_position[0], text_position[1], text_position[0] + text_width, text_position[1] + text_height], fill="black")
    draw.text(text_position, text, fill="green" if bounding_box['class'] == "Good" else "red", font=font)
    
  return image
