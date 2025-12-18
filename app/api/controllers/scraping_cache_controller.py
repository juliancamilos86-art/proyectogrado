"""
Controlador para gestión de cache de scraping en NutriChat
"""
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from urllib.parse import unquote
from app.models.database import db
from app.models.scraping_cache import ScrapingCache
import logging

logger = logging.getLogger(__name__)


class ScrapingCacheController:
    @staticmethod
    def get_or_create_cache():
        """
        Obtener o crear cache (UPSERT por URL)
        
        Body JSON:
        {
            "url": "https://ejemplo.com",  // REQUERIDO
            "html_content": "<html>...",  // OPCIONAL
            "headers": {...},             // OPCIONAL
            "status_code": 200,           // OPCIONAL
            "valido_hasta": "2024-12-31T23:59:59Z"  // OPCIONAL
        }
        
        Response:
        {
            "success": true,
            "message": "Cache obtenido/creado exitosamente",
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
            
            url = data.get('url')
            
            if not url:
                return jsonify({
                    'success': False,
                    'message': 'url es requerido'
                }), 400
            
            # Validar que url sea una cadena válida
            if not isinstance(url, str) or not url.strip():
                return jsonify({
                    'success': False,
                    'message': 'url debe ser una cadena válida'
                }), 400
            
            # Buscar cache existente por URL
            cache = ScrapingCache.get_by_url(url)
            
            if cache:
                # Actualizar cache existente si se proporcionan nuevos datos
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
            
            # Crear nuevo cache
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
            
            # Guardar en base de datos
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
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error de integridad: URL duplicada'
            }), 409
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al obtener/crear cache: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500
    
    @staticmethod
    def get_cache_by_url(url):
        """
        Obtener cache por URL
        
        Parámetros:
        - url: URL del cache (codificada en la ruta)
        
        Query params:
        - include_html: true/false (por defecto false)
        
        Response:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            # Decodificar URL si viene codificada
            url_decoded = unquote(url)
            
            cache = ScrapingCache.get_by_url(url_decoded)
            
            if not cache:
                return jsonify({
                    'success': False,
                    'message': 'Cache no encontrado'
                }), 404
            
            # Verificar si se debe incluir HTML
            include_html = request.args.get('include_html', 'false').lower() == 'true'
            
            return jsonify({
                'success': True,
                'data': cache.to_dict(include_html=include_html)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al buscar cache por URL: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_valid_cache_by_url():
        """
        Obtener cache válido por URL
        
        Body JSON:
        {
            "url": "https://ejemplo.com"  // REQUERIDO
        }
        
        Response:
        {
            "success": true,
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
            logger.error(f"Error al buscar cache válido por URL: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_expired_caches():
        """
        Obtener caches expirados
        
        Query params:
        - limit: número máximo de resultados (por defecto sin límite)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            limit = request.args.get('limit', type=int)
            
            caches = ScrapingCache.get_expired(limit=limit)
            
            return jsonify({
                'success': True,
                'data': [cache.to_json_safe() for cache in caches],
                'count': len(caches)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener caches expirados: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def delete_expired_caches():
        """
        Eliminar caches expirados
        
        Body JSON (opcional):
        {
            "limit": 100  // OPCIONAL: límite de eliminaciones
        }
        
        Response:
        {
            "success": true,
            "message": "Caches expirados eliminados",
            "deleted_count": 5
        }
        """
        try:
            data = request.get_json() or {}
            limit = data.get('limit')
            
            # Obtener caches expirados
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
            logger.error(f"Error al eliminar caches expirados: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_recent_caches():
        """
        Obtener caches recientes
        
        Query params:
        - limit: número máximo de resultados (por defecto 100)
        
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
            
            caches = ScrapingCache.get_recent(limit=limit)
            
            return jsonify({
                'success': True,
                'data': [cache.to_json_safe() for cache in caches],
                'count': len(caches)
            }), 200
            
        except Exception as e:
            logger.error(f"Error al obtener caches recientes: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500
    
    @staticmethod
    def get_caches_by_status_code(status_code):
        """
        Obtener caches por código de estado HTTP
        
        Parámetros:
        - status_code: Código de estado HTTP (200, 404, 500, etc.)
        
        Response:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            status_code = int(status_code)
            
            if status_code < 100 or status_code > 599:
                return jsonify({
                    'success': False,
                    'message': 'status_code debe ser un código HTTP válido (100-599)'
                }), 400
            
            caches = ScrapingCache.get_by_status_code(status_code)
            
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
            logger.error(f"Error al buscar caches por status_code: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error interno del servidor'
            }), 500

