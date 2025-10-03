import os
from flask import Flask
from flask_jwt_extended import JWTManager
from .config import config
from .models.database import db

def create_app(config_name=None):
    """Application Factory Pattern para Flask"""
    app = Flask(__name__)
    
    # Determinar configuración
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)


    # Registrar blueprints
    from .api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app
