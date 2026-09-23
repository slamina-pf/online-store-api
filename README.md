# online-store-api

Backend API for the online store (Shopify-like), built with FastAPI on top
of a Postgres/SQLAlchemy data layer.

## Stack

- Python 3.12+, managed with [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) + `asyncpg`
- Alembic for migrations
- Postgres (Supabase, Neon, or any Postgres 14+ instance; a local instance
  can be run via the included `docker-compose.yml`)

## Setup

```bash
uv sync
cp .env.example .env  # then set DATABASE_URL
```

`DATABASE_URL` must use the `postgresql+asyncpg://` scheme, e.g.:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/online_store
```

This works unchanged whether `host` is a local Postgres, a Supabase
connection string, or a Neon connection string.

### Local Postgres via Docker

```bash
docker compose up -d         # starts postgres:16 on localhost:5432
uv run alembic upgrade head  # create the tables
```

## Running the API

```bash
uv run uvicorn online_store_api.main:app --reload
```

Interactive docs (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API

Endpoints are organized into routers per resource, under
`src/online_store_api/api/routers/`:

- **`/products`** — products, plus nested variants/options/images (full CRUD)
- **`/collections`** — collections, plus collection↔product membership (full CRUD)

More modules (inventory, carts/orders, customers) will follow the same
per-resource router pattern.

## Migrations

```bash
uv run alembic upgrade head        # apply all migrations
uv run alembic revision --autogenerate -m "message"   # after changing models
uv run alembic check               # verify models match the latest migration
```

Models live under `src/online_store_api/models/`. Every model must be
imported in `src/online_store_api/models/__init__.py` so Alembic's
autogenerate can see it.

## Tests

```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE online_store_test"  # one-time
uv run pytest
```

Tests run against a separate `online_store_test` database (same Postgres
instance, different database) so they never touch dev data; all tables are
truncated between tests for isolation.

## Schema overview

- **Catalog**: `products`, `product_options`, `product_variants`,
  `product_images`, `collections`, `collection_products`
- **Inventory**: `inventory_items`, `inventory_locations`, `inventory_levels`
- **Customers**: `customers`, `addresses`
- **Cart/Orders**: `carts`, `cart_items`, `orders`, `order_items`,
  `order_addresses`, `order_events`
- **Payments**: `payments`, `refunds`, `stripe_events`
- **Discounts**: `discounts`

Conventions: UUIDv7 primary keys, money stored as integer cents (`*_cents`
columns) with a separate `currency` column, `timestamptz` timestamps,
soft deletes (`deleted_at`) on `products`/`customers`, and snapshotted data
on `order_items`/`order_addresses` so historical orders don't change if a
product or address is edited later.
