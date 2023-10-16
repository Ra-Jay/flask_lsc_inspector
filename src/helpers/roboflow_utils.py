from roboflow import Roboflow
import requests
from flask import current_app, jsonify

from src.helpers.file_utils import convert_BytesIO_to_image, convert_bytes_to_BytesIO, convert_image_to_ndarray, draw_boxes_on_image

def perform_inference(image_url : str, api_key=None, project_name=None, version_number=None):
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
  rf = Roboflow(api_key or current_app.config['ROBOFLOW_API_KEY'])
  project = rf.workspace().project(project_name or  current_app.config['ROBOFLOW_PROJECT'])
  custom_model = project.version(version_number or 1).model
  
  image_response = requests.get(image_url)
  
  if image_response.status_code == 200:
    image_bytes = convert_bytes_to_BytesIO(image_response.content)
    retrieved_image = convert_BytesIO_to_image(image_bytes)
    
    results = custom_model.predict(convert_image_to_ndarray(retrieved_image), confidence=20, overlap=30).json()
    
    resulting_image = draw_boxes_on_image(retrieved_image, results["predictions"])
    result_details = get_result_details(results)
    
    return {
      'image': resulting_image,
      'classification': result_details['classification'],
      'accuracy': result_details['accuracy'],
      'error_rate': result_details['error_rate']
    }
  else:
    return image_response.status_code
  
def deploy_model(api_key : str, workspace_name : str, project_name : str, dataset_version : int, model_type : str, model_path : str):
  """
  Deploy a model to Roboflow.
  
  Parameters:
    `api_key`: The API key of the user.
    
    `workspace_name`: The name of the workspace where the project is located.
    
    `project_name`: The name of the project where the dataset is located.
    
    `dataset_version`: The version number of the dataset.
    
    `model_path`: The path of the model. Might require to be "weights/best.pt".
    
  Returns:
    `None`
  """
  try:
      rf = Roboflow(api_key=api_key)
      project = rf.workspace(workspace_name).project(project_name)
      dataset = project.version(dataset_version)
      
      project.version(dataset.version).deploy(model_type=model_type, model_path=model_path)
      return 201
  except Exception as e:
      return e.args[0], 500

def get_result_details(results : dict[str, list]):
  """
  Takes a list of predictions and returns the details of the result.
  
  Parameters:
    `results`: List of predictions.
    
  Returns:
    `dict`: A dictionary containing the classification, confidence, and error rate.
  """
  classification = [prediction['class'] for prediction in results['predictions']][0]
  accuracy = round([prediction['confidence'] for prediction in results['predictions']][0], 2) * 100
  error_rate = 100 - accuracy
  
  return {
    'classification': classification,
    'accuracy': f"{accuracy:.0f}%",
    'error_rate': f"{error_rate:.0f}%"
  }