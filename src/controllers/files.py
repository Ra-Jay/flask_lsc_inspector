import os
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.helpers.file_utils import convert_file_to_bytes, get_image_dimensions, get_image_size, convert_image_to_bytes
from src.helpers.supabase_utils import upload_file_to_bucket, download_file_from_bucket, get_file_url_by_name, delete_file_by_name
from src.helpers.roboflow_utils import demo_inference, custom_inference
from src.models.files import Files
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

# This method is tested and working
@files.route('/upload', methods=['POST', 'GET'])
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
    uploaded_data = convert_file_to_bytes(uploaded_file)
    uploaded_filename = secure_filename(uploaded_file.filename)

    supabase_response = upload_file_to_bucket('lsc_files', uploaded_filename, uploaded_data)
    
    if supabase_response.status_code == HTTP_200_OK:
      supabase_file_url = get_file_url_by_name('lsc_files', uploaded_filename)
      
      if supabase_file_url is None:
          return jsonify({'error': 'Failed to get the URL of the uploaded file.'}), HTTP_404_NOT_FOUND
    
      return jsonify({
          'url': supabase_file_url,
          'filename': uploaded_filename,
          'dimensions': get_image_dimensions(uploaded_data),
          'size': get_image_size(uploaded_data)
      }), HTTP_201_CREATED

    elif supabase_response.status_code == HTTP_400_BAD_REQUEST:
        print("The file " + uploaded_filename + " was not found. Failed to upload to the supabase bucket")
        return jsonify({'error': "The file " + uploaded_filename + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST
    elif supabase_response.status_code == HTTP_409_CONFLICT:
        print("The file " + uploaded_filename + " already exists in the supabase bucket")
        return jsonify({'error': "The file " + uploaded_filename + " already exists in the supabase bucket"}), HTTP_409_CONFLICT
    else:
        print("Internal server error either in supabase or files controller.")
        return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR
    
# This method is tested and working
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
    uploaded_file_url = request.json['url']
    # api_key = request.json['api_key']
    # project_name = request.json['project_name']
    # version_number = request.json['version_number']
    
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_file_url)
    existing_file = Files.query.filter_by(name=uploaded_filename, user_id=current_user).first()
    if existing_file:
      return jsonify({
        'error': 'File already exists.',
        'url': existing_file.url
        }), HTTP_409_CONFLICT
    
    result = custom_inference(image_url=uploaded_file_url)
    if result is None:
      return jsonify({'error': 'Failed to analyze the image.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    result_data = convert_image_to_bytes(result['image'])
    supabase_response = upload_file_to_bucket('lsc_files', 'analyzed_' + uploaded_filename, result_data)
    
    if supabase_response.status_code is HTTP_200_OK:
      supabase_file_url = get_file_url_by_name('lsc_files', 'analyzed_' + uploaded_filename)
      
      if supabase_file_url is None:
        return jsonify({'error': 'Failed to get the url of the uploaded file. File failed to store in database.'}), HTTP_404_NOT_FOUND
      
      file = Files(
          name=uploaded_filename, 
          url=supabase_file_url, 
          user_id=current_user, 
          classification=result['class'], 
          accuracy=result['confidence'], 
          error_rate=result['error_rate'], 
          dimensions=get_image_dimensions(result_data), 
          size=get_image_size(result_data)
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
      
    elif supabase_response.status_code is HTTP_400_BAD_REQUEST:
      print("The file " + uploaded_filename + " was not found. Failed to upload to the supabase bucket")
      return jsonify({'error': "The file " + uploaded_filename + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST
    elif supabase_response.status_code is HTTP_409_CONFLICT:
      print("The file " + uploaded_filename + " already exists in the supabase bucket")
      return jsonify({'error': "The file " + uploaded_filename + " already exists in the supabase bucket"}), HTTP_409_CONFLICT
    else:
      print("Internal server error either in supabase or files controller.")
      return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR
 
# This method is tested and working
@files.route('/demo', methods=['POST', 'GET'])
def demo():
  if request.method == 'POST':
    uploaded_file_url = request.json['url']
    
    if uploaded_file_url is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_file_url)
    result = demo_inference(uploaded_file_url)
    
    if result is None:
      return jsonify({'error': 'Failed to analyze the image.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    result_data = convert_image_to_bytes(result)
    supabase_response = upload_file_to_bucket('lsc_files', 'demo_inferred_' + uploaded_filename, result_data)
      
    if supabase_response.status_code == HTTP_200_OK:
      supabase_file_url = get_file_url_by_name('lsc_files', 'demo_inferred_' + uploaded_filename)
      
      if supabase_file_url is None:
        return jsonify({'error': 'Failed to get the url of the uploaded file. File failed to store in database.'}), HTTP_404_NOT_FOUND
      
      return jsonify({
        'url': supabase_file_url}), HTTP_201_CREATED
    else:
      print("Internal server error either in supabase or files controller.")
      return jsonify({'error': "Internal server error either in supabase or source code"}), HTTP_500_INTERNAL_SERVER_ERROR
    
@files.post('/download')
@jwt_required()
def download():
  current_user = get_jwt_identity()
  if request.method == 'POST':
    file_id_to_download = request.json['id']
    destination = request.json['destination']
    
    file = Files.query.filter_by(user_id=current_user, id=file_id_to_download).first()
    
    if not file:
      return jsonify({'error': 'File not found.'}), HTTP_404_NOT_FOUND
    
    file_data = download_file_from_bucket('lsc_files', file.name)
    
    if file_data is None:
      return jsonify({'error': 'Failed to download the file.'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    with open(destination, 'wb') as f:
      f.write(file_data)
    
    return jsonify({
      'destination': destination
      }), HTTP_200_OK
  
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