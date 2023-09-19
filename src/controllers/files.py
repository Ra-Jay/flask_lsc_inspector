import os

import torch
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import validators
from src.helpers.file_utils import get_image_dimensions, get_image_size
from src.helpers.yolo_utils import custom_analyze_image, demo_analyze_image
from src.helpers.supabase_utils import upload_file_to_bucket, download_file_from_bucket, get_file_url_by_name, get_all_files_from_bucket, delete_file_by_name
from src.models.files import Files
from ..extensions import db
from flask import session
from time import time
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

@files.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload_file():
  """
  Handles the uploading of a file, stores the uploaded file path in the session, 
  stores it in supabase files bucket, and returns the file path This function 
  does not store the file in the database.
  """
  if request.method == 'POST':
    if 'file' not in request.files:
      return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file = request.files['file']
    
    uploaded_filename = secure_filename(uploaded_file.filename)
    
    print("===============================")
    print("Uploading the " + uploaded_filename + " file to the supabase bucket")
    
    start_time = time()
    response = upload_file_to_bucket('files', uploaded_file)
    
    print("===============================")
    elapsed_time = time() - start_time
    
    if response is HTTP_200_OK:
      print(f"Successfully uploaded the {uploaded_filename} file to the supabase bucket in {elapsed_time:.2f} seconds")
      
      url = get_file_url_by_name(uploaded_filename)
      
      if url is None:
        return jsonify({'error': 'Failed to get the url of the uploaded file.'}), HTTP_404_NOT_FOUND
      
      session['uploaded_file_url'] = url
      
      return jsonify({
        'url': url,
        'filename': uploaded_filename,
        'dimensions': get_image_dimensions(uploaded_file),
        'size': get_image_size(uploaded_file)
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
    
@files.route('/analyze', methods=['POST', 'GET'])
@jwt_required()
def analyze_file():
  """
  Handles the analysis of the uploaded file using the uploaded custom weights, stores the analysis
  results in a database, and returns the analysis details along with the resulting image.
  """
  current_user = get_jwt_identity()
  
  if request.method == 'POST':
    uploaded_filepath = session.get('uploaded_filepath')
    
    if uploaded_filepath is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_filepath)
    
    existing_file = Files.query.filter_by(name=uploaded_filename, user_id=current_user).first()
    
    if existing_file:
      return jsonify({
        'error': 'File already exists.',
        'url': existing_file.url
        }), HTTP_409_CONFLICT
    
    # Assuming the weights controller has also stored the custom weights in the session.
    session_custom_weights = session.get('uploaded_custom_weights')
    
    print("===============================")
    print("Analyzing " + uploaded_filename + " using the uploaded " + session_custom_weights['name'] + " weights")
    start_time = time()
    
    # Predict the uploaded file using the custom weights of the user that was uploaded in the database and stored in session.
    result = custom_analyze_image(uploaded_filename, session_custom_weights)
    
    elapsed_time = time() - start_time
    print("\n===============================")
    print(f"Image analyzed in {elapsed_time:.2f} seconds")
    
    # orig_img is of type numpy.ndarray
    resulting_image = torch.tensor(result[0].orig_img).numpy()
    
    classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
    accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
    error_rate = round(1 - accuracy, 2)
    
    dimensions = get_image_dimensions(resulting_image)
    size = get_image_size(resulting_image)
    
    start_time = time()
    response = upload_file_to_bucket(resulting_image)
    
    print("===============================")
    elapsed_time = time() - start_time
    
    if response is HTTP_200_OK:
      print("Uploaded the " + uploaded_filename + " to the supabase bucket in {elapsed_time:.2f} seconds")
    
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
          dimensions=dimensions, 
          size=size
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