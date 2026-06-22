from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    brand: str
    name: str
    description: Optional[str] = ""
    price: float
    currency: Optional[str] = "€"
    sizes: Optional[str] = ""         # "S,M,L"
    images: Optional[str] = ""        # "url1,url2"
    telegram_link: Optional[str] = ""
    is_active: Optional[bool] = True


def product_to_dict(p) -> dict:
    return {
        "id": p.id,
        "brand": p.brand,
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