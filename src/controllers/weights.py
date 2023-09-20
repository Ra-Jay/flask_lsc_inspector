import os
import time
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from src.helpers.supabase_utils import upload_file_to_bucket, download_file_from_bucket, get_file_url_by_name, get_all_files_from_bucket, delete_file_by_name
import validators   
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required


weights = Blueprint("weights", __name__, url_prefix="/api/v1/weights")

WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights')

@weights.route('/upload', methods=['POST', 'GET'])
@jwt_required()
def upload_weights():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No weights file found.'}), HTTP_400_BAD_REQUEST
        
        uploaded_weights = request.files['weights']
        
        uploaded_weights_name = secure_filename(uploaded_weights.filename)
        
        print("===============================")
        print("Uploading " + uploaded_weights_name + " weights to the supabase bucket")
        start_time = time()
        
        response = upload_file_to_bucket('weights', uploaded_weights)
        
        print("===============================")
        elapsed_time = time() - start_time
        
        if response is HTTP_200_OK:
            print(f"Successfully uploaded the {uploaded_weights_name} weights to the supabase bucket in {elapsed_time:.2f} seconds")
            
            url = get_file_url_by_name(uploaded_weights_name)
            
            if url is None:
                return jsonify({'error': 'Failed to get the url of the uploaded weights.'}), HTTP_404_NOT_FOUND
        
            session['uploaded_custom_weights_url'] = url
            
            weight = Weights(name=uploaded_weights_name, url=url, user_id=current_user)
            db.session.add(weight)
            db.session.commit()

            return jsonify({
                'id': weight.id,
                'name': weight.name,
                'url': weight.url,
                'created_at': weight.created_at,
                'udpated_at': weight.updated_at
            }), HTTP_201_CREATED
            
        elif response is HTTP_400_BAD_REQUEST:
            print("The weights " + uploaded_weights_name + " was not found. Failed to upload to the supabase bucket")
            return jsonify({'error': "The weights " + uploaded_weights_name + " was not found. Failed upload to the supabase bucket"}), HTTP_400_BAD_REQUEST
        elif response is HTTP_409_CONFLICT:
            print("The weights " + uploaded_weights_name + " already exists in the supabase bucket")
            return jsonify({'error': "The weights " + uploaded_weights_name + " already exists in the supabase bucket"}), HTTP_409_CONFLICT
        else:
            print("Internal server error either in supabase or weights controller.")
            return jsonify({'error': "Internal server error either in supabase or weights controller."}), HTTP_500_INTERNAL_SERVER_ERROR

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
            'name': weight.name,
            'url': weight.url,
            'created_at': weight.created_at,
            'updated_at': weight.updated_at
        })

    return jsonify({'data': data}), HTTP_200_OK

@weights.get('/<int:id>')
@jwt_required()
def get_weight(id):
    current_user = get_jwt_identity()

    weight = Weights.query.filter_by(user_id=current_user, id=id).first()

    if not weights:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
            'id': weight.id,
            'name': weight.name,
            'url': weight.url,
            'created_at': weight.created_at,
            'updated_at': weight.updated_at
        }), HTTP_200_OK


@weights.delete('/<int:id>')
@jwt_required()
def delete_weight(id):
    current_user = get_jwt_identity()

    weight = Weights.query.filter_by(user_id=current_user, id=id).first()

    if not weight:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(weight)
    db.session.commit()

    return jsonify({'message': 'Item successfully deleted'}), HTTP_200_OK