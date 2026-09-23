import json

from app.models import Recipe
from app.schemas import IngredientOut, RecipeDetail, RecipeSummary, RecipeStepOut, TagOut


def recipe_to_summary(recipe: Recipe) -> RecipeSummary:
    return RecipeSummary(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        cover_image=recipe.cover_image,
        meal_type=recipe.meal_type,
        difficulty=recipe.difficulty,
        cooking_time=recipe.cooking_time,
        servings=recipe.servings,
        status=recipe.status,
        category=recipe.category,
        created_at=recipe.created_at,
    )


def recipe_to_detail(recipe: Recipe, related: list[Recipe] | None = None) -> RecipeDetail:
    return RecipeDetail(
        **recipe_to_summary(recipe).model_dump(),
        tips=recipe.tips,
        nutrition=json_dict(recipe.nutrition),
        ingredients=[
            IngredientOut(
                id=link.ingredient.id,
                name=link.ingredient.name,
                amount=link.amount,
                unit=link.unit,
                note=link.note,
            )
            for link in recipe.ingredient_links
        ],
        steps=[
            RecipeStepOut(
                id=step.id,
                step_no=step.step_no,
                description=step.description,
                duration_seconds=step.duration_seconds,
                image=step.image,
            )
            for step in recipe.steps
        ],
        tags=[TagOut.model_validate(tag) for tag in recipe.tags],
        related_recipes=[recipe_to_summary(item) for item in (related or [])],
    )


def json_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def json_dict(value: str | None) -> dict[str, float] | None:
    if not value:
        return None
    try:
        result = json.loads(value)
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError:
        return None
