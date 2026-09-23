import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from online_store_api.schemas.product import ProductSummary


class CollectionCreate(BaseModel):
    title: str
    slug: str
    description: str | None = None


class CollectionUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class CollectionProductAdd(BaseModel):
    product_id: uuid.UUID
    position: int = 0


class CollectionProductRead(BaseModel):
    product: ProductSummary
    position: int
