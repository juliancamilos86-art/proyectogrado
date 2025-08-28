#!/usr/bin/env python3
"""
Analizador de Base de Datos Supabase
Ejecutar: python database_analyzer.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, inspect
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

def get_database_connection():
    """Crear conexión a la base de datos"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL no configurada")
        return None
    
    try:
        engine = create_engine(database_url)
        return engine
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def analyze_database_schema(engine):
    """Analizar el esquema de la base de datos"""
    print("🔍 Analizando esquema de la base de datos...\n")
    
    try:
        # Obtener información del inspector
        inspector = inspect(engine)
        
        # Obtener todos los esquemas
        schemas = inspector.get_schema_names()
        print(f"📚 Esquemas disponibles: {', '.join(schemas)}")
        
        # Analizar el esquema public
        print(f"\n📋 Tablas en el esquema 'public':")
        tables = inspector.get_table_names(schema='public')
        
        if not tables:
            print("   ⚠️  No se encontraron tablas en el esquema 'public'")
            return {}
        
        table_info = {}
        for table_name in tables:
            print(f"\n   📊 Tabla: {table_name}")
            
            # Obtener columnas
            columns = inspector.get_columns(table_name, schema='public')
            print(f"      Columnas ({len(columns)}):")
            
            column_details = []
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f", DEFAULT: {col['default']}" if col['default'] else ""
                print(f"        - {col['name']}: {col['type']} ({nullable}{default})")
                column_details.append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': col['default']
                })
            
            # Obtener claves primarias
            pk_constraint = inspector.get_pk_constraint(table_name, schema='public')
            if pk_constraint['constrained_columns']:
                print(f"      🔑 Clave primaria: {', '.join(pk_constraint['constrained_columns'])}")
            
            # Obtener claves foráneas
            fk_constraints = inspector.get_foreign_keys(table_name, schema='public')
            if fk_constraints:
                print(f"      🔗 Claves foráneas:")
                for fk in fk_constraints:
                    print(f"        - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            
            # Obtener índices
            indexes = inspector.get_indexes(table_name, schema='public')
            if indexes:
                print(f"      📇 Índices:")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"        - {idx['name']}: {', '.join(idx['column_names'])} {unique}")
            
            table_info[table_name] = {
                'columns': column_details,
                'primary_key': pk_constraint['constrained_columns'],
                'foreign_keys': fk_constraints,
                'indexes': indexes
            }
        
        return table_info
        
    except Exception as e:
        print(f"❌ Error analizando esquema: {e}")
        return {}

def get_table_counts(engine, tables):
    """Obtener conteo de registros por tabla"""
    print(f"\n📊 Conteo de registros por tabla:")
    
    counts = {}
    with engine.connect() as connection:
        for table in tables:
            try:
                result = connection.execute(text(f"SELECT COUNT(*) FROM public.{table}"))
                count = result.fetchone()[0]
                counts[table] = count
                print(f"   {table}: {count:,} registros")
            except Exception as e:
                print(f"   {table}: Error - {e}")
                counts[table] = "Error"
    
    return counts

def sample_data_from_tables(engine, tables, limit=3):
    """Obtener datos de muestra de cada tabla"""
    print(f"\n🔬 Datos de muestra (primeros {limit} registros):")
    
    with engine.connect() as connection:
        for table in tables:
            try:
                print(f"\n   📋 Tabla: {table}")
                result = connection.execute(text(f"SELECT * FROM public.{table} LIMIT {limit}"))
                rows = result.fetchall()
                columns = result.keys()
                
                if not rows:
                    print("      (Sin datos)")
                    continue
                
                # Mostrar cabeceras
                print(f"      Columnas: {', '.join(columns)}")
                
                # Mostrar datos
                for i, row in enumerate(rows, 1):
                    row_data = []
                    for value in row:
                        if value is None:
                            row_data.append("NULL")
                        elif isinstance(value, str) and len(value) > 50:
                            row_data.append(f"{value[:47]}...")
                        else:
                            row_data.append(str(value))
                    print(f"      Fila {i}: {' | '.join(row_data)}")
                    
            except Exception as e:
                print(f"      Error: {e}")

def check_supabase_specific_tables(engine):
    """Verificar tablas específicas de Supabase"""
    print(f"\n🔧 Verificando configuración de Supabase:")
    
    supabase_checks = [
        ("auth.users", "Sistema de autenticación"),
        ("storage.buckets", "Sistema de almacenamiento"),
        ("public.profiles", "Perfiles de usuario (común)"),
    ]
    
    with engine.connect() as connection:
        for table, description in supabase_checks:
            try:
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"   ✅ {table}: {count} registros - {description}")
            except Exception as e:
                print(f"   ❌ {table}: No disponible - {description}")

def generate_summary_report(table_info, counts):
    """Generar reporte resumen"""
    print(f"\n📋 RESUMEN DE LA BASE DE DATOS")
    print("=" * 50)
    
    total_tables = len(table_info)
    total_records = sum(count for count in counts.values() if isinstance(count, int))
    
    print(f"📊 Estadísticas generales:")
    print(f"   - Total de tablas: {total_tables}")
    print(f"   - Total de registros: {total_records:,}")
    
    if table_info:
        print(f"\n📋 Análisis por tabla:")
        for table, info in table_info.items():
            count = counts.get(table, 0)
            num_columns = len(info['columns'])
            has_pk = bool(info['primary_key'])
            has_fk = bool(info['foreign_keys'])
            
            print(f"   {table}:")
            print(f"     - Registros: {count:,}")
            print(f"     - Columnas: {num_columns}")
            print(f"     - Clave primaria: {'Sí' if has_pk else 'No'}")
            print(f"     - Claves foráneas: {'Sí' if has_fk else 'No'}")
    
    print(f"\n💡 Recomendaciones:")
    if total_tables == 0:
        print("   - La base de datos está vacía. Considera crear tablas para tu aplicación.")
    else:
        print("   - Base de datos configurada. Puedes comenzar a desarrollar tu aplicación.")
        print("   - Considera implementar Row Level Security (RLS) para mayor seguridad.")

def main():
    print("🚀 Analizador de Base de Datos Supabase")
    print("=" * 50)
    
    # Conectar a la base de datos
    engine = get_database_connection()
    if not engine:
        return
    
    # Analizar esquema
    table_info = analyze_database_schema(engine)
    
    if not table_info:
        print("\n⚠️  No se encontraron tablas para analizar.")
        print("   Esto puede ser normal si es una base de datos nueva.")
    else:
        # Obtener conteos
        tables = list(table_info.keys())
        counts = get_table_counts(engine, tables)
        
        # Obtener datos de muestra
        sample_data_from_tables(engine, tables)
        
        # Generar reporte
        generate_summary_report(table_info, counts)
    
    # Verificar tablas de Supabase
    check_supabase_specific_tables(engine)
    
    print(f"\n✅ Análisis completado. La conexión con Supabase está funcionando correctamente.")

if __name__ == "__main__":
    main()
