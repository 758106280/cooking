import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Tag, User


DATA_PATH = Path(__file__).resolve().parents[1] / "seed" / "recipes.json"
MAX_SEED_FILE_SIZE_BYTES = 100 * 1024**3


def seed_defaults(db: Session) -> None:
    admin = db.scalar(select(User).where(User.username == settings.admin_username))
    if not admin:
        db.add(
            User(
                username=settings.admin_username,
                nickname="家庭管理员",
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
        )
    elif not admin.nickname:
        admin.nickname = "家庭管理员"

    categories = [
        ("早餐", "meal"),
        ("午餐", "meal"),
        ("晚餐", "meal"),
        ("家常菜", "cuisine"),
        ("鲁菜", "cuisine"),
        ("川菜", "cuisine"),
        ("粤菜", "cuisine"),
        ("苏菜", "cuisine"),
        ("浙菜", "cuisine"),
        ("闽菜", "cuisine"),
        ("湘菜", "cuisine"),
        ("徽菜", "cuisine"),
        ("西餐", "cuisine"),
        ("烘焙", "cuisine"),
    ]
    for index, (name, category_type) in enumerate(categories):
        if not db.scalar(select(Category).where(Category.name == name)):
            db.add(Category(name=name, type=category_type, sort_order=index))

    tags = [
        ("快手菜", "feature"),
        ("简单", "difficulty"),
        ("下饭菜", "feature"),
        ("家常菜", "feature"),
        ("宴客菜", "feature"),
        ("海鲜", "feature"),
        ("高蛋白", "feature"),
        ("烘焙", "feature"),
        ("甜品", "feature"),
    ]
    for name, tag_type in tags:
        if not db.scalar(select(Tag).where(Tag.name == name)):
            db.add(Tag(name=name, type=tag_type))

    db.commit()
    seed_sample_recipes(db)


def seed_sample_recipes(db: Session) -> None:
    data_size = DATA_PATH.stat().st_size
    if data_size > MAX_SEED_FILE_SIZE_BYTES:
        raise RuntimeError(
            f"初始化菜谱文件超过 100 GiB 限制: {DATA_PATH} ({data_size} bytes)"
        )

    with DATA_PATH.open(encoding="utf-8") as data_file:
        recipes = json.load(data_file)

    for item in recipes:
        if db.scalar(select(Recipe).where(Recipe.name == item["name"])):
            continue

        category = db.scalar(select(Category).where(Category.name == item["cuisine"]))
        recipe_tags = []
        for tag_name in item.get("tags", []):
            tag = db.scalar(select(Tag).where(Tag.name == tag_name))
            if not tag:
                tag = Tag(name=tag_name, type="feature")
                db.add(tag)
                db.flush()
            recipe_tags.append(tag)

        recipe = Recipe(
            name=item["name"],
            description=item.get("description"),
            meal_type=item["meal_type"],
            category_id=category.id if category else None,
            difficulty=item.get("difficulty", "easy"),
            cooking_time=item.get("cooking_time", 0),
            servings=item.get("servings", 2),
            status="published",
            tips=item.get("tips"),
            nutrition=json.dumps(item["nutrition"], ensure_ascii=False)
            if item.get("nutrition") is not None
            else None,
        )
        recipe.tags = recipe_tags
        db.add(recipe)
        db.flush()

        for index, item_ingredient in enumerate(item.get("ingredients", [])):
            ingredient = db.scalar(
                select(Ingredient).where(Ingredient.name == item_ingredient["name"])
            )
            if not ingredient:
                ingredient = Ingredient(name=item_ingredient["name"])
                db.add(ingredient)
                db.flush()
            recipe.ingredient_links.append(
                RecipeIngredient(
                    ingredient=ingredient,
                    amount=item_ingredient.get("amount"),
                    unit=item_ingredient.get("unit"),
                    note=item_ingredient.get("note"),
                    sort_order=index,
                )
            )

        recipe.steps = [
            RecipeStep(
                step_no=index + 1,
                description=item_step["description"],
                duration_seconds=item_step.get("duration_seconds"),
            )
            for index, item_step in enumerate(item.get("steps", []))
        ]

    db.commit()
