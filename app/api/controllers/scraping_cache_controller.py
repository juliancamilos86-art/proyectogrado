"""
Controlador para gestión de cache de scraping en NutriChat
"""
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from urllib.parse import unquote
from app.models.database import db
from app.models.scraping_cache import ScrapingCache
from app.utils.security import safe_error_response, log_exception
import logging

logger = logging.getLogger(__name__)


class ScrapingCacheController:
    @staticmethod
    def get_or_create_cache():
        """Obtener o crear cache (UPSERT por URL)"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            url = data.get('url')

            if not url:
                return jsonify({
                    'success': False,
                    'message': 'url es requerido'
                }), 400

            if not isinstance(url, str) or not url.strip():
                return jsonify({
                    'success': False,
                    'message': 'url debe ser una cadena válida'
                }), 400

            cache = ScrapingCache.get_by_url(url)

            if cache:
                if 'html_content' in data:
                    cache.html_content = data['html_content']
                if 'headers' in data:
                    cache.set_headers(data['headers'])
                if 'status_code' in data:
                    cache.status_code = data['status_code']
                if 'valido_hasta' in data and data['valido_hasta']:
                    try:
                        cache.valido_hasta = datetime.fromisoformat(
                            data['valido_hasta'].replace('Z', '+00:00')
                        )
                    except (ValueError, AttributeError):
                        return jsonify({
                            'success': False,
                            'message': 'valido_hasta debe ser una fecha ISO válida'
                        }), 400

                db.session.commit()
                logger.info(f"Cache actualizado - URL: {url[:50]}...")

                return jsonify({
                    'success': True,
                    'message': 'Cache actualizado exitosamente',
                    'data': cache.to_json_safe()
                }), 200

            valido_hasta = None
            if 'valido_hasta' in data and data['valido_hasta']:
                try:
                    valido_hasta = datetime.fromisoformat(
                        data['valido_hasta'].replace('Z', '+00:00')
                    )
                except (ValueError, AttributeError):
                    return jsonify({
                        'success': False,
                        'message': 'valido_hasta debe ser una fecha ISO válida'
                    }), 400

            cache = ScrapingCache.create_cache(
                url=url,
                html_content=data.get('html_content'),
                headers=data.get('headers'),
                status_code=data.get('status_code'),
                valido_hasta=valido_hasta
            )

            db.session.add(cache)
            db.session.commit()

            logger.info(f"Cache creado exitosamente - URL: {url[:50]}...")

            return jsonify({
                'success': True,
                'message': 'Cache creado exitosamente',
                'data': cache.to_json_safe()
            }), 201

        except ValueError as e:
            db.session.rollback()
            logger.warning(f"ValueError en get_or_create_cache: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Datos inválidos en la solicitud'
            }), 400

        except IntegrityError as e:
            db.session.rollback()
            log_exception(logger, e, context="ScrapingCacheController.get_or_create_cache")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: URL duplicada'
            }), 409

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ScrapingCacheController.get_or_create_cache")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_cache_by_url(url):
        """Obtener cache por URL"""
        try:
            url_decoded = unquote(url)
            cache = ScrapingCache.get_by_url(url_decoded)

            if not cache:
                return jsonify({
                    'success': False,
                    'message': 'Cache no encontrado'
                }), 404

            include_html = request.args.get('include_html', 'false').lower() == 'true'

            return jsonify({
                'success': True,
                'data': cache.to_dict(include_html=include_html)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ScrapingCacheController.get_cache_by_url")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_valid_cache_by_url():
        """Obtener cache válido por URL"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No se enviaron datos'
                }), 400

            url = data.get('url')

            if not url:
                return jsonify({
                    'success': False,
                    'message': 'url es requerido'
                }), 400

            if not isinstance(url, str) or not url.strip():
                return jsonify({
                    'success': False,
                    'message': 'url debe ser una cadena válida'
                }), 400

            cache = ScrapingCache.get_valid_by_url(url)

            if not cache:
                return jsonify({
                    'success': False,
                    'message': 'Cache válido no encontrado'
                }), 404

            return jsonify({
                'success': True,
                'data': cache.to_json_safe()
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ScrapingCacheController.get_valid_cache_by_url")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_expired_caches():
        """Obtener caches expirados"""
        try:
            limit = request.args.get('limit', type=int)
            caches = ScrapingCache.get_expired(limit=limit)

            return jsonify({
                'success': True,
                'data': [cache.to_json_safe() for cache in caches],
                'count': len(caches)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ScrapingCacheController.get_expired_caches")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def delete_expired_caches():
        """Eliminar caches expirados"""
        try:
            data = request.get_json() or {}
            limit = data.get('limit')

            expired_caches = ScrapingCache.get_expired(limit=limit)
            deleted_count = 0

            for cache in expired_caches:
                db.session.delete(cache)
                deleted_count += 1

            db.session.commit()

            logger.info(f"Eliminados {deleted_count} caches expirados")

            return jsonify({
                'success': True,
                'message': 'Caches expirados eliminados exitosamente',
                'deleted_count': deleted_count
            }), 200

        except Exception as e:
            db.session.rollback()
            log_exception(logger, e, context="ScrapingCacheController.delete_expired_caches")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_recent_caches():
        """Obtener caches recientes"""
        try:
            limit = request.args.get('limit', default=100, type=int)

            if limit < 1 or limit > 1000:
                return jsonify({
                    'success': False,
                    'message': 'limit debe estar entre 1 y 1000'
                }), 400

            caches = ScrapingCache.get_recent(limit=limit)

            return jsonify({
                'success': True,
                'data': [cache.to_json_safe() for cache in caches],
                'count': len(caches)
            }), 200

        except Exception as e:
            log_exception(logger, e, context="ScrapingCacheController.get_recent_caches")
            return safe_error_response("Error interno del servidor", 500)

    @staticmethod
    def get_caches_by_status_code(status_code):
        """Obtener caches por código de estado HTTP"""
        try:
            status_code_int = int(status_code)

            if status_code_int < 100 or status_code_int > 599:
                return jsonify({
                    'success': False,
                    'message': 'status_code debe ser un código HTTP válido (100-599)'
                }), 400

            caches = ScrapingCache.get_by_status_code(status_code_int)

            return jsonify({
                'success': True,
                'data': [cache.to_json_safe() for cache in caches],
                'count': len(caches)
            }), 200

        except ValueError:
            return jsonify({
                'success': False,
                'message': 'status_code debe ser un número entero'
            }), 400

        except Exception as e:
            log_exception(logger, e, context="ScrapingCacheController.get_caches_by_status_code")
            return safe_error_response("Error interno del servidor", 500)