from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Tag
from app.schemas import CategoryOut, PaginatedRecipes, RecipeDetail, RecipeSummary, TagOut
from app.serializers import recipe_to_detail, recipe_to_summary


router = APIRouter(prefix="/api", tags=["recipes"])


def recipe_load_options():
    return (
        selectinload(Recipe.category),
        selectinload(Recipe.ingredient_links).selectinload(RecipeIngredient.ingredient),
        selectinload(Recipe.steps),
        selectinload(Recipe.tags),
    )


def get_recipe(db: Session, recipe_id: int, published_only: bool = True) -> Recipe:
    statement = select(Recipe).options(*recipe_load_options()).where(Recipe.id == recipe_id)
    if published_only:
        statement = statement.where(Recipe.status == "published")
    recipe = db.scalars(statement).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    return recipe


@router.get("/recipes", response_model=dict)
def list_recipes(
    keyword: str | None = None,
    meal_type: str | None = Query(default=None, pattern="^(breakfast|lunch|dinner)$"),
    difficulty: str | None = Query(default=None, pattern="^(easy|medium|hard)$"),
    max_cooking_time: int | None = Query(default=None, ge=0),
    category_id: int | None = None,
    tag_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    statement = (
        select(Recipe)
        .options(*recipe_load_options())
        .where(Recipe.status == "published")
    )
    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        statement = statement.outerjoin(Recipe.ingredient_links).outerjoin(Ingredient).where(
            or_(Recipe.name.ilike(like_keyword), Recipe.description.ilike(like_keyword), Ingredient.name.ilike(like_keyword))
        ).distinct()
    if meal_type:
        statement = statement.where(Recipe.meal_type == meal_type)
    if difficulty:
        statement = statement.where(Recipe.difficulty == difficulty)
    if max_cooking_time is not None:
        statement = statement.where(Recipe.cooking_time <= max_cooking_time)
    if category_id is not None:
        statement = statement.where(Recipe.category_id == category_id)
    if tag_id is not None:
        statement = statement.join(Recipe.tags).where(Tag.id == tag_id)

    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    recipes = db.scalars(
        statement.order_by(Recipe.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).unique().all()
    payload = PaginatedRecipes(
        items=[recipe_to_summary(recipe) for recipe in recipes],
        total=total,
        page=page,
        page_size=page_size,
    )
    return {"data": payload, "message": "success"}


@router.get("/recipes/{recipe_id}", response_model=dict)
def recipe_detail(recipe_id: int, db: Session = Depends(get_db)) -> dict:
    recipe = get_recipe(db, recipe_id)
    related = db.scalars(
        select(Recipe)
        .options(selectinload(Recipe.category))
        .where(
            Recipe.status == "published",
            Recipe.meal_type == recipe.meal_type,
            Recipe.id != recipe.id,
        )
        .order_by(Recipe.created_at.desc())
        .limit(4)
    ).all()
    return {"data": recipe_to_detail(recipe, related), "message": "success"}


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return db.scalars(
        select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order, Category.id)
    ).all()


@router.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)) -> list[Tag]:
    return db.scalars(select(Tag).order_by(Tag.name)).all()
