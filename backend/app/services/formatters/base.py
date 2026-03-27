from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import re


class BaseFormatter(ABC):
    """格式化器基类"""
    
    def __init__(self, config: Dict):
        """
        初始化格式化器
        
        Args:
            config: 平台配置字典
        """
        self.config = config
        self.title_config = config.get('title', {})
        self.content_config = config.get('content', {})
        self.tags_config = config.get('tags', {})
        self.cover_config = config.get('cover', {})
    
    @abstractmethod
    def format_title(self, title: str) -> Tuple[str, List[str]]:
        """
        格式化标题
        
        Args:
            title: 原始标题
            
        Returns:
            (格式化后的标题, 警告列表)
        """
        pass
    
    @abstractmethod
    def format_content(self, content: str) -> Tuple[str, List[str]]:
        """
        格式化内容
        
        Args:
            content: 原始内容
            
        Returns:
            (格式化后的内容, 警告列表)
        """
        pass
    
    @abstractmethod
    def format_tags(self, tags: List[str]) -> Tuple[List[str], List[str]]:
        """
        格式化标签
        
        Args:
            tags: 原始标签列表
            
        Returns:
            (格式化后的标签列表, 警告列表)
        """
        pass
    
    def _truncate_text(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 截断后缀
            
        Returns:
            截断后的文本
        """
        if not text:
            return ""
            
        if max_length <= 0:
            return ""
            
        if len(text) <= max_length:
            return text
            
        # 确保max_length大于suffix长度
        if max_length <= len(suffix):
            return text[:max_length]
            
        return text[:max_length - len(suffix)] + suffix
    
    def _split_paragraphs(self, content: str, max_length: int) -> List[str]:
        """
        分割段落
        
        Args:
            content: 原始内容
            max_length: 每段最大长度
            
        Returns:
            分割后的段落列表
        """
        if not content:
            return []
            
        if max_length <= 0:
            return [content]
            
        paragraphs = []
        current = ""
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                if current:
                    paragraphs.append(current.rstrip())
                    current = ""
                continue
            
            if len(current) + len(line) <= max_length:
                current += line + '\n'
            else:
                if current:
                    paragraphs.append(current.rstrip())
                current = line + '\n'
        
        if current:
            paragraphs.append(current.rstrip())
        
        return paragraphs
    
    def _optimize_punctuation(self, text: str) -> str:
        """
        优化标点符号
        
        Args:
            text: 原始文本
            
        Returns:
            优化后的文本
        """
        if not text:
            return ""
            
        # 统一中文标点
        text = text.replace(',', '，').replace('.', '。')
        text = text.replace('!', '！').replace('?', '？')
        
        # 移除多余空格，但保留段落分隔
        text = re.sub(r'[ \t]+', '', text)
        
        return text
    
    def _optimize_spaces(self, text: str) -> str:
        """
        优化中英文之间的空格
        
        Args:
            text: 原始文本
            
        Returns:
            优化后的文本
        """
        if not text:
            return ""
            
        # 在中文和英文/数字之间添加空格
        text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)
        return text
