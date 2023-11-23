from ..extensions import db
from datetime import datetime

class Weights(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    user_id=db.Column(db.String(50), db.ForeignKey('users.id'))
    workspace=db.Column(db.String(50), nullable=True)
    project_name = db.Column(db.String(50), nullable=False)
    api_key=db.Column(db.String(50),unique=False, nullable=False)
    version=db.Column(db.Integer, nullable=True)
    model_type=db.Column(db.String(50), nullable=True)
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
    type=db.Column(db.String(50), nullable=False)
        