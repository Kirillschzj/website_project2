from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    sizes = Column(String, default="")  # "XS,S,M,L,XL"
    created_at = Column(DateTime, server_default=func.now())


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now())


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
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    brand = Column(String, index=True)       # дублируем строкой для удобства
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = Column(String, default="")    # дублируем строкой
    name = Column(String)
    description = Column(String, default="")
    price = Column(Float, default=0)
    currency = Column(String, default="€")
    sizes = Column(String, default="")       # "S,M,L"
    images = Column(String, default="")      # "url1,url2"
    telegram_link = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, server_default=func.now())
