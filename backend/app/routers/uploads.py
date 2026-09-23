from pathlib import Path
from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.dependencies import require_admin
from app.models import User


router = APIRouter(prefix="/api/admin", tags=["uploads"])
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("/uploads")
async def upload_image(
    file: UploadFile = File(...),
    kind: str = "recipe_cover",
    _: User = Depends(require_admin),
) -> dict:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 jpg、png、webp 图片")
    if kind not in {"recipe_cover", "recipe_step"}:
        raise HTTPException(status_code=400, detail="不支持的图片类型")

    folder = settings.upload_path / ("recipes" if kind == "recipe_cover" else "steps")
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    destination = folder / filename
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="上传文件不是有效图片") from None
    destination.write_bytes(content)

    relative_path = f"/uploads/{'recipes' if kind == 'recipe_cover' else 'steps'}/{filename}"
    return {"data": {"path": relative_path, "url": relative_path}, "message": "上传成功"}
