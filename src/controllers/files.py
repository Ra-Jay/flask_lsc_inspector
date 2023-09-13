import os
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import validators  
from src.models.files import Files
from ..extensions import db
from time import time
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

UPLOADS_FOLDER = os.path.join('src', 'static', 'uploads')

@files.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload_file():
  if request.method == 'POST':
    if 'file' not in request.files:
      return jsonify({'error': 'No file found.'}), HTTP_400_BAD_REQUEST
    
    uploaded_file = request.files['file']
    
    uploaded_filename = secure_filename(uploaded_file.filename)
    
    existing_file = Files.query.filter_by(name=uploaded_filename).first()
    
    # TODO: Implement URL generation from AWS S3 bucket to be used and searched in the database. [RESEARCHING]
    
    if existing_file:
      return jsonify({'error': 'File already exists.'}), HTTP_409_CONFLICT
    
    print("===============================")
    print("Uploading " + uploaded_filename)
    start_time = time()
    
    if not os.path.exists(UPLOADS_FOLDER):
      print("===============================")
      print("Creating " + UPLOADS_FOLDER + " folder")
      os.makedirs(UPLOADS_FOLDER)
      
    path = os.path.join(UPLOADS_FOLDER, uploaded_filename)
      
    uploaded_file.save(path)
    
    elapsed_time = time() - start_time
    print("===============================")
    print(f"New input file saved locally at {path} folder in {elapsed_time:.2f} seconds")
    
    # This returns the path of the uploaded file to display in the frontend.
    return jsonify({'file_path': path}), HTTP_201_CREATED
    
