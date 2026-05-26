import os
import uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.utils.response import success

router = APIRouter(prefix="", tags=["上传"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "video": {".mp4", ".mov", ".avi", ".webm"},
    "document": {".pdf", ".doc", ".docx", ".txt", ".md"},
}

SUBDIRS = {
    "image": "images",
    "video": "videos",
    "document": "documents",
}


def _detect_file_type(ext: str) -> Optional[str]:
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None


def _ensure_upload_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for subdir in SUBDIRS.values():
        os.makedirs(os.path.join(UPLOAD_DIR, subdir), exist_ok=True)


_ensure_upload_dirs()


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """上传图片/视频/文档（multipart/form-data，单文件最大 10MB）"""
    original_name = file.filename or ""
    ext = os.path.splitext(original_name)[1].lower()
    file_type = _detect_file_type(ext)
    if not file_type:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，仅允许图片、视频或文档",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件不能为空")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    subdir = SUBDIRS[file_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    relative_path = f"{subdir}/{filename}"
    save_path = os.path.join(UPLOAD_DIR, relative_path)

    with open(save_path, "wb") as f:
        f.write(content)

    return success(
        data={
            "url": f"/uploads/{relative_path}",
            "filename": original_name,
            "size": len(content),
            "content_type": file.content_type or "application/octet-stream",
            "file_type": file_type,
        }
    )
