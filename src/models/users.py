from ..extensions import db
from .weights import Weights
from .files import Files
from datetime import datetime

class Users(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.Text(), nullable=False)
    email=db.Column(db.String(50), unique=True, nullable=False)
    profile_image=db.Column(db.Text, nullable=True)
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
    
    # weights=db.relationship('Weights', backref='users', uselist = False)
    # files=db.relationship('Files', backref='users')

        
    # def __repr__(self) -> str:
    #     return `user>> {self.username}`
