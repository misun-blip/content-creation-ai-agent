"""
分类管理 API：列表、创建、查询、更新、删除
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api import deps
from app.models.category import Category
from app.utils.response import success

router = APIRouter(prefix="/categories", tags=["分类"])


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def _to_out(category: Category) -> dict:
    return {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "description": category.description,
        "created_at": category.created_at.isoformat() if category.created_at else None,
    }


@router.get("")
def list_categories(
    q: str = Query("", description="按名称搜索"),
    db: Session = Depends(deps.get_db),
):
    """获取分类列表，支持按名称搜索"""
    stmt = select(Category).order_by(Category.id.asc())
    if q.strip():
        stmt = stmt.where(Category.name.contains(q.strip()))
    categories = db.execute(stmt).scalars().all()
    return success(data=[_to_out(c) for c in categories])


@router.post("")
def create_category(payload: CategoryCreate, db: Session = Depends(deps.get_db)):
    """创建分类（名称唯一）"""
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="分类名称不能为空")

    existing = db.execute(select(Category).where(Category.name == name)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="该分类已存在")

    if payload.parent_id is not None:
        parent = db.get(Category, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")

    category = Category(
        name=name,
        parent_id=payload.parent_id,
        description=(payload.description or "").strip() or None,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return success(data=_to_out(category))


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(deps.get_db)):
    """获取单个分类"""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return success(data=_to_out(category))


@router.put("/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(deps.get_db),
):
    """更新分类"""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="分类名称不能为空")
        existing = db.execute(
            select(Category).where(Category.name == name, Category.id != category_id)
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="该分类名称已存在")
        category.name = name

    if payload.parent_id is not None:
        if payload.parent_id == category_id:
            raise HTTPException(status_code=400, detail="分类不能设置自身为父分类")
        parent = db.get(Category, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父分类不存在")
        category.parent_id = payload.parent_id
    elif "parent_id" in payload.model_fields_set and payload.parent_id is None:
        category.parent_id = None

    if payload.description is not None:
        category.description = payload.description.strip() or None

    db.commit()
    db.refresh(category)
    return success(data=_to_out(category))


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(deps.get_db)):
    """删除分类（存在子分类时拒绝删除）"""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    child = db.execute(
        select(Category).where(Category.parent_id == category_id)
    ).scalars().first()
    if child:
        raise HTTPException(status_code=400, detail="存在子分类，无法删除")

    db.delete(category)
    db.commit()
    return success(message="删除成功")
