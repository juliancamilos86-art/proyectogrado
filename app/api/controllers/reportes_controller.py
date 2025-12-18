"""
Controlador para gestión de reportes y feedback en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import uuid
from app.models.database import db
from app.models.reportes import Reporte, FeedbackRecomendacion
import logging

logger = logging.getLogger(__name__)


class ReportesController:
    # ==================== REPORTES ====================
    
    @staticmethod
    @jwt_required()
    def create_reporte():
        """
        Crear un nuevo reporte
        
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
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            
            # Convertir user_id string a UUID
            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400
            
            # Crear reporte usando método del modelo
            reporte = Reporte.create_reporte(
                tipo=data.get('tipo'),
                usuario_id=usuario_id,
                parametros=data.get('parametros'),
                contenido=data.get('contenido'),
                enlace_archivo=data.get('enlace_archivo')
            )
            
            # Guardar en base de datos
            db.session.add(reporte)
            db.session.commit()
            
            logger.info(f"Reporte creado exitosamente - Usuario ID: {usuario_id}, Tipo: {data.get('tipo')}")
            
            return jsonify({
                'success': True,
                'message': 'Reporte creado exitosamente',
                'data': reporte.to_json_safe()
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
                'message': 'Error de integridad al crear reporte'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear reporte: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    @jwt_required()
    def get_reportes_by_usuario():
        """
        Obtener reportes del usuario autenticado
        
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
            
            reportes = Reporte.get_by_usuario(usuario_id)
            
            return jsonify({
                'success': True,
                'data': [reporte.to_json_safe() for reporte in reportes],
                'count': len(reportes)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener reportes por usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_reportes_by_tipo(tipo):
        """
        Obtener reportes por tipo
        
        Parámetros:
        - tipo: Tipo de reporte
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            if not tipo:
                return jsonify({
                    'success': False,
                    'message': 'tipo es requerido'
                }), 400
            
            reportes = Reporte.get_by_tipo(tipo)
            
            return jsonify({
                'success': True,
                'data': [reporte.to_json_safe() for reporte in reportes],
                'count': len(reportes)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener reportes por tipo: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_system_reportes():
        """
        Obtener reportes del sistema (sin usuario_id)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            reportes = Reporte.get_system_reportes()
            
            return jsonify({
                'success': True,
                'data': [reporte.to_json_safe() for reporte in reportes],
                'count': len(reportes)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener reportes del sistema: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
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
        try:
            # Convertir reporte_id string a UUID
            try:
                reporte_uuid = uuid.UUID(reporte_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de reporte inválido'
                }), 400
            
            reporte = Reporte.query.get(reporte_uuid)
            
            if not reporte:
                return jsonify({
                    'success': False,
                    'message': 'Reporte no encontrado'
                }), 404
            
            return jsonify({
                'success': True,
                'data': reporte.to_json_safe()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar reporte por ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    # ==================== FEEDBACK RECOMENDACION ====================
    
    @staticmethod
    @jwt_required()
    def create_feedback():
        """
        Crear un nuevo feedback de recomendación
        
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
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            lista_id = data.get('lista_id')
            
            if not lista_id:
                return jsonify({
                    'success': False,
                    'message': 'lista_id es requerido'
                }), 400
            
            # Convertir IDs string a UUID
            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError) as e:
                return jsonify({
                    'success': False,
                    'message': 'ID inválido: debe ser un UUID válido'
                }), 400
            
            # Crear feedback usando método del modelo
            feedback = FeedbackRecomendacion.create_feedback(
                usuario_id=usuario_id,
                lista_id=lista_uuid,
                aceptada=data.get('aceptada'),
                comentarios=data.get('comentarios')
            )
            
            # Guardar en base de datos
            db.session.add(feedback)
            db.session.commit()
            
            logger.info(f"Feedback creado exitosamente - Usuario ID: {usuario_id}, Lista ID: {lista_uuid}")
            
            return jsonify({
                'success': True,
                'message': 'Feedback creado exitosamente',
                'data': feedback.to_json_safe()
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
                'message': 'Error de integridad al crear feedback'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear feedback: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    @jwt_required()
    def get_feedback_by_usuario():
        """
        Obtener feedback del usuario autenticado
        
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
            
            feedbacks = FeedbackRecomendacion.get_by_usuario(usuario_id)
            
            return jsonify({
                'success': True,
                'data': [feedback.to_json_safe() for feedback in feedbacks],
                'count': len(feedbacks)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener feedback por usuario: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_feedback_by_lista(lista_id):
        """
        Obtener feedback por lista
        
        Parámetros:
        - lista_id: ID de la lista (UUID)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            # Convertir lista_id string a UUID
            try:
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de lista inválido'
                }), 400
            
            feedbacks = FeedbackRecomendacion.get_by_lista(lista_uuid)
            
            return jsonify({
                'success': True,
                'data': [feedback.to_json_safe() for feedback in feedbacks],
                'count': len(feedbacks)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener feedback por lista: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def get_feedback_aceptadas():
        """
        Obtener feedback aceptados del usuario autenticado
        
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
            
            feedbacks = FeedbackRecomendacion.get_aceptadas(usuario_id=usuario_id)
            
            return jsonify({
                'success': True,
                'data': [feedback.to_json_safe() for feedback in feedbacks],
                'count': len(feedbacks)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener feedback aceptados: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    @jwt_required()
    def get_feedback_rechazadas():
        """
        Obtener feedback rechazados del usuario autenticado
        
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
            
            feedbacks = FeedbackRecomendacion.get_rechazadas(usuario_id=usuario_id)
            
            return jsonify({
                'success': True,
                'data': [feedback.to_json_safe() for feedback in feedbacks],
                'count': len(feedbacks)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener feedback rechazados: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
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
        try:
            try:
                feedback_id_int = int(feedback_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de feedback inválido'
                }), 400
            
            feedback = FeedbackRecomendacion.query.get(feedback_id_int)
            
            if not feedback:
                return jsonify({
                    'success': False,
                    'message': 'Feedback no encontrado'
                }), 404
            
            return jsonify({
                'success': True,
                'data': feedback.to_json_safe()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar feedback por ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

