from extensions import db
from datetime import datetime

class Files(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    user_id=db.Column(db.String(50), db.ForeignKey('users.id'))
    weight_id=db.Column(db.String(50), db.ForeignKey('weights.id'))
    name = db.Column(db.String(50), unique=False, nullable=False)
    dimensions=db.Column(db.String(50), nullable=True)
    size=db.Column(db.String(50), nullable=True)
    classification=db.Column(db.String(50), nullable=True)
    accuracy=db.Column(db.String(50), nullable=True)
    error_rate=db.Column(db.String(50), nullable=True)
    url=db.Column(db.Text, nullable=True)
    created_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
        