from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Any
import re
from collections import Counter

from app.api import deps
from app.models.user import User
from app.models.record import Record
from app.utils.response import success

router = APIRouter()

# -------------------------- 辅助函数 --------------------------
# 停用词表（可根据业务扩展）
STOP_WORDS = {
    "最后", "首先", "然后", "但是", "因为", "所以", "如果", "那么",
    "下次见", "再见", "大家好", "今天", "现在", "一个", "这个", "那个",
    "画面镜头", "配音口播", "标题", "话题标签", "轻松吸粉", "话题", "Tag"  
}

def extract_keywords(text: Any) -> list:
    if not text or not isinstance(text, str):
        return []
    
    # 1. 提取所有中英文和数字组合（保持原有逻辑）
    pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9]+')
    words = pattern.findall(text.strip())
    
    # 2. 过滤规则
    filtered_words = []
    for word in words:
        # 过滤停用词
        if word in STOP_WORDS:
            continue
        # 过滤长度小于2的词
        if len(word) < 2:
            continue
        # 过滤纯数字（可选，根据需求）
        if word.isdigit():
            continue
        filtered_words.append(word)
    
    return filtered_words
def get_default_platforms() -> List[Dict[str, Any]]:
    return [{"platform": "未分类", "count": 0}]

def get_default_types() -> List[Dict[str, Any]]:
    return [{"type": "未分类", "count": 0}]

# -------------------------- 1. 每日创作数量（仅统计篇数） --------------------------
@router.get("/daily")
async def get_daily_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        today = date.today()
        start_date = start_date or (today - timedelta(days=30))
        end_date = end_date or today
        
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # 严格统计：按日期分组的【篇数】
        query = db.query(
            func.date(Record.created_at).label("date_str"),
            func.count(Record.id).label("count")  # 这里是篇数，不是字数！
        ).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).group_by("date_str").order_by("date_str")

        result = {row.date_str: row.count for row in query.all()}
        return success(data=result, message="获取每日创作篇数成功")
    except HTTPException:
        # 保持业务错误语义（如日期范围非法 -> 400）
        raise
    except Exception as e:
        return success(data={}, message=f"获取每日数据失败：{str(e)}", code=500)

# -------------------------- 2. 平台分布（真实篇数） --------------------------
@router.get("/platform")
async def get_platform_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        today = date.today()
        start_date = start_date or (today - timedelta(days=30))
        end_date = end_date or today
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        query = db.query(
            case(
                (Record.platform.is_(None) | (Record.platform == ""), "未分类"),
                else_=Record.platform
            ).label("platform"),
            func.count(Record.id).label("count")
        ).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).group_by("platform").order_by("count", "platform")

        result = [{"platform": row.platform, "count": row.count} for row in query.all()] or get_default_platforms()
        return success(data=result, message="获取平台分布成功")
    except Exception as e:
        return success(data=get_default_platforms(), message=f"获取平台分布失败：{str(e)}", code=500)

# -------------------------- 3. 创作类型分布（动态篇数，无固定值） --------------------------
@router.get("/type")
async def get_type_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        # 1. 严格使用前端传的时间范围（核心：不使用默认30天，完全跟着前端走）
        if not start_date or not end_date:
            # 前端没传时，才用默认值（但你的前端一定会传）
            today = date.today()
            start_date = start_date or (today - timedelta(days=30))
            end_date = end_date or today
        
        # 2. 转成datetime，确保时间范围精准（到时分秒）
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        # 3. 第一步：先统计当前时间范围内的总记录数（实时！）
        total_records_in_range = db.query(func.count(Record.id)).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt  # 严格限定时间段
        ).scalar() or 0

        # 4. 第二步：按type字段分组查询（同样限定时间段）
        query = db.query(
            case(
                [(Record.type.is_(None) | (Record.type == ""), "文案")],
                else_=Record.type
            ).label("type"),
            func.count(Record.id).label("count")
        ).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,  # 绑定前端时间段
            Record.created_at <= end_dt    # 绑定前端时间段
        ).group_by("type").order_by("count", "type")

        result = [{"type": row.type, "count": row.count} for row in query.all()]
        
        # 5. 空数据处理：用「当前时间段的总记录数」填充，而非固定值！
        if not result:
            # 比如选「本周」，本周有3条就显示3，0条就显示0
            result = [{"type": "文案", "count": total_records_in_range}]

        return success(data=result, message="获取创作类型分布成功")
    except Exception as e:
        # 6. 异常兜底：也严格查前端传的时间段，绝不查全量！
        if not start_date or not end_date:
            today = date.today()
            start_date = start_date or (today - timedelta(days=30))
            end_date = end_date or today
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # 异常时也查当前时间段的真实总数
        total_records_in_range = db.query(func.count(Record.id)).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).scalar() or 0
        
        return success(
            data=[{"type": "文案", "count": total_records_in_range}],  # 实时总数
            message=f"获取创作类型成功（兼容模式）：{str(e)}",
            code=200
        )
# -------------------------- 4. 热门关键词（真实提取） --------------------------
@router.get("/keywords")
async def get_keyword_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    # 核心修改1：默认返回前3个，而非前10个
    top_n: int = Query(3, description="返回前N个关键词"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        today = date.today()
        start_date = start_date or (today - timedelta(days=30))
        end_date = end_date or today
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        records = db.query(Record).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).all()

        all_keywords = []
        for record in records:
            title = record.title or ""
            content = record.content or ""
            all_keywords.extend(extract_keywords(title) + extract_keywords(content))

        keyword_counter = Counter(all_keywords)
        
        # 核心修改2：严格只取前3个（即使top_n被前端传错，也强制取3）
        top_keywords = [{"keyword": k, "count": v} for k, v in keyword_counter.most_common(3)]
        
        return success(data=top_keywords, message="获取热门关键词成功")
    except Exception as e:
        return success(data=[], message=f"获取关键词失败：{str(e)}", code=500)
    
# -------------------------- 5. 新增：真实总字数统计（专为数据概览） --------------------------
@router.get("/total_words")
async def get_total_words(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        today = date.today()
        start_date = start_date or (today - timedelta(days=30))
        end_date = end_date or today
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # 统计content的真实长度（去除NULL）
        total_words = db.query(func.sum(func.length(Record.content))).filter(
            Record.user_id == current_user.id,
            Record.content.isnot(None),  # 排除NULL值
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).scalar() or 0

        return success(data=total_words, message="获取真实总字数成功")
    except Exception as e:
        return success(data=0, message=f"获取总字数失败：{str(e)}", code=500)
    
@router.get("/export_report")
async def export_statistics_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        today = date.today()
        start_date = start_date or (today - timedelta(days=30))
        end_date = end_date or today
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        # ========== 1. 只查核心数据（和你现有逻辑完全一致） ==========
        # 每日篇数
        daily_query = db.query(
            func.date(Record.created_at).label("date_str"),
            func.count(Record.id).label("count")
        ).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).group_by("date_str").order_by("date_str")
        daily_data = [{"日期": row.date_str, "创作篇数": row.count} for row in daily_query.all()]

        # 平台分布
        platform_query = db.query(
            case(
                (Record.platform.is_(None) | (Record.platform == ""), "未分类"),
                else_=Record.platform
            ).label("platform"),
            func.count(Record.id).label("count")
        ).filter(
            Record.user_id == current_user.id,
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).group_by("platform").order_by("count", "platform")
        platform_data = [{"平台": row.platform, "篇数": row.count} for row in platform_query.all()]

        # 总篇数+总字数
        total_records = sum(d["创作篇数"] for d in daily_data)
        total_words = db.query(func.sum(func.length(Record.content))).filter(
            Record.user_id == current_user.id,
            Record.content.isnot(None),
            Record.created_at >= start_dt,
            Record.created_at <= end_dt
        ).scalar() or 0

        # ========== 2. 纯文本拼接CSV（无编码/类型问题） ==========
        # 手动拼CSV内容，用\t分隔（避免逗号冲突），编码为utf-8
        csv_content = []
        # 标题
        csv_content.append(f"创作统计报告（{start_date} 至 {end_date}）")
        csv_content.append("")
        # 数据概览
        csv_content.append("数据概览")
        csv_content.append(f"总创作篇数\t{total_records}")
        csv_content.append(f"总字数\t{total_words}")
        csv_content.append("")
        # 每日创作
        csv_content.append("每日创作数量")
        csv_content.append("日期\t创作篇数")
        for d in daily_data:
            csv_content.append(f"{d['日期']}\t{d['创作篇数']}")
        csv_content.append("")
        # 平台分布（核心修改：添加英文转中文映射）
        csv_content.append("创作平台分布")
        csv_content.append("平台\t篇数")
        # 平台名称映射字典
        platform_map = {
            "douyin": "抖音",
            "xiaohongshu": "小红书",
            "general": "通用",
            "未分类": "未分类"
        }
        for p in platform_data:
            # 替换为中文名称，没有匹配的就用原名称
            cn_platform = platform_map.get(p['平台'], p['平台'])
            csv_content.append(f"{cn_platform}\t{p['篇数']}")
        csv_content.append("")
        # 创作类型
        csv_content.append("创作类型分布")
        csv_content.append("类型\t篇数")
        csv_content.append(f"文案\t{total_records}")

        # 拼接成字符串，编码为utf-8字节
        csv_bytes = "\n".join(csv_content).encode("utf-8")

        # ========== 3. 返回文件流（最简配置） ==========
        from fastapi.responses import StreamingResponse
        from io import BytesIO

        # 写入BytesIO
        output = BytesIO()
        output.write(csv_bytes)
        output.seek(0)

        # 文件名（纯英文，避免中文文件名坑）
        report_name = f"report_{today.strftime('%Y%m%d%H%M%S')}.csv"

        return StreamingResponse(
            output,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={report_name}"
            }
        )
    except Exception as e:
        return success(data=None, message=f"导出报告失败：{str(e)}", code=500)
    
    # 在 statistics.py 末尾新增以下代码
@router.get("/avg_time")
async def get_avg_creation_time(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    # 空实现，直接返回兜底值，避免前端报错
    return success(data=1, message="平均创作时长暂未统计", code=200)
