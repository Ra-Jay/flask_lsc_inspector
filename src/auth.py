from flask_restx import Resource, Namespace 
from src.constants.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators   
from src.models.users import Users
from .extensions import db
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from .schema.users import users_model, user_input_model

# auth = Namespace("auth", __name__, url_prefix="/api/v1/auth/")

ns = Namespace("users")

@ns.route("/")
class handle_users(Resource):
    @ns.marshal_list_with(users_model)
    def get(self):
        return Users.query.all()

    @ns.expect(user_input_model)
    @ns.marshal_with(users_model)
    def post(Resource):
        username=request.json['username']
        email=request.json['email']
        password=request.json['password']

        print("User: ")
        if len(password) < 3:
            return {'error': 'Password is too short'}, HTTP_400_BAD_REQUEST

        if len(username) < 6:
            return {'error': 'Username is too short'}, HTTP_400_BAD_REQUEST

        if not username.isalnum() or ' ' in username:
            return {'error': 'Username should be alphanumeric and can contain no spaces'}, HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return {'Error': 'Email is not valid'}, HTTP_400_BAD_REQUEST

        if Users.query.filter_by(email=email).first() is not None:
            abort(409, message="Missing required fields in the request body")

        if Users.query.filter_by(username=username).first() is not None:
            abort(409, message="Missing required fields in the request body")

        pwd_hash = generate_password_hash(password)
        user=Users(username=username, password=pwd_hash, email=email)
        db.session.add(user)
        db.session.commit()

        return user, HTTP_200_OK



# @auth.post('register')
# def register():
#     username=request.json['username']
#     email=request.json['email']
#     password=request.json['password']

#     if len(password) < 3:
#         return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST

#     if len(username) < 6:
#         return jsonify({'error': 'Username is too short'}), HTTP_400_BAD_REQUEST

#     if not username.isalnum() or ' ' in username:
#         return jsonify({'error': 'Username should be alphanumeric and can contain no spaces'}), HTTP_400_BAD_REQUEST

#     if not validators.email(email):
#         return jsonify({'Error': 'Email is not valid'}), HTTP_400_BAD_REQUEST

#     if Users.query.filter_by(email=email).first() is not None:
#         return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

#     if Users.query.filter_by(username=username).first() is not None:
#         return jsonify({'error': "Username is taken"}), HTTP_409_CONFLICT

#     pwd_hash = generate_password_hash(password)

#     user=Users(username=username, password=pwd_hash, email=email)
#     db.session.add(user)
#     db.session.commit()

#     return jsonify({
#         'message': "User created",
#         'user': {
#             'username': username, 
#             'email': email,
#         }

#     }), HTTP_201_CREATED


# @auth.post('/login')
# # @swag_from('./docs/auth/login.yaml')
# def login():
#     email = request.json.get('email', '')
#     password = request.json.get('password', '')

#     user = Users.query.filter_by(email=email).first()

#     if user:
#         is_pass_correct = check_password_hash(user.password, password)

#         if is_pass_correct:
#             refresh = create_refresh_token(identity=user.id)
#             access = create_access_token(identity=user.id)

#             return jsonify({
#                 'user': {
#                     'refresh_token': refresh,
#                     'access_token': access,
#                     'username': user.username,
#                     'email': user.email
#                 }

#             }), HTTP_200_OK

#     return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED



# @auth.get('/user')
# @jwt_required(refresh=True)
# def user(): 
#     user_id = get_jwt_identity()
#     user = User.query.filter_by(id=user_id).first()
#     return jsonify({
#         'username': user.username,
#         'email': user.email
#     }), HTTP_200_OK


# @auth.get('/token/refresh')
# @jwt_required(refresh=True)
# def refresh_users_token():
#     identity = get_jwt_identity()
#     access = create_access_token(identity=identity)

#     return jsonify({
#         'access': access
#     }), HTTP_200_OK
    

# @auth.get('/')
# # @jwt_required()
# def handle_users():
    # users = User.query

    # data=[]

    # for user in users:
    #     data.append({
    #         'id': user.id,
    #         'username': user.username,
    #         'email': user.email,
    #         'created_at': user.created_at,
    #         'updated_at': user.updated_at
    #     })

    # return jsonify({'data': data}), HTTP_200_OK