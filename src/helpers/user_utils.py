from flask import jsonify
import validators

from src.constants.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from src.models.users import Users


def validate_user_details(username, password, email):
  if len(password) < 3:
    return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST

  if len(username) < 6:
    return jsonify({'error': 'Username is too short'}), HTTP_400_BAD_REQUEST

  if not username.isalnum() or ' ' in username:
    return jsonify({'error': 'Username should be alphanumeric and can contain no spaces'}), HTTP_400_BAD_REQUEST

  if not validators.email(email):
    return jsonify({'Error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

  if Users.query.filter_by(email=email).first() is not None:
    return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

  if Users.query.filter_by(username=username).first() is not None:
    return jsonify({'error': "Username is taken"}), HTTP_409_CONFLICT