from src.models.files import Files
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from src.helpers.roboflow_utils import deploy_model
from src.models.weights import Weights
from extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

weights = Blueprint("weights", __name__, url_prefix="/api/v1/weights")

@weights.post('/deploy')
@jwt_required()
def deploy():
    """
    Deploy a model to Roboflow.
    
    Body:
        `JSON Body`: The JSON body that contains the weights attributes: `project_name`, `workspace`, 
        `api_key`, `version`, `model_type`, `model_path`, and `type`.

    Returns:
        `JSON Response (201)`: The response from the server with the weights details: `id`, `user_id`, `project_name`, 
        `api_key`, `version`, `model_type`, `type`, `created_at`, and `updated_at`.
        
        `JSON Response (409)`: If the API Key of the current user already exists.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
        
        `JSON Roboflow Response`: If there is an error when deploying to the Roboflow server.
    """    
    current_user = get_jwt_identity()
    api_key = request.json['api_key']
    
    type = request.json['type']
    model_path = request.json['model_path']
    weight = Weights(
        id=uuid4(), 
        user_id=current_user, 
        workspace=request.json['workspace'], 
        project_name=request.json['project_name'], 
        api_key=api_key, 
        version=request.json['version'], 
        model_type=request.json['model_type'], 
        type=type
    )
    if type == 'custom':
        roboflow_response = deploy_model(api_key, weight.workspace, weight.project_name, weight.version, weight.model_type, model_path)
        if roboflow_response != HTTP_201_CREATED: return roboflow_response
    try:
        db.session.add(weight)
        db.session.commit()
        return jsonify({
            'id': weight.id,
            'user_id':current_user, 
            'project_name': weight.project_name,
            'api_key': weight.api_key,
            'version': weight.version,
            'model_type': weight.model_type,
            'type': weight.type,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        }), HTTP_201_CREATED
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR

@weights.get('/')
@jwt_required()
def get_all():
    """
    Retrieves the list of weights of the current user.

    Returns:
        `JSON Response (201)`: The response from the server with the list of user's `weights` and user details: 
        `id`, `refresh_token`, `access_token`, `username`, `email`, and `profile_image`.
        
        `JSON Response (404)`: If the weights is not found.
    """    
    current_user = get_jwt_identity()
    weights = Weights.query.filter_by(user_id=current_user).all()
    if not weights:
        return jsonify({'message': 'Weights not found.'}), HTTP_404_NOT_FOUND
    
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
    Retrieves the weights by its id of the current user.
    
    Parameters:
        `id`: The unique identifier of the weights that the user wants to retrieve.

    Returns:
        `JSON Response (200)`: The response from the server with the weights details: `id`, `user_id`, `project_name`,
        
        `JSON Response (404)`: If the weights is not found.
    """    
    current_user = get_jwt_identity()
    weight = Weights.query.filter_by(user_id=current_user, id=str(id)).first()
    if not weights:
        return jsonify({'message': 'No weights found.'}), HTTP_404_NOT_FOUND

    return jsonify({
            'id': weight.id,
            'user_id':current_user, 
            'project_name': weight.project_name,
            'api_key': weight.api_key,
            'version': weight.version,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        }), HTTP_200_OK

@weights.delete('/<uuid(strict=False):id>/delete')
@jwt_required()
def delete_by_id(id):
    """
    Deletes the weights by its id of the current user.

    Parameters:
        `id`: The unique identifier of the weights that the user wants to delete.

    Returns:
        `JSON Response (200)`: The response from the server with the successful `message`.
        
        `JSON Response (404)`: If the weights is not found.
        
        `JSON Response (500)`: If there is an SQLAlchemy error.
    """    
    current_user = get_jwt_identity()
    weight_id = str(id)
    weight = Weights.query.filter_by(user_id=current_user, id=weight_id).first()
    if not weight:
        return jsonify({'message': 'No weights found.'}), HTTP_404_NOT_FOUND
    
    files = Files.query.filter_by(id=str(id)).all()
    for file in files:
        db.session.delete(file)
    
    try:
        db.session.delete(weight)
        db.session.commit()
        return jsonify({'message': 'Weights successfully deleted'}), HTTP_200_OK
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e.orig)}), HTTP_500_INTERNAL_SERVER_ERROR