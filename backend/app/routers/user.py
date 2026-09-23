import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Favorite, Recipe, User, UserPreference
from app.schemas import PaginatedRecipes, PreferenceOut, PreferencesUpdate
from app.serializers import json_list, recipe_to_summary


router = APIRouter(prefix="/api", tags=["user"])


def preference_payload(preference: UserPreference) -> PreferenceOut:
    return PreferenceOut(
        preferred_cuisines=json_list(preference.preferred_cuisines),
        disliked_ingredients=json_list(preference.disliked_ingredients),
        allergies=json_list(preference.allergies),
        cooking_level=preference.cooking_level,
        appliances=json_list(preference.appliances),
        default_servings=preference.default_servings,
    )


@router.get("/favorites")
def list_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    favorites = db.scalars(
        select(Favorite)
        .where(Favorite.user_id == user.id)
        .options(selectinload(Favorite.recipe).selectinload(Recipe.category))
        .order_by(Favorite.created_at.desc())
    ).all()
    payload = PaginatedRecipes(
        items=[recipe_to_summary(item.recipe) for item in favorites],
        total=len(favorites),
        page=1,
        page_size=max(len(favorites), 1),
    )
    return {"data": payload, "message": "success"}


@router.get("/favorites/{recipe_id}/status")
def favorite_status(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    favorite = db.scalar(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    )
    return {"data": {"is_favorite": favorite is not None}, "message": "success"}


@router.post("/favorites/{recipe_id}")
def add_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id, Recipe.status == "published"))
    if not recipe:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    existing = db.scalar(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    )
    if not existing:
        db.add(Favorite(user_id=user.id, recipe_id=recipe_id))
        db.commit()
    return {"message": "收藏成功"}


@router.delete("/favorites/{recipe_id}")
def remove_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    favorite = db.scalar(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    )
    if favorite:
        db.delete(favorite)
        db.commit()
    return {"message": "已取消收藏"}


@router.get("/preferences")
def get_preferences(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    preference = db.get(UserPreference, user.id)
    if not preference:
        preference = UserPreference(user_id=user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    return {"data": preference_payload(preference), "message": "success"}


@router.patch("/preferences")
def update_preferences(
    payload: PreferencesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    preference = db.get(UserPreference, user.id)
    if not preference:
        preference = UserPreference(user_id=user.id)
        db.add(preference)

    updates = payload.model_dump(exclude_unset=True)
    json_fields = {"preferred_cuisines", "disliked_ingredients", "allergies", "appliances"}
    for key, value in updates.items():
        setattr(preference, key, json.dumps(value, ensure_ascii=False) if key in json_fields else value)
    db.commit()
    db.refresh(preference)
    return {"data": preference_payload(preference), "message": "保存成功"}
