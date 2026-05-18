"""
Controlador para gestión de logs de auditoría en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
import uuid
from app.models.database import db
from app.models.audit_log import AuditLog
from app.utils.security import safe_error_response, log_exception
import logging

logger = logging.getLogger(__name__)


class AuditLogController:
    @staticmethod
    def create_log():
        """Crear un nuevo registro de auditoría"""
        try:
            try:
                usuario_id = get_jwt_identity()
            except:
                usuario_id = "sistema_n8n_automatico"

            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            entidad = data.get('entidad')
            accion = data.get('accion')

            if not entidad:
                return jsonify({
                    'success': False,
                    'message': 'entidad es requerido'
                }), 400

            if not accion:
                return jsonify({
                    'success': False,
                    'message': 'accion es requerido'
                }), 400

            payload = data.get('payload')
            if payload is not None and not isinstance(payload, dict):
                return jsonify({
                    'success': False,
                    'message': 'payload debe ser un objeto JSON'
                }), 400

            usuario_id_uuid = None
            if 'usuario_id' in data and data['usuario_id']:
                try:
                    usuario_id_uuid = uuid.UUID(data['usuario_id'])
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'usuario_id debe ser un UUID válido'
                    }), 400
            else:
                try:
                    usuario_id_uuid = uuid.UUID(usuario_id) if usuario_id != "sistema_n8n_automatico" else None
                except (ValueError, TypeError):
                    usuario_id_uuid = None

            log = AuditLog.create_log(
                entidad=entidad,
                accion=accion,
                entidad_id=data.get('entidad_id'),
                usuario_id=usuario_id_uuid,
                payload=payload
            )

            db.session.add(log)
            db.session.commit()

            # LOG SEGURO: No expone datos controlados por usuario
            logger.info("Log de auditoría creado exitosamente")

            return jsonify({
                'success': True,
                'message': 'Log de auditoría creado exitosamente',
                'data': log.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_log: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="AuditLogController.create_log")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_log_by_id(log_id):
        """Obtener log de auditoría por ID"""
        try:
            try:
                log_id_int = int(log_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de log inválido'
                }), 400

            log = AuditLog.query.get(log_id_int)

            if not log:
                return jsonify({
                    'success': False,
                    'message': 'Log de auditoría no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'data': log.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_log_by_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_logs_by_entidad():
        """Obtener logs por entidad"""
        try:
            entidad = request.args.get('entidad')

            if not entidad:
                return jsonify({
                    'success': False,
                    'message': 'entidad es requerido como query parameter'
                }), 400

            limit = request.args.get('limit', type=int)
            logs = AuditLog.get_by_entidad(entidad, limit=limit)

            return jsonify({
                'success': True,
                'data': [log.to_json_safe() for log in logs],
                'count': len(logs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_logs_by_entidad")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_logs_by_entidad_id():
        """Obtener logs por entidad e ID"""
        try:
            entidad = request.args.get('entidad')
            entidad_id = request.args.get('entidad_id')

            if not entidad:
                return jsonify({
                    'success': False,
                    'message': 'entidad es requerido como query parameter'
                }), 400

            if not entidad_id:
                return jsonify({
                    'success': False,
                    'message': 'entidad_id es requerido como query parameter'
                }), 400

            logs = AuditLog.get_by_entidad_id(entidad, entidad_id)

            return jsonify({
                'success': True,
                'data': [log.to_json_safe() for log in logs],
                'count': len(logs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_logs_by_entidad_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_logs_by_usuario():
        """Obtener logs por usuario"""
        try:
            user_id = get_jwt_identity()
            usuario_id_param = request.args.get('usuario_id')

            if usuario_id_param:
                try:
                    usuario_id = uuid.UUID(usuario_id_param)
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'usuario_id debe ser un UUID válido'
                    }), 400
            else:
                try:
                    usuario_id = uuid.UUID(user_id)
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'ID de usuario inválido'
                    }), 400

            limit = request.args.get('limit', type=int)
            logs = AuditLog.get_by_usuario(usuario_id, limit=limit)

            return jsonify({
                'success': True,
                'data': [log.to_json_safe() for log in logs],
                'count': len(logs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_logs_by_usuario")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_logs_by_accion():
        """Obtener logs por acción"""
        try:
            accion = request.args.get('accion')

            if not accion:
                return jsonify({
                    'success': False,
                    'message': 'accion es requerido como query parameter'
                }), 400

            limit = request.args.get('limit', type=int)
            logs = AuditLog.get_by_accion(accion, limit=limit)

            return jsonify({
                'success': True,
                'data': [log.to_json_safe() for log in logs],
                'count': len(logs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_logs_by_accion")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_recent_logs():
        """Obtener logs recientes"""
        try:
            limit = request.args.get('limit', default=100, type=int)

            if limit < 1 or limit > 1000:
                return jsonify({
                    'success': False,
                    'message': 'limit debe estar entre 1 y 1000'
                }), 400

            logs = AuditLog.get_recent(limit=limit)

            return jsonify({
                'success': True,
                'data': [log.to_json_safe() for log in logs],
                'count': len(logs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="AuditLogController.get_recent_logs")
            return safe_error_response("Error interno del servidor", 500)