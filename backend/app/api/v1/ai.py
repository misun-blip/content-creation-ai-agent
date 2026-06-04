import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.models.material import Material as MaterialModel
from app.services.prompt_templates import build_topic_messages, build_content_messages
from app.services.rag_service import get_rag_service

router = APIRouter(prefix="/ai", tags=["AI 生成"])

# ====== AI 服务配置（从 .env 读取） ======
AI_CLIENT = AsyncOpenAI(
    api_key=settings.AI_API_KEY,
    base_url=settings.AI_API_BASE,
)

# 定义要使用的模型名称
CHAT_MODEL = "gpt-3.5-turbo"

# ====== 定义前端请求的数据模型 ======
class TopicRequest(BaseModel):
    keywords: str
    industry: str
    platform: str
    count: int = 5

class ContentRequest(BaseModel):
    topic: str
    length: int = 500
    style: str = "formal"
    platform: str = "general"

@router.post("/topics")
async def generate_topics(
    req: TopicRequest,
    db: Session = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user) # 联调跑通前，可先注释掉用户认证拦截
):
    """
    结合内部素材库，生成营销选题
    """
    try:
        # 1. 检索内部素材库（优先使用 RAG 语义检索，回退到 SQL 模糊匹配）
        search_kw = req.keywords.split(',')[0].strip()
        rag = get_rag_service()

        if rag.is_available and rag.get_count() > 0:
            # RAG 语义检索
            similar = rag.search_similar(query=search_kw, top_k=5)
            context_str = "\n".join(
                [f"标题: {s.get('title', '')}, 内容: {s['document']}" for s in similar]
            )
        else:
            # 回退到 SQL 模糊匹配
            materials = db.query(MaterialModel).filter(
                MaterialModel.title.contains(search_kw) | 
                MaterialModel.description.contains(search_kw)
            ).limit(3).all()
            context_str = "\n".join([f"标题: {m.title}, 内容: {m.description}" for m in materials])

        if not context_str:
            context_str = "暂无直接相关的内部素材，请结合行业通用知识生成。"

        # 2. 使用 Few-Shot 模板构造 messages
        messages = build_topic_messages(
            keywords=req.keywords,
            industry=req.industry,
            platform=req.platform,
            count=req.count,
            context_str=context_str,
        )

        # 3. 调用 AI 接口
        response = await AI_CLIENT.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.7
        )
        
        # 4. 解析 JSON 结果
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()

        result_json = json.loads(result_text)
        topics_list = result_json.get("topics", [])
        for t in topics_list:
            t["platform"] = req.platform

        return {"code": 200, "message": "生成成功", "data": {"topics": topics_list}}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI 返回的数据格式解析失败，请点击重试")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失败: {str(e)}")


@router.post("/content")
async def generate_content(
    req: ContentRequest,
    # current_user: User = Depends(deps.get_current_active_user)
):
    """
    生成具体脚本文案
    """
    try:
        # 使用 Few-Shot 模板构造 messages
        messages = build_content_messages(
            topic=req.topic, length=req.length,
            style=req.style, platform=req.platform,
        )

        response = await AI_CLIENT.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        return {"code": 200, "message": "生成成功", "data": {"content": content}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文案生成失败: {str(e)}")


@router.post("/content/stream")
async def generate_content_stream(req: ContentRequest):
    """
    SSE 流式文案生成 —— 逐字推送，前端可实时渲染
    协议：Server-Sent Events (text/event-stream)
    数据格式：data: {"content": "..."}\n\n
    结束标志：data: [DONE]\n\n
    """
    # 使用 Few-Shot 模板构造 messages
    messages = build_content_messages(
        topic=req.topic, length=req.length,
        style=req.style, platform=req.platform,
    )

    async def event_generator():
        try:
            stream = await AI_CLIENT.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.8,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    data = json.dumps({"content": delta.content}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class EvaluateRequest(BaseModel):
    content: str
    topic: str
    target_length: int

@router.post("/evaluate")
async def evaluate_content(req: EvaluateRequest):
    """
    内容质量评估 (基于规则引擎)
    """
    try:
        score = 100
        suggestions = []
        
        # 1. 文本长度检查
        actual_length = len(req.content)
        if actual_length < req.target_length * 0.7:
            score -= 15
            suggestions.append(f"字数严重不足 (当前 {actual_length} 字，目标 {req.target_length} 字)，建议丰富细节。")
        elif actual_length > req.target_length * 1.3:
            score -= 5
            suggestions.append(f"字数偏多 (当前 {actual_length} 字，目标 {req.target_length} 字)，建议精简冗余信息。")
            
        # 2. 关键词覆盖度检查
        # 简单将 topic 按空格或逗号分词作为核心关键词库
        keywords = [k.strip() for k in req.topic.replace('，', ',').replace(' ', ',').split(',') if k.strip()]
        if keywords:
            missing_kws = [k for k in keywords if k not in req.content]
            if missing_kws:
                score -= min(20, len(missing_kws) * 5)
                suggestions.append(f"未有效覆盖核心关键词: {', '.join(missing_kws)}，建议自然融入正文中。")
                
        # 3. 敏感词/违禁词检测 (模拟常见的自媒体广告违禁词)
        sensitive_words = ["第一", "最高级", "国家级", "包治百病", "绝对", "100%", "极品", "逢考必过"]
        found_sensitive = [w for w in sensitive_words if w in req.content]
        if found_sensitive:
            score -= 30
            suggestions.append(f"⚠️ 包含疑似营销违禁词: {', '.join(found_sensitive)}，存在被平台限流的风险！")
            
        # 4. 兜底与好评
        score = max(0, score) # 确保分数不为负数
        if score >= 95:
            suggestions.append("🎉 文案质量非常棒，结构完整且合规，可以直接发布！")
            
        return {
            "code": 200, 
            "message": "评估完成", 
            "data": {
                "score": score,
                "suggestions": suggestions
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")


# ====== AI 配图生成（基于 LoremFlickr 免费图库） ======

class ImageRequest(BaseModel):
    topic: str
    count: int = 3
    platform: str = "通用"

@router.post("/image")
async def generate_images(req: ImageRequest):
    """
    AI 智能配图：根据文案主题自动搜索匹配的高清图片
    流程：AI 提取英文关键词 → LoremFlickr 免费 API 获取图片 → 返回图片列表
    """
    import urllib.parse
    import random
    import time
    
    try:
        # 1. 用 AI 将中文主题翻译为英文搜索关键词
        response = await AI_CLIENT.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个翻译助手。用户给你一个中文主题，你返回1-2个最适合在图库搜索的英文关键词，用逗号分隔。只返回关键词，不要其他内容。例如用户输入'秋天咖啡馆'，你返回'autumn,cafe'"},
                {"role": "user", "content": f"主题：{req.topic}"}
            ],
            temperature=0.3,
        )
        keywords = response.choices[0].message.content.strip()

        # 2. 调用 LoremFlickr 免费 API 搜索图片
        images = []
        safe_keywords = urllib.parse.quote(keywords)
        
        # 使用大跨度随机种子 + 时间戳，确保每张图片都不同
        base_seed = int(time.time()) % 100000
        used_locks = set()
        
        for i in range(req.count):
            # 生成不重复的随机 lock 值（跨度至少 1000）
            lock_val = base_seed + i * 1000 + random.randint(0, 999)
            while lock_val in used_locks:
                lock_val += random.randint(1, 500)
            used_locks.add(lock_val)
            
            img_url = f"https://loremflickr.com/800/600/{safe_keywords}?lock={lock_val}"
            images.append({
                "url": img_url,
                "keyword": keywords,
                "description": f"配图 {i+1}: {req.topic}",
            })

        return {
            "code": 200,
            "message": "配图生成成功",
            "data": {
                "keywords": keywords,
                "images": images,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配图生成失败: {str(e)}")