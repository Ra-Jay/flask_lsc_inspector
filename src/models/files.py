from ..extensions import db
from datetime import datetime


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(50), unique=True, nullable=False)
    dimension=db.Column(db.String(50), nullable=True)
    size=db.Column(db.String(50), nullable=True)
    url=db.Column(db.Text, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())

    # user = db.relationship('Users', backref='files', foreign_keys=[user_id])

    # def __repr__(self) -> str:
    #     return f'File>> {self.name}'
        