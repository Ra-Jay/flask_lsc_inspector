from ..extensions import db
from .weights import Weights
from .files import Files
from datetime import datetime

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email=db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.Text(), nullable=False)
    # weight_id=db.Column(db.Integer, db.ForeignKey("weights.id"))
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
    
    # weights=db.relationship('Weights', backref='users', uselist = False)
    # files=db.relationship('Files', backref='users')

        
    # def __repr__(self) -> str:
    #     return `user>> {self.username}`
