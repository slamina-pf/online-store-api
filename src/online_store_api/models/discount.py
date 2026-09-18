from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from online_store_api.db.base import Base
from online_store_api.models.mixins import TimestampMixin, UUIDPKMixin


class Discount(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "discounts"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
