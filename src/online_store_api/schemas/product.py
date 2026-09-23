import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductOptionCreate(BaseModel):
    name: str
    position: int = 0


class ProductOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    name: str
    position: int


class ProductVariantCreate(BaseModel):
    sku: str
    barcode: str | None = None
    title: str | None = None
    price_cents: int
    compare_at_price_cents: int | None = None
    currency: str = "USD"
    weight_grams: int | None = None
    position: int = 0
    option1: str | None = None
    option2: str | None = None
    option3: str | None = None


class ProductVariantUpdate(BaseModel):
    sku: str | None = None
    barcode: str | None = None
    title: str | None = None
    price_cents: int | None = None
    compare_at_price_cents: int | None = None
    currency: str | None = None
    weight_grams: int | None = None
    position: int | None = None
    option1: str | None = None
    option2: str | None = None
    option3: str | None = None


class ProductVariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    barcode: str | None
    title: str | None
    price_cents: int
    compare_at_price_cents: int | None
    currency: str
    weight_grams: int | None
    position: int
    option1: str | None
    option2: str | None
    option3: str | None
    created_at: datetime
    updated_at: datetime


class ProductImageCreate(BaseModel):
    url: str
    variant_id: uuid.UUID | None = None
    alt: str | None = None
    position: int = 0


class ProductImageUpdate(BaseModel):
    url: str | None = None
    variant_id: uuid.UUID | None = None
    alt: str | None = None
    position: int | None = None


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    variant_id: uuid.UUID | None
    url: str
    alt: str | None
    position: int


class ProductCreate(BaseModel):
    title: str
    slug: str
    description: str | None = None
    status: str = "draft"
    vendor: str | None = None
    product_type: str | None = None
    published_at: datetime | None = None


class ProductUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    status: str | None = None
    vendor: str | None = None
    product_type: str | None = None
    published_at: datetime | None = None


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    status: str
    vendor: str | None
    product_type: str | None


class ProductRead(ProductSummary):
    description: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    options: list[ProductOptionRead] = []
    variants: list[ProductVariantRead] = []
    images: list[ProductImageRead] = []
