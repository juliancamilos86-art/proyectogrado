"""
Controlador para gestión de logs de auditoría en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
import uuid
from app.models.database import db
from app.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)


class AuditLogController:
    @staticmethod
    def create_log():
        """
        Crear un nuevo registro de auditoría
        
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
        try:
            
            # Intenta obtener el ID del token, si no hay, usa un ID por defecto
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
            
            # Validar payload si se proporciona
            payload = data.get('payload')
            if payload is not None and not isinstance(payload, dict):
                return jsonify({
                    'success': False,
                    'message': 'payload debe ser un objeto JSON'
                }), 400
            
            # Convertir usuario_id si se proporciona
            usuario_id = None
            if 'usuario_id' in data and data['usuario_id']:
                try:
                    usuario_id = uuid.UUID(data['usuario_id'])
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'usuario_id debe ser un UUID válido'
                    }), 400
            else:
                # Si no se proporciona, usar el usuario autenticado
                try:
                    usuario_id = uuid.UUID(usuario_id)
                except (ValueError, TypeError):
                    usuario_id = None
                    pass  # Puede ser None si no hay usuario autenticado válido
            
            # Crear log usando método del modelo
            log = AuditLog.create_log(
                entidad=entidad,
                accion=accion,
                entidad_id=data.get('entidad_id'),
                usuario_id=usuario_id,
                payload=payload
            )
            
            # Guardar en base de datos
            db.session.add(log)
            db.session.commit()
            
            logger.info(f"Log de auditoría creado exitosamente - Entidad: {entidad}, Acción: {accion}")
            
            return jsonify({
                'success': True,
                'message': 'Log de auditoría creado exitosamente',
                'data': log.to_json_safe()
            }), 201
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear log de auditoría: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    def get_log_by_id(log_id):
        """
        Obtener log de auditoría por ID
        
        Parámetros:
        - log_id: ID del log
        
        Response:
        {
            "success": true,
            "data": {...}
        }
        """
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
            logger.error(f"Error al buscar log por ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_logs_by_entidad():
        """
        Obtener logs por entidad
        
        Query params:
        - entidad: Nombre de la entidad (requerido)
        - limit: Número máximo de resultados (opcional, default: sin límite)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
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
            logger.error(f"Error al obtener logs por entidad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_logs_by_entidad_id():
        """
        Obtener logs por entidad e ID
        
        Query params:
        - entidad: Nombre de la entidad (requerido)
        - entidad_id: ID de la entidad (requerido)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
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
            logger.error(f"Error al obtener logs por entidad e ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_logs_by_usuario():
        """
        Obtener logs por usuario
        
        Query params:
        - usuario_id: ID del usuario (opcional, si no se proporciona usa el autenticado)
        - limit: Número máximo de resultados (opcional, default: sin límite)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            user_id = get_jwt_identity()
            usuario_id_param = request.args.get('usuario_id')
            
            # Si se proporciona usuario_id, validarlo
            if usuario_id_param:
                try:
                    usuario_id = uuid.UUID(usuario_id_param)
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'usuario_id debe ser un UUID válido'
                    }), 400
            else:
                # Usar el usuario autenticado
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
            logger.error(f"Error al obtener logs por usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_logs_by_accion():
        """
        Obtener logs por acción
        
        Query params:
        - accion: Nombre de la acción (requerido)
        - limit: Número máximo de resultados (opcional, default: sin límite)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
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
            logger.error(f"Error al obtener logs por acción: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_recent_logs():
        """
        Obtener logs recientes
        
        Query params:
        - limit: Número máximo de resultados (opcional, default: 100, máximo: 1000)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
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
            logger.error(f"Error al obtener logs recientes: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

