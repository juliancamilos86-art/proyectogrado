"""
Rutas principales de la API NutriChat
VERSIÓN SIMPLIFICADA - Solo funciones esenciales
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.controllers.user_controller import UserController
from app.models.user import User
from app.models.database import db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para la API
api_bp = Blueprint('api', __name__)

# ============================================================
# ENDPOINTS PÚBLICOS (Sin autenticación)
# ============================================================

@api_bp.route('/status', methods=['GET'])
def status():
    """Verificar estado de la API"""
    return jsonify({
        'success': True,
        'message': 'API NutriChat funcionando correctamente',
        'version': '1.0.0'
    }), 200


@api_bp.route('/info', methods=['GET'])
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
# AUTENTICACIÓN
# ============================================================

@api_bp.route('/users/register', methods=['POST'])
def register_user():
    """
    Registrar nuevo usuario
    
    Body JSON:
    {
        "telegram_id": 123456789,  // REQUERIDO
        "nombre": "Juan Pérez",    // OPCIONAL
        "email": "juan@email.com", // OPCIONAL
        "telefono": "+52123456789", // OPCIONAL
        "sexo": "M",               // OPCIONAL
        "fecha_nacimiento": "1990-01-15", // OPCIONAL
        "peso_kg": 70.5,          // OPCIONAL
        "altura_cm": 175.0        // OPCIONAL
    }
    """
    return UserController.register()


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Login con Telegram ID (sin contraseña)
    
    Body JSON:
    {
        "telegram_id": 123456789
    }
    
    Response:
    {
        "success": true,
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {...}
    }
    """
    return UserController.login()


# ============================================================
# ENDPOINTS PROTEGIDOS (Requieren autenticación JWT)
# ============================================================

@api_bp.route('/users/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    Obtener perfil del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    """
    return UserController.get_profile()


@api_bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    Actualizar perfil del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON (todos opcionales):
    {
        "nombre": "Juan Carlos",
        "email": "nuevo@email.com",
        "telefono": "+52987654321",
        "sexo": "M",
        "fecha_nacimiento": "1990-01-15",
        "peso_kg": 75.0,
        "altura_cm": 180.0,
        "nutritional_preferences": {
            "diet_type": "vegetariana",
            "allergies": ["lactosa"],
            "goal": "bajar_peso"
        },
        "budget_monthly": 5000,
        "budget_weekly": 1200
    }
    """
    return UserController.update_profile()


# ============================================================
# BÚSQUEDA DE USUARIOS (Para integración con bot/N8N)
# ============================================================

@api_bp.route('/users/telegram/<int:telegram_id>', methods=['GET'])
def get_user_by_telegram_id(telegram_id):
    """
    Buscar usuario por Telegram ID
    
    Útil para que N8N verifique si un usuario existe
    
    Parámetros:
    - telegram_id: ID de Telegram del usuario
    
    Response:
    {
        "success": true,
        "user": {...}
    }
    """
    return UserController.get_user_by_telegram_id(telegram_id)


@api_bp.route('/users/search/email', methods=['POST'])
def search_user_by_email():
    """
    Buscar usuario por email
    
    Body JSON:
    {
        "email": "usuario@ejemplo.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email es requerido'
            }), 400
        
        user = User.get_by_email(data['email'])
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_json_safe()
        }), 200
        
    except Exception as e:
        logger.error(f"Error buscando usuario por email: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


# ============================================================
# GESTIÓN DE PREFERENCIAS NUTRICIONALES
# ============================================================

@api_bp.route('/users/profile/nutrition', methods=['PUT'])
@jwt_required()
def update_nutritional_preferences():
    """
    Actualizar preferencias nutricionales
    
    Body JSON:
    {
        "nutritional_preferences": {
            "diet_type": "vegetariana",
            "allergies": ["lactosa", "gluten"],
            "dislikes": ["brócoli"],
            "goal": "bajar_peso"
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data or 'nutritional_preferences' not in data:
            return jsonify({
                'success': False,
                'message': 'nutritional_preferences es requerido'
            }), 400
        
        user.set_nutritional_preferences(data['nutritional_preferences'])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferencias nutricionales actualizadas',
            'nutritional_preferences': user.get_nutritional_preferences()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando preferencias: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


@api_bp.route('/users/profile/budget', methods=['PUT'])
@jwt_required()
def update_budget():
    """
    Actualizar presupuesto
    
    Body JSON:
    {
        "budget_monthly": 5000,
        "budget_weekly": 1200
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos requeridos'
            }), 400
        
        user.set_budget(
            monthly=data.get('budget_monthly'),
            weekly=data.get('budget_weekly')
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Presupuesto actualizado',
            'budget': {
                'monthly': float(user.budget_monthly) if user.budget_monthly else None,
                'weekly': float(user.budget_weekly) if user.budget_weekly else None
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando presupuesto: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor'
        }), 500


# ============================================================
# WEBHOOK PARA N8N/TELEGRAM
# ============================================================

@api_bp.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """
    Webhook para recibir mensajes de Telegram vía N8N
    
    Body JSON (ejemplo de lo que N8N enviará):
    {
        "telegram_id": 123456789,
        "message": "Texto del mensaje",
        "first_name": "Juan",
        "username": "juanperez"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos JSON requeridos'
            }), 400
        
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({
                'success': False,
                'message': 'telegram_id es requerido'
            }), 400
        
        # Buscar o crear usuario
        user = User.get_by_telegram_id(telegram_id)
        
        if not user:
            # Auto-registrar usuario desde Telegram
            user = User.create_user(
                telegram_id=telegram_id,
                nombre=data.get('first_name')
            )
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Usuario auto-registrado desde Telegram: {telegram_id}")
        
        # Actualizar última conexión
        user.update_last_connection()
        
        return jsonify({
            'success': True,
            'message': 'Webhook procesado',
            'user': user.to_json_safe(),
            'new_user': user.fecha_registro == user.ultima_conexion
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en webhook de Telegram: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error procesando webhook'
        }), 500


# ============================================================
# MANEJADORES DE ERRORES
# ============================================================

@api_bp.errorhandler(404)
def not_found(error):
    """Endpoint no encontrado"""
    return jsonify({
        'success': False,
        'message': 'Endpoint no encontrado',
        'error': 'NOT_FOUND'
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Método HTTP no permitido"""
    return jsonify({
        'success': False,
        'message': 'Método no permitido',
        'error': 'METHOD_NOT_ALLOWED'
    }), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """Error interno del servidor"""
    logger.error(f"Error interno: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor',
        'error': 'INTERNAL_SERVER_ERROR'
    }), 500


@api_bp.errorhandler(401)
def unauthorized(error):
    """No autorizado"""
    return jsonify({
        'success': False,
        'message': 'Autenticación requerida',
        'error': 'UNAUTHORIZED'
    }), 401


@api_bp.errorhandler(403)
def forbidden(error):
    """Acceso prohibido"""
    return jsonify({
        'success': False,
        'message': 'Acceso prohibido',
        'error': 'FORBIDDEN'
    }), 403