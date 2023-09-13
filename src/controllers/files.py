from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
import validators  
from src.models.files import Files
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required

files = Blueprint("files", __name__, url_prefix="/api/v1/files")

@files.route('/', methods=['POST', 'GET'])
@jwt_required()
def upload_file():
  current_user = get_jwt_identity()
  
  
