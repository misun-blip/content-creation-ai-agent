"""
仪表盘聚合 API：统计、趋势、平台分布、最近活动、热门标签
"""
import re
from collections import Counter
from datetime import date, datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.record import Record, Version
from app.models.material import Material
from app.models.tag import Tag
from app.utils.response import success
from app.core.redis_client import get_cache, set_cache

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


def _extract_keywords(text: str) -> list:
    if not text:
        return []
    pattern = re.compile(r"[\u4e00-\u9fa5a-zA-Z0-9]+")
    words = pattern.findall(text)
    return [w for w in words if len(w) >= 2]


@router.get("/stats")
async def get_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """总素材数、创作数、AI 生成次数（版本数）、平台适配数（创作数）"""
    # 尝试从缓存获取
    cache_key = f"dashboard:stats:{current_user.id}"
    cached = await get_cache(cache_key)
    if cached:
        return success(data=cached, message="成功")

    materials_count = db.query(func.count(Material.id)).scalar() or 0
    records_count = db.query(Record).filter(Record.user_id == current_user.id).count()
    versions_count = (
        db.query(func.count(Version.id))
        .join(Record, Version.record_id == Record.id)
        .filter(Record.user_id == current_user.id)
        .scalar()
        or 0
    )
    data = {
        "totalMaterials": materials_count,
        "totalCreations": records_count,
        "aiGenerations": versions_count,
        "platformAdapts": records_count,
    }
    await set_cache(cache_key, data, ttl=300)  # 缓存 5 分钟
    return success(data=data, message="成功")


@router.get("/trend")
async def get_trend(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """按月的创作趋势（最近 N 个月）"""
    end = date.today()
    start = end - timedelta(days=months * 31)
    records = (
        db.query(Record)
        .filter(
            Record.user_id == current_user.id,
            Record.created_at >= datetime.combine(start, datetime.min.time()),
            Record.created_at <= datetime.combine(end, datetime.max.time()),
        )
        .all()
    )
    month_map: dict = {}
    for r in records:
        dt = r.created_at
        if dt:
            key = dt.strftime("%Y-%m") if hasattr(dt, "strftime") else f"{dt.year}-{dt.month:02d}"
            month_map[key] = month_map.get(key, 0) + 1
    x_axis = []
    data = []
    for i in range(months):
        d = end - timedelta(days=30 * (months - 1 - i))
        key = d.strftime("%Y-%m")
        x_axis.append(f"{d.month}月")
        data.append(month_map.get(key, 0))
    return success(data={"xAxis": x_axis, "data": data}, message="成功")


@router.get("/platform")
async def get_platform(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """各平台创作数量分布"""
    rows = (
        db.query(Record.platform, func.count(Record.id))
        .filter(Record.user_id == current_user.id)
        .group_by(Record.platform)
        .all()
    )
    name_map = {"douyin": "抖音", "xiaohongshu": "小红书", "wechat": "微信", "bilibili": "B站"}
    result = [{"name": name_map.get(r.platform, r.platform), "value": r[1]} for r in rows]
    return success(data=result, message="成功")


@router.get("/type")
async def get_type(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """创作类型分布（按平台作为类型）"""
    rows = (
        db.query(Record.platform, func.count(Record.id))
        .filter(Record.user_id == current_user.id)
        .group_by(Record.platform)
        .all()
    )
    name_map = {"douyin": "抖音", "xiaohongshu": "小红书", "wechat": "微信", "bilibili": "B站"}
    x_axis = [name_map.get(r.platform, r.platform) for r in rows]
    data = [r[1] for r in rows]
    return success(data={"xAxis": x_axis, "data": data}, message="成功")


@router.get("/activities")
async def get_activities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """最近创作记录（活动流）"""
    records = (
        db.query(Record)
        .filter(Record.user_id == current_user.id)
        .order_by(Record.created_at.desc())
        .limit(limit)
        .all()
    )
    from zoneinfo import ZoneInfo
    tz_cn = ZoneInfo("Asia/Shanghai")

    def time_ago(dt: datetime) -> str:
        if not dt:
            return ""
        if dt.tzinfo is None:
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(tz_cn) - dt.astimezone(tz_cn)
        if delta.days > 0:
            return f"{delta.days}天前"
        sec = delta.seconds
        if sec >= 3600:
            return f"{sec // 3600}小时前"
        if sec >= 60:
            return f"{sec // 60}分钟前"
        return "刚刚"

    result = [
        {
            "title": f"创作：{r.title}",
            "time": time_ago(r.created_at),
            "icon": "EditPen",
            "color": "#67C23A",
        }
        for r in records
    ]
    return success(data=result, message="成功")


@router.get("/tags")
async def get_tags(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """热门标签（来自标签表按 usage_count，或从创作内容提取关键词）"""
    # 尝试从缓存获取
    cache_key = f"dashboard:tags:{current_user.id}:{limit}"
    cached = await get_cache(cache_key)
    if cached:
        return success(data=cached, message="成功")

    tags = (
        db.query(Tag)
        .order_by(Tag.usage_count.desc())
        .limit(limit)
        .all()
    )
    if tags:
        types_ = ["", "success", "warning", "danger", "info"]
        result = [
            {"name": t.name, "type": types_[i % len(types_)]}
            for i, t in enumerate(tags)
        ]
        await set_cache(cache_key, result, ttl=300)
        return success(data=result, message="成功")

    # 无标签时从最近记录中提取关键词
    records = (
        db.query(Record)
        .filter(Record.user_id == current_user.id)
        .order_by(Record.created_at.desc())
        .limit(50)
        .all()
    )
    all_kw = []
    for r in records:
        all_kw.extend(_extract_keywords(r.title))
        all_kw.extend(_extract_keywords(r.content or ""))
    top = Counter(all_kw).most_common(limit)
    types_ = ["", "success", "warning", "danger", "info"]
    result = [{"name": k, "type": types_[i % len(types_)]} for i, (k, _) in enumerate(top)]
    return success(data=result, message="成功")
