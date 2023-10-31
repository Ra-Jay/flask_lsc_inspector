from roboflow import Roboflow
from requests import get as getRequest
from flask import current_app, jsonify
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from src.helpers.file_utils import convert_bytes_to_image, convert_image_to_ndarray, draw_boxes_on_image

def perform_inference(image_url : str, api_key=None, project_name=None, version_number=None):
  """
  Takes an image URL, performs object detection using a custom
  model from Roboflow, and returns the image with bounding boxes and class labels drawn on it.
  
  Parameters:
    `image_url`: The URL of the image you want to perform inference on.
    
    `api_key`: The API key of the user.
    
    `project_name`: The name of the project where the custom model is located.
    
    `version_number`: The version number of the dataset that the model was trained from.
    
  Returns:
    `dict[str, Any]`: Dictionary that contains: `image`, `classification`, `accuracy`, and `error_rate`.
    
    `JSON Response (400)`: If the model failed to predict the image. Caused by incorrect image and/or image size.
    
    `JSON Roboflow Response (500)`: If there is an error while performing inference in Roboflow.
  """
  rf = Roboflow(api_key or current_app.config['ROBOFLOW_API_KEY'])
  project = rf.workspace().project(project_name or  current_app.config['ROBOFLOW_PROJECT'])
  custom_model = project.version(version_number or 1).model

  image_response = getRequest(image_url)
  if image_response.status_code == HTTP_200_OK:
    retrieved_image = convert_bytes_to_image(image_response.content)
    try:
      results = custom_model.predict(convert_image_to_ndarray(retrieved_image), confidence=20, overlap=30).json()
    except Exception as e:
      return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
    result_details = get_result_details(results)
    if result_details == HTTP_400_BAD_REQUEST:
      return jsonify(
        {'message': 'Model may have failed to predict this file. Try another or use smaller file.'}
        ), HTTP_400_BAD_REQUEST
    
    return {
      'image': draw_boxes_on_image(retrieved_image, results["predictions"]),
      'classification': result_details['classification'],
      'accuracy': result_details['accuracy'],
      'error_rate': result_details['error_rate']
    }
  else:
    return jsonify({'message': 'Failed to retrieve the image through its public URL.'}), image_response.status_code
  
def deploy_model(api_key : str, workspace_name : str, project_name : str, dataset_version : int, model_type : str, model_path : str):
  """
  Deploy a model to Roboflow.
  
  Parameters:
    `api_key`: The API key of the user.
    
    `workspace_name`: The name of the workspace where the project is located.
    
    `project_name`: The name of the project where the dataset is located.
    
    `dataset_version`: The version number of the dataset.
    
    `model_path`: The path of the parent folder of the model.
    
  Example:
    >>> "path/to/parent/folder/"
    >>> # this folder must contain the following files:
    >>> "weights/best.pt"
    
  Returns:
    `JSON Response (201)`: If the model was successfully deployed to Roboflow.
    
    `JSON Roboflow Response (500)`: If there is an error while deploying the model to Roboflow.
  """
  try:
      rf = Roboflow(api_key=api_key)
      project = rf.workspace(workspace_name).project(project_name)
      dataset = project.version(dataset_version)
      
      project.version(dataset.version).deploy(model_type=model_type, model_path=model_path)
      return HTTP_201_CREATED
  except Exception as e:
      return jsonify({'error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

def get_result_details(results : dict[str, list]):
  """
  Takes a list of predictions and returns the details of the result.
  
  Parameters:
    `results`: List of predictions.
    
  Returns:
    `dict`: A dictionary containing the `classification`, `confidence`, and `error rate`.
    
    `400`: If the model has returned an empty predictions. Caused by incorrect image and/or image size.
  """
  try:
    classification = [prediction['class'] for prediction in results['predictions']][0]
    accuracy = round([prediction['confidence'] for prediction in results['predictions']][0], 2) * 100
    error_rate = 100 - accuracy
    return {
      'classification': classification,
      'accuracy': f"{accuracy:.0f}%",
      'error_rate': f"{error_rate:.0f}%"
    }
  except Exception:
    return HTTP_400_BAD_REQUEST