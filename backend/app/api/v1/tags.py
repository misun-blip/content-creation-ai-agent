"""
标签管理 API：列表、创建、素材绑定标签
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.api import deps
from app.models.tag import Tag, material_tags
from app.utils.response import success

router = APIRouter(prefix="/tags", tags=["标签"])


class TagCreate(BaseModel):
    name: str


class TagOut(BaseModel):
    id: int
    name: str
    usage_count: int

    class Config:
        from_attributes = True


class MaterialTagsUpdate(BaseModel):
    tag_ids: List[int]


@router.get("")
def list_tags(
    q: str = Query("", description="按名称搜索"),
    db: Session = Depends(deps.get_db),
):
    """获取标签列表，支持按名称搜索"""
    stmt = select(Tag).order_by(Tag.usage_count.desc(), Tag.id.asc())
    if q.strip():
        stmt = stmt.where(Tag.name.contains(q.strip()))
    tags = db.execute(stmt).scalars().all()
    data = [{"id": t.id, "name": t.name, "usage_count": t.usage_count} for t in tags]
    return success(data=data)


@router.post("")
def create_tag(payload: TagCreate, db: Session = Depends(deps.get_db)):
    """创建标签（名称唯一）"""
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="标签名称不能为空")
    existing = db.execute(select(Tag).where(Tag.name == name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="该标签已存在")
    tag = Tag(name=name, usage_count=0)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return success(data={"id": tag.id, "name": tag.name, "usage_count": tag.usage_count})


@router.get("/{tag_id}")
def get_tag(tag_id: int, db: Session = Depends(deps.get_db)):
    """获取单个标签"""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return success(data={"id": tag.id, "name": tag.name, "usage_count": tag.usage_count})


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(deps.get_db)):
    """删除标签（会解除与素材的关联）"""
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(tag)
    db.commit()
    return success(message="删除成功")
