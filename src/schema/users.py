from flask_restx import fields
from ..extensions import api 

users_model = api.model("Users", {
    "id": fields.Integer,
    "username": fields.String,
    'email': fields.String,
    'password': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
})

user_input_model = api.model("UserInput", {
    "username": fields.String,
    'email': fields.String,
    'password': fields.String
})

user_login_input_model = api.model("UserLoginInput", {
    'email': fields.String,
    'password': fields.String
})