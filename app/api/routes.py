"""
Rutas principales de la API NutriChat
VERSIÓN SIMPLIFICADA - Solo funciones esenciales
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.controllers.user_controller import UserController
from app.api.controllers.telegram_sesion_controller import TelegramSesionController
from app.api.controllers.scraping_cache_controller import ScrapingCacheController
from app.api.controllers.reportes_controller import ReportesController
from app.api.controllers.productos_controller import ProductosController
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
# TELEGRAM SESIONES (Webhook / Bot)
# ============================================================

@api_bp.route('/telegram/sesion', methods=['POST'])
def get_or_create_sesion():
    """
    Obtener o crear sesión activa (UPSERT lógico)
    
    Body JSON:
    {
        "telegram_id": 123456789  // REQUERIDO
    }
    
    Response:
    {
        "success": true,
        "message": "Sesión obtenida/creada exitosamente",
        "data": {...}
    }
    """
    return TelegramSesionController.get_or_create_sesion()


@api_bp.route('/telegram/sesion/estado', methods=['PUT'])
def update_estado():
    """
    Actualizar estado de conversación
    
    Body JSON:
    {
        "telegram_id": 123456789,  // REQUERIDO
        "estado_conversacion": "esperando_presupuesto"  // REQUERIDO
    }
    
    Response:
    {
        "success": true,
        "message": "Estado actualizado exitosamente",
        "data": {...}
    }
    """
    return TelegramSesionController.update_estado()


@api_bp.route('/telegram/sesion/contexto', methods=['PUT'])
def update_contexto():
    """
    Actualizar contexto conversacional (JSONB)
    
    Body JSON:
    {
        "telegram_id": 123456789,  // REQUERIDO
        "contexto": {              // REQUERIDO
            "paso": 2,
            "categoria": "verduras"
        }
    }
    
    Response:
    {
        "success": true,
        "message": "Contexto actualizado exitosamente",
        "data": {...}
    }
    """
    return TelegramSesionController.update_contexto()


@api_bp.route('/telegram/sesion', methods=['DELETE'])
def clear_sesion():
    """
    Limpiar sesión (reset conversacional)
    
    Body JSON:
    {
        "telegram_id": 123456789  // REQUERIDO
    }
    
    Response:
    {
        "success": true,
        "message": "Sesión limpiada exitosamente",
        "data": {...}
    }
    """
    return TelegramSesionController.clear_sesion()


@api_bp.route('/telegram/sesion/<int:telegram_id>', methods=['GET'])
def get_sesion_by_telegram_id(telegram_id):
    """
    Obtener sesión por Telegram ID (uso N8N)
    
    Parámetros:
    - telegram_id: ID de Telegram del usuario
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return TelegramSesionController.get_sesion_by_telegram_id(telegram_id)


# ============================================================
# SCRAPING CACHE (Uso interno del scraper)
# ============================================================

@api_bp.route('/scraping/cache', methods=['POST'])
def get_or_create_cache():
    """
    Obtener o crear cache (UPSERT por URL)
    
    Body JSON:
    {
        "url": "https://ejemplo.com",  // REQUERIDO
        "html_content": "<html>...",  // OPCIONAL
        "headers": {...},             // OPCIONAL
        "status_code": 200,           // OPCIONAL
        "valido_hasta": "2024-12-31T23:59:59Z"  // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Cache obtenido/creado exitosamente",
        "data": {...}
    }
    """
    return ScrapingCacheController.get_or_create_cache()


@api_bp.route('/scraping/cache/url/<path:url>', methods=['GET'])
def get_cache_by_url(url):
    """
    Obtener cache por URL
    
    Parámetros:
    - url: URL del cache (codificada en la ruta)
    
    Query params:
    - include_html: true/false (por defecto false)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ScrapingCacheController.get_cache_by_url(url)


@api_bp.route('/scraping/cache/valid', methods=['POST'])
def get_valid_cache_by_url():
    """
    Obtener cache válido por URL
    
    Body JSON:
    {
        "url": "https://ejemplo.com"  // REQUERIDO
    }
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ScrapingCacheController.get_valid_cache_by_url()


@api_bp.route('/scraping/cache/expired', methods=['GET'])
def get_expired_caches():
    """
    Obtener caches expirados
    
    Query params:
    - limit: número máximo de resultados (por defecto sin límite)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ScrapingCacheController.get_expired_caches()


@api_bp.route('/scraping/cache/expired', methods=['DELETE'])
def delete_expired_caches():
    """
    Eliminar caches expirados
    
    Body JSON (opcional):
    {
        "limit": 100  // OPCIONAL: límite de eliminaciones
    }
    
    Response:
    {
        "success": true,
        "message": "Caches expirados eliminados",
        "deleted_count": 5
    }
    """
    return ScrapingCacheController.delete_expired_caches()


@api_bp.route('/scraping/cache/recent', methods=['GET'])
def get_recent_caches():
    """
    Obtener caches recientes
    
    Query params:
    - limit: número máximo de resultados (por defecto 100, máximo 1000)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return ScrapingCacheController.get_recent_caches()


@api_bp.route('/scraping/cache/status/<int:status_code>', methods=['GET'])
def get_caches_by_status_code(status_code):
    """
    Obtener caches por código de estado HTTP
    
    Parámetros:
    - status_code: Código de estado HTTP (200, 404, 500, etc.)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 3
    }
    """
    return ScrapingCacheController.get_caches_by_status_code(status_code)


# ============================================================
# REPORTES Y FEEDBACK
# ============================================================

@api_bp.route('/reportes', methods=['POST'])
@jwt_required()
def create_reporte():
    """
    Crear un nuevo reporte
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "tipo": "nutricional",  // OPCIONAL
        "parametros": {...},   // OPCIONAL
        "contenido": {...},    // OPCIONAL
        "enlace_archivo": "https://..."  // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Reporte creado exitosamente",
        "data": {...}
    }
    """
    return ReportesController.create_reporte()


@api_bp.route('/reportes/usuario', methods=['GET'])
@jwt_required()
def get_reportes_by_usuario():
    """
    Obtener reportes del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ReportesController.get_reportes_by_usuario()


@api_bp.route('/reportes/tipo/<tipo>', methods=['GET'])
def get_reportes_by_tipo(tipo):
    """
    Obtener reportes por tipo
    
    Parámetros:
    - tipo: Tipo de reporte
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 3
    }
    """
    return ReportesController.get_reportes_by_tipo(tipo)


@api_bp.route('/reportes/sistema', methods=['GET'])
def get_system_reportes():
    """
    Obtener reportes del sistema (sin usuario_id)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return ReportesController.get_system_reportes()


@api_bp.route('/reportes/<reporte_id>', methods=['GET'])
def get_reporte_by_id(reporte_id):
    """
    Obtener reporte por ID
    
    Parámetros:
    - reporte_id: ID del reporte (UUID)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ReportesController.get_reporte_by_id(reporte_id)


@api_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_feedback():
    """
    Crear un nuevo feedback de recomendación
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "lista_id": "uuid-de-lista",  // REQUERIDO
        "aceptada": true,             // OPCIONAL
        "comentarios": "Texto..."     // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Feedback creado exitosamente",
        "data": {...}
    }
    """
    return ReportesController.create_feedback()


@api_bp.route('/feedback/usuario', methods=['GET'])
@jwt_required()
def get_feedback_by_usuario():
    """
    Obtener feedback del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 8
    }
    """
    return ReportesController.get_feedback_by_usuario()


@api_bp.route('/feedback/lista/<lista_id>', methods=['GET'])
def get_feedback_by_lista(lista_id):
    """
    Obtener feedback por lista
    
    Parámetros:
    - lista_id: ID de la lista (UUID)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 2
    }
    """
    return ReportesController.get_feedback_by_lista(lista_id)


@api_bp.route('/feedback/aceptadas', methods=['GET'])
@jwt_required()
def get_feedback_aceptadas():
    """
    Obtener feedback aceptados del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ReportesController.get_feedback_aceptadas()


@api_bp.route('/feedback/rechazadas', methods=['GET'])
@jwt_required()
def get_feedback_rechazadas():
    """
    Obtener feedback rechazados del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 2
    }
    """
    return ReportesController.get_feedback_rechazadas()


@api_bp.route('/feedback/<feedback_id>', methods=['GET'])
def get_feedback_by_id(feedback_id):
    """
    Obtener feedback por ID
    
    Parámetros:
    - feedback_id: ID del feedback
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ReportesController.get_feedback_by_id(feedback_id)


# ============================================================
# PRODUCTOS Y CATEGORIAS
# ============================================================

@api_bp.route('/categorias', methods=['POST'])
def create_categoria():
    """
    Crear una nueva categoría
    
    Body JSON:
    {
        "nombre": "Verduras",      // REQUERIDO
        "descripcion": "..."      // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Categoría creada exitosamente",
        "data": {...}
    }
    """
    return ProductosController.create_categoria()


@api_bp.route('/categorias', methods=['GET'])
def get_all_categorias():
    """
    Obtener todas las categorías
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return ProductosController.get_all_categorias()


@api_bp.route('/categorias/<int:categoria_id>', methods=['GET'])
def get_categoria_by_id(categoria_id):
    """
    Obtener categoría por ID
    
    Parámetros:
    - categoria_id: ID de la categoría
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ProductosController.get_categoria_by_id(categoria_id)


@api_bp.route('/productos', methods=['POST'])
def create_producto():
    """
    Crear un nuevo producto
    
    Body JSON:
    {
        "nombre": "Tomate",           // REQUERIDO
        "marca": "Marca X",          // OPCIONAL
        "categoria_id": 1,          // OPCIONAL
        "descripcion": "...",        // OPCIONAL
        "url_producto": "...",       // OPCIONAL
        "url_imagen": "...",         // OPCIONAL
        "codigo_fuente": "...",      // OPCIONAL
        "producto_hash": "..."       // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Producto creado exitosamente",
        "data": {...}
    }
    """
    return ProductosController.create_producto()


@api_bp.route('/productos/<producto_id>', methods=['GET'])
def get_producto_by_id(producto_id):
    """
    Obtener producto por ID
    
    Parámetros:
    - producto_id: ID del producto (UUID)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ProductosController.get_producto_by_id(producto_id)


@api_bp.route('/productos/<producto_id>', methods=['PUT'])
@jwt_required()
def update_producto(producto_id):
    """
    Actualizar producto
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - producto_id: ID del producto (UUID)
    
    Body JSON (todos opcionales):
    {
        "nombre": "...",
        "marca": "...",
        "categoria_id": 1,
        "descripcion": "...",
        "url_producto": "...",
        "url_imagen": "..."
    }
    
    Response:
    {
        "success": true,
        "message": "Producto actualizado exitosamente",
        "data": {...}
    }
    """
    return ProductosController.update_producto(producto_id)


@api_bp.route('/productos/search', methods=['GET'])
def search_productos_by_nombre():
    """
    Buscar productos por nombre (búsqueda parcial)
    
    Query params:
    - nombre: Nombre a buscar (requerido)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ProductosController.search_productos_by_nombre()


@api_bp.route('/productos/categoria/<int:categoria_id>', methods=['GET'])
def get_productos_by_categoria(categoria_id):
    """
    Obtener productos por categoría
    
    Parámetros:
    - categoria_id: ID de la categoría
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 15
    }
    """
    return ProductosController.get_productos_by_categoria(categoria_id)


@api_bp.route('/productos/hash', methods=['GET'])
def get_producto_by_hash():
    """
    Obtener producto por hash
    
    Query params:
    - hash: Hash del producto (requerido)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ProductosController.get_producto_by_hash()


@api_bp.route('/productos/nutricion', methods=['POST'])
def create_nutricion():
    """
    Crear información nutricional para un producto
    
    Body JSON:
    {
        "producto_id": "uuid",          // REQUERIDO
        "porcion_g": 100.0,            // OPCIONAL
        "calorias_kcal": 250.5,        // OPCIONAL
        "proteinas_g": 10.0,           // OPCIONAL
        "grasas_totales_g": 5.0,       // OPCIONAL
        "grasas_saturadas_g": 2.0,     // OPCIONAL
        "carbohidratos_g": 30.0,       // OPCIONAL
        "azucares_g": 15.0,            // OPCIONAL
        "fibra_g": 3.0,                // OPCIONAL
        "sodio_mg": 500.0,             // OPCIONAL
        "colesterol_mg": 0.0,          // OPCIONAL
        "micronutrientes": {...},      // OPCIONAL
        "ig": 50.0,                    // OPCIONAL
        "carga_glucemica": 25.0,       // OPCIONAL
        "fuente": "..."                // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Información nutricional creada exitosamente",
        "data": {...}
    }
    """
    return ProductosController.create_nutricion()


@api_bp.route('/productos/<producto_id>/nutricion', methods=['GET'])
def get_nutricion_by_producto(producto_id):
    """
    Obtener información nutricional por producto
    
    Parámetros:
    - producto_id: ID del producto (UUID)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ProductosController.get_nutricion_by_producto(producto_id)


@api_bp.route('/productos/snapshot', methods=['POST'])
def create_snapshot():
    """
    Crear un snapshot de producto (precio, disponibilidad, etc.)
    
    Body JSON:
    {
        "producto_id": "uuid",         // REQUERIDO
        "precio": 25.50,               // OPCIONAL
        "unidad_medida": "kg",         // OPCIONAL
        "disponibilidad": true,        // OPCIONAL
        "fuente": "...",               // OPCIONAL
        "impacto_ambiental": {...},   // OPCIONAL
        "atributos_json": {...}        // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Snapshot creado exitosamente",
        "data": {...}
    }
    """
    return ProductosController.create_snapshot()


@api_bp.route('/productos/<producto_id>/snapshots', methods=['GET'])
def get_snapshots_by_producto(producto_id):
    """
    Obtener snapshots por producto
    
    Parámetros:
    - producto_id: ID del producto (UUID)
    
    Query params:
    - limit: Número máximo de resultados (opcional)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return ProductosController.get_snapshots_by_producto(producto_id)


@api_bp.route('/productos/<producto_id>/snapshot/latest', methods=['GET'])
def get_latest_snapshot_by_producto(producto_id):
    """
    Obtener el snapshot más reciente de un producto
    
    Parámetros:
    - producto_id: ID del producto (UUID)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return ProductosController.get_latest_snapshot_by_producto(producto_id)


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