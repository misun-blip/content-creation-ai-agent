from typing import Dict, List, Tuple
from .base import BaseFormatter


class XiaohongshuFormatter(BaseFormatter):
    """小红书格式化器"""
    
    def __init__(self, config: Dict):
        """
        初始化小红书格式化器
        
        Args:
            config: 平台配置字典
        """
        super().__init__(config)
        # 从配置中获取emoji分隔符列表
        formatting_config = config.get('formatting', {})
        self.paragraph_emojis = formatting_config.get('paragraph_emojis', ['📌', '✨', '💡', '🎯', '🔥', '💪'])
    
    def format_title(self, title: str) -> Tuple[str, List[str]]:
        """
        格式化标题
        
        Args:
            title: 原始标题
            
        Returns:
            (格式化后的标题, 警告列表)
        """
        max_length = self.title_config.get('max_length', 20)
        warnings = []
        
        if not title:
            return "", ["标题为空"]
        
        # 截断标题
        formatted_title = self._truncate_text(title.strip(), max_length)
        
        if len(title) > max_length:
            warnings.append(f"标题超过{max_length}字符,已自动截断")
        
        return formatted_title, warnings
    
    def format_content(self, content: str) -> Tuple[str, List[str]]:
        """
        格式化内容
        
        Args:
            content: 原始内容
            
        Returns:
            (格式化后的内容, 警告列表)
        """
        max_length = self.content_config.get('max_length', 1000)
        paragraph_max = self.content_config.get('paragraph_max_length', 300)
        warnings = []
        
        if not content:
            return "", ["内容为空"]
        
        # 优化标点和空格
        content = self._optimize_punctuation(content)
        content = self._optimize_spaces(content)
        
        # 分段处理
        paragraphs = self._split_paragraphs(content, paragraph_max)
        
        # 添加emoji分隔（从配置中读取）
        formatted_paragraphs = []
        for i, p in enumerate(paragraphs):
            if p.strip():  # 只处理非空段落
                if self.paragraph_emojis:
                    emoji = self.paragraph_emojis[i % len(self.paragraph_emojis)]
                    formatted_paragraphs.append(f"{emoji} {p.strip()}")
                else:
                    # 如果配置中没有emoji，则不添加
                    formatted_paragraphs.append(p.strip())
        
        formatted_content = '\n\n'.join(formatted_paragraphs)
        
        # 检查总长度
        if len(formatted_content) > max_length:
            warnings.append(f"内容超过{max_length}字符,可能影响显示效果")
        
        return formatted_content, warnings
    
    def format_tags(self, tags: List[str]) -> Tuple[List[str], List[str]]:
        """
        格式化标签
        
        Args:
            tags: 原始标签列表
            
        Returns:
            (格式化后的标签列表, 警告列表)
        """
        max_count = self.tags_config.get('max_count', 10)
        tag_format = self.tags_config.get('format', '#{tag}')
        warnings = []
        
        if not tags:
            return [], []
        
        # 过滤空标签
        valid_tags = [tag.strip() for tag in tags if tag and tag.strip()]
        
        # 限制标签数量
        if len(valid_tags) > max_count:
            valid_tags = valid_tags[:max_count]
            warnings.append(f"标签超过{max_count}个,已自动保留前{max_count}个")
        
        # 格式化标签
        formatted_tags = [tag_format.format(tag=tag) for tag in valid_tags]
        
        return formatted_tags, warnings
