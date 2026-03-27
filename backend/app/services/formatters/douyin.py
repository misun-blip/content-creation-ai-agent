from typing import Dict, List, Tuple
from .base import BaseFormatter


class DouyinFormatter(BaseFormatter):
    """抖音格式化器"""
    
    def format_title(self, title: str) -> Tuple[str, List[str]]:
        """
        格式化标题
        
        Args:
            title: 原始标题
            
        Returns:
            (格式化后的标题, 警告列表)
        """
        max_length = self.title_config.get('max_length', 30)
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
        max_length = self.content_config.get('max_length', 2000)
        paragraph_max = self.content_config.get('paragraph_max_length', 500)
        warnings = []
        
        if not content:
            return "", ["内容为空"]
        
        # 优化标点和空格
        content = self._optimize_punctuation(content)
        content = self._optimize_spaces(content)
        
        # 分段处理
        paragraphs = self._split_paragraphs(content, paragraph_max)
        formatted_content = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
        
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
        max_count = self.tags_config.get('max_count', 5)
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
