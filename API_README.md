# API NutriChat - Documentación de Endpoints

Documentación completa de la API NutriChat con ejemplos de peticiones para **Postman** y **n8n**.

## Información General

- **Base URL**: `http://localhost:5000/api` (desarrollo)
- **Formato**: JSON
- **Autenticación**: JWT Bearer Token (para endpoints protegidos)

---

## Tabla de Contenidos

1. [Sistema](#sistema)
2. [Usuarios y Autenticación](#usuarios-y-autenticación)
3. [Telegram](#telegram)
4. [Productos](#productos)
5. [Listas de Mercado](#listas-de-mercado)
6. [Condiciones Nutricionales](#condiciones-nutricionales)
7. [Reportes y Feedback](#reportes-y-feedback)
8. [Scraping Cache](#scraping-cache)
9. [Configuración del Sistema](#configuración-del-sistema)
10. [Auditoría](#auditoría)

---

## Sistema

### GET /api/status
Verificar estado de la API

**Autenticación**: No requerida

**Ejemplo Postman**:
```
GET http://localhost:5000/api/status
```

**Ejemplo n8n (HTTP Request Node)**:
- Method: `GET`
- URL: `http://localhost:5000/api/status`

**Response**:
```json
{
    "success": true,
    "message": "API NutriChat funcionando correctamente",
    "version": "1.0.0"
}
```

---

### GET /api/info
Información general de la API

**Autenticación**: No requerida

**Ejemplo Postman**:
```
GET http://localhost:5000/api/info
```

**Ejemplo n8n**:
- Method: `GET`
- URL: `http://localhost:5000/api/info`

---

## Usuarios y Autenticación

### POST /api/users/register
Registrar nuevo usuario

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789,
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "telefono": "+52123456789",
    "sexo": "M",
    "fecha_nacimiento": "1990-01-15",
    "peso_kg": 70.5,
    "altura_cm": 175.0
}
```

**Ejemplo Postman**:
```
POST http://localhost:5000/api/users/register
Content-Type: application/json

{
    "telegram_id": 123456789,
    "nombre": "Juan Pérez"
}
```

**Ejemplo n8n**:
- Method: `POST`
- URL: `http://localhost:5000/api/users/register`
- Body Content Type: `JSON`
- Body: `{{ $json }}` (desde nodo anterior)

**Response**:
```json
{
    "success": true,
    "message": "Usuario registrado exitosamente",
    "data": {
        "id": "uuid",
        "telegram_id": 123456789,
        "nombre": "Juan Pérez"
    }
}
```

---

### POST /api/auth/login
Login con Telegram ID

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789
}
```

**Ejemplo Postman**:
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
    "telegram_id": 123456789
}
```

**Ejemplo n8n**:
- Method: `POST`
- URL: `http://localhost:5000/api/auth/login`
- Body: `{"telegram_id": {{ $json.telegram_id }}}`

**Response**:
```json
{
    "success": true,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "uuid",
        "telegram_id": 123456789
    }
}
```

**Nota**: Guarda el `access_token` para usar en headers de endpoints protegidos.

---

### GET /api/users/profile
Obtener perfil del usuario autenticado

**Autenticación**: Requerida (JWT)

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Ejemplo Postman**:
```
GET http://localhost:5000/api/users/profile
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Ejemplo n8n**:
- Method: `GET`
- URL: `http://localhost:5000/api/users/profile`
- Authentication: `Generic Credential Type`
- Add Credential: `Header Auth`
- Name: `Authorization`
- Value: `Bearer {{ $json.access_token }}`

---

### PUT /api/users/profile
Actualizar perfil del usuario autenticado

**Autenticación**: Requerida (JWT)

**Body JSON** (todos opcionales):
```json
{
    "nombre": "Juan Carlos",
    "email": "nuevo@email.com",
    "telefono": "+52987654321",
    "sexo": "M",
    "fecha_nacimiento": "1990-01-15",
    "peso_kg": 75.0,
    "altura_cm": 180.0,
    "nutritional_preferences": {
        "diet_type": "vegetariana",
        "allergies": ["lactosa"],
        "goal": "bajar_peso"
    },
    "budget_monthly": 5000,
    "budget_weekly": 1200
}
```

**Ejemplo Postman**:
```
PUT http://localhost:5000/api/users/profile
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
    "nombre": "Juan Carlos",
    "peso_kg": 75.0
}
```

---

### GET /api/users/telegram/:telegram_id
Buscar usuario por Telegram ID

**Autenticación**: No requerida

**Ejemplo Postman**:
```
GET http://localhost:5000/api/users/telegram/123456789
```

**Ejemplo n8n**:
- Method: `GET`
- URL: `http://localhost:5000/api/users/telegram/{{ $json.telegram_id }}`

---

### POST /api/users/search/email
Buscar usuario por email

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "email": "usuario@ejemplo.com"
}
```

---

### PUT /api/users/profile/nutrition
Actualizar preferencias nutricionales

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "nutritional_preferences": {
        "diet_type": "vegetariana",
        "allergies": ["lactosa", "gluten"],
        "dislikes": ["brócoli"],
        "goal": "bajar_peso"
    }
}
```

---

### PUT /api/users/profile/budget
Actualizar presupuesto

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "budget_monthly": 5000,
    "budget_weekly": 1200
}
```

---

## Telegram

### POST /api/webhook/telegram
Webhook para recibir mensajes de Telegram vía N8N

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789,
    "message": "Texto del mensaje",
    "first_name": "Juan",
    "username": "juanperez"
}
```

**Ejemplo n8n (Webhook Trigger → HTTP Request)**:
- Webhook URL: `http://localhost:5000/api/webhook/telegram`
- Method: `POST`
- Body: 
```json
{
    "telegram_id": {{ $json.message.from.id }},
    "message": {{ $json.message.text }},
    "first_name": {{ $json.message.from.first_name }},
    "username": {{ $json.message.from.username }}
}
```

**Response**:
```json
{
    "success": true,
    "message": "Webhook procesado",
    "user": {...},
    "new_user": false
}
```

---

### POST /api/telegram/sesion
Obtener o crear sesión activa

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789
}
```

**Ejemplo Postman**:
```
POST http://localhost:5000/api/telegram/sesion
Content-Type: application/json

{
    "telegram_id": 123456789
}
```

**Ejemplo n8n**:
- Method: `POST`
- URL: `http://localhost:5000/api/telegram/sesion`
- Body: `{"telegram_id": {{ $json.telegram_id }}}`

---

### PUT /api/telegram/sesion/estado
Actualizar estado de conversación

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789,
    "estado_conversacion": "esperando_presupuesto"
}
```

**Ejemplo n8n**:
- Method: `PUT`
- URL: `http://localhost:5000/api/telegram/sesion/estado`
- Body: 
```json
{
    "telegram_id": {{ $json.telegram_id }},
    "estado_conversacion": "esperando_presupuesto"
}
```

---

### PUT /api/telegram/sesion/contexto
Actualizar contexto conversacional

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789,
    "contexto": {
        "paso": 2,
        "categoria": "verduras",
        "presupuesto": 1000
    }
}
```

**Ejemplo n8n**:
- Method: `PUT`
- URL: `http://localhost:5000/api/telegram/sesion/contexto`
- Body: 
```json
{
    "telegram_id": {{ $json.telegram_id }},
    "contexto": {{ $json.contexto }}
}
```

---

### DELETE /api/telegram/sesion
Limpiar sesión (reset conversacional)

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "telegram_id": 123456789
}
```

**Ejemplo n8n**:
- Method: `DELETE`
- URL: `http://localhost:5000/api/telegram/sesion`
- Body: `{"telegram_id": {{ $json.telegram_id }}}`

---

### GET /api/telegram/sesion/:telegram_id
Obtener sesión por Telegram ID

**Autenticación**: No requerida

**Ejemplo Postman**:
```
GET http://localhost:5000/api/telegram/sesion/123456789
```

**Ejemplo n8n**:
- Method: `GET`
- URL: `http://localhost:5000/api/telegram/sesion/{{ $json.telegram_id }}`

---

## Productos

### POST /api/categorias
Crear una nueva categoría

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "nombre": "Verduras",
    "descripcion": "Categoría de verduras frescas"
}
```

---

### GET /api/categorias
Obtener todas las categorías

**Autenticación**: No requerida

**Ejemplo Postman**:
```
GET http://localhost:5000/api/categorias
```

---

### GET /api/categorias/:categoria_id
Obtener categoría por ID

**Autenticación**: No requerida

---

### POST /api/productos
Crear un nuevo producto

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "nombre": "Tomate",
    "marca": "Marca X",
    "categoria_id": 1,
    "descripcion": "Tomate rojo",
    "url_producto": "https://ejemplo.com/tomate",
    "url_imagen": "https://ejemplo.com/tomate.jpg",
    "codigo_fuente": "d1",
    "producto_hash": "hash123"
}
```

---

### GET /api/productos/:producto_id
Obtener producto por ID

**Autenticación**: No requerida

---

### PUT /api/productos/:producto_id
Actualizar producto

**Autenticación**: Requerida (JWT)

**Body JSON** (todos opcionales):
```json
{
    "nombre": "Tomate Orgánico",
    "marca": "Nueva Marca",
    "categoria_id": 1
}
```

---

### GET /api/productos/search?nombre=tomate
Buscar productos por nombre

**Autenticación**: No requerida

**Query Params**:
- `nombre`: Nombre a buscar (requerido)

**Ejemplo Postman**:
```
GET http://localhost:5000/api/productos/search?nombre=tomate
```

**Ejemplo n8n**:
- Method: `GET`
- URL: `http://localhost:5000/api/productos/search?nombre={{ $json.nombre }}`

---

### GET /api/productos/categoria/:categoria_id
Obtener productos por categoría

**Autenticación**: No requerida

---

### GET /api/productos/hash?hash=hash123
Obtener producto por hash

**Autenticación**: No requerida

**Query Params**:
- `hash`: Hash del producto (requerido)

---

### POST /api/productos/nutricion
Crear información nutricional para un producto

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "producto_id": "uuid-del-producto",
    "porcion_g": 100.0,
    "calorias_kcal": 250.5,
    "proteinas_g": 10.0,
    "grasas_totales_g": 5.0,
    "grasas_saturadas_g": 2.0,
    "carbohidratos_g": 30.0,
    "azucares_g": 15.0,
    "fibra_g": 3.0,
    "sodio_mg": 500.0,
    "colesterol_mg": 0.0,
    "micronutrientes": {
        "vitamina_c": 50.0
    },
    "ig": 50.0,
    "carga_glucemica": 25.0,
    "fuente": "Etiqueta del producto"
}
```

---

### GET /api/productos/:producto_id/nutricion
Obtener información nutricional por producto

**Autenticación**: No requerida

---

### POST /api/productos/snapshot
Crear un snapshot de producto

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "producto_id": "uuid-del-producto",
    "precio": 25.50,
    "unidad_medida": "kg",
    "disponibilidad": true,
    "fuente": "d1.com",
    "impacto_ambiental": {
        "co2": 2.5
    },
    "atributos_json": {
        "descuento": 10
    }
}
```

---

### GET /api/productos/:producto_id/snapshots
Obtener snapshots por producto

**Autenticación**: No requerida

**Query Params**:
- `limit`: Número máximo de resultados (opcional)

---

### GET /api/productos/:producto_id/snapshot/latest
Obtener el snapshot más reciente de un producto

**Autenticación**: No requerida

---

## Listas de Mercado

### POST /api/listas
Crear una nueva lista de mercado

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "nombre": "Lista Semanal",
    "descripcion": "Lista para la semana"
}
```

---

### GET /api/listas
Obtener listas del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/listas/search?nombre=Semanal
Buscar listas por nombre

**Autenticación**: Requerida (JWT)

**Query Params**:
- `nombre`: Nombre a buscar (requerido)

---

### GET /api/listas/:lista_id
Obtener lista por ID

**Autenticación**: Requerida (JWT)

---

### PUT /api/listas/:lista_id
Actualizar lista de mercado

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "nombre": "Lista Actualizada",
    "descripcion": "Nueva descripción"
}
```

---

### DELETE /api/listas/:lista_id
Eliminar lista de mercado

**Autenticación**: Requerida (JWT)

---

### POST /api/listas/:lista_id/productos
Agregar producto a una lista

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "producto_id": "uuid-del-producto",
    "cantidad": 2.5,
    "unidad_medida": "kg",
    "precio_unitario": 25.50,
    "notas": "Tomates orgánicos"
}
```

---

### GET /api/listas/:lista_id/productos
Obtener productos de una lista

**Autenticación**: Requerida (JWT)

---

### PUT /api/listas/:lista_id/productos/:producto_id
Actualizar producto en lista

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "cantidad": 3.0,
    "unidad_medida": "kg",
    "precio_unitario": 30.00,
    "notas": "Actualizado"
}
```

---

### DELETE /api/listas/:lista_id/productos/:producto_id
Eliminar producto de una lista

**Autenticación**: Requerida (JWT)

---

## Condiciones Nutricionales

### POST /api/condiciones
Crear una nueva condición nutricional

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "nombre": "Diabetes",
    "descripcion": "Condición de diabetes tipo 2",
    "parametros": {
        "max_azucar_g": 25.0,
        "max_sodio_mg": 2000.0
    }
}
```

---

### GET /api/condiciones
Obtener todas las condiciones nutricionales

**Autenticación**: No requerida

---

### GET /api/condiciones/:condicion_id
Obtener condición por ID

**Autenticación**: No requerida

---

### GET /api/condiciones/search?nombre=Diabetes
Obtener condición por nombre

**Autenticación**: No requerida

**Query Params**:
- `nombre`: Nombre de la condición (requerido)

---

### PUT /api/condiciones/:condicion_id
Actualizar condición nutricional

**Autenticación**: Requerida (JWT)

---

### DELETE /api/condiciones/:condicion_id
Eliminar condición nutricional

**Autenticación**: Requerida (JWT)

---

### POST /api/usuario/condiciones
Agregar condición nutricional a usuario autenticado

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "condicion_id": 1
}
```

---

### GET /api/usuario/condiciones
Obtener condiciones nutricionales del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### DELETE /api/usuario/condiciones/:condicion_id
Eliminar condición nutricional del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/usuario/condiciones/:condicion_id/check
Verificar si el usuario autenticado tiene una condición específica

**Autenticación**: Requerida (JWT)

**Response**:
```json
{
    "success": true,
    "has_condicion": true
}
```

---

## Reportes y Feedback

### POST /api/reportes
Crear un nuevo reporte

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "tipo": "nutricional",
    "parametros": {
        "periodo": "semanal"
    },
    "contenido": {
        "resumen": "Resumen del reporte"
    },
    "enlace_archivo": "https://ejemplo.com/reporte.pdf"
}
```

---

### GET /api/reportes/usuario
Obtener reportes del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/reportes/tipo/:tipo
Obtener reportes por tipo

**Autenticación**: No requerida

---

### GET /api/reportes/sistema
Obtener reportes del sistema

**Autenticación**: No requerida

---

### GET /api/reportes/:reporte_id
Obtener reporte por ID

**Autenticación**: No requerida

---

### POST /api/feedback
Crear un nuevo feedback de recomendación

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "lista_id": "uuid-de-lista",
    "aceptada": true,
    "comentarios": "Me gustó la recomendación"
}
```

---

### GET /api/feedback/usuario
Obtener feedback del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/feedback/lista/:lista_id
Obtener feedback por lista

**Autenticación**: No requerida

---

### GET /api/feedback/aceptadas
Obtener feedback aceptados del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/feedback/rechazadas
Obtener feedback rechazados del usuario autenticado

**Autenticación**: Requerida (JWT)

---

### GET /api/feedback/:feedback_id
Obtener feedback por ID

**Autenticación**: No requerida

---

## Scraping Cache

### POST /api/scraping/cache
Obtener o crear cache (UPSERT por URL)

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "url": "https://ejemplo.com",
    "html_content": "<html>...</html>",
    "headers": {
        "Content-Type": "text/html"
    },
    "status_code": 200,
    "valido_hasta": "2024-12-31T23:59:59Z"
}
```

---

### GET /api/scraping/cache/url/:url
Obtener cache por URL

**Autenticación**: No requerida

**Query Params**:
- `include_html`: true/false (por defecto false)

**Nota**: La URL debe estar codificada en la ruta.

---

### POST /api/scraping/cache/valid
Obtener cache válido por URL

**Autenticación**: No requerida

**Body JSON**:
```json
{
    "url": "https://ejemplo.com"
}
```

---

### GET /api/scraping/cache/expired
Obtener caches expirados

**Autenticación**: No requerida

**Query Params**:
- `limit`: número máximo de resultados (opcional)

---

### DELETE /api/scraping/cache/expired
Eliminar caches expirados

**Autenticación**: No requerida

**Body JSON** (opcional):
```json
{
    "limit": 100
}
```

---

### GET /api/scraping/cache/recent
Obtener caches recientes

**Autenticación**: No requerida

**Query Params**:
- `limit`: número máximo de resultados (por defecto 100, máximo 1000)

---

### GET /api/scraping/cache/status/:status_code
Obtener caches por código de estado HTTP

**Autenticación**: No requerida

---

## Configuración del Sistema

### POST /api/config
Crear una nueva configuración del sistema

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "clave": "max_productos_lista",
    "valor": {
        "max": 50,
        "min": 1
    }
}
```

---

### GET /api/config
Obtener todas las configuraciones del sistema

**Autenticación**: No requerida

---

### GET /api/config/:clave
Obtener configuración por clave

**Autenticación**: No requerida

---

### GET /api/config/:clave/valor
Obtener solo el valor de una configuración por clave

**Autenticación**: No requerida

**Query Params**:
- `default`: Valor por defecto si no existe (opcional)

---

### PUT /api/config/:clave
Actualizar configuración del sistema

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "valor": {
        "max": 100,
        "min": 1
    }
}
```

---

### PUT /api/config/:clave/key
Actualizar una clave específica dentro del valor de la configuración

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "key": "max",
    "value": 100
}
```

---

### DELETE /api/config/:clave
Eliminar configuración del sistema

**Autenticación**: Requerida (JWT)

---

## Auditoría

### POST /api/audit/log
Crear un nuevo registro de auditoría

**Autenticación**: Requerida (JWT)

**Body JSON**:
```json
{
    "entidad": "Usuario",
    "accion": "CREATE",
    "entidad_id": "uuid",
    "usuario_id": "uuid",
    "payload": {
        "nombre": "Juan"
    }
}
```

---

### GET /api/audit/log/:log_id
Obtener log de auditoría por ID

**Autenticación**: Requerida (JWT)

---

### GET /api/audit/logs/entidad?entidad=Usuario
Obtener logs por entidad

**Autenticación**: Requerida (JWT)

**Query Params**:
- `entidad`: Nombre de la entidad (requerido)
- `limit`: Número máximo de resultados (opcional)

---

### GET /api/audit/logs/entidad-id?entidad=Usuario&entidad_id=uuid
Obtener logs por entidad e ID

**Autenticación**: Requerida (JWT)

**Query Params**:
- `entidad`: Nombre de la entidad (requerido)
- `entidad_id`: ID de la entidad (requerido)

---

### GET /api/audit/logs/usuario?usuario_id=uuid
Obtener logs por usuario

**Autenticación**: Requerida (JWT)

**Query Params**:
- `usuario_id`: ID del usuario (opcional, si no se proporciona usa el autenticado)
- `limit`: Número máximo de resultados (opcional)

---

### GET /api/audit/logs/accion?accion=CREATE
Obtener logs por acción

**Autenticación**: Requerida (JWT)

**Query Params**:
- `accion`: Nombre de la acción (requerido)
- `limit`: Número máximo de resultados (opcional)

---

### GET /api/audit/logs/recent?limit=100
Obtener logs recientes

**Autenticación**: Requerida (JWT)

**Query Params**:
- `limit`: Número máximo de resultados (opcional, default: 100, máximo: 1000)

---

## Configuración de Autenticación en Postman

1. **Crear Environment**:
   - Variables:
     - `base_url`: `http://localhost:5000/api`
     - `access_token`: (se llenará después del login)

2. **Collection Pre-request Script** (opcional):
```javascript
if (pm.environment.get("access_token")) {
    pm.request.headers.add({
        key: "Authorization",
        value: "Bearer " + pm.environment.get("access_token")
    });
}
```

3. **Test Script en Login**:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
}
```

---

## Configuración de Autenticación en n8n

### Opción 1: Usar Variable de Entorno

1. Crear un nodo **Set** después del login:
   - Name: `access_token`
   - Value: `{{ $json.access_token }}`

2. En nodos HTTP Request protegidos:
   - Authentication: `Generic Credential Type`
   - Add Credential: `Header Auth`
   - Name: `Authorization`
   - Value: `Bearer {{ $json.access_token }}`

### Opción 2: Usar Workflow Variable

1. Después del login, guardar token:
   - Nodo **Set**: `{{ $json.access_token }}` → `workflow.access_token`

2. En requests protegidos:
   - Header: `Authorization: Bearer {{ $workflow.access_token }}`

---

## Códigos de Estado HTTP

- `200`: Éxito
- `201`: Creado exitosamente
- `400`: Error de validación / Bad Request
- `401`: No autenticado
- `403`: Acceso prohibido
- `404`: No encontrado
- `409`: Conflicto (ej: duplicado)
- `500`: Error interno del servidor

---

## Estructura de Respuesta Estándar

### Éxito:
```json
{
    "success": true,
    "message": "Operación exitosa",
    "data": {...}
}
```

### Error:
```json
{
    "success": false,
    "message": "Descripción del error",
    "errors": [...]  // Opcional
}
```

---

## Notas Importantes

1. **JWT Token Expiración**: Los tokens expiran después de 15 minutos (configurable). Renueva el token haciendo login nuevamente.

2. **Telegram ID**: Debe ser un número entero. Ejemplo: `123456789`

3. **UUIDs**: Los IDs de productos, listas, reportes, etc. son UUIDs. Ejemplo: `550e8400-e29b-41d4-a716-446655440000`

4. **Fechas**: Formato ISO 8601. Ejemplo: `2024-01-15T10:30:00Z`

5. **JSONB Fields**: Campos como `contexto`, `nutritional_preferences`, `parametros` aceptan objetos JSON anidados.

---

## Ejemplos de Flujos Completos

### Flujo 1: Registro y Login
```
1. POST /api/users/register (con telegram_id)
2. POST /api/auth/login (obtener access_token)
3. GET /api/users/profile (usar token en header)
```

### Flujo 2: Crear Lista y Agregar Productos
```
1. POST /api/auth/login
2. POST /api/listas (crear lista)
3. POST /api/productos (crear producto si no existe)
4. POST /api/listas/{lista_id}/productos (agregar a lista)
```

### Flujo 3: Webhook Telegram → N8N
```
1. Telegram Bot → N8N Webhook Trigger
2. POST /api/webhook/telegram (auto-registra usuario)
3. POST /api/telegram/sesion (obtener/crear sesión)
4. PUT /api/telegram/sesion/estado (actualizar estado)
5. PUT /api/telegram/sesion/contexto (guardar contexto)
```

---

## Soporte

Para más información o reportar problemas, consulta la documentación del proyecto o contacta al equipo de desarrollo.
