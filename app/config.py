import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # carga variables del archivo .env

class Config:
    # ===== SECRETS - SIN VALORES HARCODEADOS =====
    # Ya NO hay "dev_secret_key" como fallback inseguro
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Fallback SEGURO: generar clave aleatoria en lugar de hardcodear
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)
        print("⚠️ ADVERTENCIA: SECRET_KEY generada automáticamente. Configurar variable de entorno en producción!")

    if not JWT_SECRET_KEY:
        JWT_SECRET_KEY = secrets.token_hex(32)
        print("⚠️ ADVERTENCIA: JWT_SECRET_KEY generada automáticamente. Configurar variable de entorno en producción!")

    # Configuración Base de Datos
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/nutrichat_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Configuración JWT
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

    @classmethod
    def validate(cls):
        """Verifica que TODAS las variables críticas estén definidas en producción"""
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            raise ValueError(
                f"❌ ERROR CRÍTICO: Variables de entorno faltantes: {', '.join(missing)}\n"
                f"El servidor no puede iniciar sin estas configuraciones."
            )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    USE_POSTGRESQL_JSONB = False
    # En testing, generamos claves aleatorias para no depender de .env
    SECRET_KEY = secrets.token_hex(32)
    JWT_SECRET_KEY = secrets.token_hex(32)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}