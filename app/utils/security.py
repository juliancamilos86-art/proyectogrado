"""Módulo de seguridad centralizado para respuestas HTTP y logging seguro"""
import logging
import traceback
from functools import wraps
from flask import jsonify, request, current_app

def safe_error_response(message="Error interno del servidor", status=500, details=None):
    """
    Retorna una respuesta HTTP segura (sin exponer detalles internos)
    """
    response = {"error": message, "status": status}

    # Solo mostrar detalles en modo debug
    if details and current_app and current_app.config.get('DEBUG', False):
        response["details"] = details

    return jsonify(response), status

def log_exception(logger, exc, context=None):
    """
    Loguea una excepción de forma segura
    """
    log_message = f"Exception: {type(exc).__name__}: {str(exc)}"
    if context:
        log_message = f"[{context}] {log_message}"

    logger.error(log_message)
    logger.debug(traceback.format_exc())

def sanitize_log_id(id_value):
    """Sanitiza IDs para logging (evita PII)"""
    if id_value is None:
        return "None"
    # Para Telegram IDs, mostramos solo los últimos 4 dígitos
    id_str = str(id_value)
    if len(id_str) > 4:
        return f"...{id_str[-4:]}"
    return id_str

def handle_errors(logger=None):
    """Decorador para manejo seguro de errores en endpoints"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(f.__module__)
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                logger.warning(f"ValueError: {str(e)}")
                return safe_error_response("Datos inválidos en la solicitud", 400)
            except Exception as e:
                log_exception(logger, e, context=f.__name__)
                return safe_error_response("Error interno del servidor", 500)
        return wrapped
    return decorator

def sanitize_telegram_id(telegram_id):
    """Sanitiza específicamente IDs de Telegram para logging"""
    if telegram_id is None:
        return "None"
    # Convertir a string y mostrar solo últimos 4 caracteres
    id_str = str(telegram_id)
    if len(id_str) <= 4:
        return "***"
    return f"...{id_str[-4:]}"