import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import AsyncOpenAI

# 从你的项目中导入依赖
from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.models.material import Material as MaterialModel

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
        # 1. 检索内部素材库（基于核心关键词简单匹配）
        search_kw = req.keywords.split(',')[0].strip()
        # 从数据库中检索包含关键词的标题或描述，限制前 3 条作为上下文参考
        materials = db.query(MaterialModel).filter(
            MaterialModel.title.contains(search_kw) | 
            MaterialModel.description.contains(search_kw)
        ).limit(3).all()
        
        # 组装素材文本
        context_str = "\n".join([f"标题: {m.title}, 内容: {m.description}" for m in materials])
        if not context_str:
            context_str = "暂无直接相关的内部素材，请结合行业通用知识生成。"

        # 2. 构造 Prompt，严格要求返回 JSON 格式
        prompt = f"""
        你是一个资深的自媒体爆款运营专家。请根据以下要求生成 {req.count} 个选题：
        - 核心关键词：{req.keywords}
        - 所属行业：{req.industry}
        - 目标平台：{req.platform}
        
        【参考我们内部的优质素材库】：
        {context_str}
        
        请结合参考素材，发挥创意，返回一个 JSON 格式的数据。
        必须严格按照以下格式返回，不要包含其他任何 Markdown 标记、代码块标记 (如 ```json) 或说明：
        {{
            "topics": [
                {{"title": "选题1标题", "description": "选题1描述"}},
                {{"title": "选题2标题", "description": "选题2描述"}}
            ]
        }}
        """

        # 3. 调用 ChatAnywhere 接口
        response = await AI_CLIENT.chat.completions.create(
            model=CHAT_MODEL,  # 这里改用上面定义的模型名称
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # 4. 解析 JSON 结果
        result_text = response.choices[0].message.content.strip()
        
        # 清理可能被大模型误加的 Markdown 代码块标记
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()

        result_json = json.loads(result_text)
        topics_list = result_json.get("topics", [])

        # 补充前端需要的平台字段
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
        # 1. 构造 Prompt，针对不同平台做差异化提示
        prompt = f"""
        你是一位顶级的爆款文案写手。请为自媒体生成一篇脚本文案。
        - 核心主题：{req.topic}
        - 目标字数：约 {req.length} 字
        - 语言风格：{req.style}
        - 适配平台：{req.platform}
        
        要求：
        1. 排版清晰，段落分明。
        2. 如果适配平台是短视频（如抖音、视频号），请包含【画面镜头】和【配音口播】的提示，方便直接作为脚本拍摄。
        3. 如果适配平台是图文（如小红书），请合理使用 Emoji 表情符号，并提供合适的标题和话题 Tag。
        4. 直接输出文案正文，不需要多余的问候语或解释说明。
        """

        # 2. 调用模型生成文案
        response = await AI_CLIENT.chat.completions.create(
            model=CHAT_MODEL,  # 这里同样修改
            messages=[{"role": "user", "content": prompt}],
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
    # 构造 Prompt（复用 /content 接口的逻辑）
    prompt = f"""
    你是一位顶级的爆款文案写手。请为自媒体生成一篇脚本文案。
    - 核心主题：{req.topic}
    - 目标字数：约 {req.length} 字
    - 语言风格：{req.style}
    - 适配平台：{req.platform}
    
    要求：
    1. 排版清晰，段落分明。
    2. 如果适配平台是短视频（如抖音、视频号），请包含【画面镜头】和【配音口播】的提示，方便直接作为脚本拍摄。
    3. 如果适配平台是图文（如小红书），请合理使用 Emoji 表情符号，并提供合适的标题和话题 Tag。
    4. 直接输出文案正文，不需要多余的问候语或解释说明。
    """

    async def event_generator():
        try:
            stream = await AI_CLIENT.chat.completions.create(
                model=CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                stream=True,  # 启用流式输出
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    # 按 SSE 协议格式推送每个 token
                    data = json.dumps({"content": delta.content}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            # 发送结束信号
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
            "X-Accel-Buffering": "no",  # 禁止 Nginx 缓冲 SSE
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