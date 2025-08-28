"""
Modelo de Usuario simplificado para NutriChat
Compatible con SQLite (testing) y PostgreSQL (producción)
"""

import uuid
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

import bcrypt
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Text, Integer, Date, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from email_validator import validate_email, EmailNotValidError

from .database import db


class User(db.Model):
    """
    Modelo de Usuario simplificado que funciona en SQLite y PostgreSQL
    """
    
    __tablename__ = 'usuarios'
    
    # Campos principales
    usuario_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Información básica
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
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
    
    # Integración con Telegram
    telegram_id = Column(BigInteger, nullable=True)
    
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
        try:
            validated_email = validate_email(email)
            return validated_email.email
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {str(e)}")
    
    # Métodos de contraseña
    def set_password(self, password: str) -> None:
        if not password or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        perfil_data = self._get_perfil_data()
        perfil_data['password_hash'] = password_hash.decode('utf-8')
        self._set_perfil_data(perfil_data)
    
    def check_password(self, password: str) -> bool:
        if not password:
            return False
        
        perfil_data = self._get_perfil_data()
        stored_hash = perfil_data.get('password_hash')
        if not stored_hash:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    
    @property
    def password_hash(self) -> Optional[str]:
        perfil_data = self._get_perfil_data()
        return perfil_data.get('password_hash')
    
    # Preferencias nutricionales
    def set_nutritional_preferences(self, preferences: Dict[str, Any]) -> None:
        perfil_data = self._get_perfil_data()
        perfil_data['nutritional_preferences'] = preferences
        self._set_perfil_data(perfil_data)
    
    def get_nutritional_preferences(self) -> Dict[str, Any]:
        perfil_data = self._get_perfil_data()
        return perfil_data.get('nutritional_preferences', {})
    
    # Presupuesto
    def set_budget(self, monthly: Optional[Decimal] = None, weekly: Optional[Decimal] = None) -> None:
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
        perfil_data = self._get_perfil_data()
        value = perfil_data.get('budget_monthly')
        return Decimal(str(value)) if value is not None else None
    
    @property
    def budget_weekly(self) -> Optional[Decimal]:
        perfil_data = self._get_perfil_data()
        value = perfil_data.get('budget_weekly')
        return Decimal(str(value)) if value is not None else None
    
    # Propiedades de conveniencia
    @property
    def is_active(self) -> bool:
        return self.activo
    
    @property
    def created_at(self) -> datetime:
        return self.fecha_registro
    
    @property
    def id(self) -> uuid.UUID:
        return self.usuario_id
    
    @property
    def age(self) -> Optional[int]:
        if self.fecha_nacimiento:
            today = datetime.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    @property
    def bmi(self) -> Optional[float]:
        if self.peso_kg and self.altura_cm:
            height_m = float(self.altura_cm) / 100
            return round(float(self.peso_kg) / (height_m ** 2), 2)
        return None
    
    # Serialización
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
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
        return self.to_dict(include_sensitive=False)
    
    # Métodos de clase
    @classmethod
    def create_user(cls, email: str, password: str, **kwargs) -> 'User':
        user = cls(email=email, **kwargs)
        user.set_password(password)
        return user
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_telegram_id(cls, telegram_id: int) -> Optional['User']:
        return cls.query.filter_by(telegram_id=telegram_id).first()
    
    def update_last_connection(self) -> None:
        self.ultima_conexion = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self) -> str:
        return f"<User {self.email} - {self.nombre or 'Sin nombre'}>"
    
    def __str__(self) -> str:
        return f"{self.nombre or self.email} ({'Activo' if self.activo else 'Inactivo'})"
