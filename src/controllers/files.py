from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, current_app, request, jsonify
from src.helpers.file_utils import generate_hex, get_file, get_file_base_name, get_image_dimensions, get_image_size, convert_image_to_bytes
from src.helpers.supabase_utils import delete_file_by_name, upload_file_to_bucket
from src.helpers.roboflow_utils import perform_inference
from src.models.files import Files
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

@files.route('/upload', methods=['POST', 'GET'])
def upload():
  """
  Handles the uploaded file to the supabase bucket. 
  The file object includes the following attributes: `id`, `name`, `dimensions`, `size`, `url`,
  
  Body:
    `Multipart-Form/Form-Data`: The multipart-form/form-data as a file with the key 'file'.
    
  Returns:
    `JSON Response`: File object with a status code of `201`, otherwise returns the error response from the server.
  """  
  if request.method == 'POST':
    if 'file' not in request.files:
      return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
    
    file = get_file(request.files['file'])
    file_name : str = file['name']
    file_data : bytes = file['data']

    supabase_response = upload_file_to_bucket(
        current_app.config['SUPABASE_BUCKET_FILES'], 
        'uploads/' + generate_hex() + file_name, 
        file_data
      )
    if type(supabase_response) is str:
      return jsonify({
          'url': supabase_response,
          'name': file_name,
          'dimensions': get_image_dimensions(file_data),
          'size': get_image_size(file_data)
      }), HTTP_201_CREATED
    else:
      return supabase_response
    
@files.route('/analyze', methods=['POST', 'GET'])
@jwt_required()
def analyze():
  """
  Handles the analysis of the uploaded file using the uploaded custom model/weights of the user from the session.
  The file object includes the following attributes: `id`, `name`, `dimensions`, `size`, `url`, 
  `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.
  
  Body:
    `JSON Body`: The JSON body that contains the following attributes: `url`, `api_key`, `project_name`, and `version_number`.

  Returns:
    `JSON Response`: File object with a status code of `201 (HTTP_201_CREATED)`.
    
    `400 (HTTP_400_BAD_REQUEST)`: If no file is uploaded.
    
    `409 (HTTP_409_CONFLICT)`: If the file already exists in the supabase bucket.
    
    `500 (HTTP_500_INTERNAL_SERVER_ERROR)`: If there is an internal server error either in supabase or source code.
  """  
  current_user = get_jwt_identity()
  if request.method == 'POST':
    uploaded_file_url = request.json['url']
    project_name = request.json['project_name']
    api_key = request.json['api_key']
    version = request.json['version']
    weight_id = request.json['weight_id']
    # Add this if the implmentation of the user having previously deployed a model to roboflow is ready.
    # api_key = request.json['api_key']
    # project_name = request.json['project_name']
    # version_number = request.json['version_number']
    print("--=-=-=-=-=-=-=-==-=-=-", api_key)
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file_name = get_file_base_name(uploaded_file_url)
    existing_file = Files.query.filter_by(name=uploaded_file_name, user_id=current_user).first()
    if existing_file:
      return jsonify({
        'error': 'File already exists.',
        'url': existing_file.url
        }), HTTP_409_CONFLICT
    
    # Add the api_key, project_name, and version_number if the implmentation of the user having previously deployed a model to roboflow is ready.
    result = perform_inference(image_url=uploaded_file_url, project_name=project_name, api_key=api_key, version_number=version)
    
    if result is None:
      return jsonify({'error': 'Failed to analyze the image.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    result_data = convert_image_to_bytes(result['image'])
    
    file = Files(
        id=uuid.uuid4(),
        name=uploaded_file_name, 
        user_id=current_user, 
        classification=result['classification'], 
        accuracy=result['accuracy'],  
        error_rate=result['error_rate'], 
        dimensions=get_image_dimensions(result_data), 
        size=get_image_size(result_data),
        url='',
        weight_id=weight_id
      )
    db.session.add(file)
    db.session.commit()
    
    new_file_name = generate_hex() + uploaded_file_name
    
    supabase_response = upload_file_to_bucket(
        current_app.config['SUPABASE_BUCKET_FILES'], 
        'main/' + new_file_name,
        result_data
      )
    if type(supabase_response) is str:
      file.name = new_file_name
      file.url = supabase_response
      db.session.commit()
      
      return jsonify({
        'id': file.id,
        'name': file.name,
        'dimensions': file.dimensions,
        'size': file.size,
        'url': file.url,
        'classification': file.classification,
        'accuracy': file.accuracy,
        'error_rate': file.error_rate
        }), HTTP_201_CREATED
    else:
      return supabase_response
 
@files.route('/demo', methods=['POST', 'GET'])
def demo():
  """
  Handles the analysis of the uploaded file using the uploaded custom model/weights of the user from the session.
  
  Body:
    `JSON Body`: The JSON body that contains the `url` attribute only.
    
  Returns:
    `JSON Response`: File object with a status code of `201 (HTTP_201_CREATED)`.
    
    `400 (HTTP_400_BAD_REQUEST)`: If no file is uploaded.
    
    `409 (HTTP_409_CONFLICT)`: If the file already exists in the supabase bucket.
    
    `500 (HTTP_500_INTERNAL_SERVER_ERROR)`: If there is an internal server error either in supabase or source code.
  """
  if request.method == 'POST':
    uploaded_file_url = request.json['url']
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file_name = get_file_base_name(uploaded_file_url)
      
    result = perform_inference(image_url=uploaded_file_url)
    if result is None:
      return jsonify({'error': 'Failed to analyze the image.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    supabase_response = upload_file_to_bucket(
        current_app.config['SUPABASE_BUCKET_FILES'], 
        'demos/' + generate_hex() + uploaded_file_name, 
        convert_image_to_bytes(result['image'])
      )
    if type(supabase_response) is str:
      return jsonify({
        'url': supabase_response,
        'classification': result['classification'],
        'accuracy': result['accuracy'],
        'error_rate': result['error_rate'],
        }), HTTP_201_CREATED
    else:
      return supabase_response
    
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
    return jsonify({'message': 'No files found'}), HTTP_204_NO_CONTENT
  
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

@files.get('/<uuid(strict=False):id>')
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
  file = Files.query.filter_by(user_id=current_user, id=str(id)).first()
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

@files.delete('/<uuid(strict=False):id>')
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
  file = Files.query.filter_by(user_id=current_user, id=str(id)).first()
  if not file:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  delete_file_by_name(current_app.config['SUPABASE_BUCKET_FILES'], 'main/' + file.name)
  
  db.session.delete(file)
  db.session.commit()
  
  return jsonify({'message': 'File successfully deleted'}), HTTP_200_OK

@files.delete('/')
@jwt_required()
def delete_all():
  """
  Deletes all the files of current user's identity.

  Parameters:
    `id`: The unique identifier of the file that the user wants to delete.

  Returns:
    `JSON response`: Message with a status code of `200 (HTTP_200_OK)`.

    `404 (HTTP_404_NOT_FOUND)`: If the file is not found.
  """
  current_user = get_jwt_identity()
  
  files = Files.query.filter_by(user_id=current_user)
  if not files:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  for file in files:
    delete_file_by_name(current_app.config['SUPABASE_BUCKET_FILES'], 'main/' + file.name)
  
  db.session.query(Files).filter_by(user_id=current_user).delete()
  db.session.commit()
  
  return jsonify({'message': 'File successfully deleted'}), HTTP_200_OK