from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    data: dict
    message: str = "success"


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    sort_order: int
    is_active: bool


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str | None = None


class IngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    amount: float | None = None
    unit: str | None = Field(default=None, max_length=32)
    note: str | None = Field(default=None, max_length=255)


class IngredientOut(IngredientInput):
    id: int


class IngredientCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str | None = None


class RecipeStepInput(BaseModel):
    step_no: int = Field(ge=1)
    description: str = Field(min_length=1)
    duration_seconds: int | None = Field(default=None, ge=0)
    image: str | None = None


class RecipeStepOut(RecipeStepInput):
    id: int


class RecipeBase(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    cover_image: str | None = None
    meal_type: str = Field(pattern="^(breakfast|lunch|dinner)$")
    category_id: int | None = None
    difficulty: str = Field(default="easy", pattern="^(easy|medium|hard)$")
    cooking_time: int = Field(default=0, ge=0)
    servings: int = Field(default=2, ge=1)
    tips: str | None = None
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    nutrition: dict[str, float] | None = None
    ingredients: list[IngredientInput] = Field(default_factory=list)
    steps: list[RecipeStepInput] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class RecipeSummary(BaseModel):
    id: int
    name: str
    description: str | None = None
    cover_image: str | None = None
    meal_type: str
    difficulty: str
    cooking_time: int
    servings: int
    status: str
    category: CategoryOut | None = None
    created_at: datetime


class RecipeDetail(RecipeSummary):
    tips: str | None = None
    nutrition: dict[str, float] | None = None
    ingredients: list[IngredientOut]
    steps: list[RecipeStepOut]
    tags: list[TagOut]
    related_recipes: list[RecipeSummary] = Field(default_factory=list)


class PaginatedRecipes(BaseModel):
    items: list[RecipeSummary | RecipeDetail]
    total: int
    page: int
    page_size: int


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)


class ProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar: str | None = Field(default=None, max_length=255)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    role: str


class PreferencesUpdate(BaseModel):
    preferred_cuisines: list[str] | None = None
    disliked_ingredients: list[str] | None = None
    allergies: list[str] | None = None
    cooking_level: str | None = None
    appliances: list[str] | None = None
    default_servings: int | None = Field(default=None, ge=1)


class CatalogCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    type: str = Field(default="general", max_length=32)
    sort_order: int = 0


class CatalogUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    type: str = Field(default="general", max_length=32)
    sort_order: int = 0
    is_active: bool = True


class PreferenceOut(BaseModel):
    preferred_cuisines: list[str]
    disliked_ingredients: list[str]
    allergies: list[str]
    cooking_level: str | None = None
    appliances: list[str]
    default_servings: int
