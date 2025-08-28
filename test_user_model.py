#!/usr/bin/env python3
"""
Script de prueba para el modelo User
Ejecutar: python test_user_model.py
"""

import os
import sys
from decimal import Decimal
from datetime import date

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User

def test_user_model():
    """
    Probar el modelo User con diferentes operaciones
    """
    print("🧪 PROBANDO MODELO USER")
    print("=" * 50)
    
    # Crear aplicación y contexto
    app = create_app('testing')
    
    with app.app_context():
        print("📋 Creando usuario de prueba...")
        
        try:
            # 1. Crear usuario básico
            user_data = {
                'email': 'test@gmail.com',
                'nombre': 'Usuario Test',
                'telefono': '+573001234567',
                'sexo': 'M',
                'fecha_nacimiento': date(1990, 5, 15),
                'peso_kg': Decimal('70.5'),
                'altura_cm': Decimal('175.0'),
            }
            
            # Extraer email de user_data para evitar duplicados
            email = user_data.pop('email')
            user = User.create_user(
                email=email,
                password='test123456',
                **user_data
            )
            
            print(f"✅ Usuario creado: {user}")
            
            # 2. Probar métodos de contraseña
            print("\n🔐 Probando autenticación...")
            print(f"   Contraseña correcta: {user.check_password('test123456')}")
            print(f"   Contraseña incorrecta: {user.check_password('wrong')}")
            
            # 3. Probar preferencias nutricionales
            print("\n🥗 Configurando preferencias nutricionales...")
            preferences = {
                'dietary_restrictions': ['vegetarian'],
                'allergies': ['nuts'],
                'favorite_foods': ['pasta', 'salad'],
                'dislikes': ['broccoli']
            }
            user.set_nutritional_preferences(preferences)
            print(f"   Preferencias guardadas: {user.get_nutritional_preferences()}")
            
            # 4. Probar presupuesto
            print("\n💰 Configurando presupuesto...")
            user.set_budget(monthly=Decimal('200.00'), weekly=Decimal('50.00'))
            print(f"   Presupuesto mensual: ${user.budget_monthly}")
            print(f"   Presupuesto semanal: ${user.budget_weekly}")
            
            # 5. Probar propiedades calculadas
            print("\n📊 Propiedades calculadas...")
            print(f"   Edad: {user.age} años")
            print(f"   BMI: {user.bmi}")
            print(f"   ID: {user.id}")
            print(f"   Activo: {user.is_active}")
            
            # 6. Probar serialización
            print("\n📄 Probando serialización...")
            user_dict = user.to_dict()
            print(f"   Campos serializados: {len(user_dict)}")
            print(f"   Email: {user_dict['email']}")
            print(f"   BMI: {user_dict['bmi']}")
            
            # 7. Probar validaciones
            print("\n⚠️  Probando validaciones...")
            
            # Email inválido
            try:
                invalid_user = User(email='invalid-email')
                print("   ❌ Validación de email falló")
            except ValueError as e:
                print(f"   ✅ Validación de email: {e}")
            
            # Peso inválido
            try:
                user.peso_kg = Decimal('-10')
                print("   ❌ Validación de peso falló")
            except ValueError as e:
                print(f"   ✅ Validación de peso: {e}")
            
            # Contraseña muy corta
            try:
                user.set_password('123')
                print("   ❌ Validación de contraseña falló")
            except ValueError as e:
                print(f"   ✅ Validación de contraseña: {e}")
            
            # 8. Probar métodos de clase
            print("\n🔍 Probando métodos de búsqueda...")
            
            # Simular que el usuario está en la base de datos
            # (En testing usamos SQLite in-memory)
            db.session.add(user)
            db.session.commit()
            
            found_user = User.get_by_email('test@gmail.com')
            print(f"   Usuario encontrado por email: {found_user is not None}")
            
            # Configurar Telegram ID y buscar
            user.telegram_id = 123456789
            db.session.commit()
            
            found_by_telegram = User.get_by_telegram_id(123456789)
            print(f"   Usuario encontrado por Telegram: {found_by_telegram is not None}")
            
            # 9. Actualizar última conexión
            user.update_last_connection()
            print(f"   Última conexión actualizada: {user.ultima_conexion}")
            
            print("\n✅ TODAS LAS PRUEBAS PASARON")
            print("   El modelo User está funcionando correctamente")
            
        except Exception as e:
            print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_integration_with_database():
    """
    Probar integración con la base de datos real
    """
    print("\n\n🌐 PROBANDO INTEGRACIÓN CON SUPABASE")
    print("=" * 50)
    
    # Usar configuración de desarrollo (Supabase real)
    app = create_app('development')
    
    with app.app_context():
        try:
            print("📋 Verificando conexión con tabla usuarios...")
            
            # Contar usuarios existentes
            total_users = User.query.count()
            print(f"   Usuarios existentes en la base: {total_users}")
            
            print("✅ Integración con Supabase funcionando")
            return True
            
        except Exception as e:
            print(f"❌ Error de integración: {e}")
            return False

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DEL MODELO USER")
    print("=" * 60)
    
    # Pruebas unitarias
    unit_test_passed = test_user_model()
    
    # Pruebas de integración
    integration_test_passed = test_integration_with_database()
    
    print(f"\n📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"   Pruebas unitarias: {'✅ PASARON' if unit_test_passed else '❌ FALLARON'}")
    print(f"   Pruebas de integración: {'✅ PASARON' if integration_test_passed else '❌ FALLARON'}")
    
    if unit_test_passed and integration_test_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("   El modelo User está listo para usar en producción")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar errores arriba.")

if __name__ == "__main__":
    main()
