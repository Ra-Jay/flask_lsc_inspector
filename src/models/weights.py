from ..extensions import db
from datetime import datetime


class Weights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(50), unique=True, nullable=False)
    url=db.Column(db.Text, nullable=False)
    trained_at=db.Column(db.DateTime, nullable=True)
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())

    # user = db.relationship('Users', backref='weights')

    # def __repr__(self) -> str:
    #     return `Weights>> {self.id}`
        