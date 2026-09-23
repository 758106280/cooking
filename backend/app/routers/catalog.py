from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_admin
from app.models import Category, Ingredient, Tag, User
from app.schemas import CatalogCreate, CatalogUpdate, CategoryOut, IngredientCatalogOut, TagOut


router = APIRouter(prefix="/api/admin", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut])
def admin_categories(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[Category]:
    return db.scalars(select(Category).order_by(Category.sort_order, Category.id)).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CatalogCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Category:
    if db.scalar(select(Category).where(Category.name == payload.name)):
        raise HTTPException(status_code=409, detail="分类名称已存在")
    item = Category(name=payload.name, type=payload.type, sort_order=payload.sort_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/categories/{item_id}", response_model=CategoryOut)
def update_category(item_id: int, payload: CatalogUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Category:
    item = db.get(Category, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="分类不存在")
    item.name = payload.name
    item.type = payload.type
    item.sort_order = payload.sort_order
    item.is_active = payload.is_active
    db.commit()
    db.refresh(item)
    return item


@router.delete("/categories/{item_id}")
def delete_category(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, str]:
    item = db.get(Category, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="分类不存在")
    item.is_active = False
    db.commit()
    return {"message": "分类已停用"}


@router.get("/tags", response_model=list[TagOut])
def admin_tags(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[Tag]:
    return db.scalars(select(Tag).order_by(Tag.name)).all()


@router.post("/tags", response_model=TagOut, status_code=201)
def create_tag(payload: CatalogCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Tag:
    if db.scalar(select(Tag).where(Tag.name == payload.name)):
        raise HTTPException(status_code=409, detail="标签名称已存在")
    item = Tag(name=payload.name, type=payload.type)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/tags/{item_id}", response_model=TagOut)
def update_tag(item_id: int, payload: CatalogUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Tag:
    item = db.get(Tag, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="标签不存在")
    item.name = payload.name
    item.type = payload.type
    db.commit()
    db.refresh(item)
    return item


@router.delete("/tags/{item_id}")
def delete_tag(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, str]:
    item = db.get(Tag, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(item)
    db.commit()
    return {"message": "标签已删除"}


@router.get("/ingredients", response_model=list[IngredientCatalogOut])
def admin_ingredients(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[Ingredient]:
    return db.scalars(select(Ingredient).order_by(Ingredient.name)).all()


@router.post("/ingredients", response_model=IngredientCatalogOut, status_code=201)
def create_ingredient(payload: CatalogCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Ingredient:
    if db.scalar(select(Ingredient).where(Ingredient.name == payload.name)):
        raise HTTPException(status_code=409, detail="食材名称已存在")
    item = Ingredient(name=payload.name, category=payload.type)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/ingredients/{item_id}", response_model=IngredientCatalogOut)
def update_ingredient(item_id: int, payload: CatalogUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Ingredient:
    item = db.get(Ingredient, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="食材不存在")
    item.name = payload.name
    item.category = payload.type
    db.commit()
    db.refresh(item)
    return item


@router.delete("/ingredients/{item_id}")
def delete_ingredient(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, str]:
    item = db.get(Ingredient, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="食材不存在")
    db.delete(item)
    db.commit()
    return {"message": "食材已删除"}
