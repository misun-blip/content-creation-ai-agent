from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.material import Material as MaterialModel
from app.models.tag import Tag, material_tags
from app.utils.response import success

router = APIRouter(prefix="/materials", tags=["素材库"])

# ====== Pydantic Schema ======
class MaterialCreate(BaseModel):
    title: str
    description: str
    category: str
    preview: str
    type: Optional[str] = "template"  # template / image / video
    file_path: Optional[str] = None

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    preview: Optional[str] = None
    type: Optional[str] = None
    file_path: Optional[str] = None

class MaterialTagsUpdate(BaseModel):
    tag_ids: List[int]

class Material(BaseModel):
    id: int
    title: str
    description: str
    category: str
    preview: str
    uploadDate: str
    type: str = "template"
    file_path: Optional[str] = None
    tags: List[str] = []

    class Config:
        from_attributes = True

# ====== Schema 转换 ======
def to_schema(m: MaterialModel) -> Material:
    tag_names = [t.name for t in (m.tags if hasattr(m, "tags") and m.tags else [])]

    # 兼容旧字段名：如果还存在 content/created_at，则做一次兜底映射
    description_val = getattr(m, "description", None)
    if description_val is None and hasattr(m, "content"):
        description_val = getattr(m, "content") or ""

    category_val = getattr(m, "category", None) or "default"
    preview_val = getattr(m, "preview", None) or ""
    file_path_val = getattr(m, "file_path", None)

    upload_date_val = getattr(m, "upload_date", None)
    if upload_date_val is None and hasattr(m, "created_at"):
        created_at_val = getattr(m, "created_at")
        if created_at_val is not None:
            try:
                upload_date_val = created_at_val.date()
            except Exception:
                upload_date_val = date.today()
    if upload_date_val is None:
        upload_date_val = date.today()

    return Material(
        id=m.id,
        title=m.title,
        description=description_val or "",
        category=category_val,
        preview=preview_val,
        uploadDate=str(upload_date_val),
        type=getattr(m, "type", "template") or "template",
        file_path=file_path_val,
        tags=tag_names,
    )

@router.get("/categories")
def list_categories(db: Session = Depends(deps.get_db)):
    """获取素材分类列表（当前系统内出现过的分类）"""
    from sqlalchemy import distinct
    stmt = select(distinct(MaterialModel.category)).where(
        MaterialModel.category != "",
    ).order_by(MaterialModel.category)
    rows = db.execute(stmt).scalars().all()
    # scalars() 返回的已是 category 字符串，不需要再取 r[0]
    return success(data=[r for r in rows])


@router.get("")
def list_materials(
    q: str = Query("", description="关键字搜索（标题/描述）"),
    category: str = Query("", description="分类筛选"),
    tag: str = Query("", description="按标签名称筛选"),
    db: Session = Depends(deps.get_db),
):
    # 使用 ORM 查询，兼容 description/category/preview/upload_date 等新字段
    stmt = select(MaterialModel).options(joinedload(MaterialModel.tags))

    q_stripped = q.strip()
    if q_stripped:
        # 关键字在 description 中模糊匹配
        stmt = stmt.where(MaterialModel.description.ilike(f"%{q_stripped}%"))

    category_stripped = category.strip()
    if category_stripped:
        stmt = stmt.where(MaterialModel.category == category_stripped)

    tag_stripped = tag.strip()
    if tag_stripped:
        stmt = (
            stmt.join(material_tags, material_tags.c.material_id == MaterialModel.id)
            .join(Tag, Tag.id == material_tags.c.tag_id)
            .where(Tag.name == tag_stripped)
        )

    stmt = stmt.order_by(MaterialModel.id.desc())
    # joinedload(MaterialModel.tags) 会导致结果行重复，需要 unique() 去重
    rows = db.execute(stmt).unique().scalars().all()

    materials = [to_schema(m).model_dump() for m in rows]
    return success(data=materials)

@router.post("")
def create_material(payload: MaterialCreate, db: Session = Depends(deps.get_db)):
    mat_type = (payload.type or "template").strip() or "template"
    if mat_type not in ("template", "image", "video"):
        mat_type = "template"
    item = MaterialModel(
        title=payload.title,
        description=payload.description,
        category=payload.category or "default",
        preview=payload.preview or "",
        upload_date=date.today(),
        type=mat_type,
        file_path=payload.file_path,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data=to_schema(item).model_dump())

@router.put("/{material_id}")
def update_material(material_id: int, payload: MaterialUpdate, db: Session = Depends(deps.get_db)):
    item = db.get(MaterialModel, material_id)
    if not item:
        raise HTTPException(status_code=404, detail="Material not found")

    patch = payload.model_dump(exclude_none=True)
    for k, v in patch.items():
        setattr(item, k, v)

    db.commit()
    db.refresh(item)
    return success(data=to_schema(item).model_dump())

@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(deps.get_db)):
    item = db.get(MaterialModel, material_id)
    if not item:
        return success(data={"deleted": 0}, message="记录不存在")

    db.delete(item)
    db.commit()
    return success(data={"deleted": 1}, message="删除成功")


@router.put("/{material_id}/tags")
def set_material_tags(
    material_id: int,
    payload: MaterialTagsUpdate,
    db: Session = Depends(deps.get_db),
):
    """为素材设置标签（覆盖原有标签）"""
    item = db.get(MaterialModel, material_id)
    if not item:
        raise HTTPException(status_code=404, detail="素材不存在")

    db.execute(delete(material_tags).where(material_tags.c.material_id == material_id))

    for tag_id in payload.tag_ids:
        tag = db.get(Tag, tag_id)
        if tag:
            db.execute(
                material_tags.insert().values(material_id=material_id, tag_id=tag_id)
            )

    db.commit()

    # 更新涉及标签的 usage_count
    affected_tag_ids = list(payload.tag_ids)
    for tid in affected_tag_ids:
        tag = db.get(Tag, tid)
        if tag:
            cnt = db.execute(
                select(func.count()).select_from(material_tags).where(material_tags.c.tag_id == tid)
            ).scalar()
            tag.usage_count = cnt or 0
    db.commit()
    return success(message="标签已更新")