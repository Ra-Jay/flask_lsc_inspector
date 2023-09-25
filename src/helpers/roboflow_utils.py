import os
from roboflow import Roboflow
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import numpy as np

default_api_key = os.environ.get('ROBOFLOW_API_KEY')
default_project = os.environ.get('ROBOFLOW_PROJECT')

# This method is tested and working.
def demo_inference(image_url):
  """
  Takes an image URL, performs object detection using a pre-trained
  model from Roboflow, and returns the image with bounding boxes and class labels drawn on it.
  
  Parameters: 
    `image_url`: The URL of the image you want to perform inference on. 
    
  Returns: 
    `image`: Image object with bounding boxes and class labels drawn on it.
    
    `status_code`: The status code of the response. If the status code is not 200, then the image is not returned.
  """
  rf = Roboflow(api_key=default_api_key)
  project = rf.workspace().project(default_project)

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
  
def custom_inference(image_url, api_key, project_name, version_number):
  """
  Takes an image URL, performs object detection using a custom
  model from Roboflow, and returns the image with bounding boxes and class labels drawn on it.
  
  Parameters:
    `image_url`: The URL of the image you want to perform inference on.
    
    `api_key`: The API key of the user.
    
    `project_name`: The name of the project where the custom model is located.
    
    `version_number`: The version number of the custom model.
    
  Returns:
    `image`: Image object with bounding boxes and class labels drawn on it.
    
    `status_code`: The status code of the response. If the status code is not 200, then the image is not returned.
  """
  rf = Roboflow(api_key=api_key)
  project = rf.workspace().project(project_name)
  
  custom_model = project.version(version_number).model
  
  results = custom_model.predict(image_url, confidence=20)
  
  response = requests.get(image_url)
  
  if response.status_code == 200:
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    
    image_data = np.asarray(image)
    
    results = custom_model.predict(image_data, confidence=20, overlap=30).json()

    draw = ImageDraw.Draw(image)

    for bounding_box in results["predictions"]:
        x0 = bounding_box['x'] - bounding_box['width'] / 2
        x1 = bounding_box['x'] + bounding_box['width'] / 2
        y0 = bounding_box['y'] - bounding_box['height'] / 2
        y1 = bounding_box['y'] + bounding_box['height'] / 2
        
        draw.rectangle([x0, y0, x1, y1], outline="red", width=2)
        draw.text((x0, y0), f"{bounding_box['class']}: {bounding_box['confidence']:.2f}", fill="red")
    
    return image
  else:
    return response.status_code