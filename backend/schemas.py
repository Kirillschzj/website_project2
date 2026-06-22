from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    brand: str
    brand_id: Optional[int] = None
    category: Optional[str] = ""
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    price: float
    currency: Optional[str] = "€"
    sizes: Optional[str] = ""
    images: Optional[str] = ""
    telegram_link: Optional[str] = ""
    is_active: Optional[bool] = True


def product_to_dict(p) -> dict:
    return {
        "id": p.id,
        "brand": p.brand,
        "brand_id": p.brand_id,
        "category": p.category,
        "category_id": p.category_id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "currency": p.currency,
        "price_display": f"{p.currency}{int(p.price):,}",
        "sizes": p.sizes.split(",") if p.sizes else [],
        "images": p.images.split(",") if p.images else [],
        "telegram_link": p.telegram_link,
        "created_at": str(p.created_at),
    }
