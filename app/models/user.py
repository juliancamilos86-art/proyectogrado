"""
Modelo de Usuario simplificado para NutriChat
Compatible con SQLite (testing) y PostgreSQL (producción)
"""

import uuid
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Text, Integer, Date, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from email_validator import validate_email, EmailNotValidError

from .database import db


class User(db.Model):
    """
    Modelo de Usuario simplificado que funciona en SQLite y PostgreSQL
    Autenticación únicamente por Telegram ID (sin contraseñas)
    """

    __tablename__ = 'usuarios'

    # Campos principales
    usuario_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Información básica
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)  # Opcional ahora
    telefono = Column(String, nullable=True)
    rol_id = Column(Integer, nullable=False, default=2)

    # Fechas y estado
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultima_conexion = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)

    # Información personal
    sexo = Column(String(10), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    peso_kg = Column(Numeric(5, 2), nullable=True)
    altura_cm = Column(Numeric(5, 2), nullable=True)

    # Perfil como texto JSON (compatible con SQLite y PostgreSQL)
    perfil_json = Column(Text, nullable=True)

    # Integración con Telegram (CAMPO PRINCIPAL PARA AUTENTICACIÓN)
    telegram_id = Column(BigInteger, nullable=False, unique=True)  # Ahora es obligatorio

    def __init__(self, **kwargs):
        if 'perfil_json' not in kwargs:
            kwargs['perfil_json'] = json.dumps({})
        super().__init__(**kwargs)

    def _get_perfil_data(self) -> Dict[str, Any]:
        """Obtener datos del perfil como diccionario"""
        if not self.perfil_json:
            return {}
        try:
            return json.loads(self.perfil_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _set_perfil_data(self, data: Dict[str, Any]) -> None:
        """Establecer datos del perfil"""
        self.perfil_json = json.dumps(data, default=str)

    @validates('email')
    def validate_email_format(self, key, email):
        """Validar formato de email (si se proporciona)"""
        if email is None or email == '':
            return None
        try:
            validated_email = validate_email(email)
            return validated_email.email
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {str(e)}")

    # ==================== MÉTODOS DE CREACIÓN ====================
    
    @classmethod
    def create_user(cls, telegram_id: int, nombre: str = None, **kwargs) -> 'User':
        """
        Crear un nuevo usuario con Telegram ID
        
        Args:
            telegram_id: ID único de Telegram (requerido)
            nombre: Nombre del usuario
            **kwargs: Campos adicionales opcionales
        
        Returns:
            User: Instancia del usuario creado
        
        Raises:
            ValueError: Si telegram_id no es válido
        """
        if not telegram_id:
            raise ValueError("telegram_id es requerido")
        
        if not isinstance(telegram_id, int):
            raise ValueError("telegram_id debe ser un número entero")
        
        # Generar email temporal si no se proporciona
        if 'email' not in kwargs or not kwargs['email']:
            kwargs['email'] = None
        
        user = cls(
            telegram_id=telegram_id,
            nombre=nombre,
            **kwargs
        )
        
        return user

    # ==================== PREFERENCIAS NUTRICIONALES ====================
    
    def set_nutritional_preferences(self, preferences: Dict[str, Any]) -> None:
        """Establecer preferencias nutricionales"""
        perfil_data = self._get_perfil_data()
        perfil_data['nutritional_preferences'] = preferences
        self._set_perfil_data(perfil_data)

    def get_nutritional_preferences(self) -> Dict[str, Any]:
        """Obtener preferencias nutricionales"""
        perfil_data = self._get_perfil_data()
        return perfil_data.get('nutritional_preferences', {})

    # ==================== PRESUPUESTO ====================
    
    def set_budget(self, monthly: Optional[Decimal] = None, weekly: Optional[Decimal] = None) -> None:
        """Establecer presupuesto mensual y/o semanal"""
        perfil_data = self._get_perfil_data()

        if monthly is not None:
            if monthly < 0:
                raise ValueError("El presupuesto mensual no puede ser negativo")
            perfil_data['budget_monthly'] = float(monthly)

        if weekly is not None:
            if weekly < 0:
                raise ValueError("El presupuesto semanal no puede ser negativo")
            perfil_data['budget_weekly'] = float(weekly)

        self._set_perfil_data(perfil_data)

    @property
    def budget_monthly(self) -> Optional[Decimal]:
        """Obtener presupuesto mensual"""
        perfil_data = self._get_perfil_data()
        value = perfil_data.get('budget_monthly')
        return Decimal(str(value)) if value is not None else None

    @property
    def budget_weekly(self) -> Optional[Decimal]:
        """Obtener presupuesto semanal"""
        perfil_data = self._get_perfil_data()
        value = perfil_data.get('budget_weekly')
        return Decimal(str(value)) if value is not None else None

    # ==================== PROPIEDADES DE CONVENIENCIA ====================
    
    @property
    def is_active(self) -> bool:
        """Verificar si el usuario está activo"""
        return self.activo

    @property
    def created_at(self) -> datetime:
        """Obtener fecha de registro"""
        return self.fecha_registro

    @property
    def id(self) -> uuid.UUID:
        """Obtener ID del usuario"""
        return self.usuario_id

    @property
    def age(self) -> Optional[int]:
        """Calcular edad del usuario"""
        if self.fecha_nacimiento:
            today = datetime.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    @property
    def bmi(self) -> Optional[float]:
        """Calcular índice de masa corporal (BMI)"""
        if self.peso_kg and self.altura_cm:
            height_m = float(self.altura_cm) / 100
            return round(float(self.peso_kg) / (height_m ** 2), 2)
        return None

    # ==================== SERIALIZACIÓN ====================
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convertir usuario a diccionario"""
        data = {
            'id': str(self.usuario_id),
            'email': self.email,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'rol_id': self.rol_id,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None,
            'activo': self.activo,
            'sexo': self.sexo,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'peso_kg': float(self.peso_kg) if self.peso_kg else None,
            'altura_cm': float(self.altura_cm) if self.altura_cm else None,
            'telegram_id': self.telegram_id,
            'age': self.age,
            'bmi': self.bmi,
            'nutritional_preferences': self.get_nutritional_preferences(),
            'budget_monthly': float(self.budget_monthly) if self.budget_monthly else None,
            'budget_weekly': float(self.budget_weekly) if self.budget_weekly else None,
        }

        if include_sensitive:
            data['perfil_data'] = self._get_perfil_data()

        return data

    def to_json_safe(self) -> Dict[str, Any]:
        """Convertir a JSON seguro (sin datos sensibles)"""
        return self.to_dict(include_sensitive=False)

    # ==================== MÉTODOS DE CONSULTA ====================
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Buscar usuario por email"""
        if not email:
            return None
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_telegram_id(cls, telegram_id: int) -> Optional['User']:
        """Buscar usuario por Telegram ID"""
        return cls.query.filter_by(telegram_id=telegram_id).first()

    def update_last_connection(self) -> None:
        """Actualizar última conexión del usuario"""
        self.ultima_conexion = datetime.utcnow()
        db.session.commit()

    # ==================== REPRESENTACIÓN ====================
    
    def __repr__(self) -> str:
        return f"<User telegram_id={self.telegram_id} - {self.nombre or 'Sin nombre'}>"

    def __str__(self) -> str:
        return f"{self.nombre or f'Usuario {self.telegram_id}'} ({'Activo' if self.activo else 'Inactivo'})"