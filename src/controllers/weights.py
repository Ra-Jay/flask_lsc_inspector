import os
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
# from werkzeug.security import check_api_key_hash, generate_api_key_hash
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

weights = Blueprint("weights", __name__, url_prefix="/api/v1/weights")

WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights')

@weights.post('/')
@jwt_required()
def post():
    """
    The weights object includes the following attributes: `id`, `name`, `url`, `created_at`, `updated_at`.

    Returns:
        `JSON Response`: Weights object with a status code of `201 (HTTP_201_CREATED)`.
        
        `HTTP_400_BAD_REQUEST`: If the weights file is not found.
        
        `HTTP_409_CONFLICT`: If the api_key already exists.
        
        `HTTP_500_INTERNAL_SERVER_ERROR`: If there is an internal server error.
    """    
    current_user = get_jwt_identity()

    if request.method == 'POST':
        project_name = request.json.get('project_name', '')
        api_key = request.json.get('api_key', '')
        version = request.json.get('version', '')

        if Weights.query.filter_by(api_key=api_key).first():
            return jsonify({'error': 'API Key already exists.'}), HTTP_409_CONFLICT

        weight = Weights(id=uuid.uuid4(), user_id=current_user, project_name=project_name, api_key=api_key, version=version)
        db.session.add(weight)
        db.session.commit()

        return jsonify({
            'id': weight.id,
            'user_id':current_user, 
            'project_name': weight.project_name,
            'api_key': weight.api_key,
            'version': weight.version,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        }), HTTP_201_CREATED
            
@weights.get('/')
@jwt_required()
def get_all():
    """
    Retrieves all the weights objects based on the current user's identity.
    The weights object includes the following attributes: `id`, `name`, `url`, `created_at`, `updated_at`.

    Returns:
        `JSON Response`: List of weights objects with a status code of `200 (HTTP_200_OK)`.
        
        `HTTP_404_NOT_FOUND`: If the weights is not found.
    """    
    current_user = get_jwt_identity()

    weights = Weights.query.filter_by(user_id=current_user).all()

    if not weights:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
    data = []
    for weight in weights:
        data.append({
           'id': weight.id,
            'user_id':current_user, 
            'project_name': weight.project_name,
            'api_key': weight.api_key,
            'version': weight.version,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        })

    return jsonify({'data': data}), HTTP_200_OK

@weights.get('/<uuid(strict=False):id>')
@jwt_required()
def get_by_id(id):
    """
    Retrieves the weights object based on its ID and the current user's identity.
    The weights object includes the following attributes: `id`, `name`, `url`, `created_at`, `updated_at`.
    
    Parameters:
        `id`: The unique identifier of the weights that the user wants to retrieve.

    Returns:
        `JSON Response`: Weight object with a status code of `200 (HTTP_200_OK)`.
        
        `HTTP_404_NOT_FOUND`: If the weights is not found.
    """    
    current_user = get_jwt_identity()

    weight = Weights.query.filter_by(user_id=current_user, id=str(id)).first()

    if not weights:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
            'id': weight.id,
            'user_id':current_user, 
            'project_name': weight.project_name,
            'api_key': weight.api_key,
            'version': weight.version,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        }), HTTP_200_OK


@weights.delete('/<uuid(strict=False):id>')
@jwt_required()
def delete_by_id(id):
    """
    Deletes the weights object based on its ID and the current user's identity.

    Parameters:
        `id`: The unique identifier of the weights that the user wants to delete.

    Returns:
        `JSON Response`: Message with a status code of `200 (HTTP_200_OK)`.
        
        `HTTP_404_NOT_FOUND`: If the weights is not found.
    """    
    current_user = get_jwt_identity()

    weight = Weights.query.filter_by(user_id=current_user, id=str(id)).first()

    if not weight:
        return jsonify({'message': 'Weights not found'}), HTTP_404_NOT_FOUND

    db.session.delete(weight)
    db.session.commit()

    return jsonify({'message': 'Weights successfully deleted'}), HTTP_200_OK