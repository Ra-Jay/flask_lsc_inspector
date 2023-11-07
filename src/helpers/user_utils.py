from flask import jsonify
from validators import email as validate_email
from werkzeug.security import check_password_hash, generate_password_hash

from src.constants.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from src.models.users import Users

def get_hash(password : str):
  """
  Generates a hash from a password.
  
  Parameters:
    `password`: The password that you want to generate a hash from.
    
  Returns:
    `str`: The hash of the password.
  """
  return generate_password_hash(password)

def check_hash(password : str, hash : str):
  """
  Checks if the password matches the hash.
  
  Parameters:
    `password`: The password that you want to check.
    
    `hash`: The hash that you want to check.
    
  Returns:
    `bool`: True if the password matches the hash, otherwise False.
  """
  return check_password_hash(password, hash)

def validate_user_details(username : str, password : str, email : str):
  """
  Validates the user details.
  
  Parameters:
    `username`: The username of the user.
    
    `password`: The password of the user.
    
    `email`: The email of the user.
    
  Returns:
    `JSON Response`: The error response from the server if none of the criteria meets, otherwise returns none.
  """
  if len(password) < 3:
    return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST

  if len(username) < 6:
    return jsonify({'error': 'Username is too short'}), HTTP_400_BAD_REQUEST

  if not username.isalnum() or ' ' in username:
    return jsonify({'error': 'Username should be alphanumeric and can contain no spaces'}), HTTP_400_BAD_REQUEST

  if not validate_email(email):
    return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

  if Users.query.filter_by(email=email).first() is not None:
    return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

  if Users.query.filter_by(username=username).first() is not None:
    return jsonify({'error': "Username is taken"}), HTTP_409_CONFLICT