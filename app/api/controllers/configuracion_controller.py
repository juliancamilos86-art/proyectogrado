"""
Controlador para gestión de configuración del sistema en NutriChat
"""
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from app.models.database import db
from app.models.configuracion_sistema import ConfiguracionSistema
from app.utils.security import safe_error_response, log_exception
import logging

logger = logging.getLogger(__name__)


class ConfiguracionController:
    @staticmethod
    def create_config():
        """Crear una nueva configuración del sistema"""
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

            if not isinstance(valor, dict):
                return jsonify({
                    'success': False,
                    'message': 'valor debe ser un objeto JSON'
                }), 400

            config_existente = ConfiguracionSistema.get_by_clave(clave)
            if config_existente:
                return jsonify({
                    'success': False,
                    'message': 'Esta configuración ya existe'
                }), 409

            config = ConfiguracionSistema.create_config(
                clave=clave,
                valor=valor
            )

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
            logger.warning(f"ValueError en create_config: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ConfiguracionController.create_config")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: configuración duplicada'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ConfiguracionController.create_config")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_config_by_clave(clave):
        """Obtener configuración por clave"""
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
            log_exception(logger, e, context="ConfiguracionController.get_config_by_clave")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_all_configs():
        """Obtener todas las configuraciones del sistema"""
        try:
            configs = ConfiguracionSistema.get_all()

            return jsonify({
                'success': True,
                'data': [config.to_json_safe() for config in configs],
                'count': len(configs)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ConfiguracionController.get_all_configs")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_valor_by_clave(clave):
        """Obtener solo el valor de una configuración por clave"""
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
            log_exception(logger, e, context="ConfiguracionController.get_valor_by_clave")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def update_config(clave):
        """Actualizar configuración del sistema"""
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

            if not isinstance(valor, dict):
                return jsonify({
                    'success': False,
                    'message': 'valor debe ser un objeto JSON'
                }), 400

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
            logger.warning(f"ValueError en update_config: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ConfiguracionController.update_config")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def update_config_key(clave):
        """Actualizar una clave específica dentro del valor de la configuración"""
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
            logger.warning(f"ValueError en update_config_key: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ConfiguracionController.update_config_key")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def delete_config(clave):
        """Eliminar configuración del sistema"""
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
            log_exception(logger, e, context="ConfiguracionController.delete_config")
            return safe_error_response("Error interno del servidor", 500)