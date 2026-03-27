from typing import Dict, List, Optional
import logging
from ..config.platform_config import platform_config
from .formatters.douyin import DouyinFormatter
from .formatters.xiaohongshu import XiaohongshuFormatter
from .formatters.wechat import WechatFormatter
from ..schemas.adapter import FormatResult

logger = logging.getLogger(__name__)


class AdapterService:
    """平台适配服务"""
    
    def __init__(self):
        """初始化适配服务"""
        self.formatters = {
            'douyin': DouyinFormatter,
            'xiaohongshu': XiaohongshuFormatter,
            'wechat': WechatFormatter
        }
        logger.info(f"适配服务初始化完成，支持的平台: {list(self.formatters.keys())}")
    
    def adapt_content(
        self,
        content: str,
        platform: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        auto_format: bool = True
    ) -> FormatResult:
        """
        适配内容到指定平台
        
        Args:
            content: 原始内容
            platform: 目标平台代码
            title: 标题（可选）
            tags: 标签列表（可选）
            auto_format: 是否自动排版
            
        Returns:
            格式化结果
        """
        logger.info(f"开始适配内容到平台: {platform}")
        logger.debug(f"输入参数 - content长度: {len(content)}, title: {title}, tags: {tags}, auto_format: {auto_format}")
        
        # 获取平台配置
        platform_config_data = platform_config.get_platform_config(platform)
        
        if not platform_config_data:
            logger.error(f"不支持的平台: {platform}")
            raise ValueError(f"不支持的平台: {platform}")
        
        logger.debug(f"获取到平台配置: {platform_config_data.get('name', platform)}")
        
        # 获取格式化器
        formatter_class = self.formatters.get(platform)
        if not formatter_class:
            logger.error(f"未找到平台格式化器: {platform}")
            raise ValueError(f"未找到平台格式化器: {platform}")
        
        formatter = formatter_class(platform_config_data)
        logger.info(f"使用格式化器: {formatter.__class__.__name__}")
        
        # 格式化内容
        warnings = []
        suggestions = []
        
        # 格式化标题
        if title:
            logger.debug(f"格式化标题: {title[:50]}...")
            formatted_title, title_warnings = formatter.format_title(title)
            warnings.extend(title_warnings)
            logger.info(f"标题格式化完成，长度: {len(formatted_title)}")
        else:
            logger.info("未提供标题，将自动生成")
            formatted_title = self._generate_title(content)
            suggestions.append("已自动生成标题")
            logger.debug(f"自动生成的标题: {formatted_title}")
        
        # 格式化正文
        logger.debug(f"格式化正文，原始长度: {len(content)}")
        formatted_content, content_warnings = formatter.format_content(content)
        warnings.extend(content_warnings)
        logger.info(f"正文格式化完成，格式化后长度: {len(formatted_content)}")
        
        # 格式化标签
        if tags:
            logger.debug(f"格式化标签: {tags}")
            formatted_tags, tags_warnings = formatter.format_tags(tags)
            warnings.extend(tags_warnings)
            logger.info(f"标签格式化完成，数量: {len(formatted_tags)}")
        else:
            logger.info("未提供标签，将自动提取")
            formatted_tags = self._extract_tags(content)
            suggestions.append("已自动提取标签")
            logger.debug(f"自动提取的标签: {formatted_tags}")
        
        # 生成预览
        preview = self._generate_preview(
            formatted_title,
            formatted_content,
            formatted_tags,
            platform
        )
        logger.info(f"预览生成完成，长度: {len(preview)}")
        
        # 记录警告和建议
        if warnings:
            logger.warning(f"适配过程中产生 {len(warnings)} 个警告: {warnings}")
        if suggestions:
            logger.info(f"适配过程中产生 {len(suggestions)} 个建议: {suggestions}")
        
        result = FormatResult(
            title=formatted_title,
            content=formatted_content,
            tags=formatted_tags,
            preview=preview,
            warnings=warnings,
            suggestions=suggestions
        )
        
        logger.info(f"内容适配完成，平台: {platform}")
        return result
    
    def _generate_title(self, content: str) -> str:
        """
        从内容生成标题
        
        Args:
            content: 原始内容
            
        Returns:
            生成的标题
        """
        logger.debug("开始生成标题")
        
        if not content:
            logger.warning("内容为空，返回默认标题")
            return "无标题"
            
        # 简单实现:取第一句话的前20个字符
        first_sentence = content.split('。')[0].split('\n')[0].strip()
        if not first_sentence:
            logger.warning("无法从内容中提取有效句子，返回默认标题")
            return "无标题"
            
        generated_title = first_sentence[:20]
        logger.debug(f"生成的标题: {generated_title}")
        return generated_title
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        从内容提取标签
        
        Args:
            content: 原始内容
            
        Returns:
            提取的标签列表
        """
        logger.debug("开始提取标签")
        
        if not content:
            logger.warning("内容为空，返回空标签列表")
            return []
            
        # 简单实现:提取关键词
        # 实际项目中可以使用jieba分词
        keywords = ['热点', '推荐', '分享', '干货', '教程']
        extracted_tags = keywords[:3]
        logger.debug(f"提取的标签: {extracted_tags}")
        return extracted_tags
    
    def _generate_preview(
        self,
        title: str,
        content: str,
        tags: List[str],
        platform: str
    ) -> str:
        """
        生成预览
        
        Args:
            title: 格式化后的标题
            content: 格式化后的内容
            tags: 格式化后的标签列表
            platform: 平台代码
            
        Returns:
            预览文本
        """
        logger.debug(f"开始生成预览，平台: {platform}")
        
        # 确保参数不为None
        title = title or ""
        content = content or ""
        tags = tags or []
        
        tag_str = ' '.join(tags) if tags else ""
        
        # 根据平台调整预览格式
        if platform == "wechat":
            # 微信视频号不显示标签
            preview = f"{title}\n\n{content}"
            logger.debug("生成微信预览（不包含标签）")
        else:
            preview = f"{title}\n\n{content}\n\n{tag_str}"
            logger.debug("生成普通预览（包含标签）")
        
        return preview


# 全局服务实例
adapter_service = AdapterService()
