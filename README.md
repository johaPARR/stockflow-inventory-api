# StockFlow API

🌎 **Language / Idioma:** [English](#english) · [Español](#español)

---

<a id="english"></a>

## 🇬🇧 English

**Inventory Management & Ecommerce Integration API**

StockFlow is a backend REST API for product catalog management, inventory control, stock movement tracking, and ecommerce order integration. It is built with Python, FastAPI, and PostgreSQL, and includes database migrations, automated tests, Docker support, and a GitHub Actions CI workflow.

### Features

- **Category management:** create, list, retrieve, and update product categories.
- **Product management:** create, list, retrieve, and update products, including SKU-based identification.
- **Inventory control:** retrieve stock levels and register stock entries, exits, and adjustments.
- **Movement history:** record and consult inventory movements, including previous and resulting quantities.
- **Ecommerce integration:** receive confirmed-order webhooks and deduct stock for the products included in an order.
- **Transaction safety:** validate stock availability and process order inventory changes atomically to avoid partial updates.
- **Idempotency:** prevent a confirmed order from being processed more than once.
- **API documentation:** interactive Swagger UI, ReDoc, and an OpenAPI 3.1 specification.
- **Health monitoring:** health-check endpoint for service availability.

### Technology Stack

| Technology     | Purpose                                       |
|----------------|-----------------------------------------------|
| Python         | Backend programming language                  |
| FastAPI        | REST API framework                            |
| PostgreSQL     | Relational database                           |
| SQLAlchemy     | ORM and database access                       |
| Alembic        | Database schema migrations                    |
| Pydantic       | Request and response validation               |
| Docker         | Application containerization                  |
| Docker Compose | Local application and database orchestration  |
| Pytest         | Automated testing                             |
| GitHub Actions | Continuous integration workflow               |

### Architecture

The application uses a layered structure to separate HTTP handling, validation, business rules, and persistence.

```text
app/
├── api/
│   ├── dependencies.py
│   └── v1/
│       ├── category_routes.py
│       ├── product_routes.py
│       ├── inventory_routes.py
│       ├── movement_routes.py
│       └── webhook_routes.py
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
└── services/

alembic/
├── versions/
└── env.py

tests/

.github/
└── workflows/
    └── tests.yml
```

- **API routes:** expose versioned HTTP endpoints.
- **Schemas:** validate incoming data and serialize responses.
- **Services:** implement business rules and transaction handling.
- **Repositories:** encapsulate database queries and persistence.
- **Models:** define relational database entities.
- **Alembic:** manages database schema versions.

### API Endpoints

Base URL for local development: `http://localhost:8000`

| Resource                | Method | Endpoint                                     |
|-------------------------|--------|----------------------------------------------|
| Categories              | POST   | `/api/v1/categories`                         |
| Categories              | GET    | `/api/v1/categories`                         |
| Category                | GET    | `/api/v1/categories/{category_id}`           |
| Category                | PATCH  | `/api/v1/categories/{category_id}`           |
| Products                | POST   | `/api/v1/products`                           |
| Products                | GET    | `/api/v1/products`                           |
| Product                 | GET    | `/api/v1/products/{product_id}`              |
| Product                 | PATCH  | `/api/v1/products/{product_id}`              |
| Inventory               | GET    | `/api/v1/inventory`                          |
| Product inventory       | GET    | `/api/v1/inventory/{product_id}`             |
| Stock entry             | POST   | `/api/v1/inventory/entries`                  |
| Stock exit              | POST   | `/api/v1/inventory/exits`                    |
| Stock adjustment        | POST   | `/api/v1/inventory/adjustments`              |
| Movement history        | GET    | `/api/v1/movements`                          |
| Product movements       | GET    | `/api/v1/movements/product/{product_id}`     |
| Confirmed-order webhook | POST   | `/api/v1/webhooks/orders/confirmed`          |
| Health check            | GET    | `/health`                                    |

### Ecommerce Webhook

The endpoint `POST /api/v1/webhooks/orders/confirmed` receives an ecommerce order after it has been confirmed.

Example request:

```json
{
  "order_id": "ORDER-1001",
  "items": [
    {
      "sku": "PROD-001",
      "quantity": 2
    }
  ]
}
```

The API identifies products by SKU, validates that the requested quantities are available, deducts inventory, and records the corresponding stock movements. The order is processed as a single transaction. Repeated notifications for an already processed order are rejected to avoid duplicate stock deductions.

### Local Setup

#### Requirements

- Python 3.13 or later for the local environment.
- Docker Desktop with Docker Compose.
- Git.

#### 1. Clone the repository

```bash
git clone https://github.com/johaPARR/stockflow-inventory-api.git
cd stockflow-inventory-api
```

#### 2. Configure environment variables

Create a `.env` file in the project root. Use your own local PostgreSQL credentials:

```env
POSTGRES_DB=stockflow_db
POSTGRES_USER=stockflow_user
POSTGRES_PASSWORD=your_secure_password

DATABASE_URL=postgresql+psycopg://stockflow_user:your_secure_password@localhost:5432/stockflow_db
TEST_DATABASE_URL=postgresql+psycopg://stockflow_user:your_secure_password@localhost:5432/stockflow_test_db
DATABASE_URL_DOCKER=postgresql+psycopg://stockflow_user:your_secure_password@db:5432/stockflow_db
```

Replace `your_secure_password` with your own password. Do not commit `.env` or real credentials to version control. The repository includes `.env.example` as a template.

#### 3. Start the application

```bash
docker compose up -d --build
```

Docker Compose starts the API and PostgreSQL services. The application container runs `alembic upgrade head` before starting the FastAPI server.

#### 4. Open the API documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI specification: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

#### 5. Stop the services

```bash
docker compose down
```

This command stops and removes the containers but preserves the named database volume. Do not add `-v` if you want to keep the local database data.

### Database Migrations

Apply existing migrations:

```bash
alembic upgrade head
```

Generate a migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
```

Review generated migration files before applying them.

### Automated Tests

The project uses Pytest and FastAPI's test client. The test suite covers category and product endpoints, inventory operations, movement history, and confirmed-order webhook behavior, including validation, duplicate-order handling, and transaction rollback scenarios.

Run the tests locally after configuring the test database:

```bash
pytest -v
```

**Latest local test result: 30 tests passed.**

### Continuous Integration

The workflow is defined in `.github/workflows/tests.yml`. It is configured to run on pushes and pull requests targeting the `main` branch.

The workflow:

1. Checks out the repository.
2. Sets up Python 3.13.
3. Starts a PostgreSQL service.
4. Installs project dependencies.
5. Creates the test database.
6. Applies Alembic migrations.
7. Runs the Pytest suite.

The workflow configuration is included in the repository; its successful execution should be confirmed in the GitHub Actions tab after the workflow is pushed.

### Project Status

The local API, PostgreSQL integration, migrations, Docker Compose setup, interactive API documentation, and 30-test local suite have been verified. The GitHub Actions workflow is configured. Public deployment and production verification are not yet included in this release.

### Author

**Backend API Development | Python | FastAPI | PostgreSQL | SQLAlchemy | Docker**

GitHub: https://github.com/johaPARR

---

<a id="español"></a>

## 🇪🇸 Español

**API de gestión de inventario e integración con ecommerce**

StockFlow es una API REST backend para administrar catálogos de productos, controlar inventario, registrar movimientos de stock e integrar órdenes de compra provenientes de plataformas ecommerce. Está desarrollada con Python, FastAPI y PostgreSQL, e incluye migraciones de base de datos, pruebas automatizadas, soporte para Docker y un flujo de Integración Continua con GitHub Actions.

### Funcionalidades

- **Gestión de categorías:** crear, listar, consultar y actualizar categorías de productos.
- **Gestión de productos:** crear, listar, consultar y actualizar productos, con identificación mediante SKU.
- **Control de inventario:** consultar existencias y registrar entradas, salidas y ajustes de stock.
- **Historial de movimientos:** registrar y consultar movimientos de inventario, incluyendo cantidades anteriores y resultantes.
- **Integración con ecommerce:** recibir webhooks de órdenes confirmadas y descontar el stock de los productos incluidos en cada orden.
- **Seguridad transaccional:** validar la disponibilidad y procesar los cambios de inventario de forma atómica para evitar actualizaciones parciales.
- **Idempotencia:** impedir que una misma orden confirmada se procese más de una vez.
- **Documentación de API:** Swagger UI interactivo, ReDoc y especificación OpenAPI 3.1.
- **Monitoreo de disponibilidad:** endpoint de health check.

### Tecnologías

| Tecnología     | Uso                                       |
|----------------|-------------------------------------------|
| Python         | Lenguaje de desarrollo backend            |
| FastAPI        | Framework para API REST                   |
| PostgreSQL     | Base de datos relacional                  |
| SQLAlchemy     | ORM y acceso a datos                      |
| Alembic        | Migraciones de base de datos              |
| Pydantic       | Validación de solicitudes y respuestas    |
| Docker         | Contenedorización de la aplicación        |
| Docker Compose | Orquestación local de API y base de datos |
| Pytest         | Pruebas automatizadas                     |
| GitHub Actions | Flujo de integración continua             |

### Arquitectura

La aplicación utiliza una arquitectura por capas para separar el manejo HTTP, la validación, las reglas de negocio y la persistencia.

```text
app/
├── api/
│   ├── dependencies.py
│   └── v1/
│       ├── category_routes.py
│       ├── product_routes.py
│       ├── inventory_routes.py
│       ├── movement_routes.py
│       └── webhook_routes.py
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
└── services/

alembic/
├── versions/
└── env.py

tests/

.github/
└── workflows/
    └── tests.yml
```

- **Rutas de API:** exponen los endpoints HTTP versionados.
- **Schemas:** validan los datos recibidos y serializan las respuestas.
- **Services:** implementan las reglas de negocio y el manejo de transacciones.
- **Repositories:** encapsulan las consultas y operaciones de persistencia.
- **Models:** definen las entidades de la base de datos relacional.
- **Alembic:** administra las versiones del esquema de base de datos.

### Endpoints de la API

URL base para desarrollo local: `http://localhost:8000`

| Recurso                     | Método | Endpoint                                     |
|-----------------------------|--------|----------------------------------------------|
| Categorías                  | POST   | `/api/v1/categories`                         |
| Categorías                  | GET    | `/api/v1/categories`                         |
| Categoría                   | GET    | `/api/v1/categories/{category_id}`           |
| Categoría                   | PATCH  | `/api/v1/categories/{category_id}`           |
| Productos                   | POST   | `/api/v1/products`                           |
| Productos                   | GET    | `/api/v1/products`                           |
| Producto                    | GET    | `/api/v1/products/{product_id}`              |
| Producto                    | PATCH  | `/api/v1/products/{product_id}`              |
| Inventario                  | GET    | `/api/v1/inventory`                          |
| Inventario de producto      | GET    | `/api/v1/inventory/{product_id}`             |
| Entrada de stock            | POST   | `/api/v1/inventory/entries`                  |
| Salida de stock             | POST   | `/api/v1/inventory/exits`                    |
| Ajuste de stock             | POST   | `/api/v1/inventory/adjustments`              |
| Historial de movimientos    | GET    | `/api/v1/movements`                          |
| Movimientos por producto    | GET    | `/api/v1/movements/product/{product_id}`     |
| Webhook de orden confirmada | POST   | `/api/v1/webhooks/orders/confirmed`          |
| Health check                | GET    | `/health`                                    |

### Webhook de integración ecommerce

El endpoint `POST /api/v1/webhooks/orders/confirmed` recibe una orden ecommerce una vez confirmada.

Ejemplo de solicitud:

```json
{
  "order_id": "ORDER-1001",
  "items": [
    {
      "sku": "PROD-001",
      "quantity": 2
    }
  ]
}
```

La API identifica los productos mediante SKU, valida que las cantidades solicitadas estén disponibles, descuenta el inventario y registra los movimientos correspondientes. La orden se procesa dentro de una única transacción. Las notificaciones repetidas de una orden ya procesada se rechazan para evitar descuentos duplicados.

### Instalación local

#### Requisitos

- Python 3.13 o superior para el entorno local.
- Docker Desktop con Docker Compose.
- Git.

#### 1. Clonar el repositorio

```bash
git clone https://github.com/johaPARR/stockflow-inventory-api.git
cd stockflow-inventory-api
```

#### 2. Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto. Usar credenciales propias para PostgreSQL:

```env
POSTGRES_DB=stockflow_db
POSTGRES_USER=stockflow_user
POSTGRES_PASSWORD=your_secure_password

DATABASE_URL=postgresql+psycopg://stockflow_user:your_secure_password@localhost:5432/stockflow_db
TEST_DATABASE_URL=postgresql+psycopg://stockflow_user:your_secure_password@localhost:5432/stockflow_test_db
DATABASE_URL_DOCKER=postgresql+psycopg://stockflow_user:your_secure_password@db:5432/stockflow_db
```

Reemplazar `your_secure_password` por una contraseña propia. No subir `.env` ni credenciales reales al repositorio. El proyecto incluye `.env.example` como plantilla.

#### 3. Iniciar la aplicación

```bash
docker compose up -d --build
```

Docker Compose inicia los servicios de la API y PostgreSQL. Antes de iniciar FastAPI, el contenedor de la aplicación ejecuta `alembic upgrade head`.

#### 4. Abrir la documentación

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Especificación OpenAPI: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/health

#### 5. Detener los servicios

```bash
docker compose down
```

Este comando detiene y elimina los contenedores, pero conserva el volumen nombrado de la base de datos. No agregar `-v` si se desea conservar los datos locales.

### Migraciones de base de datos

Aplicar las migraciones existentes:

```bash
alembic upgrade head
```

Generar una migración después de modificar los modelos SQLAlchemy:

```bash
alembic revision --autogenerate -m "describir el cambio"
```

Revisar los archivos de migración generados antes de aplicarlos.

### Pruebas automatizadas

El proyecto utiliza Pytest y el cliente de pruebas de FastAPI. La suite cubre endpoints de categorías y productos, operaciones de inventario, historial de movimientos y comportamiento del webhook de órdenes confirmadas. Incluye validaciones, control de órdenes duplicadas y escenarios de rollback transaccional.

Ejecutar las pruebas localmente después de configurar la base de datos de test:

```bash
pytest -v
```

**Último resultado local: 30 pruebas aprobadas.**

### Integración continua

El workflow está definido en `.github/workflows/tests.yml`. Está configurado para ejecutarse ante pushes y pull requests dirigidos a la rama `main`.

El flujo:

1. Descarga el repositorio.
2. Configura Python 3.13.
3. Inicia un servicio PostgreSQL.
4. Instala las dependencias.
5. Crea la base de datos de pruebas.
6. Aplica las migraciones de Alembic.
7. Ejecuta la suite de Pytest.

La configuración del workflow está incluida en el repositorio; su ejecución exitosa deberá confirmarse en la pestaña GitHub Actions después de subirlo.

### Estado del proyecto

Se verificaron localmente la API, la integración con PostgreSQL, las migraciones, la configuración de Docker Compose, la documentación interactiva y la suite local de 30 pruebas. El workflow de GitHub Actions está configurado. El despliegue público y su verificación en producción todavía no forman parte de esta versión.

### Autoría

**Desarrollo Backend de APIs | Python | FastAPI | PostgreSQL | SQLAlchemy | Docker**

GitHub: https://github.com/johaPARR

---

*StockFlow API — Solución backend para gestión de inventario e integración con ecommerce.*
