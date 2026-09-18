import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from online_store_api.db.base import Base
from online_store_api.models.mixins import TimestampMixin, UUIDPKMixin


class Cart(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "carts"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_token: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(UUIDPKMixin, Base):
    __tablename__ = "cart_items"

    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_at_add_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="items")
