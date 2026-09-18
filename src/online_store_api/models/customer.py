import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from online_store_api.db.base import Base
from online_store_api.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPKMixin


class Customer(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "customers"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    accepts_marketing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    addresses: Mapped[list["Address"]] = relationship(back_populates="customer")


class Address(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "addresses"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_default_shipping: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default_billing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    customer: Mapped["Customer | None"] = relationship(back_populates="addresses")
