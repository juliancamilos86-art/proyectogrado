"""
Rutas de condiciones nutricionales: condiciones y relaciones usuario-condición
"""
from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.api.controllers.condiciones_controller import CondicionesController

# Crear blueprint para rutas de condiciones
condiciones_bp = Blueprint('condiciones', __name__)


# ============================================================
# CONDICIONES NUTRICIONALES
# ============================================================

@condiciones_bp.route('/condiciones', methods=['POST'])
@jwt_required()
def create_condicion():
    """
    Crear una nueva condición nutricional
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "nombre": "Diabetes",           // REQUERIDO
        "descripcion": "...",          // OPCIONAL
        "parametros": {                // OPCIONAL
            "max_azucar_g": 25.0,
            "max_sodio_mg": 2000.0
        }
    }
    
    Response:
    {
        "success": true,
        "message": "Condición creada exitosamente",
        "data": {...}
    }
    """
    return CondicionesController.create_condicion()


@condiciones_bp.route('/condiciones', methods=['GET'])
def get_all_condiciones():
    """
    Obtener todas las condiciones nutricionales
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return CondicionesController.get_all_condiciones()


@condiciones_bp.route('/condiciones/<int:condicion_id>', methods=['GET'])
def get_condicion_by_id(condicion_id):
    """
    Obtener condición por ID
    
    Parámetros:
    - condicion_id: ID de la condición
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return CondicionesController.get_condicion_by_id(condicion_id)


@condiciones_bp.route('/condiciones/search', methods=['GET'])
def get_condicion_by_nombre():
    """
    Obtener condición por nombre
    
    Query params:
    - nombre: Nombre de la condición (requerido)
    
    Response:
    {
        "success": true,
        "data": {...}
    }
    """
    return CondicionesController.get_condicion_by_nombre()


@condiciones_bp.route('/condiciones/<int:condicion_id>', methods=['PUT'])
@jwt_required()
def update_condicion(condicion_id):
    """
    Actualizar condición nutricional
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - condicion_id: ID de la condición
    
    Body JSON (todos opcionales):
    {
        "nombre": "...",
        "descripcion": "...",
        "parametros": {...}
    }
    
    Response:
    {
        "success": true,
        "message": "Condición actualizada exitosamente",
        "data": {...}
    }
    """
    return CondicionesController.update_condicion(condicion_id)


@condiciones_bp.route('/condiciones/<int:condicion_id>', methods=['DELETE'])
@jwt_required()
def delete_condicion(condicion_id):
    """
    Eliminar condición nutricional
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - condicion_id: ID de la condición
    
    Response:
    {
        "success": true,
        "message": "Condición eliminada exitosamente"
    }
    """
    return CondicionesController.delete_condicion(condicion_id)


# ============================================================
# USUARIO CONDICION
# ============================================================

@condiciones_bp.route('/usuario/condiciones', methods=['POST'])
@jwt_required()
def add_condicion_to_usuario():
    """
    Agregar condición nutricional a usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body JSON:
    {
        "condicion_id": 1  // REQUERIDO
    }
    
    Response:
    {
        "success": true,
        "message": "Condición agregada al usuario exitosamente",
        "data": {...}
    }
    """
    return CondicionesController.add_condicion_to_usuario()


@condiciones_bp.route('/usuario/condiciones', methods=['GET'])
@jwt_required()
def get_condiciones_by_usuario():
    """
    Obtener condiciones nutricionales del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 3
    }
    """
    return CondicionesController.get_condiciones_by_usuario()


@condiciones_bp.route('/usuario/condiciones/<int:condicion_id>', methods=['DELETE'])
@jwt_required()
def remove_condicion_from_usuario(condicion_id):
    """
    Eliminar condición nutricional del usuario autenticado
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - condicion_id: ID de la condición
    
    Response:
    {
        "success": true,
        "message": "Condición eliminada del usuario exitosamente"
    }
    """
    return CondicionesController.remove_condicion_from_usuario(condicion_id)


@condiciones_bp.route('/usuario/condiciones/<int:condicion_id>/check', methods=['GET'])
@jwt_required()
def check_usuario_has_condicion(condicion_id):
    """
    Verificar si el usuario autenticado tiene una condición específica
    
    Headers:
    Authorization: Bearer <access_token>
    
    Parámetros:
    - condicion_id: ID de la condición
    
    Response:
    {
        "success": true,
        "has_condicion": true/false
    }
    """
    return CondicionesController.check_usuario_has_condicion(condicion_id)

