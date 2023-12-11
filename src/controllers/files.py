from constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, current_app, request, jsonify
from helpers.file_utils import generate_hex, get_file, get_file_base_name, get_image_dimensions, get_image_size, convert_image_to_bytes
from helpers.supabase_utils import delete_file_by_name, upload_file_to_bucket
from helpers.roboflow_utils import perform_inference
from models.files import Files
from extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

@files.post('/upload')
def upload():
  """
  Handles the uploaded file to the Supabase. 
  
  Body:
    `Multipart-Form/Form-Data`: The multipart-form/form-data as a file with the key 'file'.
    
  Returns:
    `JSON Response (201)`: The response from the server with the file details: `url`, `name`, `dimensions`, and `size`.
    
    `JSON Response (400)`: If no file is uploaded.
    
    `JSON Supabase Response`: If there is an error while uploading the file to Supabase.
  """  
  if 'file' not in request.files:
    return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
  
  file = get_file(request.files['file'])
  file_name : str = file['name']
  file_data : bytes = file['data']
  supabase_response = upload_file_to_bucket("FILES", f"uploads/users/{generate_hex()}{file_name}", file_data)
  if type(supabase_response) is str:
    return jsonify({
        'url': supabase_response,
        'name': file_name,
        'dimensions': get_image_dimensions(file_data),
        'size': get_image_size(file_data)
    }), HTTP_201_CREATED
  else: return supabase_response
    
@files.post('/analyze')
@jwt_required()
def analyze():
  """
  Handles the analysis of the uploaded file using the custom weights of the user.
  
  Body:
    `JSON Body`: The JSON body that contains: `url`, `api_key`, `project_name`, and `version_number`.

  Returns:
    `JSON Response (201)`: The response from the server with the file details: `id`, `name`, `dimensions`, `size`, `url`, `classification`, `accuracy`, and `error_rate`.
    
    `JSON Response (400)`: If no file is uploaded.
    
    `JSON Response (409)`: If the file already exists in the database.
    
    `JSON Response (500)`: If there is an SQLAlchemy error.
    
    `JSON Roboflow Response`: If there is an error while performing inference in Roboflow.
    
    `JSON Supabase Response`: If there is an error while uploading the file to Supabase.
  """  
  uploaded_file_url = request.json['url']
  if uploaded_file_url is None:
    return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
  
  current_user = get_jwt_identity()
  uploaded_file_name = get_file_base_name(uploaded_file_url)
  existing_file = Files.query.filter_by(name=uploaded_file_name, user_id=current_user).first()
  if existing_file:
    return jsonify({'error': 'File already exists.', 'url': existing_file.url}), HTTP_409_CONFLICT
  
  project_name = request.json['project_name']
  api_key = request.json['api_key']
  version = request.json['version']
  weight_id = request.json['weight_id']
  result = perform_inference(image_url=uploaded_file_url, project_name=project_name, api_key=api_key, version_number=version)
  if type(result) is not dict:
    return result
  
  result_data = convert_image_to_bytes(result['image'])
  new_file_name = generate_hex() + uploaded_file_name
  supabase_response = upload_file_to_bucket("FILES", f"main/{current_user}/{new_file_name}",result_data)
  if type(supabase_response) is str:
    try:
      file = Files(
          id=uuid4(),
          name=new_file_name, 
          user_id=current_user, 
          classification=result['classification'], 
          accuracy=result['accuracy'],  
          error_rate=result['error_rate'], 
          dimensions=get_image_dimensions(result_data), 
          size=get_image_size(result_data),
          url=supabase_response,
          weight_id=weight_id
        )
      db.session.add(file)
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
    except SQLAlchemyError as e:
      db.session.rollback()
      return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR
  else: return supabase_response
 
@files.post('/demo')
def demo():
  """
  Handles the analysis of the uploaded file using the pre-defined weights of the application.
  
  Body:
    `JSON Body`: The JSON body that contains the `url` attribute only.
    
  Returns:
    `JSON Response (201)`: The response from the server with the file details: `url`, `classification`, `accuracy`, and `error_rate`.
    
    `JSON Response (400)`: If no file is uploaded.
    
    `JSON Roboflow Response`: If there is an error while performing inference in Roboflow.
    
    `JSON Supabase Response`: If there is an error while uploading the file to Supabase.
  """
  uploaded_file_url = request.json['url']
  if uploaded_file_url is None:
    return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
  
  result = perform_inference(uploaded_file_url)
  if type(result) is not dict:
    return result
  
  supabase_response = upload_file_to_bucket(
      "FILES", f"demos/{generate_hex()}{get_file_base_name(uploaded_file_url)}", convert_image_to_bytes(result['image'])
    )
  if type(supabase_response) is str:
    return jsonify({
      'url': supabase_response,
      'classification': result['classification'],
      'accuracy': result['accuracy'],
      'error_rate': result['error_rate'],
      }), HTTP_201_CREATED
  else: return supabase_response
    
@files.get('/')
@jwt_required()
def get_all():
  """
  Retrieves files of the current user.
  
  Returns: 
    `JSON Response (200)`: The response from the server with the list of file and its 
    details: `id`, `name`, `dimensions`, `size`, `url`, `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.
    
    `JSON Response (204)`: If there are no files found.
  """
  files = Files.query.filter_by(user_id=get_jwt_identity())
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
  Retrieves file by its id of the current user.
  
  Parameters: 
    `id`: The unique identifier of the file that the user wants to retrieve.
    
  Returns:
    `JSON Response (200)`: The response from the server with the file details: `id`, `name`, `dimensions`, 
    `size`, `url`, `classification`, `accuracy`, `error_rate`, `created_at`, and `updated_at`.
    
    `JSON Response (404)`: If the file is not found.
  """
  file = Files.query.filter_by(user_id=get_jwt_identity(), id=str(id)).first()
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

@files.delete('/<uuid(strict=False):id>/delete')
@jwt_required()
def delete_by_id(id):
  """
  Deletes the file by its id of the current user.

  Parameters:
    `id`: The unique identifier of the file that the user wants to delete.

  Returns:
    `JSON Response (200)`: The response from the server with the successful `message`.
    
    `JSON Response (404)`: If the file is not found.
    
    `JSON Response (500)`: If there is an SQLAlchemy error.
  """
  current_user = get_jwt_identity()
  file = Files.query.filter_by(user_id=current_user, id=str(id)).first()
  if not file:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  supabase_response = delete_file_by_name("FILES", f"main/{current_user}/{file.name}")
  if supabase_response != HTTP_200_OK:
    return supabase_response
  try:
    db.session.delete(file)
    db.session.commit()
    return jsonify({'message': 'File successfully deleted'}), HTTP_200_OK
  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR

@files.delete('/clear')
@jwt_required()
def delete_all():
  """
  Deletes all the files of current user's identity.

  Parameters:
    `id`: The unique identifier of the file that the user wants to delete.

  Returns:
    `JSON Response (200)`: The response from the server with the successful `message`.
    
    `JSON Response (404)`: If the file is not found.
    
    `JSON Response (500)`: If there is an SQLAlchemy error.
  """
  current_user = get_jwt_identity()
  files = Files.query.filter_by(user_id=current_user)
  if not files:
    return jsonify({'message': 'File not found'}), HTTP_404_NOT_FOUND
  
  for file in files:
    supabase_response = delete_file_by_name("FILES", f"main/{current_user}/{file.name}")
    if supabase_response != HTTP_200_OK:
      return supabase_response
  
  try:
    db.session.query(Files).filter_by(user_id=current_user).delete()
    db.session.commit()
    return jsonify({'message': 'File successfully deleted'}), HTTP_200_OK
  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR