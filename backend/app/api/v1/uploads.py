import os
import uuid
from fastapi import APIRouter, UploadFile, File
from app.core.config import settings
from app.utils.response import success

# 注意：在 app.main 中通过 app.include_router(uploads.router, prefix="/api/v1/uploads")
# 统一挂载，因此这里不再额外添加前缀，保证最终路径为 /api/v1/uploads。
router = APIRouter(prefix="", tags=["上传"])

# 默认上传目录：backend/uploads
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    # 生成安全文件名
    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 返回可访问的 URL（main.py 挂载静态目录 /uploads）
    return success(data={"url": f"/uploads/{filename}", "filename": file.filename})