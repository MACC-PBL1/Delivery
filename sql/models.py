#añadir delivery table
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Delivery():
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, default="pending")      # pending, shipped, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="deliveries")


# En la clase Order, añade:
# deliveries = relationship("Delivery", back_populates="order", cascade="all, delete-orphan")
