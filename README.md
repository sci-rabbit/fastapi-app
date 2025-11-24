# fastapi-app

Асинхронный backend интернет-приложение(API) на FastAPI. Проект построен как production-ready сервис: слои Router → Service → Repository, строгая валидация Pydantic v2, собственный модуль авторизации на FastAPI Users, кеш/лимитер в Redis и наблюдаемость через structlog.

## Основные возможности
- **Асинхронный REST API**: CRUD по пользователям, заказам, товарам, категориям и постам, пагинация и выборки по связям.
- **Чистая архитектура**: Router → Service → Repository + helper `run_crud_action`, который управляет транзакциями `AsyncSession`, refresh’ем и сериализацией схем.
- **PostgreSQL + SQLAlchemy 2.0 async**: UUID PK, audit-поля, Alembic-миграции, чёткое разделение доменных/инфраструктурных моделей.
- **Redis-интеграция**: FastAPI Cache, FastAPI Limiter, rate limiting всего API, быстрый запуск через lifespan.
- **Авторизация**: FastAPI Users, bearer-токены, хранение access tokens в Postgres, регистрация/верификация/reset password, ограничения по ролям `current_active_user / current_active_superuser`.
- **Наблюдаемость и устойчивость**: structlog + стандартный logging, middleware с `X-Request-ID`, централизованные обработчики ошибок, health-check эндпоинты, rate limiting.
- **Готовность к CI/CD**: reproducible окружение на Docker Compose, конфиги через `pydantic-settings`, dotenv-driven деплой.

## Технологический стек
- **Backend**: Python 3.12, FastAPI 0.116, Uvicorn
- **Данные**: SQLAlchemy 2.0 (async), asyncpg, Alembic, PostgreSQL 17
- **Auth**: FastAPI Users, bearer transport, access-token storage в БД
- **Infra**: Redis 7.4, fastapi-cache2, fastapi-limiter, Docker / Docker Compose
- **Утилиты**: Pydantic v2, FastAPI Pagination, structlog, orjson, Poetry

## Структура репозитория
```
.
├── docker-compose.yaml
├── main.py
├── pyproject.toml / poetry.lock
├── alembic/
│   ├── env.py
│   └── versions/                  # миграции
└── fastapi_application/
    ├── create_fastapi_app.py      # Lifespan, Redis, cache, limiter
    ├── middleware.py              # CorrelationIdMiddleware
    ├── error_handlers.py          # Централизованные exception handlers
    ├── core/
    │   ├── config.py              # Pydantic Settings (.env)
    │   ├── logging_config.py
    │   ├── db.py                  # Async engine + session factory
    │   ├── models/                # SQLAlchemy модели (User, Product, Order...)
    │   ├── schemas/               # Pydantic схемы
    │   └── authentication/
    │       ├── transport.py       # BearerTransport tokenUrl
    │       ├── fa_users.py        # FastAPIUsers + current_user deps
    │       └── user_manager.py    # кастомный UserManager
    ├── api/
    │   ├── __init__.py            # глобальный RateLimiter и префикс /api
    │   ├── api_v1/
    │   │   ├── __init__.py        # health-checks, включение роутеров
    │   │   ├── views/
    │   │   │   ├── auth_views.py
    │   │   │   ├── user_views.py
    │   │   │   ├── product_views.py
    │   │   │   ├── category_views.py
    │   │   │   ├── order_views.py
    │   │   │   └── post_views.py
    │   │   └── main_dependencies_for_views.py
    │   ├── repositories/          # BaseRepository, *Repository
    │   ├── services/              # бизнес-логика и логирование
    │   └── dependencies/
    │       └── authentication/    # backend, strategy, user manager, dbs
    └── redis_conf/
        └── redis.py               # async Redis client
```

## Авторизация и безопасность
- **FastAPI Users**: `authentication_backend` использует bearer-транспорт (`tokenUrl=settings.api.bearer_token_url`) и `DatabaseStrategy`, которая хранит access-токены в Postgres (`AccessToken` модель).
- **Маршруты** (см. `fastapi_application/api/api_v1/views/auth_views.py`):
  - `POST /api/v1/auth/login` — получение bearer-токена.
  - `POST /api/v1/auth/logout`.
  - `POST /api/v1/auth/register` — регистрация пользователя (`UserCreate`).
  - `POST /api/v1/auth/request-verify-token` / `POST /api/v1/auth/verify`.
  - `POST /api/v1/auth/forgot-password` / `POST /api/v1/auth/reset-password`.
- **Защищённые ресурсы**: параметры `Depends(current_active_user)` и `Depends(current_active_superuser)` ограничивают доступ (например, `user_router` доступен только суперадминам).
- **Rate limiting и HTTP Bearer**: глобальный `RateLimiter` в `fastapi_application/api/__init__.py` и `HTTPBearer(auto_error=False)` в `api_v1/__init__.py`.

## Быстрый старт

### 1. Требования
- Python ≥ 3.12
- Poetry ≥ 1.8
- Docker + Docker Compose

### 2. Клонирование и зависимости
```bash
git clone <repo-url> fastapi-app
cd fastapi-app
poetry install
```

### 3. Конфигурация
Создайте `.env` рядом с `fastapi_application/core/config.py`:
```env
DB__USER=postgres
DB__PASSWORD=postgres
DB__HOST=localhost
DB__PORT=5544
DB__NAME=bshop

REDIS__HOST=localhost
REDIS__PORT=6380
REDIS__PASSWORD=redispass

ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET=changeme
ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET=changeme
```

### 4. Поднимите инфраструктуру
```bash
docker compose up -d
```
Запускает PostgreSQL 17 и Redis 7 (volume’ы `postgres_data`, `redis_data`).

### 5. Миграции
```bash
init alembic alembic
```
```bash
alembic revision --autogenerate
```
```bash
alembic upgrade head
```

### 6. Запуск приложения
```bash
python main.py
```
Swagger UI: `http://localhost:8000/docs`. Все эндпоинты находятся под `/api/v1`, авторизация — `/api/v1/auth/*`.

## Полезные детали
- **Кеширование**: `fastapi-cache2` инициализируется в lifespan (`create_fastapi_app.py`), вьюшки могут использовать `@cache`.
- **Correlation IDs**: middleware генерирует/пробрасывает `X-Request-ID` и добавляет его в structlog.
- **Health-checks**: `GET /api/v1/health` и `/api/v1/health/db`.
- **Логи**: `setup_logging` поддерживает JSON и human-friendly вывод; уровень задаётся в `.env`.