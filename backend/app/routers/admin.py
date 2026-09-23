import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_admin
from app.models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Tag, User
from app.routers.recipes import get_recipe
from app.schemas import PaginatedRecipes, RecipeCreate, RecipeDetail, RecipeUpdate
from app.serializers import recipe_to_detail, recipe_to_summary


router = APIRouter(prefix="/api/admin", tags=["admin"])


def replace_recipe_children(db: Session, recipe: Recipe, payload: RecipeCreate | RecipeUpdate) -> None:
    if payload.category_id is not None and not db.get(Category, payload.category_id):
        raise HTTPException(status_code=400, detail="分类不存在")

    recipe.ingredient_links.clear()
    for index, item in enumerate(payload.ingredients):
        ingredient = db.scalar(select(Ingredient).where(Ingredient.name == item.name.strip()))
        if not ingredient:
            ingredient = Ingredient(name=item.name.strip())
            db.add(ingredient)
            db.flush()
        recipe.ingredient_links.append(
            RecipeIngredient(
                ingredient=ingredient,
                amount=item.amount,
                unit=item.unit,
                note=item.note,
                sort_order=index,
            )
        )

    recipe.steps.clear()
    for step in payload.steps:
        recipe.steps.append(
            RecipeStep(
                step_no=step.step_no,
                description=step.description,
                duration_seconds=step.duration_seconds,
                image=step.image,
            )
        )

    if payload.tag_ids:
        tags = db.scalars(select(Tag).where(Tag.id.in_(payload.tag_ids))).all()
        if len(tags) != len(set(payload.tag_ids)):
            raise HTTPException(status_code=400, detail="存在无效标签")
        recipe.tags = list(tags)
    else:
        recipe.tags = []


@router.get("/recipes", response_model=dict)
def admin_list_recipes(
    status: str | None = Query(default=None, pattern="^(draft|published|archived)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    statement = select(Recipe).where(True)
    if status:
        statement = statement.where(Recipe.status == status)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    recipes = db.scalars(
        statement.order_by(Recipe.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    payload = PaginatedRecipes(
        items=[recipe_to_summary(recipe) for recipe in recipes],
        total=total,
        page=page,
        page_size=page_size,
    )
    return {"data": payload, "message": "success"}


@router.get("/recipes/{recipe_id}", response_model=dict)
def admin_recipe_detail(
    recipe_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    recipe = get_recipe(db, recipe_id, published_only=False)
    return {"data": recipe_to_detail(recipe), "message": "success"}


@router.post("/recipes", response_model=dict, status_code=201)
def create_recipe(
    payload: RecipeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    recipe = Recipe(
        name=payload.name,
        description=payload.description,
        cover_image=payload.cover_image,
        meal_type=payload.meal_type,
        category_id=payload.category_id,
        difficulty=payload.difficulty,
        cooking_time=payload.cooking_time,
        servings=payload.servings,
        status=payload.status,
        tips=payload.tips,
        nutrition=json.dumps(payload.nutrition, ensure_ascii=False) if payload.nutrition is not None else None,
    )
    db.add(recipe)
    db.flush()
    replace_recipe_children(db, recipe, payload)
    db.commit()
    recipe = get_recipe(db, recipe.id, published_only=False)
    return {"data": recipe_to_detail(recipe), "message": "创建成功"}


@router.put("/recipes/{recipe_id}", response_model=dict)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    recipe = get_recipe(db, recipe_id, published_only=False)
    for field in (
        "name",
        "description",
        "cover_image",
        "meal_type",
        "category_id",
        "difficulty",
        "cooking_time",
        "servings",
        "status",
        "tips",
        "nutrition",
    ):
        value = getattr(payload, field)
        setattr(recipe, field, json.dumps(value, ensure_ascii=False) if field == "nutrition" and value is not None else value)
    replace_recipe_children(db, recipe, payload)
    db.commit()
    recipe = get_recipe(db, recipe.id, published_only=False)
    return {"data": recipe_to_detail(recipe), "message": "更新成功"}


@router.delete("/recipes/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    db.delete(recipe)
    db.commit()
    return {"message": "删除成功"}


@router.post("/recipes/{recipe_id}/publish")
def publish_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    recipe.status = "published"
    db.commit()
    return {"message": "发布成功"}


@router.post("/recipes/{recipe_id}/archive")
def archive_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    recipe.status = "archived"
    db.commit()
    return {"message": "下架成功"}
