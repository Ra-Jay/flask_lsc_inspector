import os
import time
from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import validators   
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required


weights = Blueprint("weights", __name__, url_prefix="/api/v1/weights")

WEIGHTS_FOLDER = os.path.join('src', 'static', 'pre-trained_weights')

@weights.route('/', methods=['POST', 'GET'])
@jwt_required()
def upload_weights():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No weights file found.'}), HTTP_400_BAD_REQUEST
        
        uploaded_weights = request.files['file']
        
        uploaded_weights_name = secure_filename(uploaded_weights.filename)
        
        print("===============================")
        print("Uploading " + uploaded_weights_name)
        start_time = time()

        if not os.path.exists(WEIGHTS_FOLDER):
            print("===============================")
            print("Creating " + WEIGHTS_FOLDER + " folder")
            os.makedirs(WEIGHTS_FOLDER)
            
        path = os.path.join(WEIGHTS_FOLDER, uploaded_weights_name)
            
        uploaded_weights.save(path)
        session['uploaded_file'] = path
        
        elapsed_time = time() - start_time 
        print("===============================")
        print(f"New weights saved locally at {path} folder in {elapsed_time:.2f} seconds")
            
        name = request.get_json().get('name', '')
        url = request.get_json().get('url', '')
        
        # TODO: Generate URL to upload the weights to the cloud.

        if not validators.url(url):
            return jsonify({'error': 'enter a valid url.'}), HTTP_400_BAD_REQUEST
        
        if Weights.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already exists.'}), HTTP_409_CONFLICT

        if Weights.query.filter_by(name=uploaded_weights_name).first():
            return jsonify({'error': 'Name already exists.'}), HTTP_409_CONFLICT

        weight = Weights(name=uploaded_weights_name, url=url, user_id=current_user)
        db.session.add(weight)
        db.session.commit()
        
        # TODO: Download/Preview the existing file through its URL and return it.
        # (Assuming the file can be previewed using its URL)
        return jsonify({
            'id': weight.id,
            'name': weight.name,
            'url': weight.url,
            'created_at': weight.created_at,
            'udpated_at': weight.updated_at
        }), HTTP_201_CREATED

    else:
        weights = Weights.query.filter_by(user_id=current_user)

        data=[]

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