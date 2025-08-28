#!/usr/bin/env python3
"""
Script para probar la conexión con Supabase
Ejecutar: python test_supabase_connection.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

def test_database_connection():
    """Probar conexión PostgreSQL con Supabase"""
    print("🔗 Probando conexión PostgreSQL...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url or 'YOUR_PASSWORD_HERE' in database_url:
        print("❌ ERROR: DATABASE_URL no configurada o falta la contraseña")
        print("   Actualiza la variable DATABASE_URL en el archivo .env")
        return False
    
    try:
        # Crear engine de SQLAlchemy
        engine = create_engine(database_url)
        
        # Probar conexión
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexión PostgreSQL exitosa!")
            print(f"   Versión: {version}")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión PostgreSQL: {e}")
        return False

def test_supabase_client():
    """Probar cliente de Supabase"""
    print("\n🔗 Probando cliente Supabase...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key or 'your_supabase' in supabase_key:
        print("❌ ERROR: Credenciales de Supabase no configuradas")
        print("   Configura SUPABASE_URL y SUPABASE_ANON_KEY en .env")
        return False
    
    try:
        # Crear cliente de Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Probar consulta simple
        response = supabase.table('_realtime_schema').select("*").limit(1).execute()
        print("✅ Cliente Supabase conectado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error cliente Supabase: {e}")
        return False

def show_configuration():
    """Mostrar configuración actual"""
    print("📋 Configuración actual:")
    print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL', 'No configurada')}")
    print(f"   DATABASE_URL: {'Configurada' if os.getenv('DATABASE_URL') and 'YOUR_PASSWORD' not in os.getenv('DATABASE_URL', '') else 'Pendiente contraseña'}")
    print(f"   SUPABASE_ANON_KEY: {'Configurada' if os.getenv('SUPABASE_ANON_KEY') and 'your_supabase' not in os.getenv('SUPABASE_ANON_KEY', '') else 'No configurada'}")

def main():
    print("🚀 Probando conexión con Supabase\n")
    
    show_configuration()
    print()
    
    # Probar conexiones
    db_ok = test_database_connection()
    supabase_ok = test_supabase_client()
    
    print("\n📊 Resumen:")
    if db_ok and supabase_ok:
        print("✅ ¡Todas las conexiones funcionan correctamente!")
        print("   Ya puedes usar Supabase en tu aplicación.")
    elif db_ok:
        print("⚠️  Conexión PostgreSQL OK, pero falta configurar cliente Supabase")
    elif supabase_ok:
        print("⚠️  Cliente Supabase OK, pero falta configurar PostgreSQL")
    else:
        print("❌ Revisa tu configuración en el archivo .env")
        print("\n🔧 Pasos pendientes:")
        print("   1. Reemplaza YOUR_PASSWORD_HERE con tu contraseña real")
        print("   2. Agrega tu SUPABASE_ANON_KEY desde el panel de Supabase")
        print("   3. Verifica tu SUPABASE_URL")

if __name__ == "__main__":
    main()
