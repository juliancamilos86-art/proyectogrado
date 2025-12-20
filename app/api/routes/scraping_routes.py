"""
Rutas de scraping cache: gestión de cache de scraping
"""
from flask import Blueprint
from app.api.controllers.scraping_cache_controller import ScrapingCacheController

# Crear blueprint para rutas de scraping
scraping_bp = Blueprint('scraping', __name__)


# ============================================================
# SCRAPING CACHE (Uso interno del scraper)
# ============================================================

@scraping_bp.route('/scraping/cache', methods=['POST'])
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
    return ScrapingCacheController.get_or_create_cache()


@scraping_bp.route('/scraping/cache/url/<path:url>', methods=['GET'])
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
    return ScrapingCacheController.get_cache_by_url(url)


@scraping_bp.route('/scraping/cache/valid', methods=['POST'])
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
    return ScrapingCacheController.get_valid_cache_by_url()


@scraping_bp.route('/scraping/cache/expired', methods=['GET'])
def get_expired_caches():
    """
    Obtener caches expirados
    
    Query params:
    - limit: número máximo de resultados (por defecto sin límite)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 5
    }
    """
    return ScrapingCacheController.get_expired_caches()


@scraping_bp.route('/scraping/cache/expired', methods=['DELETE'])
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
    return ScrapingCacheController.delete_expired_caches()


@scraping_bp.route('/scraping/cache/recent', methods=['GET'])
def get_recent_caches():
    """
    Obtener caches recientes
    
    Query params:
    - limit: número máximo de resultados (por defecto 100, máximo 1000)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 10
    }
    """
    return ScrapingCacheController.get_recent_caches()


@scraping_bp.route('/scraping/cache/status/<int:status_code>', methods=['GET'])
def get_caches_by_status_code(status_code):
    """
    Obtener caches por código de estado HTTP
    
    Parámetros:
    - status_code: Código de estado HTTP (200, 404, 500, etc.)
    
    Response:
    {
        "success": true,
        "data": [...],
        "count": 3
    }
    """
    return ScrapingCacheController.get_caches_by_status_code(status_code)


