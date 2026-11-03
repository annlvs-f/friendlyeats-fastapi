# FriendlyEats FastAPI — Sprint 1

Aplicación web para promocionar los restaurantes populares de la zona (Puebla y alrededores).

**Sprint 1:** versión local funcional con CRUD de restaurantes sobre **Firestore (emulador)**,
API REST con FastAPI y vistas HTML con Jinja2.

> Fuera de alcance en este sprint: autenticación, reseñas, subida de imágenes y despliegue.

## Roles

| Rol | Qué hace | Estado en el Sprint 1 |
|---|---|---|
| Visitante | Ver listado, filtrar y ver detalle | Disponible |
| Administrador | Crear, editar y eliminar restaurantes | Disponible (sin login: la interfaz está abierta) |
| Propietario | Gestionar su propio restaurante (`ownerId`) | Sprint 2, con Firebase Authentication |

## Arquitectura

```
Navegador ──► Vistas HTML (Jinja2, app/main.py)
          └─► API REST (app/api/v1/restaurants.py)
                          │
                          ▼
              Servicio (app/services)          reglas de negocio, errores 404/400
                          │
                          ▼
              Repositorio (app/repositories)   único lugar que toca Firestore
                          │
                          ▼
              Firestore (emulador local)       colección "restaurants"
```

```
friendlyeats-fastapi/
├── app/
│   ├── main.py                  # app, /health y vistas HTML
│   ├── core/                    # config.py (variables de entorno), firebase.py (cliente)
│   ├── domain/                  # models.py (constantes), schemas.py (Pydantic)
│   ├── repositories/            # restaurant_repository.py
│   ├── services/                # restaurant_service.py
│   ├── api/v1/restaurants.py    # endpoints REST
│   └── templates/               # base, restaurants, restaurant_detail, restaurant_form, error, _macros
├── static/                      # css/styles.css, js/app.js, img/
├── scripts/seed.py              # 10 restaurantes de prueba
├── tests/                       # pruebas de API y de vistas
├── firebase.json · firestore.rules · firestore.indexes.json · .firebaserc
├── .env.example · requirements.txt · pytest.ini
```

## Requisitos

- Python 3.12 o 3.13 (las versiones más nuevas pueden no tener instaladores de algunas librerías)
- Node.js (LTS) y Firebase CLI: `npm install -g firebase-tools`
- Java (JDK 17 o superior): lo necesita el emulador de Firestore
- Git

## Instalación

```powershell
# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno (el .env nunca se sube a Git)
copy .env.example .env
```

Firebase: `firebase login` y `firebase init` (Firestore y Emulators). Para el Sprint 1 se usa el
proyecto de demostración `demo-friendlyeats`, que no necesita proyecto real ni facturación.

## Cómo ejecutar (2 terminales)

```powershell
# Terminal 1: emulador de Firestore (puerto 8080, interfaz en el 4000)
firebase emulators:start --only firestore --project demo-friendlyeats

# Terminal 2: datos semilla (una vez) y aplicación
python -m scripts.seed
uvicorn app.main:app --reload

# Pruebas (con el emulador encendido)
pytest -v
```

Direcciones:

- Aplicación: <http://localhost:8000>
- Documentación interactiva de la API: <http://localhost:8000/docs>
- Datos en el emulador: <http://localhost:4000/firestore>

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/health` | Estado del servicio | 200 |
| POST | `/api/v1/restaurants` | Crear (devuelve el ID) | 201 · 422 |
| GET | `/api/v1/restaurants` | Listar con filtros y paginación | 200 · 422 |
| GET | `/api/v1/restaurants/{id}` | Detalle | 200 · 404 |
| PATCH | `/api/v1/restaurants/{id}` | Editar solo los campos enviados | 200 · 400 · 404 · 422 |
| DELETE | `/api/v1/restaurants/{id}` | Eliminar | 204 · 404 |

Parámetros de `GET /api/v1/restaurants`: `city`, `category`, `price` (1 a 3), `order_by` (`name` o `avgRating`),
`limit` (1 a 100, por defecto 20) y `start_after` (ID del último restaurante de la página anterior).

Vistas HTML: `/` (listado con filtros), `/restaurants/new`, `/restaurants/{id}` y `/restaurants/{id}/edit`.

Ejemplo de documento:

```json
{ "name": "La Abuela", "category": "Mexicana", "city": "Puebla", "price": 2,
  "photoUrl": "https://...", "avgRating": 0, "numRatings": 0 }
```

## Decisiones técnicas

- **Capas (API, Servicio, Repositorio):** si cambia la base de datos, solo se modifica el repositorio.
- **Emulador de Firestore:** permite desarrollar y probar sin costo ni riesgo para datos reales.
  No hay credenciales en el código ni en Git.
- **Cliente de Firestore perezoso:** se conecta la primera vez que se usa, no al importar el módulo.
- **`avgRating` y `numRatings` los controla el servidor:** se crean en 0 y `PATCH` solo acepta
  `name`, `category`, `city`, `price` y `photoUrl`. Las reseñas (Sprint 2) los actualizarán con transacciones.
- **Paginación por cursor** (`start_after`) en lugar de offset, que es lo eficiente en Firestore.
- **Categoría y ciudad con sugerencias:** el formulario ofrece una lista, pero permite escribir una nueva.
- **`photoUrl`:** opcional y con validación `http(s)`. Si la imagen no carga, se muestra una letra de color.
- **Índices compuestos:** en Firestore real, filtrar por un campo y ordenar por otro puede requerir índices
  compuestos. El emulador no los exige.
- **Pruebas:** corren contra el emulador. Cada prueba crea sus datos y los borra al terminar.
- **`firestore.rules`:** bloquea el acceso directo de clientes; el Admin SDK (FastAPI) no pasa por las reglas.

## Datos semilla

`python -m scripts.seed` carga 10 restaurantes ficticios (Puebla, Atlixco y Cholula). Se puede repetir
sin duplicar, porque usa IDs fijos.

## Siguiente sprint

Firebase Authentication, roles y control de propietario con `ownerId`, Security Rules y reseñas con transacciones.