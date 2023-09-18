import io
import os
import numpy as np
from ultralytics import YOLO
from PIL import Image

from supabase import create_client, Client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(url, key, options={'timeout': 10})

def supabase_upload(filepath):
    with open(filepath, 'rb+') as f:
        response = supabase.storage.from_('lsc_bucket').upload(filepath, f)
        
    return response

# For demo purposes only
DEMO_WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights', 'yolov8s', 'lsc_v1.pt')

# When an image has been uploaded, it will preview in the frontend and will be saved in the uploads folder
UPLOADS_FOLDER = os.path.join('src', 'static', 'uploads')

def demo_analyze_image(filename):
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result
  
# Using the custom weights of the user that was retreived from the database through their user_id.
def custom_analyze_image(filename, custom_weights):
    
    # TODO: Download custom weights from the url attribute of the custom_weights object to use as parameter for the YOLO object. [RESEARCHING]
    model = YOLO(DEMO_WEIGHTS_FOLDER)
    
    file_path = os.path.join(UPLOADS_FOLDER, filename)
    
    result = model.predict(
        source=file_path, 
        show=False, 
        conf=0.20,
        save=False
    )
    
    return result

def get_file_dimensions(file):
    try:
        img = Image.fromarray(np.uint8(file))
        width, height = img.size
        return f"{width}x{height}"
    except Exception as e:
        print(f"Error while getting dimensions: {e}")
        return None

def get_file_size(file):
    try:
        img = Image.fromarray(np.uint8(file))
        with io.BytesIO() as buf:
            img.save(buf, format='PNG')
            size_in_bytes = buf.tell()
            size_in_kb = size_in_bytes / 1024
            return f"{size_in_kb:.2f} kB"
    except Exception as e:
        print(f"Error while getting ndarray size: {e}")
        return None
