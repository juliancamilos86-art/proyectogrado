"""
Controlador para gestión de listas de mercado en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation
import uuid
from app.models.database import db
from app.models.listas import ListaMercado, ProductosEnLista
from app.models.productos import Producto
from app.utils.security import safe_error_response, log_exception
import logging

logger = logging.getLogger(__name__)


class ListasController:
    # ==================== LISTAS DE MERCADO ====================

    @staticmethod
    def create_lista():
        """Crear una nueva lista de mercado"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}

            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400

            lista = ListaMercado.create_lista(
                usuario_id=usuario_id,
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion')
            )

            db.session.add(lista)
            db.session.commit()

            logger.info(f"Lista creada exitosamente - Usuario ID: {usuario_id}")

            return jsonify({
                'success': True,
                'message': 'Lista creada exitosamente',
                'data': lista.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_lista: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.create_lista")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al crear lista'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.create_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_listas_by_usuario():
        """Obtener listas del usuario autenticado"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400

            listas = ListaMercado.get_by_usuario(usuario_id)

            return jsonify({
                'success': True,
                'data': [lista.to_json_safe() for lista in listas],
                'count': len(listas)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ListasController.get_listas_by_usuario")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_lista_by_id(lista_id):
        """Obtener lista por ID (solo si pertenece al usuario autenticado)"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)

            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para acceder a esta lista'
                }), 403

            return jsonify({
                'success': True,
                'data': lista.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ListasController.get_lista_by_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def update_lista(lista_id):
        """Actualizar lista de mercado"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)

            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para modificar esta lista'
                }), 403

            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            if 'nombre' in data:
                lista.nombre = data['nombre'].strip() if data['nombre'] else None
            if 'descripcion' in data:
                lista.descripcion = data['descripcion'].strip() if data['descripcion'] else None

            lista.update_timestamp()
            db.session.commit()

            logger.info(f"Lista actualizada exitosamente - ID: {lista_id}")

            return jsonify({
                'success': True,
                'message': 'Lista actualizada exitosamente',
                'data': lista.to_json_safe()
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.update_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def delete_lista(lista_id):
        """Eliminar lista de mercado"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)

            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para eliminar esta lista'
                }), 403

            db.session.delete(lista)
            db.session.commit()

            logger.info(f"Lista eliminada exitosamente - ID: {lista_id}")

            return jsonify({
                'success': True,
                'message': 'Lista eliminada exitosamente'
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.delete_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def search_listas_by_nombre():
        """Buscar listas por nombre"""
        try:
            user_id = get_jwt_identity()
            nombre = request.args.get('nombre')

            if not nombre:
                return jsonify({
                    'success': False,
                    'message': 'nombre es requerido como query parameter'
                }), 400

            try:
                usuario_id = uuid.UUID(user_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de usuario inválido'
                }), 400

            listas = ListaMercado.get_by_nombre(usuario_id, nombre)

            return jsonify({
                'success': True,
                'data': [lista.to_json_safe() for lista in listas],
                'count': len(listas)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ListasController.search_listas_by_nombre")
            return safe_error_response("Error interno del servidor", 500)

    # ==================== PRODUCTOS EN LISTA ====================

    @staticmethod
    def add_producto_to_lista(lista_id):
        """Agregar producto a una lista"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            producto_id = data.get('producto_id')

            if not producto_id:
                return jsonify({
                    'success': False,
                    'message': 'producto_id es requerido'
                }), 400

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido: debe ser un UUID válido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)
            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para modificar esta lista'
                }), 403

            producto = Producto.query.get(producto_uuid)
            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            item_existente = ProductosEnLista.get_item(lista_uuid, producto_uuid)
            if item_existente:
                return jsonify({
                    'success': False,
                    'message': 'Este producto ya está en la lista'
                }), 409

            cantidad = None
            if 'cantidad' in data and data['cantidad'] is not None:
                try:
                    cantidad = Decimal(str(data['cantidad']))
                    if cantidad <= 0:
                        return jsonify({
                            'success': False,
                            'message': 'La cantidad debe ser mayor a cero'
                        }), 400
                except (InvalidOperation, ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'cantidad debe ser un número válido'
                    }), 400

            precio_unitario = None
            if 'precio_unitario' in data and data['precio_unitario'] is not None:
                try:
                    precio_unitario = Decimal(str(data['precio_unitario']))
                    if precio_unitario < 0:
                        return jsonify({
                            'success': False,
                            'message': 'El precio no puede ser negativo'
                        }), 400
                except (InvalidOperation, ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'precio_unitario debe ser un número válido'
                    }), 400

            item = ProductosEnLista.create_item_lista(
                lista_id=lista_uuid,
                producto_id=producto_uuid,
                cantidad=cantidad,
                unidad_medida=data.get('unidad_medida'),
                precio_unitario=precio_unitario,
                notas=data.get('notas')
            )

            db.session.add(item)
            lista.update_timestamp()
            db.session.commit()

            logger.info(f"Producto agregado a lista exitosamente - Lista ID: {lista_id}")

            return jsonify({
                'success': True,
                'message': 'Producto agregado a la lista exitosamente',
                'data': item.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en add_producto_to_lista: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.add_producto_to_lista")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al agregar producto'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.add_producto_to_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_productos_by_lista(lista_id):
        """Obtener productos de una lista"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)
            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para acceder a esta lista'
                }), 403

            productos = ProductosEnLista.get_by_lista(lista_uuid)

            return jsonify({
                'success': True,
                'data': [item.to_json_safe() for item in productos],
                'count': len(productos)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ListasController.get_productos_by_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def update_producto_in_lista(lista_id, producto_id):
        """Actualizar producto en lista"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)
            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para modificar esta lista'
                }), 403

            item = ProductosEnLista.get_item(lista_uuid, producto_uuid)
            if not item:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado en la lista'
                }), 404

            if 'cantidad' in data and data['cantidad'] is not None:
                try:
                    cantidad = Decimal(str(data['cantidad']))
                    if cantidad <= 0:
                        return jsonify({
                            'success': False,
                            'message': 'La cantidad debe ser mayor a cero'
                        }), 400
                    item.actualizar_cantidad(cantidad)
                except (InvalidOperation, ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'cantidad inválida'
                    }), 400

            if 'unidad_medida' in data:
                item.unidad_medida = data['unidad_medida'].strip() if data['unidad_medida'] else None

            if 'precio_unitario' in data and data['precio_unitario'] is not None:
                try:
                    precio = Decimal(str(data['precio_unitario']))
                    if precio < 0:
                        return jsonify({
                            'success': False,
                            'message': 'El precio no puede ser negativo'
                        }), 400
                    item.establecer_precio(precio)
                except (InvalidOperation, ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'precio_unitario inválido'
                    }), 400

            if 'notas' in data:
                item.notas = data['notas'].strip() if data['notas'] else None

            lista.update_timestamp()
            db.session.commit()

            logger.info(f"Producto actualizado en lista exitosamente - Lista ID: {lista_id}")

            return jsonify({
                'success': True,
                'message': 'Producto actualizado exitosamente',
                'data': item.to_json_safe()
            }), 200

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en update_producto_in_lista: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.update_producto_in_lista")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def remove_producto_from_lista(lista_id, producto_id):
        """Eliminar producto de una lista"""
        try:
            user_id = get_jwt_identity()

            try:
                usuario_id = uuid.UUID(user_id)
                lista_uuid = uuid.UUID(lista_id)
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID inválido'
                }), 400

            lista = ListaMercado.query.get(lista_uuid)
            if not lista:
                return jsonify({
                    'success': False,
                    'message': 'Lista no encontrada'
                }), 404

            if lista.usuario_id != usuario_id:
                return jsonify({
                    'success': False,
                    'message': 'No tienes permiso para modificar esta lista'
                }), 403

            item = ProductosEnLista.get_item(lista_uuid, producto_uuid)
            if not item:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado en la lista'
                }), 404

            db.session.delete(item)
            lista.update_timestamp()
            db.session.commit()

            logger.info(f"Producto eliminado de lista exitosamente - Lista ID: {lista_id}")

            return jsonify({
                'success': True,
                'message': 'Producto eliminado de la lista exitosamente'
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ListasController.remove_producto_from_lista")
            return safe_error_response("Error interno del servidor", 500)