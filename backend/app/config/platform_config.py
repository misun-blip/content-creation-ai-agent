import yaml
from pathlib import Path
from typing import Dict, Any, Union, List
import logging

logger = logging.getLogger(__name__)


class PlatformConfig:
    """平台配置管理器"""
    
    # 必需的配置字段
    REQUIRED_PLATFORM_FIELDS = ['name', 'code', 'title', 'content', 'tags', 'cover']
    REQUIRED_NESTED_FIELDS = {
        'title': ['max_length'],
        'content': ['max_length', 'paragraph_max_length'],
        'tags': ['max_count', 'format'],
        'cover': ['ratio']
    }
    
    def __init__(self, config_path: Union[str, Path, None] = None):
        """
        初始化平台配置管理器
        
        Args:
            config_path: 配置文件路径，默认为platform_config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent / "platform_config.yaml"
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"平台配置文件不存在: {self.config_path}，使用默认配置")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning("平台配置文件为空，使用默认配置")
                return self._get_default_config()
            
            # 验证配置结构
            if 'platforms' not in config:
                logger.warning("平台配置文件缺少platforms字段，使用默认配置")
                return self._get_default_config()
            
            # 验证配置
            if not self._validate_config(config):
                logger.warning("平台配置验证失败，使用默认配置")
                return self._get_default_config()
            
            return config
        except yaml.YAMLError as e:
            logger.error(f"平台配置文件格式错误: {e}，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"加载平台配置失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取最小默认配置（仅作为后备，实际配置应从YAML文件加载）
        
        Returns:
            默认配置字典
        """
        return {
            'platforms': {},
            'formatting_rules': {
                'auto_paragraph': True,
                'emoji_insertion': True,
                'space_optimization': True,
                'punctuation_optimization': True
            }
        }
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置文件的完整性和正确性
        
        Args:
            config: 配置字典
            
        Returns:
            验证是否通过
        """
        try:
            platforms = config.get('platforms', {})
            
            if not platforms:
                logger.warning("平台配置中没有定义任何平台")
                return False
            
            # 验证每个平台配置
            for platform_code, platform_config in platforms.items():
                if not self._validate_platform_config(platform_code, platform_config):
                    return False
            
            # 验证格式化规则
            if 'formatting_rules' in config:
                self._validate_formatting_rules(config['formatting_rules'])
            
            logger.info(f"配置验证通过，共加载 {len(platforms)} 个平台配置")
            return True
            
        except Exception as e:
            logger.error(f"配置验证过程中发生错误: {e}")
            return False
    
    def _validate_platform_config(self, platform_code: str, platform_config: Dict[str, Any]) -> bool:
        """
        验证单个平台配置
        
        Args:
            platform_code: 平台代码
            platform_config: 平台配置字典
            
        Returns:
            验证是否通过
        """
        # 检查必需字段
        missing_fields = []
        for field in self.REQUIRED_PLATFORM_FIELDS:
            if field not in platform_config:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"平台 {platform_code} 缺少必需字段: {missing_fields}")
            return False
        
        # 验证嵌套字段
        for section, required_fields in self.REQUIRED_NESTED_FIELDS.items():
            if section not in platform_config:
                logger.error(f"平台 {platform_code} 缺少 {section} 配置")
                return False
            
            section_config = platform_config[section]
            for field in required_fields:
                if field not in section_config:
                    logger.error(f"平台 {platform_code} 的 {section} 配置缺少 {field} 字段")
                    return False
        
        # 验证字段类型和值
        if not self._validate_field_types(platform_code, platform_config):
            return False
        
        return True
    
    def _validate_field_types(self, platform_code: str, platform_config: Dict[str, Any]) -> bool:
        """
        验证字段类型和值
        
        Args:
            platform_code: 平台代码
            platform_config: 平台配置字典
            
        Returns:
            验证是否通过
        """
        try:
            # 验证标题配置
            title_config = platform_config['title']
            if not isinstance(title_config['max_length'], int) or title_config['max_length'] <= 0:
                logger.error(f"平台 {platform_code} 的 title.max_length 必须是正整数")
                return False
            
            # 验证内容配置
            content_config = platform_config['content']
            if not isinstance(content_config['max_length'], int) or content_config['max_length'] <= 0:
                logger.error(f"平台 {platform_code} 的 content.max_length 必须是正整数")
                return False
            
            if not isinstance(content_config['paragraph_max_length'], int) or content_config['paragraph_max_length'] <= 0:
                logger.error(f"平台 {platform_code} 的 content.paragraph_max_length 必须是正整数")
                return False
            
            # 验证标签配置
            tags_config = platform_config['tags']
            if not isinstance(tags_config['max_count'], int) or tags_config['max_count'] < 0:
                logger.error(f"平台 {platform_code} 的 tags.max_count 必须是非负整数")
                return False
            
            # 验证封面配置
            cover_config = platform_config['cover']
            if not isinstance(cover_config['ratio'], str) or not cover_config['ratio']:
                logger.error(f"平台 {platform_code} 的 cover.ratio 必须是非空字符串")
                return False
            
            return True
            
        except (KeyError, TypeError) as e:
            logger.error(f"平台 {platform_code} 配置字段类型验证失败: {e}")
            return False
    
    def _validate_formatting_rules(self, formatting_rules: Dict[str, Any]) -> bool:
        """
        验证格式化规则
        
        Args:
            formatting_rules: 格式化规则字典
            
        Returns:
            验证是否通过
        """
        try:
            for rule_name, rule_value in formatting_rules.items():
                if not isinstance(rule_value, bool):
                    logger.warning(f"格式化规则 {rule_name} 的值必须是布尔类型，当前为 {type(rule_value)}")
            
            return True
            
        except Exception as e:
            logger.error(f"格式化规则验证失败: {e}")
            return False
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        获取指定平台的配置
        
        Args:
            platform: 平台代码（douyin/xiaohongshu/wechat）
            
        Returns:
            平台配置字典
        """
        platforms = self.config.get('platforms', {})
        return platforms.get(platform, {})
    
    def get_all_platforms(self) -> Dict[str, Any]:
        """
        获取所有平台配置
        
        Returns:
            所有平台配置字典
        """
        return self.config.get('platforms', {})
    
    def get_formatting_rules(self) -> Dict[str, Any]:
        """
        获取格式化规则
        
        Returns:
            格式化规则字典
        """
        return self.config.get('formatting_rules', {})
    
    def get_supported_platforms(self) -> List[str]:
        """
        获取支持的平台代码列表
        
        Returns:
            平台代码列表
        """
        return list(self.config.get('platforms', {}).keys())
    
    def is_platform_supported(self, platform: str) -> bool:
        """
        检查平台是否支持
        
        Args:
            platform: 平台代码
            
        Returns:
            是否支持
        """
        return platform in self.config.get('platforms', {})
    
    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        Returns:
            重新加载是否成功
        """
        try:
            old_config = self.config
            self.config = self._load_config()
            logger.info("配置文件重新加载成功")
            return True
        except Exception as e:
            logger.error(f"重新加载配置文件失败: {e}")
            self.config = old_config
            return False


# 全局配置实例
platform_config = PlatformConfig()
