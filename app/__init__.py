import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
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
    CORS(app)

    # ===== HEADERS DE SEGURIDAD HTTP =====
    @app.after_request
    def add_security_headers(response):
        # Prevenir MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Prevenir clickjacking (ataques UI)
        response.headers['X-Frame-Options'] = 'DENY'
        # Protección XSS básica
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Control de caché (evita información sensible en caché)
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        # Política de referer
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Forzar HTTPS solo en producción
        if app.config.get('ENABLE_SECURITY_HEADERS', False):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Registrar blueprints
    from .api.routes import register_routes
    register_routes(app)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    return app