from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    op: Mapped[str | None] = mapped_column(String(20), nullable=True)
    a: Mapped[float | None] = mapped_column(Float, nullable=True)
    b: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Expression calculation
    expression: Mapped[str | None] = mapped_column(String(255), nullable=True)

    result: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="calculations")
