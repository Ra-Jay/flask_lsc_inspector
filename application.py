from flask import Flask
from extensions import api, db
from src.controllers.user import users
from src.controllers.weights import weights
from src.controllers.files import files
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from os import environ, urandom

def create_app(*args, **kwargs):
    test_config = kwargs.get('test_config')
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=urandom(24).hex(),
            SQLALCHEMY_DATABASE_URI=environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=environ.get(  'JWT_SECRET_KEY'),
            SUPABASE_URL=environ.get('SUPABASE_URL'),
            SUPABASE_KEY=environ.get('SUPABASE_KEY'),
            SUPABASE_BUCKET_FILES=environ.get('SUPABASE_BUCKET_FILES'),
            SUPABASE_BUCKET_WEIGHTS=environ.get('SUPABASE_BUCKET_WEIGHTS'),
            SUPABASE_BUCKET_PROFILE_IMAGES=environ.get('SUPABASE_BUCKET_PROFILE_IMAGES'),
            ROBOFLOW_API_KEY=environ.get('ROBOFLOW_API_KEY'),
            ROBOFLOW_PROJECT=environ.get('ROBOFLOW_PROJECT'),
        )
    else: 
        app.config.from_mapping(test_config)

    try:
        db.app = app
        api.init_app(app)
        db.init_app(app)
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(e)

    JWTManager(app)
    app.register_blueprint(users)
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
    return app

def serve():
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
    
    
if __name__ == '__main__':
    serve()
