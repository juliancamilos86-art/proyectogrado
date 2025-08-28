"""
Modelos de datos para NutriChat

Este módulo expone todos los modelos de la aplicación para facilitar
las importaciones desde otras partes del código.
"""

from .database import db
from .user import User

# Exportar todos los modelos principales
__all__ = [
    'db',
    'User',
]
