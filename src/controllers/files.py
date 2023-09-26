import os

import torch
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import validators
from src.helpers.file_utils import convert_file_to_bytes, get_image_dimensions, get_image_size, convert_file_to_image, convert_image_to_bytes
from src.helpers.yolo_utils import custom_analyze_image, demo_analyze_image
from src.helpers.supabase_utils import upload_file_to_bucket, download_file_from_bucket, get_file_url_by_name, get_all_files_from_bucket, delete_file_by_name
from src.helpers.roboflow_utils import demo_inference, custom_inference
from src.models.files import Files
from ..extensions import db
from flask import session
from time import time
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

@files.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload():
  """
  Handles the uploaded file to the supabase bucket. 
  The file object includes the following attributes: `id`, `name`, `dimensions`, `size`, `url`,
  `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.
  
  Returns:
    `JSON Response`: File object with a status code of `201 (HTTP_201_CREATED)`.
    
    `400 (HTTP_400_BAD_REQUEST)`: If no file is uploaded.
    
    `409 (HTTP_409_CONFLICT)`: If the file already exists in the supabase bucket.
    
    `500 (HTTP_500_INTERNAL_SERVER_ERROR)`: If there is an internal server error either in supabase or source code.
  """  
  if request.method == 'POST':
    if 'file' not in request.files:
      return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file = request.files['file']
    
    # Convert FileStorage uploaded_file to bytes
    uploaded_data = convert_file_to_bytes(uploaded_file)
    
    uploaded_filename = secure_filename(uploaded_file.filename)
    
    print("===============================")
    print("Uploading the " + uploaded_filename + " file to the supabase bucket")
    
    start_time = time()
    response = upload_file_to_bucket('lsc_files', uploaded_filename, uploaded_data)
    
    print("===============================")
    elapsed_time = time() - start_time
    
    if response.status_code == HTTP_200_OK:
      print(f"Successfully uploaded the {uploaded_filename} file to the supabase bucket in {elapsed_time:.2f} seconds")
      
      response_url = str(response.request.url)
      
      if response_url is None:
          return jsonify({'error': 'Failed to get the URL of the uploaded file.'}), HTTP_404_NOT_FOUND
      
      session['uploaded_file_url'] = response_url
    
      return jsonify({
          'url': str(response_url),
          'filename': uploaded_filename,
          'dimensions': get_image_dimensions(uploaded_data),
          'size': get_image_size(uploaded_data)
      }), HTTP_201_CREATED

    elif response.status_code == HTTP_400_BAD_REQUEST:
        print("The file " + uploaded_filename + " was not found. Failed to upload to the supabase bucket")
        return jsonify({'error': "The file " + uploaded_filename + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST

    elif response.status_code == HTTP_409_CONFLICT:
        print("The file " + uploaded_filename + " already exists in the supabase bucket")
        return jsonify({'error': "The file " + uploaded_filename + " already exists in the supabase bucket"}), HTTP_409_CONFLICT

    else:
        print("Internal server error either in supabase or files controller.")
        return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR
    
@files.route('/analyze', methods=['POST', 'GET'])
@jwt_required()
def analyze():
  """
  Handles the analysis of the uploaded file using the uploaded custom model/weights of the user from the session.
  The file object includes the following attributes: `id`, `name`, `dimensions`, `size`, `url`, 
  `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.

  Returns:
    `JSON Response`: File object with a status code of `201 (HTTP_201_CREATED)`.
    
    `400 (HTTP_400_BAD_REQUEST)`: If no file is uploaded.
    
    `409 (HTTP_409_CONFLICT)`: If the file already exists in the supabase bucket.
    
    `500 (HTTP_500_INTERNAL_SERVER_ERROR)`: If there is an internal server error either in supabase or source code.
  """  
  current_user = get_jwt_identity()
  
  if request.method == 'POST':
    uploaded_file_url = session.get('uploaded_file_url')
    
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_file_url)
    
    existing_file = Files.query.filter_by(name=uploaded_filename, user_id=current_user).first()
    
    if existing_file:
      return jsonify({
        'error': 'File already exists.',
        'url': existing_file.url
        }), HTTP_409_CONFLICT
    
    # Assuming the weights controller has also stored the custom weights and retrieved its url from supabase in the session.
    session_custom_weights_url = session.get('uploaded_custom_weights_url')
    
    weights_filename = os.path.basename(session_custom_weights_url)
    
    print("===============================")
    print("Analyzing " + uploaded_filename + " using the uploaded " + weights_filename + " weights")
    start_time = time()
    
    # Predict the uploaded file using the custom weights of the user that was uploaded in the database and stored in session.
    result = custom_analyze_image(uploaded_file_url, session_custom_weights_url)
    
    elapsed_time = time() - start_time
    print("\n===============================")
    print(f"Image analyzed in {elapsed_time:.2f} seconds")
    
    # orig_img is of type numpy.ndarray
    resulting_image = torch.tensor(result[0].orig_img).numpy()
    
    classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
    accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
    error_rate = round(1 - accuracy, 2)
    
    start_time = time()
    # Assuming the resulting image file was previously uploaded in supabase files bucket without the results yet, 
    # delete that file first before uploading the new one with the results and boxes.
    delete_file_by_name('files', uploaded_filename)
    response = upload_file_to_bucket('files', resulting_image)
    
    print("===============================")
    elapsed_time = time() - start_time
    
    if response is HTTP_200_OK:
      print(f"Successfully uploaded then {uploaded_filename} file to the supabase bucket in {elapsed_time:.2f} seconds")
    
      url = get_file_url_by_name(uploaded_filename)
      
      if url is None:
        return jsonify({'error': 'Failed to get the url of the uploaded file. File failed to store in database.'}), HTTP_404_NOT_FOUND
      
      file = Files(
          name=uploaded_filename, 
          url=url, 
          user_id=current_user, 
          classification=classification, 
          accuracy=accuracy, 
          error_rate=error_rate, 
          dimensions=get_image_dimensions(resulting_image), 
          size=get_image_size(resulting_image)
        )
      db.session.add(file)
      db.session.commit()
      
      return jsonify({
        'id': file.id,
        'name': file.name,
        'dimensions': file.dimensions,
        'size': file.size,
        'url': file.url,
        'classification': classification,
        'accuracy': accuracy,
        'error_rate': error_rate,
        'resulting_image': resulting_image
        }), HTTP_201_CREATED
      
    elif response is HTTP_400_BAD_REQUEST:
      print("The file " + uploaded_filename + " was not found. Failed to upload to the supabase bucket")
      return jsonify({'error': "The file " + uploaded_filename + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST
    elif response is HTTP_409_CONFLICT:
      print("The file " + uploaded_filename + " already exists in the supabase bucket")
      return jsonify({'error': "The file " + uploaded_filename + " already exists in the supabase bucket"}), HTTP_409_CONFLICT
    else:
      print("Internal server error either in supabase or files controller.")
      return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR

# First half of demo method is tested except for returning the resulting_image.    
@files.route('/demo', methods=['POST', 'GET'])
@jwt_required()
def demo():
  if request.method == 'POST':
    uploaded_file_url = session.get('uploaded_file_url')
    
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_file_url)
    
    print("===============================")
    print("Analyzing " + uploaded_filename + " file")
    start_time = time()
    
    result = demo_inference(uploaded_file_url)
    
    elapsed_time = time() - start_time
    print("\n===============================")
    print(f"Image analyzed in {elapsed_time:.2f} seconds")
    
    if result is None:
      return jsonify({'error': 'Failed to analyze the image.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    # Return the resulting image as bytes to the frontend
    resulting_image = convert_image_to_bytes(result)
    
    start_time = time()
    response = upload_file_to_bucket('files', uploaded_filename, result)
    
    print("===============================")
    elapsed_time = time() - start_time
      
    if response is HTTP_200_OK:
      print(f"Successfully uploaded the {uploaded_filename} file to the supabase bucket in {elapsed_time:.2f} seconds")
      
      url = get_file_url_by_name(uploaded_filename)
      
      if url is None:
        return jsonify({'error': 'Failed to get the url of the uploaded file. File failed to store in database.'}), HTTP_404_NOT_FOUND
      
      return jsonify({
        'url': url}), HTTP_201_CREATED
      
    else:
      print("Internal server error either in supabase or files controller.")
      return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR
    
    

@files.get('/')
@jwt_required()
def get_all():
  """
  Retrieves files associated with the current user. Each file object in the list includes the following attributes: 
  `id`, `name`, `dimensions`, `size`, `url`, `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`. 
  
  Returns: 
    `JSON response`: List of file objects with a status code of `200 (HTTP_200_OK)`.
    
    `404 (HTTP_404_NOT_FOUND)`: If the files are not found.
  """
  current_user = get_jwt_identity()
  
  files = Files.query.filter_by(user_id=current_user)
  
  if not files:
    return jsonify({'message': 'No files found'}), HTTP_404_NOT_FOUND
  
  data=[]
  
  for file in files:
    data.append({
      'id': file.id,
      'name': file.name,
      'dimensions': file.dimensions,
      'size': file.size,
      'url': file.url,
      'classification': file.classification,
      'accuracy': file.accuracy,
      'error_rate': file.error_rate,
      'created_at': file.created_at,
      'updated_at': file.updated_at
      })
  
  return jsonify({'data': data}), HTTP_200_OK

@files.get('/<int:id>')
@jwt_required()
def get_by_id(id):
  """
  Retrieves information about a file based on its ID and the current user's identity. 
  The file object includes the following attributes: `id`, `name`, `dimensions`, `size`, `url`, 
  `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.
  
  Parameters: 
    `id`: The unique identifier of the file that the user want to retrieve.
    
  Returns:
    `JSON response`: File object with a status code of `200 (HTTP_200_OK)`.

    `404 (HTTP_404_NOT_FOUND)`: If the file is not found.
  """
  current_user = get_jwt_identity()
  
  file = Files.query.filter_by(user_id=current_user, id=id).first()
  
  if not file:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  return jsonify({
    'id': file.id,
    'name': file.name,
    'dimensions': file.dimensions,
    'size': file.size,
    'url': file.url,
    'classification': file.classification,
    'accuracy': file.accuracy,
    'error_rate': file.error_rate,
    'created_at': file.created_at,
    'updated_at': file.updated_at
    }), HTTP_200_OK

@files.delete('/<int:id>/delete')
@jwt_required()
def delete_by_id(id):
  """
  Deletes the file object based on its ID and the current user's identity.

  Parameters:
    `id`: The unique identifier of the file that the user wants to delete.

  Returns:
    `JSON response`: Message with a status code of `200 (HTTP_200_OK)`.

    `404 (HTTP_404_NOT_FOUND)`: If the file is not found.
  """
  current_user = get_jwt_identity()
  
  file = Files.query.filter_by(user_id=current_user, id=id).first()
  
  if not file:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  delete_file_by_name('files', file.name)
  
  db.session.delete(file)
  db.session.commit()
  
  return jsonify({'message': 'File successfully deleted'}), HTTP_200_OK