import time
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.helpers.file_utils import convert_file_to_bytes
from src.helpers.supabase_utils import get_file_url_by_name, upload_file_to_bucket
from src.helpers.user_utils import validate_user_details   
from src.models.users import Users
from ..extensions import db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

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

    user=Users(username=username, password=generate_password_hash(password), email=email)
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
        if check_password_hash(user.password, password):
            return jsonify({
                'user': {
                    'refresh_token': create_refresh_token(identity=user.id),
                    'access_token': create_access_token(identity=user.id),
                    'username': user.username,
                    'email': user.email
                }

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

@auth.put('/<int:id>/edit')
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
    user = Users.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    validate_user_details(username, password, email)
    pwd_hash = generate_password_hash(password)

    user.username = username
    user.password = pwd_hash
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

@auth.put('/<int:id>/profile-image/edit')
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
    user = Users.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User is not found'}), HTTP_404_NOT_FOUND

    profile_image = request.files['profile_image']
    profile_image_data = convert_file_to_bytes(profile_image)
    profile_image_name = secure_filename(profile_image.filename)
    
    supabase_response = upload_file_to_bucket('lsc_profile_images', profile_image_name, profile_image_data)
    
    if supabase_response.status_code == HTTP_200_OK:
        supabase_file_url = get_file_url_by_name('lsc_profile_images', profile_image_name)
        
        if supabase_file_url is None:
            return jsonify({'error': 'Failed to get the url of the uploaded profile image.'}), HTTP_404_NOT_FOUND
        
        user.profile_image = supabase_file_url

        db.session.commit()

        return jsonify({
            'id': user.id,
            'username': user.username,
            'profile_image': user.profile_image,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }), HTTP_201_CREATED
        
    elif supabase_response.status_code == HTTP_400_BAD_REQUEST:
        print("The profile image " + profile_image_name + " was not found. Failed to upload to the supabase bucket")
        return jsonify({'error': "The profile image " + profile_image_name + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST
    elif supabase_response.status_code == HTTP_409_CONFLICT:
        print("The profile image " + profile_image_name + " already exists in the supabase bucket")
        return jsonify({'error': "The profile image " + profile_image_name + " already exists in the supabase bucket"}), HTTP_409_CONFLICT
    else:
        print("Internal server error either in supabase or user controller.")
        return jsonify({'error': "Internal server error either in supabase or profile image controller."}), HTTP_500_INTERNAL_SERVER_ERROR