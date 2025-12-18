"""
Controlador para gestión de sesiones de Telegram en NutriChat
"""
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from app.models.database import db
from app.models.telegram_sesion import TelegramSesion
import logging

logger = logging.getLogger(__name__)


class TelegramSesionController:
    @staticmethod
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
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            telegram_id = data.get('telegram_id')
            
            if not telegram_id:
                return jsonify({
                    'success': False,
                    'message': 'telegram_id es requerido'
                }), 400
            
            # Validar que telegram_id sea un número entero
            try:
                telegram_id = int(telegram_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'telegram_id debe ser un número entero'
                }), 400
            
            # Buscar sesión más reciente por telegram_id
            sesion = TelegramSesion.get_by_telegram_id(telegram_id)
            
            if sesion:
                logger.info(f"Sesión encontrada - Telegram ID: {telegram_id}")
                return jsonify({
                    'success': True,
                    'message': 'Sesión obtenida exitosamente',
                    'data': sesion.to_json_safe()
                }), 200
            
            # Si no existe, crear nueva sesión
            sesion = TelegramSesion.create_sesion(telegram_id=telegram_id)
            
            # Guardar en base de datos
            db.session.add(sesion)
            db.session.commit()
            
            logger.info(f"Sesión creada exitosamente - Telegram ID: {telegram_id}")
            
            return jsonify({
                'success': True,
                'message': 'Sesión creada exitosamente',
                'data': sesion.to_json_safe()
            }), 201
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al crear sesión'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al obtener/crear sesión: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
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
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            telegram_id = data.get('telegram_id')
            estado_conversacion = data.get('estado_conversacion')
            
            if not telegram_id:
                return jsonify({
                    'success': False,
                    'message': 'telegram_id es requerido'
                }), 400
            
            if estado_conversacion is None:
                return jsonify({
                    'success': False,
                    'message': 'estado_conversacion es requerido'
                }), 400
            
            # Validar que telegram_id sea un número entero
            try:
                telegram_id = int(telegram_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'telegram_id debe ser un número entero'
                }), 400
            
            # Buscar sesión activa por telegram_id
            sesion = TelegramSesion.get_by_telegram_id(telegram_id)
            
            # Si no existe, crear una nueva
            if not sesion:
                sesion = TelegramSesion.create_sesion(
                    telegram_id=telegram_id,
                    estado_conversacion=estado_conversacion
                )
                db.session.add(sesion)
            else:
                # Actualizar solo estado_conversacion
                sesion.estado_conversacion = estado_conversacion.strip() if estado_conversacion else None
            
            # Hacer commit
            db.session.commit()
            
            logger.info(f"Estado actualizado - Telegram ID: {telegram_id}, Estado: {estado_conversacion}")
            
            return jsonify({
                'success': True,
                'message': 'Estado actualizado exitosamente',
                'data': sesion.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar estado: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
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
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            telegram_id = data.get('telegram_id')
            contexto = data.get('contexto')
            
            if not telegram_id:
                return jsonify({
                    'success': False,
                    'message': 'telegram_id es requerido'
                }), 400
            
            if contexto is None:
                return jsonify({
                    'success': False,
                    'message': 'contexto es requerido'
                }), 400
            
            # Validar que telegram_id sea un número entero
            try:
                telegram_id = int(telegram_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'telegram_id debe ser un número entero'
                }), 400
            
            # Validar que contexto sea un diccionario
            if not isinstance(contexto, dict):
                return jsonify({
                    'success': False,
                    'message': 'contexto debe ser un objeto JSON'
                }), 400
            
            # Buscar sesión activa por telegram_id
            sesion = TelegramSesion.get_by_telegram_id(telegram_id)
            
            # Si no existe, crear una nueva
            if not sesion:
                sesion = TelegramSesion.create_sesion(
                    telegram_id=telegram_id,
                    contexto=contexto
                )
                db.session.add(sesion)
            else:
                # Usar método del modelo para establecer contexto
                sesion.set_contexto(contexto)
            
            # Hacer commit
            db.session.commit()
            
            logger.info(f"Contexto actualizado - Telegram ID: {telegram_id}")
            
            return jsonify({
                'success': True,
                'message': 'Contexto actualizado exitosamente',
                'data': sesion.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar contexto: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
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
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            telegram_id = data.get('telegram_id')
            
            if not telegram_id:
                return jsonify({
                    'success': False,
                    'message': 'telegram_id es requerido'
                }), 400
            
            # Validar que telegram_id sea un número entero
            try:
                telegram_id = int(telegram_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'telegram_id debe ser un número entero'
                }), 400
            
            # Buscar sesión activa por telegram_id
            sesion = TelegramSesion.get_by_telegram_id(telegram_id)
            
            if not sesion:
                return jsonify({
                    'success': False,
                    'message': 'Sesión no encontrada'
                }), 404
            
            # Limpiar estado y contexto (NO eliminar el registro)
            sesion.estado_conversacion = None
            sesion.clear_contexto()
            
            # Hacer commit
            db.session.commit()
            
            logger.info(f"Sesión limpiada - Telegram ID: {telegram_id}")
            
            return jsonify({
                'success': True,
                'message': 'Sesión limpiada exitosamente',
                'data': sesion.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al limpiar sesión: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
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
        try:
            sesion = TelegramSesion.get_by_telegram_id(int(telegram_id))
            
            if not sesion:
                return jsonify({
                    'success': False,
                    'message': 'Sesión no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': sesion.to_json_safe()
            }), 200
            
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Telegram ID inválido'
            }), 400
            
        except Exception as e:
            logger.error(f"Error al buscar sesión por Telegram ID: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

