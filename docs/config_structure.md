# 平台配置文件结构设计

---

**文档版本**: 1.0  
**编制日期**: 2026年2月  
**编制人**: 平台适配模块负责人  
**配置文件**: `backend/app/config/platform_config.yaml`

---

## 1. 概述

本文档描述了平台配置文件的结构设计，用于存储各平台的格式规范和适配规则。配置文件采用YAML格式，易于阅读和维护。

---

## 2. 配置文件结构

### 2.1 整体结构

```
platform_config.yaml
├── platforms                    # 平台配置节点
│   ├── douyin                  # 抖音平台配置
│   │   ├── name                # 平台名称
│   │   ├── code                # 平台代码
│   │   ├── title               # 标题配置
│   │   │   ├── max_length      # 标题最大长度
│   │   │   ├── emoji_enabled   # 是否支持emoji
│   │   │   └── tips           # 标题提示信息
│   │   ├── content             # 内容配置
│   │   │   ├── max_length      # 内容最大长度
│   │   │   ├── paragraph_max_length  # 段落最大长度
│   │   │   └── tips           # 内容提示信息
│   │   ├── tags                # 标签配置
│   │   │   ├── max_count       # 标签最大数量
│   │   │   ├── format          # 标签格式
│   │   │   └── tips           # 标签提示信息
│   │   └── cover               # 封面配置
│   │       ├── ratio           # 封面比例
│   │       └── tips           # 封面提示信息
│   ├── xiaohongshu            # 小红书平台配置
│   │   └── ...                 # 结构同抖音
│   └── wechat                 # 微信视频号平台配置
│       └── ...                 # 结构同抖音
└── formatting_rules            # 格式化规则
    ├── auto_paragraph          # 自动分段
    ├── emoji_insertion         # emoji插入
    ├── space_optimization      # 空格优化
    └── punctuation_optimization  # 标点优化
```

### 2.2 详细结构说明

#### 2.2.1 platforms节点

存储所有平台的配置信息，每个平台作为一个子节点。

```yaml
platforms:
  douyin:
    # 抖音平台配置
  xiaohongshu:
    # 小红书平台配置
  wechat:
    # 微信视频号平台配置
```

#### 2.2.2 平台配置节点

每个平台包含以下子节点：

**基本信息**:
- `name`: 平台名称（中文）
- `code`: 平台代码（英文，用于程序识别）

**标题配置**:
- `max_length`: 标题最大长度（字符数）
- `emoji_enabled`: 是否支持emoji（true/false）
- `tips`: 标题提示信息（给用户的建议）

**内容配置**:
- `max_length`: 内容最大长度（字符数）
- `paragraph_max_length`: 段落最大长度（字符数）
- `tips`: 内容提示信息（给用户的建议）

**标签配置**:
- `max_count`: 标签最大数量
- `format`: 标签格式（如"#{tag}"）
- `tips`: 标签提示信息（给用户的建议）

**封面配置**:
- `ratio`: 封面比例（如"9:16"）
- `tips`: 封面提示信息（给用户的建议）

#### 2.2.3 formatting_rules节点

存储全局格式化规则，适用于所有平台。

```yaml
formatting_rules:
  auto_paragraph: true          # 自动分段
  emoji_insertion: true         # emoji插入
  space_optimization: true      # 空格优化
  punctuation_optimization: true # 标点优化
```

---

## 3. 配置文件示例

### 3.1 完整配置示例

```yaml
platforms:
  douyin:
    name: "抖音"
    code: "douyin"
    title:
      max_length: 30
      emoji_enabled: true
      tips: "标题需要吸引眼球,可使用emoji"
    content:
      max_length: 2000
      paragraph_max_length: 500
      tips: "正文第一段为钩子,吸引用户停留"
    tags:
      max_count: 5
      format: "#{tag}"
      tips: "标签需要与内容相关"
    cover:
      ratio: "9:16"
      tips: "竖屏高清图片"
    
  xiaohongshu:
    name: "小红书"
    code: "xiaohongshu"
    title:
      max_length: 20
      emoji_enabled: true
      tips: "标题需要简洁有力"
    content:
      max_length: 1000
      paragraph_max_length: 300
      tips: "正文需要分段清晰,使用emoji分隔"
    tags:
      max_count: 10
      format: "#{tag}"
      tips: "标签需要覆盖主要关键词"
    cover:
      ratio: "3:4"
      tips: "3:4比例高清图片"
    
  wechat:
    name: "微信视频号"
    code: "wechat"
    title:
      max_length: 30
      emoji_enabled: false
      tips: "标题需要简洁明了"
    content:
      max_length: 200
      paragraph_max_length: 200
      tips: "描述需要概括内容要点"
    tags:
      max_count: 0
      format: ""
      tips: "不支持标签"
    cover:
      ratio: "16:9"
      tips: "16:9比例高清图片"

formatting_rules:
  auto_paragraph: true
  emoji_insertion: true
  space_optimization: true
  punctuation_optimization: true
```

---

## 4. 配置加载器设计

### 4.1 PlatformConfig类

```python
import yaml
from pathlib import Path
from typing import Dict, Any

class PlatformConfig:
    """平台配置管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "platform_config.yaml"
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """获取指定平台的配置"""
        platforms = self.config.get('platforms', {})
        return platforms.get(platform, {})
    
    def get_all_platforms(self) -> Dict[str, Any]:
        """获取所有平台配置"""
        return self.config.get('platforms', {})
    
    def get_formatting_rules(self) -> Dict[str, Any]:
        """获取格式化规则"""
        return self.config.get('formatting_rules', {})

# 全局配置实例
platform_config = PlatformConfig()
```

### 4.2 使用示例

```python
from app.config.platform_config import platform_config

# 获取抖音平台配置
douyin_config = platform_config.get_platform_config('douyin')

# 获取所有平台配置
all_platforms = platform_config.get_all_platforms()

# 获取格式化规则
formatting_rules = platform_config.get_formatting_rules()
```

---

## 5. 配置文件管理

### 5.1 配置文件位置

配置文件位于: `backend/app/config/platform_config.yaml`

### 5.2 配置文件更新

当平台规范发生变化时，需要更新配置文件：

1. 修改对应的配置项
2. 保存配置文件
3. 重启后端服务使配置生效

### 5.3 配置文件验证

使用以下命令验证配置文件格式是否正确：

```bash
python -c "import yaml; yaml.safe_load(open('backend/app/config/platform_config.yaml', 'r', encoding='utf-8'))"
```

---

## 6. 扩展性设计

### 6.1 添加新平台

要添加新平台支持，只需在配置文件中添加新的平台节点：

```yaml
platforms:
  douyin:
    # 抖音配置
  xiaohongshu:
    # 小红书配置
  wechat:
    # 微信视频号配置
  bilibili:  # 新平台
    name: "哔哩哔哩"
    code: "bilibili"
    title:
      max_length: 50
      emoji_enabled: true
      tips: "标题需要简洁明了"
    content:
      max_length: 2000
      paragraph_max_length: 500
      tips: "内容需要分段清晰"
    tags:
      max_count: 12
      format: "#{tag}"
      tips: "标签需要与内容相关"
    cover:
      ratio: "16:9"
      tips: "16:9比例高清图片"
```

### 6.2 添加新配置项

要添加新的配置项，只需在对应平台节点下添加新的子节点：

```yaml
platforms:
  douyin:
    name: "抖音"
    code: "douyin"
    title:
      max_length: 30
      emoji_enabled: true
      tips: "标题需要吸引眼球,可使用emoji"
    content:
      max_length: 2000
      paragraph_max_length: 500
      tips: "正文第一段为钩子,吸引用户停留"
    tags:
      max_count: 5
      format: "#{tag}"
      tips: "标签需要与内容相关"
    cover:
      ratio: "9:16"
      tips: "竖屏高清图片"
    # 新增配置项
    video:
      max_duration: 300  # 视频最大时长（秒）
      min_duration: 15   # 视频最小时长（秒）
      tips: "视频时长建议在15-300秒之间"
```

---

## 7. 注意事项

1. **编码格式**: 配置文件必须使用UTF-8编码
2. **缩进**: 使用2个空格缩进，不要使用Tab
3. **注释**: 可以使用#添加注释
4. **验证**: 修改配置后要验证格式是否正确
5. **备份**: 修改配置前要备份原文件
6. **版本控制**: 配置文件应纳入版本控制

---

## 8. 参考资源

- [YAML官方文档](https://yaml.org/)
- [PyYAML文档](https://pyyaml.org/)

---

**文档结束**
