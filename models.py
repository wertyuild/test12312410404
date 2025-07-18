from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
import enum
from .database import Base

class OrderStatus(str, enum.Enum):
    pending = "pending"
    notified = "notified"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    stars = Column(Integer)
    payment_method = Column(String)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending) 