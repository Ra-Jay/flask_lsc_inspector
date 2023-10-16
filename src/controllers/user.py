from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, current_app, request, jsonify
from src.helpers.file_utils import get_file, generate_hex
from src.helpers.supabase_utils import get_file_url_by_name, upload_file_to_bucket
from src.helpers.user_utils import check_hash, get_hash, validate_user_details   
from src.models.users import Users
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
import os
import uuid

auth = Blueprint("auth", __name__, url_prefix="/api/v1/users")

@auth.post('register')
def register():
    """
    Register a user.
    
    Parameters:
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response`: The response from the server.
    """
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    validate_user_details(username, password, email)

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

@auth.post('/login')
def login():
    """
    Login a user.
    
    Parameters:
        `JSON Body`: The JSON body that contains the user attributes: `email` and `password`.
        
    Returns:
        `JSON Response`: The response from the server.
    """
    email = request.json.get('email', '')
    password = request.json.get('password', '')

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
                    'refresh_token': create_refresh_token(identity=user.id),
                    'access_token': create_access_token(identity=user.id),
                    'username': user.username,
                    'email': user.email,
                    'profile_image': user.profile_image,
                    'id': user.id,
                },'weights': weights

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

# Only for testing purposes
@auth.get('/user')
@jwt_required(refresh=True)
def user():
    user_id = get_jwt_identity()
    user = Users.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK

@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    """
    Refresh the user's access token.
    
    Returns:
        `JSON Response`: The response from the server.
    """
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
    
# Only for testing purposes
@auth.get('/')
def get_users():
    users = Users.query.all()
    data=[]
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        })

    return jsonify({'data': data}), HTTP_200_OK

@auth.put('/<uuid(strict=False):id>/edit')
@jwt_required()
def edit(id):
    """
    Edit a user.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response`: The response from the server.
    """
    user = Users.query.filter_by(id=str(id)).first()

    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    username=request.json['username']
    email=request.json['email']

    validate_user_details(username, user.password, email)
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
    }), HTTP_201_CREATED

@auth.put('/<uuid(strict=False):id>/profile-image/edit')
@jwt_required()
def edit_profile_image(id):
    """
    Edit a user's profile image.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `profile_image`: The input type as "profile_image" in the form-data.
        
    Returns:
        `JSON Response`: The response from the server.
    """
    print("id -----------------------:", type(str(id)))
    user = Users.query.filter_by(id=str(id)).first()
    print("id -----------------------:", user)

    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    image = get_file(request.files['profile_image'])
    image_name : str = image['name']
    image_data : bytes = image['data']
    
    supabase_response = upload_file_to_bucket(
            current_app.config['SUPABASE_BUCKET_PROFILE_IMAGES'], 
            generate_hex() + image_name, 
            image_data
        )
    if type(supabase_response) is str:
        user.profile_image = supabase_response
        db.session.commit()

        return jsonify({
            'id': user.id,
            'username': user.username,
            'profile_image': user.profile_image,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }), HTTP_201_CREATED
    else:
        return supabase_response
    
@auth.put('/<uuid(strict=False):id>/password')
@jwt_required()
def update_password(id):
    """
    Edit a user.
    
    Parameters:
        `id`: The id of the user that you want to edit.
        
        `JSON Body`: The JSON body that contains the user attributes: `username`, `email`, and `password`.
        
    Returns:
        `JSON Response`: The response from the server.
    """
    old_password= request.json['old_password']
    new_password= request.json['new_password']

    user = Users.query.filter_by(id=str(id)).first()

    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND
   
    if check_hash(user.password, old_password):
        user.passw0rd = get_hash(new_password)
    else :
          return jsonify({'message': 'Password doens\'t match.'}), HTTP_404_NOT_FOUND

    db.session.commit()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'password': user.password,
        'email': user.email,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }), HTTP_201_CREATED
