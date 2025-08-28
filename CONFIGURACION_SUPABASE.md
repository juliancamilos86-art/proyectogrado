# 🚀 Configuración de Supabase - Guía Paso a Paso

## 📋 Información que necesitas de Supabase

Ve a tu **panel de Supabase** y recopila la siguiente información:

### 1. 🔑 Contraseña de la Base de Datos
- Ve a **Settings → Database**
- Busca tu contraseña o resetéala si es necesario
- **IMPORTANTE**: Anótala de forma segura

### 2. 🔐 API Keys
- Ve a **Settings → API**
- Copia las siguientes claves:
  - **anon / public key** (para el frontend)
  - **service_role / secret key** (para operaciones del backend)

### 3. 🌐 Project URL
- En **Settings → API** también encontrarás tu **Project URL**
- Formato: `https://tu-proyecto.supabase.co`

---

## ⚙️ Pasos de Configuración

### Paso 1: Actualizar archivo .env
Edita el archivo `.env` y reemplaza estos valores:

```env
# Reemplaza YOUR_PASSWORD_HERE con tu contraseña real
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA_REAL@db.ifhuhzxvnoykqtaecqlt.supabase.co:5432/postgres

# Agrega tus claves de API
SUPABASE_ANON_KEY=tu_clave_anon_real_aqui
SUPABASE_SERVICE_ROLE_KEY=tu_clave_service_role_aqui
```

### Paso 2: Probar la conexión
Ejecuta el script de prueba:

```bash
python test_supabase_connection.py
```

### Paso 3: Instalar dependencias nuevas
Si no las has instalado aún:

```bash
pip install -r requirements.txt
```

### Paso 4: Iniciar la aplicación
```bash
python run.py
```

---

## 🔍 Verificación de Configuración

El script `test_supabase_connection.py` verificará:

✅ **Conexión PostgreSQL**: Usando SQLAlchemy
✅ **Cliente Supabase**: Usando la librería de Supabase
✅ **Variables de entorno**: Que estén correctamente configuradas

---

## 🛠️ Estructura de Archivos Actualizada

```
proyecto_nutrichat/
├── .env                    # ← Configuración con tus datos reales
├── .env.example           # ← Plantilla para el equipo
├── app/
│   ├── __init__.py        # ← Configurado con JWT y Factory Pattern
│   ├── config.py          # ← Configuración por entornos
│   └── models/
│       └── database.py    # ← Configuración SQLAlchemy
└── test_supabase_connection.py  # ← Script de pruebas
```

---

## 🚨 Problemas Comunes

### Error: "password authentication failed"
- Verifica que la contraseña sea correcta
- Asegúrate de no tener espacios extra

### Error: "could not connect to server"
- Verifica tu conexión a internet
- Confirma que la URL de Supabase sea correcta

### Error: "Invalid API key"
- Verifica que las claves API sean correctas
- Asegúrate de usar la clave correcta (anon vs service_role)

---

## 🎯 Próximos Pasos

Una vez que la conexión funcione:

1. **Crear modelos de datos** (usuarios, productos, etc.)
2. **Configurar autenticación JWT** completa
3. **Implementar endpoints de API**
4. **Configurar Row Level Security** en Supabase (opcional)

---

## 💡 Consejos de Seguridad

- ✅ Nunca subas el archivo `.env` al repositorio
- ✅ Usa `service_role_key` solo en el backend
- ✅ La `anon_key` puede usarse en el frontend
- ✅ Configura Row Level Security para mayor seguridad
