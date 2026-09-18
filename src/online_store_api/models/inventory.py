import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from online_store_api.db.base import Base
from online_store_api.models.mixins import TimestampMixin, UUIDPKMixin


class InventoryLocation(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "inventory_locations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)


class InventoryItem(UUIDPKMixin, Base):
    __tablename__ = "inventory_items"

    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False)


class InventoryLevel(Base):
    __tablename__ = "inventory_levels"

    inventory_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="CASCADE"), primary_key=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_locations.id", ondelete="CASCADE"), primary_key=True
    )
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
