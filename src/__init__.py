from flask import Flask
import os
from src.extensions import api, db
from src.controllers.user import auth
from src.controllers.weights import weights
from src.controllers.files import files
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
     
    app = Flask(__name__,
    instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get(  'JWT_SECRET_KEY'),
            SUPABASE_URL=os.environ.get('SUPABASE_URL'),
            SUPABASE_KEY=os.environ.get('SUPABASE_KEY'),
            SUPABASE_BUCKET_FILES=os.environ.get('SUPABASE_BUCKET_FILES'),
            SUPABASE_BUCKET_WEIGHTS=os.environ.get('SUPABASE_BUCKET_WEIGHTS'),
            SUPABASE_BUCKET_PROFILE_IMAGES=os.environ.get('SUPABASE_BUCKET_PROFILE_IMAGES'),
        )

    else: 
        app.config.from_mapping(test_config)

    db.app = app
    api.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(weights)
    app.register_blueprint(files)
        
    return app