from flask import Flask
from src.constants.status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.extensions import api, db
from src.controllers.user import auth
from src.controllers.weights import weights
from src.controllers.files import files
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os

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
            ROBOFLOW_API_KEY=os.environ.get('ROBOFLOW_API_KEY'),
            ROBOFLOW_PROJECT=os.environ.get('ROBOFLOW_PROJECT'),
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

    SWAGGER_URL = '/swagger'
    API_URL = '../static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  
        API_URL,
        config={  
            'app_name': "LSC-Inspector Application"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    CORS(app)
        
    # @app.errorhandler(HTTP_404_NOT_FOUND)
    # def handle_404(e):
    #     return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    # @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    # def handle_500(e):
    #     return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERRORs
    return app
