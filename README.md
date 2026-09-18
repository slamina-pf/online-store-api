# online-store-api

Backend API for the online store (Shopify-like). This repo currently holds
the database layer: SQLAlchemy models and Alembic migrations. FastAPI routes
will be added in a later phase.

## Stack

- Python 3.12+, managed with [uv](https://docs.astral.sh/uv/)
- SQLAlchemy 2.0 (async) + `asyncpg`
- Alembic for migrations
- Postgres (Supabase, Neon, or any Postgres 14+ instance)

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

## Migrations

```bash
uv run alembic upgrade head        # apply all migrations
uv run alembic revision --autogenerate -m "message"   # after changing models
uv run alembic check               # verify models match the latest migration
```

Models live under `src/online_store_api/models/`. Every model must be
imported in `src/online_store_api/models/__init__.py` so Alembic's
autogenerate can see it.

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
