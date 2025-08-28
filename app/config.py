import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # carga variables del archivo .env

class Config:
    # Configuración Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    
    # Configuración Base de Datos
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/nutrichat_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Configuración JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30)))
    
    # Configuración Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = "development"

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = "production"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Forzar el uso de JSON estándar para SQLite
    USE_POSTGRESQL_JSONB = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
