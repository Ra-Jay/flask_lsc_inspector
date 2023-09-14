import os

import torch
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import validators
from src.helpers.utility import custom_analyze_image  
from src.models.files import Files
from ..extensions import db
from flask import session
from time import time
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

UPLOADS_FOLDER = os.path.join('src', 'static', 'uploads')

@files.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload_file():
  """
  Handles the uploading of a file, saves it locally, stores the uploaded file path in the session, and returns the file path.
  """
  if request.method == 'POST':
    if 'file' not in request.files:
      return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file = request.files['file']
    
    uploaded_filename = secure_filename(uploaded_file.filename)
    
    print("===============================")
    print("Uploading " + uploaded_filename)
    start_time = time()
    
    if not os.path.exists(UPLOADS_FOLDER):
      print("===============================")
      print("Creating " + UPLOADS_FOLDER + " folder")
      os.makedirs(UPLOADS_FOLDER)
      
    path = os.path.join(UPLOADS_FOLDER, uploaded_filename)
      
    uploaded_file.save(path)
    session['uploaded_file'] = path
    
    elapsed_time = time() - start_time
    print("===============================")
    print(f"New input file saved locally at {path} folder in {elapsed_time:.2f} seconds")
    
    return jsonify({'file_path': path}), HTTP_201_CREATED
    
@files.route('/analyze', methods=['POST', 'GET'])
@jwt_required()
def analyze_file():
  current_user = get_jwt_identity()
  
  if request.method == 'POST':
    uploaded_filepath = session.get('uploaded_filepath')
    
    if uploaded_filepath is None:
      return jsonify({'error': 'No uploaded file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_filename = os.path.basename(uploaded_filepath)
    
    existing_file = Files.query.filter_by(name=uploaded_filename, user_id=current_user).first()
    
    if existing_file:
      # TODO: Download/Preview the existing file through its URL and return it.
      # (Assuming the file can be previewed using its URL)
      return jsonify({
        'error': 'File already exists.',
        'file_path': existing_file.url
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
    resulting_image = result.orig_img
    
    classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
    accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
    error_rate = round(1 - accuracy, 2)
    
    # TODO: Get the dimensions and size of the uploaded file to be reused. Can also get the dimensions and size of the resulting image instead.
    
    # TODO: Generate URL to upload the resulting image to the cloud.
    
    file = Files(
        name=uploaded_filename, 
        url="TO BE IMPLEMENTED", 
        user_id=current_user, 
        classification=classification, 
        accuracy=accuracy, 
        error_rate=error_rate, 
        dimensions="TO BE IMPLEMENTED", 
        size="TO BE IMPLEMENTED"
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