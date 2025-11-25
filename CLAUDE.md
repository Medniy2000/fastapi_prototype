# FastAPI Prototype - Comprehensive Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Layer Breakdown](#layer-breakdown)
6. [Key Components](#key-components)
7. [Configuration](#configuration)
8. [Database](#database)
9. [Authentication & Authorization](#authentication--authorization)
10. [Messaging & Background Tasks](#messaging--background-tasks)
11. [Testing](#testing)
12. [API Endpoints](#api-endpoints)
13. [Running the Application](#running-the-application)
14. [Development Workflow](#development-workflow)

---

## Project Overview

This is a **FastAPI-based prototype** implementing **Domain-Driven Design (DDD)** and **Onion Architecture** principles. It provides a solid foundation for building scalable, maintainable backend applications with:

- Clean separation of concerns across layers
- Comprehensive CRUD operations with advanced query building
- Multiple interface types (REST API, gRPC)
- Asynchronous message processing (RabbitMQ, Kafka)
- Background task processing (Celery)
- JWT-based authentication
- Production-ready error handling
- Extensive test coverage

**Status**: Template/Prototype (not production-ready yet, but provides a solid foundation)

---

## Architecture

### Architectural Pattern: Onion Architecture + DDD

The project follows **Onion Architecture** with four main layers:

```
┌─────────────────────────────────────────┐
│         Interfaces Layer                │
│  (API, gRPC, CLI, Error Handlers)      │
├─────────────────────────────────────────┤
│       Application Layer                 │
│  (Application Services, DTOs)           │
├─────────────────────────────────────────┤
│         Domain Layer                    │
│  (Aggregates, Entities, Services,       │
│   Value Objects, Domain Events)         │
├─────────────────────────────────────────┤
│      Infrastructure Layer               │
│  (Repositories, Persistence, Messaging, │
│   Extensions, Tasks)                    │
└─────────────────────────────────────────┘
```

**Key Principles:**
- **Dependency Rule**: Dependencies point inward (outer layers depend on inner layers)
- **Domain Independence**: Domain layer has no external dependencies
- **Interface Segregation**: Multiple interface types (REST, gRPC) share same core logic

---

## Tech Stack

### Core Framework
- **FastAPI** (0.116.1) - Modern async web framework
- **Uvicorn** (0.35.0) - ASGI server
- **Gunicorn** (23.0.0) - Production WSGI server

### Database & ORM
- **PostgreSQL** - Primary database
- **SQLAlchemy** (async) - ORM with async support
- **Alembic** (1.16.4) - Database migrations
- **asyncpg** (0.30.0) - Async PostgreSQL driver
- **psycopg2-binary** (2.9.9) - Sync PostgreSQL driver

### Authentication & Security
- **python-jose** (3.5.0) - JWT tokens
- **passlib[bcrypt]** (1.7.4) - Password hashing

### Messaging & Background Tasks
- **Celery** (5.5.3) - Distributed task queue
- **Redis** (6.4.0) - Cache & Celery broker
- **aio-pika** (9.5.7) - Async RabbitMQ client
- **aiokafka** (0.12.0) - Async Kafka client

### RPC
- **grpcio** (1.69.0) - gRPC framework
- **grpcio-tools** (1.69.0) - Protocol buffer tools

### Testing
- **pytest** (8.3.4) - Testing framework
- **pytest-asyncio** (0.25.0) - Async test support
- **pytest-cov** (6.0.0) - Coverage reporting

### Code Quality
- **mypy** (1.14.0) - Static type checker
- **flake8** (7.1.1) - Linting
- **black** (24.10.0) - Code formatting

### Documentation
- **Sphinx** (8.1.3) - Documentation generator

### Utilities
- **loguru** (0.7.3) - Logging
- **pydantic** - Data validation
- **environs** (14.3.0) - Environment variables

---

## Project Structure

```
fastapi_prototype/
├── .launch/                    # Docker launch configurations
│   ├── api/                   # API container
│   ├── celery/                # Celery worker container
│   ├── consume/               # Message consumer container
│   └── tests/                 # Test container
│
├── docs/                      # Sphinx documentation
│   └── source/
│       └── conf.py
│
├── src/                       # Main source code
│   └── app/
│       ├── application/       # Application Layer
│       │   ├── common/       # Base services, DTOs
│       │   ├── container.py  # Service container
│       │   ├── dto/          # Data Transfer Objects
│       │   └── services/     # Application services
│       │       ├── auth_service.py
│       │       ├── common_service.py
│       │       └── users_service.py
│       │
│       ├── config/           # Configuration
│       │   ├── settings.py   # Application settings
│       │   └── celery.py     # Celery configuration
│       │
│       ├── domain/           # Domain Layer (Core Business Logic)
│       │   ├── common/       # Shared domain components
│       │   │   ├── aggregates/    # Base aggregate
│       │   │   ├── entities/      # Base entity
│       │   │   ├── events/        # Domain events
│       │   │   ├── exceptions.py  # Custom exceptions
│       │   │   └── services/      # Base domain service
│       │   │
│       │   ├── auth/         # Auth domain
│       │   │   ├── services/
│       │   │   │   ├── auth_service.py
│       │   │   │   └── jwt_service.py
│       │   │   └── value_objects/
│       │   │       └── jwt_vob.py
│       │   │
│       │   └── users/        # Users domain
│       │       ├── aggregates/
│       │       │   └── user_agg.py
│       │       ├── services/
│       │       │   └── users_service.py
│       │       └── value_objects/
│       │           └── users_vob.py
│       │
│       ├── infrastructure/   # Infrastructure Layer
│       │   ├── common/       # Logging utilities
│       │   ├── extensions/   # External service integrations
│       │   │   ├── psql_ext/      # PostgreSQL extension
│       │   │   └── redis_ext/     # Redis extension
│       │   │
│       │   ├── messaging/    # Message queue clients
│       │   │   ├── clients/
│       │   │   │   ├── kafka_client.py
│       │   │   │   └── rabbitmq_client.py
│       │   │   └── mq_client.py
│       │   │
│       │   ├── persistence/  # Database layer
│       │   │   ├── migrations/    # Alembic migrations
│       │   │   │   ├── env.py
│       │   │   │   └── versions/
│       │   │   └── models/        # SQLAlchemy models
│       │   │       ├── mixins.py
│       │   │       └── users.py
│       │   │
│       │   ├── repositories/ # Repository pattern
│       │   │   ├── base/
│       │   │   │   ├── abstract.py
│       │   │   │   ├── base_psql_repository.py
│       │   │   │   └── base_redis_repository.py
│       │   │   ├── container.py
│       │   │   ├── users_repository.py
│       │   │   ├── common_psql_repository.py
│       │   │   └── common_redis_repository.py
│       │   │
│       │   ├── tasks/        # Celery tasks
│       │   │   └── example_task.py
│       │   │
│       │   └── utils/        # Infrastructure utilities
│       │       └── common.py
│       │
│       └── interfaces/       # Interface Layer
│           ├── api/          # REST API
│           │   ├── core/
│           │   │   ├── dependencies.py
│           │   │   └── schemas/
│           │   ├── error_handlers.py
│           │   ├── routers.py
│           │   └── v1/
│           │       ├── endpoints/
│           │       │   ├── auth/        # Auth endpoints
│           │       │   ├── debug/       # Debug endpoints
│           │       │   └── users/       # Users endpoints
│           │       └── routers.py
│           │
│           ├── cli/          # CLI interfaces
│           │   ├── main.py            # FastAPI app initialization
│           │   ├── celery_app.py      # Celery app
│           │   ├── consume.py         # Message consumer
│           │   └── gunicorn_config.py # Gunicorn config
│           │
│           └── grpc/         # gRPC server
│               ├── server.py
│               ├── client.py
│               ├── pb/              # Generated protobuf code
│               └── services/        # gRPC service implementations
│
├── static/                   # Static files
│
├── tests/                    # Test suite
│   ├── application/         # Application layer tests
│   ├── domain/              # Domain layer tests
│   ├── fixtures/            # Test fixtures
│   ├── infrastructure/      # Infrastructure tests
│   └── conftest.py          # Pytest configuration
│
├── .env.example             # Environment variables template
├── alembic.ini              # Alembic configuration
├── pyproject.toml           # Poetry dependencies & config
├── pytest.ini               # Pytest configuration
├── docker-compose-tests.yml # Test environment
├── local_prepare.sh         # Launch infrastructure
├── local_run.sh             # Launch application
└── beautify.sh              # Code quality checks
```

---

## Layer Breakdown

### 1. Domain Layer (Core Business Logic)

**Location**: `src/app/domain/`

**Purpose**: Contains pure business logic, independent of frameworks and external systems.

**Components**:

#### Aggregates (`domain/*/aggregates/`)
- Root entities that ensure consistency boundaries
- Example: `UserAggregate` - src/app/domain/users/aggregates/user_agg.py:9
```python
@dataclass
class UserAggregate(BaseAggregate):
    id: int
    uuid: str
    email: str
    # ... domain properties
```

#### Entities (`domain/common/entities/`)
- Domain objects with identity
- Base: `BaseEntity` - src/app/domain/common/entities/base.py:5

#### Value Objects (`domain/*/value_objects/`)
- Immutable objects defined by their attributes
- Examples: `EmailPasswordPair`, `TokenPair`, `DecodedToken`

#### Domain Services (`domain/*/services/`)
- Business logic that doesn't fit in entities
- Examples:
  - `DomainJWTService` - src/app/domain/auth/services/jwt_service.py:15 - JWT operations
  - `DomainUsersService` - src/app/domain/users/services/users_service.py:4

#### Domain Events (`domain/common/events/`)
- Events that represent domain occurrences
- Base: `DomainEvent` - src/app/domain/common/events/base.py

#### Custom Exceptions (`domain/common/exceptions.py`)
- `AppException` - Base exception
- `ValidationError` - Data validation failed
- `NotFoundError` - Resource not found
- `AlreadyExistsError` - Resource already exists
- `AuthenticationError` - Auth failed
- `AuthorizationError` - Insufficient permissions

### 2. Application Layer

**Location**: `src/app/application/`

**Purpose**: Orchestrates domain logic, implements use cases.

**Components**:

#### Application Services (`application/services/`)
Coordinate domain objects to fulfill use cases:

- **AppUserService** - src/app/application/services/users_service.py:16
  - `create_user_by_email()` - src/app/application/services/users_service.py:29
  - `create_user_by_phone()` - src/app/application/services/users_service.py:53

- **AppAuthService** - src/app/application/services/auth_service.py
  - Authentication & token management

- **AppCommonService** - src/app/application/services/common_service.py
  - Common application operations

#### DTOs (Data Transfer Objects) (`application/dto/`)
- Transfer data between layers
- Example: `UserShortDTO` - src/app/application/dto/user.py

#### Container (`application/container.py`)
- Service locator pattern - src/app/application/container.py:7
- Provides lazy-loaded service instances

### 3. Infrastructure Layer

**Location**: `src/app/infrastructure/`

**Purpose**: Implements technical concerns (persistence, messaging, etc.).

**Components**:

#### Repositories (`infrastructure/repositories/`)

**Base Repository** - src/app/infrastructure/repositories/base/base_psql_repository.py:598

Provides comprehensive CRUD operations with:
- **Security validations** (SQL injection prevention)
- **Advanced filtering** with lookup operations:
  - `gt`, `gte`, `lt`, `lte` - Comparisons
  - `e`, `ne` - Equality
  - `in`, `not_in` - List operations
  - `like`, `ilike` - Pattern matching
  - `jsonb_like`, `jsonb_not_like` - JSONB field queries
- **Ordering** with ASC/DESC support
- **Pagination** (limit/offset)
- **Bulk operations** (create_bulk, update_bulk)
- **Type validation** for filter values

Example usage:
```python
# Filter with lookups
users = await UsersPSQLRepository.get_list(
    filter_data={
        "age__gte": 18,           # age >= 18
        "email__ilike": "test",   # email ILIKE '%test%'
        "status__in": ["active", "pending"],
        "meta__preferences__jsonb_like": "dark_mode",
        "limit": 10,
        "offset": 0
    },
    order_data=("-created_at", "name")  # DESC, then ASC
)
```

**Concrete Repositories**:
- `UsersPSQLRepository` - src/app/infrastructure/repositories/users_repository.py:5
- `CommonPSQLRepository` - Generic repository
- `CommonRedisRepository` - Redis operations

#### Persistence (`infrastructure/persistence/`)

**Models** (`persistence/models/`):
- SQLAlchemy ORM models
- Example: `User` model - src/app/infrastructure/persistence/models/users.py:10
  - Inherits from `Base` and `PKMixin`
  - Includes: id, uuid, timestamps, user fields

**Migrations** (`persistence/migrations/`):
- Alembic migrations - src/app/infrastructure/persistence/migrations/env.py
- Automatic schema version control

#### Extensions (`infrastructure/extensions/`)

**PostgreSQL Extension** - src/app/infrastructure/extensions/psql_ext/psql_ext.py
- Async SQLAlchemy engine
- Session management via `get_session()` context manager
- Connection pooling

**Redis Extension** - src/app/infrastructure/extensions/redis_ext/redis_ext.py
- Redis client wrapper
- Connection pooling

#### Messaging (`infrastructure/messaging/`)

**RabbitMQ Client** - src/app/infrastructure/messaging/clients/rabbitmq_client.py:12
- Async message publishing: `produce_messages()`
- Message consumption: `consume()`
- Connection pooling
- Auto-reconnection

**Kafka Client** - src/app/infrastructure/messaging/clients/kafka_client.py
- Similar async interface

#### Tasks (`infrastructure/tasks/`)
- Celery tasks for background processing
- Example: `say_meow` - src/app/infrastructure/tasks/example_task.py:8

### 4. Interfaces Layer

**Location**: `src/app/interfaces/`

**Purpose**: Exposes application to external world.

#### REST API (`interfaces/api/`)

**Structure**:
- `routers.py` - Main API router - src/app/interfaces/api/routers.py:5
- `error_handlers.py` - Global exception handlers - src/app/interfaces/api/error_handlers.py
- `v1/` - API version 1

**Endpoints**:

1. **Auth Endpoints** - src/app/interfaces/api/v1/endpoints/auth/resources.py
   - `POST /api/v1/auth/sign-up/` - User registration
   - `POST /api/v1/auth/tokens/` - Get token pair (email/password)
   - `POST /api/v1/auth/tokens/refresh/` - Refresh tokens

2. **Users Endpoints** - src/app/interfaces/api/v1/endpoints/users/resources.py
   - `GET /api/v1/users/me/` - Get current user

3. **Debug Endpoints** - src/app/interfaces/api/v1/endpoints/debug/resources.py
   - Health checks and debugging

**Error Handling** - src/app/interfaces/api/error_handlers.py:26
- Standardized error responses with error IDs
- Debug mode shows detailed traces
- Maps domain exceptions to HTTP status codes

**Dependencies** - src/app/interfaces/api/core/dependencies.py:9
- `validate_api_key()` - Extract bearer token
- `validate_auth_data()` - Verify JWT and decode payload

#### gRPC Server (`interfaces/grpc/`)

**Server** - src/app/interfaces/grpc/server.py:14
- Async gRPC server
- Dynamic worker pool based on CPU count
- Services:
  - `DebugService` - Health checks
  - `ExampleService` - Example RPC

**Protocol Buffers** (`interfaces/grpc/pb/`)
- Generated protobuf code
- Organized by service

#### CLI (`interfaces/cli/`)

**Main Application** - src/app/interfaces/cli/main.py:12
- FastAPI app initialization
- Middleware registration (CORS)
- Router inclusion
- Lifecycle events (startup/shutdown)

**Celery App** - src/app/interfaces/cli/celery_app.py:3
- Celery worker configuration
- Task auto-discovery

**Message Consumer** - src/app/interfaces/cli/consume.py:15
- Standalone consumer process
- Event-driven task dispatching
- Maps events to handlers

---

## Key Components

### 1. Base Repository with Advanced Query Building

**File**: src/app/infrastructure/repositories/base/base_psql_repository.py

**Features**:
- **Security First**: SQL injection prevention, input validation
- **Lookup Operations**: Rich query DSL (gt, gte, like, in, jsonb_like, etc.)
- **Type Safety**: Runtime type validation against column types
- **Performance**: Bulk operations, connection pooling
- **Flexibility**: Dynamic dataclass generation, custom output types

**Key Classes**:
- `PSQLLookupRegistry` - Lookup operation mapping - src/app/infrastructure/repositories/base/base_psql_repository.py:36
- `SecurityValidator` - Input security validation - src/app/infrastructure/repositories/base/base_psql_repository.py:214
- `QueryBuilder` - SQL query construction - src/app/infrastructure/repositories/base/base_psql_repository.py:334
- `BasePSQLRepository` - Repository base class - src/app/infrastructure/repositories/base/base_psql_repository.py:598

### 2. JWT Authentication System

**Components**:
- **DomainJWTService** - src/app/domain/auth/services/jwt_service.py:15
  - Token creation (access & refresh)
  - Token verification
  - Expiration handling

- **Token Types**: Access (5 min default), Refresh (5 days default)
- **Session IDs**: Each token pair has linked session IDs

### 3. Error Handling System

**Exception Hierarchy** - src/app/domain/common/exceptions.py:4
```
AppException (base)
├── ValidationError
├── NotFoundError
├── AlreadyExistsError
├── AuthenticationError
└── AuthorizationError
```

**Error Handler** - src/app/interfaces/api/error_handlers.py
- Generates unique error IDs for tracking
- Debug mode: Shows full traceback + details
- Production mode: Hides sensitive information
- Logs all 500+ errors

### 4. Message Queue Integration

**RabbitMQ Client** - src/app/infrastructure/messaging/clients/rabbitmq_client.py:12
- Connection pooling (5 connections, 10 channels)
- Auto-reconnection on failure
- Support for multiple exchanges/queues
- Event-driven message processing

**Consumer Pattern** - src/app/interfaces/cli/consume.py:15
```python
HANDLERS_MAP = {
    "event_name": {
        "handler": task_function,
        "celery_queue": queue_name
    }
}
```

### 5. Dependency Injection (Service Container)

**Application Container** - src/app/application/container.py:7
```python
container.users_service  # Returns AppUserService
container.auth_service   # Returns AppAuthService
```

**Domain Containers**:
- `domain.users.container`
- `domain.auth.container`

**Repository Container** - src/app/infrastructure/repositories/container.py

---

## Configuration

### Environment Variables

**File**: `.env.example` (copy to `.env`)

**Key Settings**:

```bash
# Base
PROJECT_NAME=APP_DDD
SECRET_KEY=<your-secret-key>

# Launch Mode: LOCAL, TEST, PROD
LAUNCH_MODE=TEST
DEBUG=False

# API
API_PORT=8081
SHOW_API_DOCS=True
CORS_ORIGIN_WHITELIST=["*"]

# gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50051

# Auth
ACCESS_TOKEN_EXPIRES_MINUTES=5
REFRESH_TOKEN_EXPIRES_DAYS=5

# Database
DB_HOST=127.0.0.1
DB_PORT=5440
DB_NAME=proto
DB_USER=dev
DB_PASSWORD=dev
CONNECTIONS_POOL_MIN_SIZE=10
CONNECTIONS_POOL_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://127.0.0.1:6380/0

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6380/11
CELERY_RESULT_BACKEND=redis://127.0.0.1:6380/12

# Message Broker
MESSAGE_BROKER_URL=amqp://dev:dev@0.0.0.0:5672
DEFAULT_EXCHANGER=YOUR_DEFAULT_EXCHANGER
DEFAULT_QUEUE=YOUR_DEFAULT_QUEUE
```

### Settings Class

**File**: src/app/config/settings.py:14

**Launch Modes**:
- `SettingsLocal` - Local development
- `SettingsTest` - Testing
- `SettingsProd` - Production (DEBUG=False)

**Usage**:
```python
from src.app.config.settings import settings

db_url = settings.DB_URL
api_port = settings.API_PORT
```

---

## Database

### Models

**User Model** - src/app/infrastructure/persistence/models/users.py:10

```python
class User(Base, PKMixin):
    __tablename__ = "users"

    # Metadata
    meta = Column(JSONB, default=dict)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, onupdate=datetime.now)

    # Profile
    first_name = Column(String(128))
    last_name = Column(String(128))
    email = Column(String(128))
    password_hashed = Column(String(128))
    birthday = Column(DateTime)
    photo = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)
    is_guest = Column(Boolean)

    # Contact
    phone = Column(String(64))
    street = Column(String(128))
    city = Column(String(64))
    state = Column(String(24))
    zip_code = Column(String(24))
    country = Column(String(64))
```

### Mixins

**PKMixin** - src/app/infrastructure/persistence/models/mixins.py
- Provides `id` (auto-increment) and `uuid` (UUID4)

### Migrations

**Alembic Configuration** - `alembic.ini`

**Commands**:
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Migration Files**: `src/app/infrastructure/persistence/migrations/versions/`

### Database Session

**Connection Management** - src/app/infrastructure/extensions/psql_ext/psql_ext.py

```python
async with get_session() as session:
    # Your database operations
    result = await session.execute(query)
    await session.commit()
```

---

## Authentication & Authorization

### JWT Token Flow

1. **Sign Up**: `POST /api/v1/auth/sign-up/`
   - Create user with hashed password
   - Returns user data

2. **Login**: `POST /api/v1/auth/tokens/`
   - Verify email/password
   - Generate token pair (access + refresh)
   - Returns tokens + user UUID

3. **Refresh**: `POST /api/v1/auth/tokens/refresh/`
   - Verify refresh token
   - Generate new token pair
   - Returns new tokens

4. **Protected Endpoints**: Add `Depends(validate_auth_data)`
   ```python
   @router.get("/me/")
   async def get_me(auth_data: dict = Depends(validate_auth_data)):
       uuid = auth_data["uuid"]
       # ... fetch user
   ```

### Token Structure

**Access Token**:
```json
{
  "user": {
    "uuid": "user-uuid",
    "sid": "session-id"
  },
  "type": "access",
  "exp": 1234567890
}
```

**Refresh Token**:
```json
{
  "user": {
    "uuid": "user-uuid",
    "sid": "extended-session-id#linked-access-sid"
  },
  "type": "refresh",
  "exp": 1234567890
}
```

### Password Hashing

**Service**: `DomainAuthService` - src/app/domain/auth/services/auth_service.py
- Uses bcrypt via passlib
- Automatic salt generation

---

## Messaging & Background Tasks

### Celery Tasks

**Configuration** - src/app/config/celery.py

**Creating Tasks**:
```python
# src/app/infrastructure/tasks/my_task.py
from src.app.interfaces.cli.celery_app import celery_app

@celery_app.task()
def my_async_task(arg1, arg2):
    # Task logic
    return result
```

**Running Worker**:
```bash
celery -A src.app.interfaces.cli.celery_app worker \
  -l INFO -E -B \
  -Q default_queue \
  --concurrency=2 \
  -n default@%h
```

### RabbitMQ Consumer

**Configuration** - src/app/interfaces/cli/consume.py:12

**Handler Mapping**:
```python
HANDLERS_MAP = {
    "event_name": {
        "handler": handler_function,  # Can be Celery task or async function
        "celery_queue": "queue_name"  # Optional
    }
}
```

**Message Format**:
```json
{
  "event": "event_name",
  "data": {
    "key": "value"
  }
}
```

**Running Consumer**:
```bash
python -m src.app.interfaces.cli.consume
```

### Publishing Messages

```python
from src.app.infrastructure.messaging.mq_client import mq_client

await mq_client.produce_messages(
    messages=[{"event": "user_created", "data": {"user_id": 123}}],
    queue_name="default_queue",
    exchanger_name="default_exchanger"
)
```

---

## Testing

### Test Structure

```
tests/
├── application/          # Application service tests
│   └── users/
│       └── services/
│           └── test_users_service.py
├── domain/              # Domain logic tests
│   └── users/
├── infrastructure/      # Infrastructure tests
│   ├── messaging/
│   └── repositories/
├── fixtures/            # Test data & fixtures
│   ├── constants.py
│   └── users.py
└── conftest.py         # Pytest configuration
```

### Running Tests

**All Tests**:
```bash
pytest

# With coverage
pytest --cov=src --cov-report=html
```

**Specific Tests**:
```bash
pytest tests/application/users/
pytest tests/infrastructure/repositories/
```

**Docker Tests**:
```bash
docker-compose -f docker-compose-tests.yml up --abort-on-container-exit
```

### Test Examples

**Repository Tests** - tests/infrastructure/repositories/test_users_repository.py
- CRUD operations
- Bulk operations
- Filtering & pagination
- Type validation

**Service Tests** - tests/application/users/services/test_users_service.py:15
- User creation
- Count operations
- Update/delete operations
- Bulk operations

### Fixtures

**conftest.py** - tests/conftest.py:13
```python
@pytest.fixture(scope="session")
def e_loop() -> AbstractEventLoop:
    return asyncio.get_event_loop()

@pytest.fixture(scope="function")
def client(db: Session) -> Generator:
    with TestClient(app) as c:
        yield c
```

---

## API Endpoints

### Authentication

#### Sign Up
```http
POST /api/v1/auth/sign-up/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response 200:
{
  "uuid": "...",
  "email": "user@example.com",
  "created_at": "2025-01-01T00:00:00"
}
```

#### Get Tokens
```http
POST /api/v1/auth/tokens/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response 200:
{
  "user_data": {"uuid": "..."},
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

#### Refresh Tokens
```http
POST /api/v1/auth/tokens/refresh/
Authorization: Bearer <refresh_token>

Response 200:
{
  "user_data": {"uuid": "..."},
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

### Users

#### Get Current User
```http
GET /api/v1/users/me/
Authorization: Bearer <access_token>

Response 200:
{
  "id": 1,
  "uuid": "...",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

### API Documentation

Access interactive API docs:
- Swagger UI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`

---

## Running the Application

### Prerequisites

- Python 3.12
- Poetry (for dependency management)
- Docker & Docker Compose (for infrastructure)
- PostgreSQL
- Redis
- RabbitMQ (optional, for messaging)

### Setup

1. **Clone & Install**:
```bash
cd fastapi_prototype
poetry env use 3.12
poetry install
```

2. **Environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Infrastructure**:
```bash
# Launch PostgreSQL, Redis, RabbitMQ
bash local_prepare.sh

# Or with recreate
bash local_prepare.sh --recreate
```

### Running Services

#### 1. FastAPI (REST API)

**Development**:
```bash
uvicorn src.app.interfaces.cli.main:app --reload --port 8081
```

**Production**:
```bash
gunicorn src.app.interfaces.cli.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8081
```

**Docker**:
```bash
bash local_run.sh --run_api
```

#### 2. gRPC Server

```bash
python -m src.app.interfaces.grpc.server
```

#### 3. Celery Worker

```bash
celery -A src.app.interfaces.cli.celery_app worker \
  -l INFO -E -B \
  -Q default_queue \
  --concurrency=2 \
  -n default@%h
```

**Docker**:
```bash
bash local_run.sh --run_celery
```

#### 4. Message Consumer

```bash
python -m src.app.interfaces.cli.consume
```

**Docker**:
```bash
bash local_run.sh --run_consume
```

### Docker Compose

**Full Stack**:
```bash
# Launch infrastructure
bash local_prepare.sh

# Launch application services
bash local_run.sh --run_api --run_grpc

# With recreate
bash local_run.sh --recreate --run_api
```

---

## Development Workflow

### Code Quality

**Check All**:
```bash
bash beautify.sh
```

**Individual Tools**:
```bash
# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/ tests/
```

### Database Migrations

1. **Create Migration**:
```bash
alembic revision --autogenerate -m "add user table"
```

2. **Review** generated file in `src/app/infrastructure/persistence/migrations/versions/`

3. **Apply**:
```bash
alembic upgrade head
```

4. **Rollback** (if needed):
```bash
alembic downgrade -1
```

### gRPC Development

1. **Define Service** in `.proto` file

2. **Generate Code**:
```bash
python -m grpc_tools.protoc \
  --proto_path ./src/app/interfaces/grpc/protos \
  --python_out=./src/app/interfaces/grpc/pb/your_service \
  --grpc_python_out=./src/app/interfaces/grpc/pb/your_service \
  ./src/app/interfaces/grpc/protos/your_service.proto
```

3. **Implement Service** in `src/app/interfaces/grpc/services/`

4. **Register** in `server.py`

### Adding New Domain

1. **Create Domain Structure**:
```
src/app/domain/new_domain/
├── __init__.py
├── aggregates/
│   └── new_agg.py
├── services/
│   └── new_service.py
├── value_objects/
│   └── new_vob.py
└── container.py
```

2. **Create Infrastructure**:
```
src/app/infrastructure/persistence/models/
└── new_model.py

src/app/infrastructure/repositories/
└── new_repository.py
```

3. **Create Application Service**:
```
src/app/application/services/
└── new_service.py
```

4. **Create API Endpoints**:
```
src/app/interfaces/api/v1/endpoints/new_domain/
├── resources.py
└── schemas/
```

5. **Add Tests**:
```
tests/
├── domain/new_domain/
├── application/new_domain/
└── infrastructure/repositories/test_new_repository.py
```

### Documentation

**Build Sphinx Docs**:
```bash
cd docs
make html
# Open docs/build/html/index.html
```

---

## Best Practices

### 1. Repository Usage

```python
# ✅ Good: Use lookups for filtering
users = await repo.get_list(
    filter_data={
        "age__gte": 18,
        "status__in": ["active", "pending"],
        "email__ilike": "test"
    }
)

# ❌ Bad: Don't construct raw SQL
users = await session.execute("SELECT * FROM users WHERE age >= 18")
```

### 2. Error Handling

```python
# ✅ Good: Use domain exceptions
from src.app.domain.common.exceptions import NotFoundError

user = await repo.get_first(filter_data={"id": user_id})
if not user:
    raise NotFoundError(
        message="User not found",
        details=[{"key": "user_id", "value": user_id}]
    )

# ❌ Bad: Generic exceptions
if not user:
    raise Exception("User not found")
```

### 3. Dependency Injection

```python
# ✅ Good: Use containers
from src.app.application.container import container

user_service = container.users_service
users = await user_service.get_list()

# ❌ Bad: Direct instantiation
user_service = AppUserService()
```

### 4. Async Operations

```python
# ✅ Good: Proper async/await
async def get_users():
    async with get_session() as session:
        result = await session.execute(query)
        return result.scalars().all()

# ❌ Bad: Blocking operations in async context
async def get_users():
    time.sleep(1)  # Blocks event loop!
```

### 5. Testing

```python
# ✅ Good: Test business logic, not implementation
def test_user_creation_validates_email():
    with pytest.raises(ValidationError):
        await service.create_user_by_email("invalid-email", "pass")

# ❌ Bad: Testing implementation details
def test_user_creation_calls_repository():
    with patch('repo.create') as mock:
        await service.create_user_by_email("test@test.com", "pass")
        assert mock.called
```

---

## Common Issues & Solutions

### Issue: Database connection pool exhausted

**Solution**:
```python
# Always use context managers
async with get_session() as session:
    # Operations
    await session.commit()
```

### Issue: Alembic can't detect model changes

**Solution**:
- Ensure model is imported in `models/container.py`
- Check `target_metadata` in `migrations/env.py`
- Try: `alembic revision --autogenerate -m "force" --head=head`

### Issue: JWT token expired errors

**Solution**:
- Check `ACCESS_TOKEN_EXPIRES_MINUTES` in `.env`
- Implement refresh token flow
- Add token refresh interceptor in client

### Issue: Celery tasks not executing

**Solution**:
1. Check Celery worker is running
2. Verify `CELERY_BROKER_URL` is correct
3. Ensure task is imported in `celery_app.py`
4. Check queue name matches

### Issue: Tests failing with database errors

**Solution**:
- Ensure test database is separate from dev
- Run migrations on test DB
- Use fixtures for test data
- Clean up data between tests

---

## Performance Optimization Tips

1. **Repository Bulk Operations**:
   - Use `create_bulk()` and `update_bulk()` for multiple records
   - Set `is_return_require=False` when you don't need returned data

2. **Database Connection Pooling**:
   - Tune `CONNECTIONS_POOL_MIN_SIZE` and `CONNECTIONS_POOL_MAX_OVERFLOW`
   - Monitor pool usage

3. **Query Optimization**:
   - Use `select()` with specific columns, not `SELECT *`
   - Add database indexes for frequently filtered columns
   - Use pagination for large result sets

4. **Async Operations**:
   - Use `asyncio.gather()` for parallel async calls
   - Avoid blocking operations in async functions

5. **Caching**:
   - Use Redis for frequently accessed data
   - Implement cache invalidation strategy

---

## Security Considerations

1. **SQL Injection Prevention**:
   - Repository implements input validation
   - Use parameterized queries (SQLAlchemy handles this)
   - Validate filter keys against allowed columns

2. **Authentication**:
   - JWT tokens with expiration
   - Password hashing with bcrypt
   - Refresh token rotation

3. **Input Validation**:
   - Pydantic schemas for API input
   - Repository validates filter data types
   - Length limits on string inputs

4. **Environment Variables**:
   - Never commit `.env` file
   - Use strong `SECRET_KEY`
   - Rotate secrets regularly

5. **Error Messages**:
   - Hide sensitive data in production
   - Use error IDs for tracking
   - Log security events

---

## Project Status & Roadmap

### Current Status
✅ **Implemented**:
- Core architecture (DDD + Onion)
- User domain with authentication
- Repository pattern with advanced querying
- REST API with FastAPI
- gRPC server
- Message queue integration (RabbitMQ, Kafka)
- Background tasks (Celery)
- Comprehensive testing
- Docker support

⚠️ **Not Production-Ready**:
- Missing comprehensive error recovery
- Limited logging/monitoring
- No rate limiting
- Basic security measures
- Incomplete documentation

### Roadmap for Production

**Phase 1: Core Stability**
- [ ] Add rate limiting middleware
- [ ] Implement comprehensive logging (structured logs)
- [ ] Add health check endpoints
- [ ] Implement circuit breakers for external services
- [ ] Add request/response tracing

**Phase 2: Security Hardening**
- [ ] Implement role-based access control (RBAC)
- [ ] Add API key management
- [ ] Security audit & penetration testing
- [ ] Implement audit logging
- [ ] Add input sanitization middleware

**Phase 3: Observability**
- [ ] Integrate APM (e.g., Prometheus, Grafana)
- [ ] Add distributed tracing (e.g., Jaeger)
- [ ] Implement alerting system
- [ ] Add performance metrics
- [ ] Create operational dashboards

**Phase 4: Scalability**
- [ ] Implement caching strategy
- [ ] Add database read replicas
- [ ] Optimize query performance
- [ ] Implement sharding strategy
- [ ] Add horizontal scaling support

---

## Contributing Guidelines

1. **Code Style**:
   - Follow PEP 8
   - Use Black for formatting (line length: 115)
   - Type hints required for all functions
   - Run `bash beautify.sh` before committing

2. **Branching Strategy**:
   - `main` - Production-ready code
   - `dev` - Development branch
   - `feature/*` - New features
   - `bugfix/*` - Bug fixes

3. **Commit Messages**:
   - Use conventional commits format
   - Examples:
     - `feat: add user profile endpoint`
     - `fix: resolve JWT expiration bug`
     - `docs: update API documentation`

4. **Pull Requests**:
   - Reference related issues
   - Include tests for new features
   - Update documentation
   - Ensure CI passes

5. **Testing**:
   - Maintain >80% test coverage
   - Write unit tests for business logic
   - Write integration tests for endpoints
   - Add fixtures for test data

---

## Useful Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Celery: https://docs.celeryq.dev/
- Pytest: https://docs.pytest.org/

### Project Files
- Configuration: `.env.example`, `pyproject.toml`, `alembic.ini`
- Scripts: `local_prepare.sh`, `local_run.sh`, `beautify.sh`
- Documentation: `README.rst`, `CLAUDE.md`

### Architecture References
- Domain-Driven Design: Eric Evans
- Clean Architecture: Robert C. Martin
- Onion Architecture: Jeffrey Palermo

---

## Contact & Support

- **Team Email**: dream_team@gmail.com (from settings)
- **Issues**: Create an issue in the repository
- **Documentation**: See `/docs` folder for detailed API docs

---

## License

[Specify your license here]

---

**Generated Documentation** - This file provides comprehensive documentation for the FastAPI DDD prototype project. It covers architecture, components, usage, and best practices for development and deployment.