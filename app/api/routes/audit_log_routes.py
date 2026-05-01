"""
Rutas de logs de auditoría: registro y consulta de eventos del sistema
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.api.controllers.audit_log_controller import AuditLogController

# Crear blueprint para rutas de audit log
audit_log_bp = Blueprint('audit_log', __name__)


# ============================================================
# LOGS DE AUDITORÍA
# ============================================================

@audit_log_bp.route('/audit/log', methods=['POST'])
#@jwt_required()
def create_log():
    """
    Crear un nuevo registro de auditoría
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "entidad": "Usuario",           // REQUERIDO
        "accion": "CREATE",            // REQUERIDO
        "entidad_id": "uuid",          // OPCIONAL
        "usuario_id": "uuid",          // OPCIONAL
        "payload": {...}               // OPCIONAL
    }
    
    Response:
    {
        "success": true,
        "message": "Log de auditoría creado exitosamente",
        "data": {...}
    }
    """
    return AuditLogController.create_log()


@audit_log_bp.route('/audit/log/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log_by_id(log_id):
    """
    Obtener log de auditoría por ID
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - log_id: ID del log
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return AuditLogController.get_log_by_id(log_id)


@audit_log_bp.route('/audit/logs/entidad', methods=['GET'])
@jwt_required()
def get_logs_by_entidad():
    """
    Obtener logs por entidad
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query params:
    - entidad: Nombre de la entidad (requerido)
    - limit: Número máximo de resultados (opcional, default: sin límite)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 15
    }
    """
    return AuditLogController.get_logs_by_entidad()


@audit_log_bp.route('/audit/logs/entidad-id', methods=['GET'])
@jwt_required()
def get_logs_by_entidad_id():
    """
    Obtener logs por entidad e ID
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query params:
    - entidad: Nombre de la entidad (requerido)
    - entidad_id: ID de la entidad (requerido)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return AuditLogController.get_logs_by_entidad_id()


@audit_log_bp.route('/audit/logs/usuario', methods=['GET'])
@jwt_required()
def get_logs_by_usuario():
    """
    Obtener logs por usuario
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query params:
    - usuario_id: ID del usuario (opcional, si no se proporciona usa el autenticado)
    - limit: Número máximo de resultados (opcional, default: sin límite)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return AuditLogController.get_logs_by_usuario()


@audit_log_bp.route('/audit/logs/accion', methods=['GET'])
@jwt_required()
def get_logs_by_accion():
    """
    Obtener logs por acción
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query params:
    - accion: Nombre de la acción (requerido)
    - limit: Número máximo de resultados (opcional, default: sin límite)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 8
    }
    """
    return AuditLogController.get_logs_by_accion()


@audit_log_bp.route('/audit/logs/recent', methods=['GET'])
@jwt_required()
def get_recent_logs():
    """
    Obtener logs recientes
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query params:
    - limit: Número máximo de resultados (opcional, default: 100, máximo: 1000)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 100
    }
    """
    return AuditLogController.get_recent_logs()

