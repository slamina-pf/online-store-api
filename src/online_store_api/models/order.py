import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from online_store_api.db.base import Base
from online_store_api.models.mixins import TimestampMixin, UUIDPKMixin


class Order(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    subtotal_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tax_cents: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    shipping_cents: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    discount_cents: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    financial_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    fulfillment_status: Mapped[str] = mapped_column(
        String(30), default="unfulfilled", nullable=False
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    addresses: Mapped[list["OrderAddress"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    events: Mapped[list["OrderEvent"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(UUIDPKMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    sku_snapshot: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")


class OrderAddress(UUIDPKMixin, Base):
    __tablename__ = "order_addresses"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    order: Mapped["Order"] = relationship(back_populates="addresses")


class OrderEvent(UUIDPKMixin, Base):
    __tablename__ = "order_events"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="events")
