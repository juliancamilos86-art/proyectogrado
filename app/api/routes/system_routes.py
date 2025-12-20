"""
Rutas del sistema: endpoints públicos y configuración del sistema
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.api.controllers.configuracion_controller import ConfiguracionController

# Crear blueprint para rutas del sistema
system_bp = Blueprint('system', __name__)


# ============================================================
# ENDPOINTS PÚBLICOS (Sin autenticación)
# ============================================================

@system_bp.route('/status', methods=['GET'])
def status():
    """Verificar estado de la API"""
    return jsonify({
        'success': True,
        'message': 'API NutriChat funcionando correctamente',
        'version': '1.0.0'
    }), 200


@system_bp.route('/info', methods=['GET'])
def get_api_info():
    """Información general de la API"""
    return jsonify({
        'success': True,
        'data': {
            'name': 'NutriChat API',
            'version': '1.0.0',
            'description': 'API para gestión de perfiles nutricionales con Telegram',
            'endpoints': {
                'public': [
                    'POST /api/users/register - Registrar usuario',
                    'POST /api/auth/login - Login con telegram_id',
                    'GET /api/status - Estado de la API'
                ],
                'authenticated': [
                    'GET /api/users/profile - Obtener perfil',
                    'PUT /api/users/profile - Actualizar perfil'
                ]
            }
        }
    }), 200


# ============================================================
# CONFIGURACIÓN DEL SISTEMA
# ============================================================

@system_bp.route('/config', methods=['POST'])
@jwt_required()
def create_config():
    """
    Crear una nueva configuración del sistema
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "clave": "max_productos_lista",  // REQUERIDO
        "valor": {                       // REQUERIDO
            "max": 50,
            "min": 1
        }
    }
    
    Response:
    {
        "success": true,
        "message": "Configuración creada exitosamente",
        "data": {...}
    }
    """
    return ConfiguracionController.create_config()


@system_bp.route('/config', methods=['GET'])
def get_all_configs():
    """
    Obtener todas las configuraciones del sistema
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ConfiguracionController.get_all_configs()


@system_bp.route('/config/<clave>', methods=['GET'])
def get_config_by_clave(clave):
    """
    Obtener configuración por clave
    
    Parámetros:
    - clave: Clave de la configuración
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ConfiguracionController.get_config_by_clave(clave)


@system_bp.route('/config/<clave>/valor', methods=['GET'])
def get_valor_by_clave(clave):
    """
    Obtener solo el valor de una configuración por clave
    
    Parámetros:
    - clave: Clave de la configuración
    
    Query params:
    - default: Valor por defecto si no existe (opcional)
    
    Response:
    {
        "success": true,
        "data": {...}  // Solo el valor, no el objeto completo
    }
    """
    return ConfiguracionController.get_valor_by_clave(clave)


@system_bp.route('/config/<clave>', methods=['PUT'])
@jwt_required()
def update_config(clave):
    """
    Actualizar configuración del sistema
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - clave: Clave de la configuración
    
    Body JSON:
    {
        "valor": {  // REQUERIDO
            "max": 100,
            "min": 1
        }
    }
    
    Response:
    {
        "success": true,
        "message": "Configuración actualizada exitosamente",
        "data": {...}
    }
    """
    return ConfiguracionController.update_config(clave)


@system_bp.route('/config/<clave>/key', methods=['PUT'])
@jwt_required()
def update_config_key(clave):
    """
    Actualizar una clave específica dentro del valor de la configuración
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - clave: Clave de la configuración
    
    Body JSON:
    {
        "key": "max",    // REQUERIDO - clave dentro del valor
        "value": 100    // REQUERIDO - nuevo valor
    }
    
    Response:
    {
        "success": true,
        "message": "Clave de configuración actualizada exitosamente",
        "data": {...}
    }
    """
    return ConfiguracionController.update_config_key(clave)


@system_bp.route('/config/<clave>', methods=['DELETE'])
@jwt_required()
def delete_config(clave):
    """
    Eliminar configuración del sistema
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - clave: Clave de la configuración
    
    Response:
    {
        "success": true,
        "message": "Configuración eliminada exitosamente"
    }
    """
    return ConfiguracionController.delete_config(clave)


