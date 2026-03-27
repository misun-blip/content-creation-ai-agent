from typing import Dict, List, Tuple
from .base import BaseFormatter


class WechatFormatter(BaseFormatter):
    """微信视频号格式化器"""
    
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
        max_length = self.content_config.get('max_length', 200)
        warnings = []
        
        if not content:
            return "", ["内容为空"]
        
        # 优化标点和空格
        content = self._optimize_punctuation(content)
        content = self._optimize_spaces(content)
        
        # 截断内容
        formatted_content = self._truncate_text(content, max_length)
        
        if len(content) > max_length:
            warnings.append(f"描述超过{max_length}字符,已自动截断")
        
        return formatted_content, warnings
    
    def format_tags(self, tags: List[str]) -> Tuple[List[str], List[str]]:
        """
        格式化标签
        
        Args:
            tags: 原始标签列表
            
        Returns:
            (格式化后的标签列表, 警告列表)
        """
        warnings = []
        
        # 微信视频号不支持标签
        if tags:
            warnings.append("微信视频号不支持标签,标签已忽略")
        
        return [], warnings
