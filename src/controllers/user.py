from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, current_app, request, jsonify
from src.helpers.file_utils import get_file, generate_hex
from src.helpers.supabase_utils import upload_file_to_bucket
from src.helpers.user_utils import check_hash, get_hash, validate_user_details   
from src.models.users import Users
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

users = Blueprint("users", __name__, url_prefix="/api/v1/users")

@users.post('/register')
def register():
    """
    Register a user.
    
    Parameters:
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response (201)`: The response from the server with the message and user details: `username` and `email`.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
    """
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    validate_user_details(username, password, email)
    try:
        user=Users(id = uuid.uuid4(), username=username, password=get_hash(password), email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': "User created",
            'user': {
                'username': username, 
                'email': email,
            }
        }), HTTP_201_CREATED
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR

@users.post('/login')
def login():
    """
    Login a user.
    
    Parameters:
        `JSON Body`: The JSON body that contains the user attributes: `email` and `password`.
        
    Returns:
        `JSON Response (200)`: The response from the server with the list of user's `weights` and user details: `id`, `refresh_token`, `access_token`, `username`, `email`, and `profile_image`.
        
        `JSON Response (401)`: If the user is not authorized.
    """
    email = request.json['email']
    password = request.json['password']

    user = Users.query.filter_by(email=email).first()
    if user:
        user_weights = Weights.query.filter_by(user_id=user.id).all()
        weights = []
        for weight in user_weights:
            weights.append({
                'id': weight.id,
                'user_id':user.id, 
                'project_name': weight.project_name,
                'api_key': weight.api_key,
                'version': weight.version,
                'model_type': weight.model_type,
            })
        if check_hash(user.password, password):
            return jsonify({
                'user': {
                    'id': user.id,
                    'refresh_token': create_refresh_token(identity=user.id),
                    'access_token': create_access_token(identity=user.id),
                    'username': user.username,
                    'email': user.email,
                    'profile_image': user.profile_image,
                },'weights': weights
            }), HTTP_200_OK
    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@users.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    """
    Refresh the user's access token.
    
    Returns:
        `JSON Response (200)`: The response from the server with the `access` token as a string.
    """
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK

@users.put('/<uuid(strict=False):id>/edit')
@jwt_required()
def edit(id : uuid):
    """
    Edit a user.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response (200)`: The response from the server with the user details: `id`, `username`, `password`, `email`, `created_at`, and `updated_at`.
        
        `JSON Response (401)`: If the user is not authorized.
        
        `JSON Response (404)`: If the user is not found.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
    """
    str_id = str(id)
    if str_id != get_jwt_identity():
        return jsonify({'message': 'You are not authorized to edit this user.'}), HTTP_401_UNAUTHORIZED
    
    user = Users.query.filter_by(id=str_id).first()
    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    username=request.json['username']
    email=request.json['email']
    validate_user_details(username, user.password, email)
    try:
        user.username = username
        user.email = email
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }), HTTP_200_OK
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR

@users.put('/<uuid(strict=False):id>/profile-image/edit')
@jwt_required()
def edit_profile_image(id : uuid):
    """
    Edit a user's profile image.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `Multipart-Form/Form-Data`: The multipart-form/form-data as a file with the key 'profile_image'.
        
    Returns:
        `JSON Response (200)`: The response from the server with the user details: `id`, `username`, `profile_image`, `created_at`, and `updated_at`.
        
        `JSON Response (401)`: If the user is not authorized.
        
        `JSON Response (404)`: If the user is not found.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
        
        `JSON Supabase Response`: If there is an error while uploading the file to Supabase.
    """
    str_id = str(id)
    if str_id != get_jwt_identity():
        return jsonify({'message': 'You are not authorized to edit this user.'}), HTTP_401_UNAUTHORIZED
    
    user = Users.query.filter_by(id=str_id).first()
    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    image = get_file(request.files['profile_image'])
    supabase_response = upload_file_to_bucket(
            current_app.config['SUPABASE_BUCKET_PROFILE_IMAGES'], 
            generate_hex() + image['name'], 
            image['data']
        )
    if type(supabase_response) is str:
        try:
            user.profile_image = supabase_response
            db.session.commit()
            return jsonify({
                'id': user.id,
                'username': user.username,
                'profile_image': user.profile_image,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }), HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return supabase_response
    
@users.put('/<uuid(strict=False):id>/password/edit')
@jwt_required()
def edit_password(id):
    """
    Edit a user.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response (200)`: The response from the server with the user details: `id`, `username`, `password`, `email`, `created_at`, and `updated_at`.
        
        `JSON Response (400)`: If the old password doesn't match.
        
        `JSON Response (401)`: If the user is not authorized.
        
        `JSON Response (404)`: If the user is not found.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
    """
    str_id = str(id)
    if str_id != get_jwt_identity():
        return jsonify({'message': 'You are not authorized to edit this user.'}), HTTP_401_UNAUTHORIZED
    
    user = Users.query.filter_by(id=str_id).first()
    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND
    
    old_password= request.json['old_password']
    new_password= request.json['new_password']
    if check_hash(user.password, old_password):
        try:
            user.password = get_hash(new_password)
            user.updated_at = datetime.now()
            db.session.commit()
            return jsonify({
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'email': user.email,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }), HTTP_200_OK
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR
    else :
          return jsonify({'message': 'Password doesn\'t match.'}), HTTP_400_BAD_REQUEST
