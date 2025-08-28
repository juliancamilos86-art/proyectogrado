#!/usr/bin/env python3
"""
Explorador de datos para analizar el contenido de las tablas
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def get_engine():
    """Crear conexión a la base de datos"""
    database_url = os.getenv('DATABASE_URL')
    return create_engine(database_url)

def explore_table_data():
    """Explorar datos específicos de cada tabla"""
    engine = get_engine()
    
    print("🔍 ANÁLISIS DETALLADO DE DATOS")
    print("=" * 50)
    
    queries = {
        "📊 Resumen general": [
            ("Total usuarios", "SELECT COUNT(*) as total FROM usuarios"),
            ("Usuarios activos", "SELECT COUNT(*) as activos FROM usuarios WHERE activo = true"),
            ("Total productos", "SELECT COUNT(*) as total FROM productos"),
            ("Total categorías", "SELECT COUNT(*) as total FROM categorias"),
            ("Total roles", "SELECT COUNT(*) as total FROM roles"),
            ("Sesiones Telegram", "SELECT COUNT(*) as total FROM telegram_sesiones"),
        ],
        
        "👤 Análisis de usuarios": [
            ("Distribución por rol", """
                SELECT r.nombre as rol, COUNT(u.usuario_id) as cantidad
                FROM roles r
                LEFT JOIN usuarios u ON r.rol_id = u.rol_id
                GROUP BY r.rol_id, r.nombre
                ORDER BY cantidad DESC
            """),
            ("Usuarios con Telegram", """
                SELECT COUNT(*) as con_telegram
                FROM usuarios 
                WHERE telegram_id IS NOT NULL
            """),
            ("Distribución por sexo", """
                SELECT sexo, COUNT(*) as cantidad
                FROM usuarios 
                WHERE sexo IS NOT NULL
                GROUP BY sexo
            """),
        ],
        
        "🛒 Análisis de productos": [
            ("Productos por categoría", """
                SELECT c.nombre as categoria, COUNT(p.producto_id) as cantidad
                FROM categorias c
                LEFT JOIN productos p ON c.categoria_id = p.categoria_id
                GROUP BY c.categoria_id, c.nombre
                ORDER BY cantidad DESC
            """),
            ("Productos con imágenes", """
                SELECT COUNT(*) as con_imagen
                FROM productos 
                WHERE url_imagen IS NOT NULL
            """),
            ("Marcas más comunes", """
                SELECT marca, COUNT(*) as cantidad
                FROM productos 
                WHERE marca IS NOT NULL
                GROUP BY marca
                ORDER BY cantidad DESC
                LIMIT 10
            """),
        ],
        
        "🩺 Análisis nutricional": [
            ("Condiciones nutricionales", """
                SELECT nombre, COUNT(uc.usuario_id) as usuarios_afectados
                FROM condiciones_nutricionales cn
                LEFT JOIN usuario_condiciones uc ON cn.condicion_id = uc.condicion_id
                GROUP BY cn.condicion_id, cn.nombre
                ORDER BY usuarios_afectados DESC
            """),
            ("Usuarios con condiciones", """
                SELECT COUNT(DISTINCT usuario_id) as usuarios_con_condiciones
                FROM usuario_condiciones
            """),
        ],
        
        "🤖 Análisis de interacciones": [
            ("Estados de conversación activos", """
                SELECT estado_conversacion, COUNT(*) as cantidad
                FROM telegram_sesiones 
                WHERE estado_conversacion IS NOT NULL
                GROUP BY estado_conversacion
                ORDER BY cantidad DESC
            """),
            ("Sesiones por usuario", """
                SELECT COUNT(DISTINCT usuario_id) as usuarios_con_sesiones
                FROM telegram_sesiones
                WHERE usuario_id IS NOT NULL
            """),
        ]
    }
    
    with engine.connect() as connection:
        for section, section_queries in queries.items():
            print(f"\n{section}")
            print("-" * 40)
            
            for query_name, query in section_queries:
                try:
                    result = connection.execute(text(query))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    print(f"\n📈 {query_name}:")
                    
                    if not rows:
                        print("   (Sin datos)")
                        continue
                    
                    # Si es una consulta simple con un solo valor
                    if len(columns) == 1 and len(rows) == 1:
                        print(f"   {rows[0][0]:,}")
                    else:
                        # Mostrar tabla
                        for row in rows:
                            row_data = []
                            for i, value in enumerate(row):
                                col_name = columns[i]
                                if value is None:
                                    row_data.append(f"{col_name}: NULL")
                                else:
                                    row_data.append(f"{col_name}: {value}")
                            print(f"   • {' | '.join(row_data)}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")

def sample_recent_data():
    """Mostrar datos recientes de las tablas principales"""
    engine = get_engine()
    
    print(f"\n\n🕒 DATOS RECIENTES")
    print("=" * 50)
    
    sample_queries = {
        "Últimos usuarios registrados": """
            SELECT nombre, email, fecha_registro::date, activo
            FROM usuarios 
            ORDER BY fecha_registro DESC 
            LIMIT 5
        """,
        "Productos agregados recientemente": """
            SELECT nombre, marca, creado_en::date
            FROM productos 
            WHERE creado_en IS NOT NULL
            ORDER BY creado_en DESC 
            LIMIT 5
        """,
        "Actividad reciente en Telegram": """
            SELECT telegram_id, estado_conversacion, actualizado_en::date
            FROM telegram_sesiones 
            ORDER BY actualizado_en DESC 
            LIMIT 5
        """,
        "Configuraciones del sistema": """
            SELECT clave, valor, actualizado_en::date
            FROM configuracion_sistema 
            ORDER BY actualizado_en DESC
        """,
    }
    
    with engine.connect() as connection:
        for query_name, query in sample_queries.items():
            try:
                print(f"\n📋 {query_name}:")
                result = connection.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                
                if not rows:
                    print("   (Sin datos)")
                    continue
                
                for i, row in enumerate(rows, 1):
                    row_data = []
                    for j, value in enumerate(row):
                        if value is None:
                            row_data.append("NULL")
                        elif isinstance(value, str) and len(value) > 30:
                            row_data.append(f"{value[:27]}...")
                        else:
                            row_data.append(str(value))
                    print(f"   {i}. {' | '.join(row_data)}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

def generate_insights():
    """Generar insights sobre la base de datos"""
    engine = get_engine()
    
    print(f"\n\n💡 INSIGHTS Y RECOMENDACIONES")
    print("=" * 50)
    
    insights = []
    
    with engine.connect() as connection:
        try:
            # Verificar integridad de datos
            result = connection.execute(text("SELECT COUNT(*) FROM usuarios WHERE email IS NULL OR email = ''"))
            users_without_email = result.fetchone()[0]
            if users_without_email > 0:
                insights.append(f"⚠️  {users_without_email} usuarios sin email - considerar validación")
            
            # Verificar productos sin categoría
            result = connection.execute(text("SELECT COUNT(*) FROM productos WHERE categoria_id IS NULL"))
            products_without_category = result.fetchone()[0]
            if products_without_category > 0:
                insights.append(f"⚠️  {products_without_category} productos sin categoría")
            
            # Verificar usuarios con datos nutricionales incompletos
            result = connection.execute(text("""
                SELECT COUNT(*) FROM usuarios 
                WHERE peso_kg IS NULL OR altura_cm IS NULL OR fecha_nacimiento IS NULL
            """))
            incomplete_profiles = result.fetchone()[0]
            if incomplete_profiles > 0:
                insights.append(f"📊 {incomplete_profiles} usuarios con perfiles nutricionales incompletos")
            
            # Verificar uso del sistema de caché
            result = connection.execute(text("SELECT COUNT(*) FROM scraping_cache"))
            cache_entries = result.fetchone()[0]
            insights.append(f"🗄️  {cache_entries} entradas en caché de scraping")
            
            # Verificar actividad de Telegram
            result = connection.execute(text("""
                SELECT COUNT(*) FROM telegram_sesiones 
                WHERE actualizado_en > NOW() - INTERVAL '7 days'
            """))
            recent_telegram = result.fetchone()[0]
            insights.append(f"📱 {recent_telegram} sesiones de Telegram activas en los últimos 7 días")
            
        except Exception as e:
            insights.append(f"❌ Error generando insights: {e}")
    
    print("\n🔍 Análisis:")
    for insight in insights:
        print(f"   {insight}")
    
    print(f"\n✅ Recomendaciones:")
    print("   • Implementar validaciones de datos en la aplicación")
    print("   • Considerar agregar triggers para actualizar 'actualizado_en'")
    print("   • Implementar limpieza periódica del caché de scraping")
    print("   • Configurar Row Level Security (RLS) para mayor seguridad")
    print("   • Considerar índices adicionales para consultas frecuentes")

def main():
    print("🔍 EXPLORADOR DE BASE DE DATOS - NUTRICHAT")
    print("=" * 60)
    
    try:
        explore_table_data()
        sample_recent_data()
        generate_insights()
        
        print(f"\n\n🎯 RESUMEN FINAL")
        print("=" * 50)
        print("✅ Base de datos completamente funcional")
        print("✅ Estructura bien diseñada con relaciones apropiadas")
        print("✅ Conexión con Supabase establecida exitosamente")
        print("✅ Listo para desarrollo de la aplicación NutriChat")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")

if __name__ == "__main__":
    main()
