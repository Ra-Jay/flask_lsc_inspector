from flask_restx import fields
from ..extensions import api 

weights_model = api.model("Weights", {
    "id": fields.Integer,
    "url": fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
})

weights_input_model = api.model("WeightsInput", {
    "name": fields.String,
    'url': fields.String
})