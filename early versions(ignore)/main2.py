import hashlib
import hmac
import json
import os
import time
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
import models
import schemas

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_telegram_auth(data: dict) -> bool:
    check_hash = data.pop("hash", None)
    if not check_hash:
        return False
    if abs(time.time() - int(data.get("auth_date", 0))) > 86400:
        return False
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, check_hash)


def verify_admin(x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden")


# ═══════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════

@app.post("/api/auth/telegram")
def auth_telegram(payload: dict, db: Session = Depends(get_db)):
    data = dict(payload)
    if not verify_telegram_auth(data):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth data")
    tg_id = str(payload.get("id"))
    user = db.query(models.User).filter(models.User.telegram_id == tg_id).first()
    if not user:
        user = models.User(
            telegram_id=tg_id,
            username=payload.get("username", ""),
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            photo_url=payload.get("photo_url", ""),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"ok": True, "user_id": user.id, "username": user.username, "first_name": user.first_name}


# ═══════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(models.Category).order_by(models.Category.name).all()
    return [{"id": c.id, "name": c.name, "sizes": c.sizes.split(",") if c.sizes else []} for c in cats]

@app.post("/api/admin/categories", dependencies=[Depends(verify_admin)])
def create_category(data: dict, db: Session = Depends(get_db)):
    existing = db.query(models.Category).filter(models.Category.name == data["name"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = models.Category(name=data["name"], sizes=data.get("sizes", ""))
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "sizes": cat.sizes.split(",") if cat.sizes else []}

@app.put("/api/admin/categories/{cat_id}", dependencies=[Depends(verify_admin)])
def update_category(cat_id: int, data: dict, db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    cat.name = data.get("name", cat.name)
    cat.sizes = data.get("sizes", cat.sizes)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "sizes": cat.sizes.split(",") if cat.sizes else []}

@app.delete("/api/admin/categories/{cat_id}", dependencies=[Depends(verify_admin)])
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(cat)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════════
# BRANDS
# ═══════════════════════════════════════════════════════

@app.get("/api/brands")
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(models.Brand).order_by(models.Brand.name).all()
    return [{"id": b.id, "name": b.name} for b in brands]

@app.post("/api/admin/brands", dependencies=[Depends(verify_admin)])
def create_brand(data: dict, db: Session = Depends(get_db)):
    existing = db.query(models.Brand).filter(models.Brand.name == data["name"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Brand already exists")
    brand = models.Brand(name=data["name"])
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return {"id": brand.id, "name": brand.name}

@app.delete("/api/admin/brands/{brand_id}", dependencies=[Depends(verify_admin)])
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(brand)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════════════

@app.get("/api/products")
def get_products(
    search: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    size: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Product).filter(models.Product.is_active == True)
    if search:
        q = q.filter(
            models.Product.name.ilike(f"%{search}%") |
            models.Product.brand.ilike(f"%{search}%")
        )
    if brand:
        q = q.filter(models.Product.brand == brand)
    if category:
        q = q.filter(models.Product.category == category)
    if size:
        q = q.filter(models.Product.sizes.ilike(f"%{size}%"))
    if price_min is not None:
        q = q.filter(models.Product.price >= price_min)
    if price_max is not None:
        q = q.filter(models.Product.price <= price_max)
    if sort == "price-asc":
        q = q.order_by(models.Product.price.asc())
    elif sort == "price-desc":
        q = q.order_by(models.Product.price.desc())
    elif sort == "brand":
        q = q.order_by(models.Product.brand.asc())
    else:
        q = q.order_by(models.Product.created_at.desc())
    return [schemas.product_to_dict(p) for p in q.all()]

@app.get("/api/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return schemas.product_to_dict(p)

@app.post("/api/admin/products", dependencies=[Depends(verify_admin)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = models.Product(**product.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return schemas.product_to_dict(p)

@app.put("/api/admin/products/{product_id}", dependencies=[Depends(verify_admin)])
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in product.dict().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return schemas.product_to_dict(p)

@app.delete("/api/admin/products/{product_id}", dependencies=[Depends(verify_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    p.is_active = False
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════════════
# WISHLIST
# ═══════════════════════════════════════════════════════

@app.get("/api/wishlist/{user_id}")
def get_wishlist(user_id: int, db: Session = Depends(get_db)):
    items = db.query(models.Wishlist).filter(models.Wishlist.user_id == user_id).all()
    product_ids = [i.product_id for i in items]
    products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
    return [schemas.product_to_dict(p) for p in products]

@app.post("/api/wishlist/{user_id}/{product_id}")
def toggle_wishlist(user_id: int, product_id: int, db: Session = Depends(get_db)):
    existing = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == user_id,
        models.Wishlist.product_id == product_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "removed"}
    item = models.Wishlist(user_id=user_id, product_id=product_id)
    db.add(item)
    db.commit()
    return {"action": "added"}


# ═══════════════════════════════════════════════════════
# ADMIN — USERS
# ═══════════════════════════════════════════════════════

@app.get("/api/admin/users", dependencies=[Depends(verify_admin)])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "telegram_id": u.telegram_id, "username": u.username,
             "first_name": u.first_name, "created_at": str(u.created_at)} for u in users]
