"""
Controlador para gestión de condiciones nutricionales en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
import uuid
from app.models.database import db
from app.models.condiciones import CondicionNutricional, UsuarioCondicion
from app.models.user import User
from app.utils.security import safe_error_response, log_exception
import logging

logger = logging.getLogger(__name__)


class CondicionesController:
    # ==================== CONDICIONES NUTRICIONALES ====================

    @staticmethod
    def create_condicion():
        """Crear una nueva condición nutricional"""
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

            if CondicionNutricional.get_by_nombre(nombre):
                return jsonify({
                    'success': False,
                    'message': 'Esta condición ya existe'
                }), 409

            parametros = data.get('parametros')
            if parametros is not None and not isinstance(parametros, dict):
                return jsonify({
                    'success': False,
                    'message': 'parametros debe ser un objeto JSON'
                }), 400

            condicion = CondicionNutricional.create_condicion(
                nombre=nombre,
                descripcion=data.get('descripcion'),
                parametros=parametros
            )

            db.session.add(condicion)
            db.session.commit()

            # LOG SEGURO: No expone el nombre (dato controlado por usuario)
            logger.info("Condición creada exitosamente")

            return jsonify({
                'success': True,
                'message': 'Condición creada exitosamente',
                'data': condicion.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_condicion: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.create_condicion")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: condición duplicada'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.create_condicion")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_all_condiciones():
        """Obtener todas las condiciones nutricionales"""
        try:
            condiciones = CondicionNutricional.query.order_by(CondicionNutricional.nombre).all()

            return jsonify({
                'success': True,
                'data': [condicion.to_json_safe() for condicion in condiciones],
                'count': len(condiciones)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="CondicionesController.get_all_condiciones")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_condicion_by_id(condicion_id):
        """Obtener condición por ID"""
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
            log_exception(logger, e, context="CondicionesController.get_condicion_by_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_condicion_by_nombre():
        """Obtener condición por nombre"""
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
            log_exception(logger, e, context="CondicionesController.get_condicion_by_nombre")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def update_condicion(condicion_id):
        """Actualizar condición nutricional"""
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

            if 'nombre' in data:
                nuevo_nombre = data['nombre'].strip() if data['nombre'] else None
                if nuevo_nombre != condicion.nombre:
                    if nuevo_nombre and CondicionNutricional.get_by_nombre(nuevo_nombre):
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

            # LOG SEGURO: No expone el ID
            logger.info("Condición actualizada exitosamente")

            return jsonify({
                'success': True,
                'message': 'Condición actualizada exitosamente',
                'data': condicion.to_json_safe()
            }), 200

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en update_condicion: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.update_condicion")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al actualizar condición'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.update_condicion")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def delete_condicion(condicion_id):
        """Eliminar condición nutricional"""
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

            # LOG SEGURO: No expone el ID
            logger.info("Condición eliminada exitosamente")

            return jsonify({
                'success': True,
                'message': 'Condición eliminada exitosamente'
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.delete_condicion")
            return safe_error_response("Error interno del servidor", 500)

    # ==================== USUARIO CONDICION ====================

    @staticmethod
    def add_condicion_to_usuario():
        """Agregar condición nutricional a usuario autenticado"""
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

            try:
                usuario_id = uuid.UUID(user_id)
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            usuario = User.query.get(usuario_id)
            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado'
                }), 404

            condicion = CondicionNutricional.get_by_id(condicion_id_int)
            if not condicion:
                return jsonify({
                    'success': False,
                    'message': 'Condición no encontrada'
                }), 404

            if UsuarioCondicion.usuario_tiene_condicion(usuario_id, condicion_id_int):
                return jsonify({
                    'success': False,
                    'message': 'El usuario ya tiene esta condición'
                }), 409

            usuario_condicion = UsuarioCondicion.create_usuario_condicion(
                usuario_id=usuario_id,
                condicion_id=condicion_id_int
            )

            db.session.add(usuario_condicion)
            db.session.commit()

            # LOG SEGURO: No expone IDs sensibles
            logger.info("Condición agregada a usuario exitosamente")

            return jsonify({
                'success': True,
                'message': 'Condición agregada al usuario exitosamente',
                'data': usuario_condicion.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en add_condicion_to_usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.add_condicion_to_usuario")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: relación duplicada'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.add_condicion_to_usuario")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_condiciones_by_usuario():
        """Obtener condiciones nutricionales del usuario autenticado"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400

            relaciones = UsuarioCondicion.get_by_usuario(usuario_id)

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
            log_exception(logger, e, context="CondicionesController.get_condiciones_by_usuario")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def remove_condicion_from_usuario(condicion_id):
        """Eliminar condición nutricional del usuario autenticado"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                condicion_id_int = int(condicion_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            relacion = UsuarioCondicion.get_relacion(usuario_id, condicion_id_int)

            if not relacion:
                return jsonify({
                    'success': False,
                    'message': 'El usuario no tiene esta condición'
                }), 404

            db.session.delete(relacion)
            db.session.commit()

            # LOG SEGURO: No expone IDs sensibles
            logger.info("Condición eliminada de usuario exitosamente")

            return jsonify({
                'success': True,
                'message': 'Condición eliminada del usuario exitosamente'
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="CondicionesController.remove_condicion_from_usuario")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def check_usuario_has_condicion(condicion_id):
        """Verificar si el usuario autenticado tiene una condición específica"""
        try:
            user_id = get_jwt_identity()

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
            log_exception(logger, e, context="CondicionesController.check_usuario_has_condicion")
            return safe_error_response("Error interno del servidor", 500)