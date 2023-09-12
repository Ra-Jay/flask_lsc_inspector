from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators   
from src.models.weights import Weights
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required


weights = Blueprint("weights", __name__, url_prefix="/api/v1/weights")

@weights.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_weights():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        name = request.get_json().get('name', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'enter a valid url.'}), HTTP_400_BAD_REQUEST
        
        if Weights.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already exists.'}), HTTP_409_CONFLICT

        if Weights.query.filter_by(name=name).first():
            return jsonify({'error': 'Name already exists.'}), HTTP_409_CONFLICT

        weight = Weights(name=name, url=url, user_id=current_user)
        db.session.add(weight)
        db.session.commit()

        return jsonify({
            'id': weight.id,
            'name': weight.name,
            'url': weight.name,
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
                'ur': weight.url,
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