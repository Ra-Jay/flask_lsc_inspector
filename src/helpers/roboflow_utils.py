import os
from roboflow import Roboflow
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import numpy as np

api_key = os.environ.get('ROBOFLOW_API_KEY')
project = os.environ.get('ROBOFLOW_PROJECT')

def demo_inference(image_url):
  rf = Roboflow(api_key=api_key)
  project = rf.workspace().project(project)

  demo_model = project.version(1).model
  
  results = demo_model.predict(image_url, confidence=20)
  
  response = requests.get(image_url)
  
  if response.status_code == 200:
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    
    image_data = np.asarray(image)
    
    results = demo_model.predict(image_data, confidence=20, overlap=30).json()

    draw = ImageDraw.Draw(image)

    for bounding_box in results["predictions"]:
        x0 = bounding_box['x'] - bounding_box['width'] / 2
        x1 = bounding_box['x'] + bounding_box['width'] / 2
        y0 = bounding_box['y'] - bounding_box['height'] / 2
        y1 = bounding_box['y'] + bounding_box['height'] / 2
        
        draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
        draw.text((x0, y0), f"{bounding_box['class']}: {bounding_box['confidence']:.2f}", fill="red")
        
    # Convert image to bytes if uploading to bucket
    # buffered = BytesIO()
    # image.save(buffered, format="PNG")
    # image_data = buffered.getvalue()
    
    return image
  else:
    return response.status_code
  