from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators   
from src.models.users import Users
from .extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required
# from .schema.users import users_model, user_input_model


auth = Blueprint("weights", __name__, url_prefix="/api/v1/weights/")

@weights.route('/', methods=['POST', 'GET'])
@jwt_required
def bookmarks():

