"""
Controlador para gestión de configuración del sistema en NutriChat
"""
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from app.models.database import db
from app.models.configuracion_sistema import ConfiguracionSistema
import logging

logger = logging.getLogger(__name__)


class ConfiguracionController:
    @staticmethod
    def create_config():
        """
        Crear una nueva configuración del sistema
        
        Body JSON:
        {
            "clave": "max_productos_lista",  // REQUERIDO
            "valor": {                       // REQUERIDO
                "max": 50,
                "min": 1
            }
        }
        
        Response:
        {
            "success": true,
            "message": "Configuración creada exitosamente",
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
            
            clave = data.get('clave')
            valor = data.get('valor')
            
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            if valor is None:
                return jsonify({
                    'success': False,
                    'message': 'valor es requerido'
                }), 400
            
            # Validar que valor sea un diccionario
            if not isinstance(valor, dict):
                return jsonify({
                    'success': False,
                    'message': 'valor debe ser un objeto JSON'
                }), 400
            
            # Verificar si la configuración ya existe
            config_existente = ConfiguracionSistema.get_by_clave(clave)
            if config_existente:
                return jsonify({
                    'success': False,
                    'message': 'Esta configuración ya existe'
                }), 409
            
            # Crear configuración usando método del modelo
            config = ConfiguracionSistema.create_config(
                clave=clave,
                valor=valor
            )
            
            # Guardar en base de datos
            db.session.add(config)
            db.session.commit()
            
            logger.info(f"Configuración creada exitosamente - Clave: {clave}")
            
            return jsonify({
                'success': True,
                'message': 'Configuración creada exitosamente',
                'data': config.to_json_safe()
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
                'message': 'Error de integridad: configuración duplicada'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al crear configuración: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    def get_config_by_clave(clave):
        """
        Obtener configuración por clave
        
        Parámetros:
        - clave: Clave de la configuración
        
        Response:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            config = ConfiguracionSistema.get_by_clave(clave)
            
            if not config:
                return jsonify({
                    'success': False,
                    'message': 'Configuración no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': config.to_json_safe()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar configuración por clave: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_all_configs():
        """
        Obtener todas las configuraciones del sistema
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            configs = ConfiguracionSistema.get_all()
            
            return jsonify({
                'success': True,
                'data': [config.to_json_safe() for config in configs],
                'count': len(configs)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener configuraciones: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_valor_by_clave(clave):
        """
        Obtener solo el valor de una configuración por clave
        
        Parámetros:
        - clave: Clave de la configuración
        
        Query params:
        - default: Valor por defecto si no existe (opcional)
        
        Response:
        {
            "success": true,
            "data": {...}  // Solo el valor, no el objeto completo
        }
        """
        try:
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            default = request.args.get('default')
            
            config = ConfiguracionSistema.get_by_clave(clave)
            
            if not config:
                if default is not None:
                    return jsonify({
                        'success': True,
                        'data': default
                    }), 200
                return jsonify({
                    'success': False,
                    'message': 'Configuración no encontrada'
                }), 404
            
            return jsonify({
                'success': True,
                'data': config.get_valor()
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener valor de configuración: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def update_config(clave):
        """
        Actualizar configuración del sistema
        
        Parámetros:
        - clave: Clave de la configuración
        
        Body JSON:
        {
            "valor": {  // REQUERIDO
                "max": 100,
                "min": 1
            }
        }
        
        Response:
        {
            "success": true,
            "message": "Configuración actualizada exitosamente",
            "data": {...}
        }
        """
        try:
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            config = ConfiguracionSistema.get_by_clave(clave)
            
            if not config:
                return jsonify({
                    'success': False,
                    'message': 'Configuración no encontrada'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            valor = data.get('valor')
            
            if valor is None:
                return jsonify({
                    'success': False,
                    'message': 'valor es requerido'
                }), 400
            
            # Validar que valor sea un diccionario
            if not isinstance(valor, dict):
                return jsonify({
                    'success': False,
                    'message': 'valor debe ser un objeto JSON'
                }), 400
            
            # Actualizar valor usando método del modelo
            config.set_valor(valor)
            
            db.session.commit()
            
            logger.info(f"Configuración actualizada exitosamente - Clave: {clave}")
            
            return jsonify({
                'success': True,
                'message': 'Configuración actualizada exitosamente',
                'data': config.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar configuración: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def update_config_key(clave):
        """
        Actualizar una clave específica dentro del valor de la configuración
        
        Parámetros:
        - clave: Clave de la configuración
        
        Body JSON:
        {
            "key": "max",    // REQUERIDO - clave dentro del valor
            "value": 100    // REQUERIDO - nuevo valor
        }
        
        Response:
        {
            "success": true,
            "message": "Clave de configuración actualizada exitosamente",
            "data": {...}
        }
        """
        try:
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            config = ConfiguracionSistema.get_by_clave(clave)
            
            if not config:
                return jsonify({
                    'success': False,
                    'message': 'Configuración no encontrada'
                }), 404
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400
            
            key = data.get('key')
            value = data.get('value')
            
            if not key:
                return jsonify({
                    'success': False,
                    'message': 'key es requerido'
                }), 400
            
            if value is None:
                return jsonify({
                    'success': False,
                    'message': 'value es requerido'
                }), 400
            
            # Actualizar clave específica usando método del modelo
            config.set_valor_key(key, value)
            
            db.session.commit()
            
            logger.info(f"Clave de configuración actualizada exitosamente - Clave: {clave}, Key: {key}")
            
            return jsonify({
                'success': True,
                'message': 'Clave de configuración actualizada exitosamente',
                'data': config.to_json_safe()
            }), 200
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar clave de configuración: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def delete_config(clave):
        """
        Eliminar configuración del sistema
        
        Parámetros:
        - clave: Clave de la configuración
        
        Response:
        {
            "success": true,
            "message": "Configuración eliminada exitosamente"
        }
        """
        try:
            if not clave:
                return jsonify({
                    'success': False,
                    'message': 'clave es requerido'
                }), 400
            
            config = ConfiguracionSistema.get_by_clave(clave)
            
            if not config:
                return jsonify({
                    'success': False,
                    'message': 'Configuración no encontrada'
                }), 404
            
            db.session.delete(config)
            db.session.commit()
            
            logger.info(f"Configuración eliminada exitosamente - Clave: {clave}")
            
            return jsonify({
                'success': True,
                'message': 'Configuración eliminada exitosamente'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al eliminar configuración: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

