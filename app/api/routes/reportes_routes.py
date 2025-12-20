"""
Rutas de reportes y feedback
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.api.controllers.reportes_controller import ReportesController

# Crear blueprint para rutas de reportes
reportes_bp = Blueprint('reportes', __name__)


# ============================================================
# REPORTES Y FEEDBACK
# ============================================================

@reportes_bp.route('/reportes', methods=['POST'])
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


@reportes_bp.route('/reportes/usuario', methods=['GET'])
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


@reportes_bp.route('/reportes/tipo/<tipo>', methods=['GET'])
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


@reportes_bp.route('/reportes/sistema', methods=['GET'])
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


@reportes_bp.route('/reportes/<reporte_id>', methods=['GET'])
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


@reportes_bp.route('/feedback', methods=['POST'])
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


@reportes_bp.route('/feedback/usuario', methods=['GET'])
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


@reportes_bp.route('/feedback/lista/<lista_id>', methods=['GET'])
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


@reportes_bp.route('/feedback/aceptadas', methods=['GET'])
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


@reportes_bp.route('/feedback/rechazadas', methods=['GET'])
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


@reportes_bp.route('/feedback/<feedback_id>', methods=['GET'])
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


