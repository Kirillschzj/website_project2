from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, default="")
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    photo_url = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    name = Column(String)
    description = Column(String, default="")
    price = Column(Float, default=0)
    currency = Column(String, default="€")
    sizes = Column(String, default="")   # хранится как "S,M,L"
    images = Column(String, default="")  # хранится как "url1,url2"
    telegram_link = Column(String, default="")  # ссылка на продавца/бота
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, server_default=func.now())