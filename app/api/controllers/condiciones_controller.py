"""
Controlador para gestión de condiciones nutricionales en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import uuid
from app.models.database import db
from app.models.condiciones import CondicionNutricional, UsuarioCondicion
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class CondicionesController:
    # ==================== CONDICIONES NUTRICIONALES ====================
    
    @staticmethod
    def create_condicion():
        """
        Crear una nueva condición nutricional
        
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
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            nombre = data.get('nombre')
            
            if not nombre:
                return jsonify({
                    'success': False,
                    'message': 'nombre es requerido'
                }), 400
            
            # Verificar si la condición ya existe
            if CondicionNutricional.get_by_nombre(nombre):
                return jsonify({
                    'success': False,
                    'message': 'Esta condición ya existe'
                }), 409
            
            # Validar parametros si se proporciona
            parametros = data.get('parametros')
            if parametros is not None and not isinstance(parametros, dict):
                return jsonify({
                    'success': False,
                    'message': 'parametros debe ser un objeto JSON'
                }), 400
            
            # Crear condición usando método del modelo
            condicion = CondicionNutricional.create_condicion(
                nombre=nombre,
                descripcion=data.get('descripcion'),
                parametros=parametros
            )
            
            # Guardar en base de datos
            db.session.add(condicion)
            db.session.commit()
            
            logger.info(f"Condición creada exitosamente - Nombre: {nombre}")
            
            return jsonify({
                'success': True,
                'message': 'Condición creada exitosamente',
                'data': condicion.to_json_safe()
            }), 201
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: condición duplicada'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear condición: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    def get_all_condiciones():
        """
        Obtener todas las condiciones nutricionales
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            condiciones = CondicionNutricional.query.order_by(CondicionNutricional.nombre).all()
            
            return jsonify({
                'success': True,
                'data': [condicion.to_json_safe() for condicion in condiciones],
                'count': len(condiciones)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener condiciones: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
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
        try:
            try:
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de condición inválido'
                }), 400
            
            condicion = CondicionNutricional.get_by_id(condicion_id_int)
            
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': condicion.to_json_safe()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar condición por ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
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
        try:
            nombre = request.args.get('nombre')
            
            if not nombre:
                return jsonify({
                    'success': False,
                    'message': 'nombre es requerido como query parameter'
                }), 400
            
            condicion = CondicionNutricional.get_by_nombre(nombre)
            
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': condicion.to_json_safe()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar condición por nombre: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def update_condicion(condicion_id):
        """
        Actualizar condición nutricional
        
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
        try:
            try:
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de condición inválido'
                }), 400
            
            condicion = CondicionNutricional.get_by_id(condicion_id_int)
            
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            # Actualizar campos
            if 'nombre' in data:
                nuevo_nombre = data['nombre'].strip() if data['nombre'] else None
                if nuevo_nombre and nuevo_nombre != condicion.nombre:
                    # Verificar que el nuevo nombre no esté en uso
                    if CondicionNutricional.get_by_nombre(nuevo_nombre):
                        return jsonify({
                            'success': False,
                            'message': 'Este nombre de condición ya está en uso'
                        }), 409
                    condicion.nombre = nuevo_nombre
            
            if 'descripcion' in data:
                condicion.descripcion = data['descripcion'].strip() if data['descripcion'] else None
            
            if 'parametros' in data:
                parametros = data['parametros']
                if parametros is not None and not isinstance(parametros, dict):
                    return jsonify({
                        'success': False,
                        'message': 'parametros debe ser un objeto JSON'
                    }), 400
                condicion.set_parametros(parametros)
            
            db.session.commit()
            
            logger.info(f"Condición actualizada exitosamente - ID: {condicion_id}")
            
            return jsonify({
                'success': True,
                'message': 'Condición actualizada exitosamente',
                'data': condicion.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al actualizar condición'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar condición: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def delete_condicion(condicion_id):
        """
        Eliminar condición nutricional
        
        Parámetros:
        - condicion_id: ID de la condición
        
        Response:
        {
            "success": true,
            "message": "Condición eliminada exitosamente"
        }
        """
        try:
            try:
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de condición inválido'
                }), 400
            
            condicion = CondicionNutricional.get_by_id(condicion_id_int)
            
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404
            
            db.session.delete(condicion)
            db.session.commit()
            
            logger.info(f"Condición eliminada exitosamente - ID: {condicion_id}")
            
            return jsonify({
                'success': True,
                'message': 'Condición eliminada exitosamente'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al eliminar condición: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    # ==================== USUARIO CONDICION ====================
    
    @staticmethod
    @jwt_required()
    def add_condicion_to_usuario():
        """
        Agregar condición nutricional a usuario autenticado
        
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
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            condicion_id = data.get('condicion_id')
            
            if not condicion_id:
                return jsonify({
                    'success': False,
                    'message': 'condicion_id es requerido'
                }), 400
            
            # Convertir IDs
            try:
                usuario_id = uuid.UUID(user_id)
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400
            
            # Verificar que el usuario existe
            usuario = User.query.get(usuario_id)
            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404
            
            # Verificar que la condición existe
            condicion = CondicionNutricional.get_by_id(condicion_id_int)
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404
            
            # Verificar si el usuario ya tiene esta condición
            if UsuarioCondicion.usuario_tiene_condicion(usuario_id, condicion_id_int):
                return jsonify({
                    'success': False,
                    'message': 'El usuario ya tiene esta condición'
                }), 409
            
            # Crear relación usando método del modelo
            usuario_condicion = UsuarioCondicion.create_usuario_condicion(
                usuario_id=usuario_id,
                condicion_id=condicion_id_int
            )
            
            # Guardar en base de datos
            db.session.add(usuario_condicion)
            db.session.commit()
            
            logger.info(f"Condición agregada a usuario exitosamente - Usuario ID: {usuario_id}, Condición ID: {condicion_id_int}")
            
            return jsonify({
                'success': True,
                'message': 'Condición agregada al usuario exitosamente',
                'data': usuario_condicion.to_json_safe()
            }), 201
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: relación duplicada'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al agregar condición a usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    @jwt_required()
    def get_condiciones_by_usuario():
        """
        Obtener condiciones nutricionales del usuario autenticado
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            user_id = get_jwt_identity()
            
            # Convertir user_id string a UUID
            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400
            
            # Obtener relaciones
            relaciones = UsuarioCondicion.get_by_usuario(usuario_id)
            
            # Obtener información completa de las condiciones
            condiciones_data = []
            for relacion in relaciones:
                condicion = CondicionNutricional.get_by_id(relacion.condicion_id)
                if condicion:
                    condiciones_data.append(condicion.to_json_safe())
            
            return jsonify({
                'success': True,
                'data': condiciones_data,
                'count': len(condiciones_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener condiciones del usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def remove_condicion_from_usuario(condicion_id):
        """
        Eliminar condición nutricional del usuario autenticado
        
        Parámetros:
        - condicion_id: ID de la condición
        
        Response:
        {
            "success": true,
            "message": "Condición eliminada del usuario exitosamente"
        }
        """
        try:
            user_id = get_jwt_identity()
            
            # Convertir IDs
            try:
                usuario_id = uuid.UUID(user_id)
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400
            
            # Buscar la relación
            relacion = UsuarioCondicion.get_relacion(usuario_id, condicion_id_int)
            
            if not relacion:
                return jsonify({
                    'success': False,
                    'message': 'El usuario no tiene esta condición'
                }), 404
            
            db.session.delete(relacion)
            db.session.commit()
            
            logger.info(f"Condición eliminada de usuario exitosamente - Usuario ID: {usuario_id}, Condición ID: {condicion_id_int}")
            
            return jsonify({
                'success': True,
                'message': 'Condición eliminada del usuario exitosamente'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al eliminar condición de usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def check_usuario_has_condicion(condicion_id):
        """
        Verificar si el usuario autenticado tiene una condición específica
        
        Parámetros:
        - condicion_id: ID de la condición
        
        Response:
        {
            "success": true,
            "has_condicion": true/false
        }
        """
        try:
            user_id = get_jwt_identity()
            
            # Convertir IDs
            try:
                usuario_id = uuid.UUID(user_id)
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400
            
            has_condicion = UsuarioCondicion.usuario_tiene_condicion(usuario_id, condicion_id_int)
            
            return jsonify({
                'success': True,
                'has_condicion': has_condicion
            }), 200
            
        except Exception as e:
            logger.error(f"Error al verificar condición del usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

