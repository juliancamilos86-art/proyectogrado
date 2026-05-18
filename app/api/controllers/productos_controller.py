"""
Controlador para gestión de productos en NutriChat
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from decimal import Decimal, InvalidOperation
import uuid
from datetime import datetime, timezone
from app.models.database import db
from app.models.productos import Categoria, Producto, ProductoNutricion, ProductoSnapshot
from app.utils.security import safe_error_response, log_exception, sanitize_telegram_id
import logging

logger = logging.getLogger(__name__)


class ProductosController:
    # ==================== CATEGORIAS ====================

    @staticmethod
    def create_categoria():
        """
        Crear una nueva categoría
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

            if Categoria.get_by_nombre(nombre):
                return jsonify({
                    'success': False,
                    'message': 'Esta categoría ya existe'
                }), 409

            categoria = Categoria.create_categoria(
                nombre=nombre,
                descripcion=data.get('descripcion')
            )

            db.session.add(categoria)
            db.session.commit()

            logger.info(f"Categoría creada exitosamente - Nombre: {nombre}")

            return jsonify({
                'success': True,
                'message': 'Categoría creada exitosamente',
                'data': categoria.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_categoria: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_categoria")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: categoría duplicada'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_categoria")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_categoria_by_id(categoria_id):
        """Obtener categoría por ID"""
        try:
            try:
                categoria_id_int = int(categoria_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de categoría inválido'
                }), 400

            categoria = Categoria.query.get(categoria_id_int)

            if not categoria:
                return jsonify({
                    'success': False,
                    'message': 'Categoría no encontrada'
                }), 404

            return jsonify({
                'success': True,
                'data': categoria.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_categoria_by_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_all_categorias():
        """Obtener todas las categorías"""
        try:
            categorias = Categoria.query.order_by(Categoria.nombre).all()
            return jsonify({
                'success': True,
                'data': [categoria.to_json_safe() for categoria in categorias],
                'count': len(categorias)
            }), 200
        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_all_categorias")
            return safe_error_response("Error interno del servidor", 500)

    # ==================== PRODUCTOS ====================

    @staticmethod
    def create_producto():
        """Crear un nuevo producto"""
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

            categoria_id = data.get('categoria_id')
            if categoria_id is not None:
                try:
                    categoria_id = int(categoria_id)
                    if not Categoria.query.get(categoria_id):
                        return jsonify({
                            'success': False,
                            'message': 'Categoría no encontrada'
                        }), 404
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'categoria_id debe ser un número entero'
                    }), 400

            producto = Producto.create_producto(
                nombre=nombre,
                marca=data.get('marca'),
                categoria_id=categoria_id,
                descripcion=data.get('descripcion'),
                url_producto=data.get('url_producto'),
                url_imagen=data.get('url_imagen'),
                codigo_fuente=data.get('codigo_fuente'),
                producto_hash=data.get('producto_hash')
            )

            db.session.add(producto)
            db.session.commit()

            logger.info(f"Producto creado exitosamente - Nombre: {nombre}")

            return jsonify({
                'success': True,
                'message': 'Producto creado exitosamente',
                'data': producto.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_producto: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_producto")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al crear producto'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_producto")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_producto_by_id(producto_id):
        """Obtener producto por ID"""
        try:
            try:
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de producto inválido'
                }), 400

            producto = Producto.query.get(producto_uuid)

            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'data': producto.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_producto_by_id")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def search_productos_by_nombre():
        """Buscar productos por nombre"""
        try:
            nombre = request.args.get('nombre')

            if not nombre:
                return jsonify({
                    'success': False,
                    'message': 'nombre es requerido como query parameter'
                }), 400

            productos = Producto.get_by_nombre(nombre)

            return jsonify({
                'success': True,
                'data': [producto.to_json_safe() for producto in productos],
                'count': len(productos)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.search_productos_by_nombre")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_productos_by_categoria(categoria_id):
        """Obtener productos por categoría"""
        try:
            try:
                categoria_id_int = int(categoria_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de categoría inválido'
                }), 400

            categoria = Categoria.query.get(categoria_id_int)
            if not categoria:
                return jsonify({
                    'success': False,
                    'message': 'Categoría no encontrada'
                }), 404

            productos = Producto.get_by_categoria(categoria_id_int)

            return jsonify({
                'success': True,
                'data': [producto.to_json_safe() for producto in productos],
                'count': len(productos)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_productos_by_categoria")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_producto_by_hash():
        """Obtener producto por hash"""
        try:
            producto_hash = request.args.get('hash')

            if not producto_hash:
                return jsonify({
                    'success': False,
                    'message': 'hash es requerido como query parameter'
                }), 400

            producto = Producto.get_by_hash(producto_hash)

            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'data': producto.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_producto_by_hash")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_all_productos():
        """Obtener todos los productos con paginación básica"""
        try:
            limit = request.args.get('limit', default=100, type=int)
            productos = Producto.query.limit(limit).all()

            return jsonify({
                'success': True,
                'data': [producto.to_json_safe() for producto in productos],
                'count': len(productos)
            }), 200
        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_all_productos")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    @jwt_required()
    def update_producto(producto_id):
        """Actualizar producto"""
        try:
            try:
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de producto inválido'
                }), 400

            producto = Producto.query.get(producto_uuid)

            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            updatable_fields = [
                'nombre', 'marca', 'descripcion', 'url_producto',
                'url_imagen', 'codigo_fuente'
            ]

            for field in updatable_fields:
                if field in data:
                    setattr(producto, field, data[field].strip() if isinstance(data[field], str) else data[field])

            if 'categoria_id' in data:
                categoria_id = data['categoria_id']
                if categoria_id is not None:
                    try:
                        categoria_id = int(categoria_id)
                        if not Categoria.query.get(categoria_id):
                            return jsonify({
                                'success': False,
                                'message': 'Categoría no encontrada'
                            }), 404
                    except (ValueError, TypeError):
                        return jsonify({
                            'success': False,
                            'message': 'categoria_id debe ser un número entero'
                        }), 400
                producto.categoria_id = categoria_id

            producto.update_timestamp()
            db.session.commit()

            logger.info(f"Producto actualizado exitosamente - ID: {producto_id}")

            return jsonify({
                'success': True,
                'message': 'Producto actualizado exitosamente',
                'data': producto.to_json_safe()
            }), 200

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en update_producto: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.update_producto")
            return safe_error_response("Error interno del servidor", 500)

    # ==================== PRODUCTO NUTRICION ====================

    @staticmethod
    def create_nutricion():
        """Crear información nutricional para un producto"""
        try:
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
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'producto_id debe ser un UUID válido'
                }), 400

            producto = Producto.query.get(producto_uuid)
            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            nutricion_existente = ProductoNutricion.get_by_producto(producto_uuid)
            if nutricion_existente:
                return jsonify({
                    'success': False,
                    'message': 'Este producto ya tiene información nutricional'
                }), 409

            def to_decimal(value):
                if value is None:
                    return None
                try:
                    return Decimal(str(value))
                except (InvalidOperation, ValueError, TypeError):
                    return None

            nutricion = ProductoNutricion.create_nutricion(
                producto_id=producto_uuid,
                porcion_g=to_decimal(data.get('porcion_g')),
                calorias_kcal=to_decimal(data.get('calorias_kcal')),
                proteinas_g=to_decimal(data.get('proteinas_g')),
                grasas_totales_g=to_decimal(data.get('grasas_totales_g')),
                grasas_saturadas_g=to_decimal(data.get('grasas_saturadas_g')),
                carbohidratos_g=to_decimal(data.get('carbohidratos_g')),
                azucares_g=to_decimal(data.get('azucares_g')),
                fibra_g=to_decimal(data.get('fibra_g')),
                sodio_mg=to_decimal(data.get('sodio_mg')),
                colesterol_mg=to_decimal(data.get('colesterol_mg')),
                micronutrientes=data.get('micronutrientes'),
                ig=to_decimal(data.get('ig')),
                carga_glucemica=to_decimal(data.get('carga_glucemica')),
                fuente=data.get('fuente')
            )

            db.session.add(nutricion)
            db.session.commit()

            logger.info(f"Información nutricional creada exitosamente - Producto ID: {producto_id}")

            return jsonify({
                'success': True,
                'message': 'Información nutricional creada exitosamente',
                'data': nutricion.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_nutricion: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_nutricion")
            return jsonify({
                'success': False,
                'message': 'Error de integridad al crear información nutricional'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_nutricion")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_nutricion_by_producto(producto_id):
        """Obtener información nutricional por producto"""
        try:
            try:
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de producto inválido'
                }), 400

            nutricion = ProductoNutricion.get_by_producto(producto_uuid)

            if not nutricion:
                return jsonify({
                    'success': False,
                    'message': 'Información nutricional no encontrada'
                }), 404

            return jsonify({
                'success': True,
                'data': nutricion.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_nutricion_by_producto")
            return safe_error_response("Error interno del servidor", 500)

    # ==================== PRODUCTO SNAPSHOT ====================

    @staticmethod
    def create_snapshot():
        """Crear un snapshot de producto"""
        try:
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
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'producto_id debe ser un UUID válido'
                }), 400

            producto = Producto.query.get(producto_uuid)
            if not producto:
                return jsonify({
                    'success': False,
                    'message': 'Producto no encontrado'
                }), 404

            precio = None
            if 'precio' in data and data['precio'] is not None:
                try:
                    precio = Decimal(str(data['precio']))
                except (InvalidOperation, ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': 'precio debe ser un número válido'
                    }), 400

            snapshot = ProductoSnapshot.create_snapshot(
                producto_id=producto_uuid,
                precio=precio,
                unidad_medida=data.get('unidad_medida'),
                disponibilidad=data.get('disponibilidad', True),
                fuente=data.get('fuente'),
                impacto_ambiental=data.get('impacto_ambiental'),
                atributos_json=data.get('atributos_json')
            )

            db.session.add(snapshot)
            db.session.commit()

            logger.info(f"Snapshot creado exitosamente - Producto ID: {producto_id}")

            return jsonify({
                'success': True,
                'message': 'Snapshot creado exitosamente',
                'data': snapshot.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en create_snapshot: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_snapshot")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: ya existe un snapshot para este producto en esta fecha'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ProductosController.create_snapshot")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_snapshots_by_producto(producto_id):
        """Obtener snapshots por producto"""
        try:
            try:
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de producto inválido'
                }), 400

            limit = request.args.get('limit', type=int)
            snapshots = ProductoSnapshot.get_by_producto(producto_uuid, limit=limit)

            return jsonify({
                'success': True,
                'data': [snapshot.to_json_safe() for snapshot in snapshots],
                'count': len(snapshots)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_snapshots_by_producto")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_latest_snapshot_by_producto(producto_id):
        """Obtener el snapshot más reciente de un producto"""
        try:
            try:
                producto_uuid = uuid.UUID(producto_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'ID de producto inválido'
                }), 400

            snapshot = ProductoSnapshot.get_latest_by_producto(producto_uuid)

            if not snapshot:
                return jsonify({
                    'success': False,
                    'message': 'Snapshot no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'data': snapshot.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_latest_snapshot_by_producto")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_latest_snapshots_bulk():
        """Obtener últimos snapshots en bulk"""
        try:
            subquery = db.session.query(
                ProductoSnapshot.producto_id,
                func.max(ProductoSnapshot.fecha_captura).label('max_fecha')
            ).group_by(ProductoSnapshot.producto_id).subquery()

            latest_snapshots = db.session.query(ProductoSnapshot).join(
                subquery,
                (ProductoSnapshot.producto_id == subquery.c.producto_id) &
                (ProductoSnapshot.fecha_captura == subquery.c.max_fecha)
            ).all()

            return jsonify({
                "status": "success",
                "data": [
                    {
                        "producto_id": str(s.producto_id),
                        "precio": float(s.precio) if s.precio else None,
                        "disponibilidad": s.disponibilidad
                    } for s in latest_snapshots
                ]
            }), 200
        except Exception as e:
            log_exception(logger, e, context="ProductosController.get_latest_snapshots_bulk")
            return jsonify({"status": "error", "message": "Error interno del servidor"}), 500