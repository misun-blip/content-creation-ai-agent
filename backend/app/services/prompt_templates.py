"""
Few-Shot 提示词模板库
按平台和场景组织 prompt，支持 few-shot 示例提升生成质量
"""

from typing import List, Dict


# ==================== 系统角色定义 ====================

SYSTEM_PROMPTS = {
    "topic_expert": "你是一位资深的自媒体爆款运营专家，擅长发现热点话题、分析用户兴趣，能够精准把握不同平台的内容调性和流量规律。",
    "content_writer": "你是一位顶级的爆款文案写手，擅长根据不同平台特点创作高质量内容。你的文案具有强吸引力、高互动性，深谙各平台推荐算法的偏好。",
}


# ==================== 平台风格定义 ====================

PLATFORM_STYLES = {
    "抖音": {
        "name": "抖音",
        "content_format": "短视频脚本",
        "requirements": [
            "必须包含【画面镜头】和【配音口播】两个部分",
            "开头3秒必须有强钩子（反问/悬念/共鸣）",
            "节奏紧凑，避免冗长铺垫",
            "口播风格口语化、有感染力",
            "结尾引导互动（点赞、评论、关注）",
        ],
    },
    "小红书": {
        "name": "小红书",
        "content_format": "图文笔记",
        "requirements": [
            "标题包含 emoji 和关键词，不超过20字",
            "正文多用 emoji 分隔段落，增强可读性",
            "提供3-5个相关话题 Tag",
            "语气亲和、种草感强，像闺蜜分享",
            "结尾用提问引导评论区互动",
        ],
    },
    "微信视频号": {
        "name": "微信视频号",
        "content_format": "视频脚本",
        "requirements": [
            "包含【画面描述】和【旁白/字幕】",
            "内容偏知识分享或生活感悟风格",
            "语气稳重、有深度，适合30+用户群",
            "时长控制在1-3分钟",
            "结尾引导转发朋友圈",
        ],
    },
    "通用": {
        "name": "通用平台",
        "content_format": "文章",
        "requirements": [
            "排版清晰，段落分明",
            "有明确的标题、正文、总结结构",
            "语言精炼，有逻辑性",
        ],
    },
}


# ==================== Few-Shot 示例 ====================

TOPIC_FEW_SHOTS = [
    {
        "role": "user",
        "content": "关键词：护肤，行业：美妆，平台：小红书，数量：3",
    },
    {
        "role": "assistant",
        "content": '{"topics": [{"title": "换季烂脸急救指南｜3步修复敏感肌", "description": "针对换季敏感肌问题，从清洁、修复、防护三步出发，推荐平价好用的产品组合"}, {"title": "早C晚A到底怎么用？新手避坑全攻略", "description": "科普早C晚A的正确使用方法，包含浓度选择、建立耐受时间表、常见错误示范"}, {"title": "黄皮女生的显白神器｜这5支口红闭眼入", "description": "精选5支适合黄皮肤色的口红色号，附上手臂试色和上嘴对比图"}]}',
    },
]

CONTENT_FEW_SHOTS = {
    "抖音": [
        {
            "role": "user",
            "content": "主题：春季护肤，字数：300字，风格：轻松活泼",
        },
        {
            "role": "assistant",
            "content": """【画面1】镜头对准梳妆台，手拿一瓶精华，做出惊讶表情
【口播】姐妹们！春天到了你的脸是不是又开始闹脾气了？

【画面2】快速切换：脸部特写→干燥起皮→泛红
【口播】换季烂脸，干燥、泛红、爆痘，一个都没少！

【画面3】手持产品，逐个展示
【口播】但是！我用了这三步急救法，一周就好了！
第一步：换温和氨基酸洗面奶，别再用皂基了
第二步：厚涂修复面霜，我用的这款含神经酰胺
第三步：出门必涂防晒，紫外线是敏感肌最大的敌人

【画面4】前后对比照
【口播】你看！一周效果肉眼可见！觉得有用的姐妹点个赞，我下期分享油皮急救方案！""",
        },
    ],
    "小红书": [
        {
            "role": "user",
            "content": "主题：春季护肤，字数：400字，风格：种草",
        },
        {
            "role": "assistant",
            "content": """🌸 换季烂脸别慌！这套急救方案真的有用

姐妹们春天是不是又开始过敏了😭
去年这个时候我也是，脸又干又红还脱皮
后来摸索出一套修复方案，亲测一周见效！

✅ 第一步：精简护肤
把你那些乱七八糟的精华全停掉
只留：温和洁面 + 修复面霜 + 防晒
少即是多，皮肤屏障受损的时候别折腾！

✅ 第二步：重点修复
推荐含这些成分的面霜👇
🔹 神经酰胺 — 修复皮肤屏障
🔹 角鲨烷 — 锁水保湿
🔹 积雪草 — 舒缓镇定

✅ 第三步：严格防晒
紫外线是敏感肌的头号杀手！
选物理防晒霜，温和不刺激

💡 一周后你会发现：
泛红消退了、不脱皮了、皮肤摸起来滑滑的

有同款烂脸经历的姐妹评论区举手🙋‍♀️

#换季护肤 #敏感肌修复 #护肤干货 #平价护肤 #烂脸急救""",
        },
    ],
}


# ==================== 构建消息的工具函数 ====================


def get_platform_style(platform: str) -> dict:
    """获取平台风格配置，未知平台回退到通用"""
    return PLATFORM_STYLES.get(platform, PLATFORM_STYLES["通用"])


def build_topic_messages(
    keywords: str,
    industry: str,
    platform: str,
    count: int,
    context_str: str = "",
) -> List[Dict[str, str]]:
    """
    构建选题推荐的完整 messages 列表（含 few-shot）
    """
    style = get_platform_style(platform)

    system_msg = (
        f"{SYSTEM_PROMPTS['topic_expert']}\n"
        f"目标平台：{style['name']}，内容形式：{style['content_format']}。"
    )

    user_prompt = f"""请根据以下要求生成 {count} 个选题：
- 核心关键词：{keywords}
- 所属行业：{industry}
- 目标平台：{platform}
"""
    if context_str:
        user_prompt += f"\n【参考内部素材库】：\n{context_str}\n"

    user_prompt += """
请严格按照以下 JSON 格式返回，不要包含 Markdown 标记或其他说明：
{"topics": [{"title": "选题标题", "description": "选题描述"}, ...]}"""

    messages = [{"role": "system", "content": system_msg}]
    messages.extend(TOPIC_FEW_SHOTS)
    messages.append({"role": "user", "content": user_prompt})

    return messages


def build_content_messages(
    topic: str,
    length: int,
    style: str,
    platform: str,
) -> List[Dict[str, str]]:
    """
    构建文案生成的完整 messages 列表（含 few-shot）
    """
    plat = get_platform_style(platform)

    system_msg = (
        f"{SYSTEM_PROMPTS['content_writer']}\n"
        f"目标平台：{plat['name']}，内容形式：{plat['content_format']}。\n"
        f"平台要求：\n" + "\n".join(f"- {r}" for r in plat["requirements"])
    )

    user_prompt = f"""请生成一篇文案：
- 核心主题：{topic}
- 目标字数：约 {length} 字
- 语言风格：{style}
- 适配平台：{platform}

直接输出文案正文，不需要多余的问候语或解释说明。"""

    messages = [{"role": "system", "content": system_msg}]

    # 添加平台对应的 few-shot（如果有）
    if platform in CONTENT_FEW_SHOTS:
        messages.extend(CONTENT_FEW_SHOTS[platform])

    messages.append({"role": "user", "content": user_prompt})

    return messages
