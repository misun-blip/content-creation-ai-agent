# 平台适配模块API文档

---

**文档版本**: 1.0  
**编制日期**: 2026年2月  
**编制人**: 平台适配模块负责人  
**API版本**: v1.0

---

## 1. 适配内容接口

### 接口地址
`POST /api/v1/adapter/adapt`

### 接口描述
将原始内容适配到指定平台的格式要求，返回适配后的内容。

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 原始内容 |
| platform | string | 是 | 目标平台(douyin/xiaohongshu/wechat) |
| title | string | 否 | 标题 |
| tags | array | 否 | 标签列表 |
| auto_format | boolean | 否 | 是否自动排版，默认true |

### 请求示例

```json
{
  "content": "这是一段测试内容,用于测试平台适配功能。",
  "platform": "douyin",
  "title": "测试标题",
  "tags": ["测试", "适配"],
  "auto_format": true
}
```

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 响应码，200表示成功 |
| message | string | 响应消息 |
| data | object | 适配结果数据 |

### data参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| title | string | 格式化后的标题 |
| content | string | 格式化后的内容 |
| tags | array | 格式化后的标签列表 |
| preview | string | 完整预览文本 |
| warnings | array | 警告信息列表 |
| suggestions | array | 建议信息列表 |

### 响应示例

```json
{
  "code": 200,
  "message": "适配成功",
  "data": {
    "title": "测试标题",
    "content": "这是一段测试内容,用于测试平台适配功能。",
    "tags": ["#测试", "#适配"],
    "preview": "测试标题\n\n这是一段测试内容,用于测试平台适配功能。\n\n#测试 #适配",
    "warnings": [],
    "suggestions": []
  }
}
```

### 错误响应

#### 400错误 - 参数错误

```json
{
  "detail": "不支持的平台: invalid"
}
```

#### 422错误 - 验证错误

```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500错误 - 服务器错误

```json
{
  "detail": "适配失败: 服务器内部错误"
}
```

---

## 2. 获取平台列表接口

### 接口地址
`GET /api/v1/adapter/platforms`

### 接口描述
获取所有支持的平台及其格式配置信息。

### 请求参数
无

### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 响应码，200表示成功 |
| message | string | 响应消息 |
| data | array | 平台列表数据 |

### data数组元素说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | string | 平台代码(douyin/xiaohongshu/wechat) |
| name | string | 平台名称 |
| title | object | 标题配置 |
| content | object | 内容配置 |
| tags | object | 标签配置 |
| cover | object | 封面配置 |

### title参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| max_length | integer | 标题最大长度 |
| emoji_enabled | boolean | 是否支持emoji |
| tips | string | 标题提示信息 |

### content参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| max_length | integer | 内容最大长度 |
| paragraph_max_length | integer | 每段最大长度 |
| tips | string | 内容提示信息 |

### tags参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| max_count | integer | 标签最大数量 |
| format | string | 标签格式 |
| tips | string | 标签提示信息 |

### cover参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| ratio | string | 封面比例 |
| tips | string | 封面提示信息 |

### 响应示例

```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "code": "douyin",
      "name": "抖音",
      "title": {
        "max_length": 30,
        "emoji_enabled": true,
        "tips": "标题需要吸引眼球,可使用emoji"
      },
      "content": {
        "max_length": 2000,
        "paragraph_max_length": 500,
        "tips": "正文第一段为钩子,吸引用户停留"
      },
      "tags": {
        "max_count": 5,
        "format": "#{tag}",
        "tips": "标签需要与内容相关"
      },
      "cover": {
        "ratio": "9:16",
        "tips": "竖屏高清图片"
      }
    },
    {
      "code": "xiaohongshu",
      "name": "小红书",
      "title": {
        "max_length": 20,
        "emoji_enabled": true,
        "tips": "标题需要简洁有力"
      },
      "content": {
        "max_length": 1000,
        "paragraph_max_length": 300,
        "tips": "正文需要分段清晰,使用emoji分隔"
      },
      "tags": {
        "max_count": 10,
        "format": "#{tag}",
        "tips": "标签需要覆盖主要关键词"
      },
      "cover": {
        "ratio": "3:4",
        "tips": "3:4比例高清图片"
      }
    },
    {
      "code": "wechat",
      "name": "微信视频号",
      "title": {
        "max_length": 30,
        "emoji_enabled": false,
        "tips": "标题需要简洁明了"
      },
      "content": {
        "max_length": 200,
        "paragraph_max_length": 200,
        "tips": "描述需要概括内容要点"
      },
      "tags": {
        "max_count": 0,
        "format": "",
        "tips": "不支持标签"
      },
      "cover": {
        "ratio": "16:9",
        "tips": "16:9比例高清图片"
      }
    }
  ]
}
```

---

## 3. 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|--------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未授权 | 需要登录 |
| 404 | 资源不存在 | 检查接口地址 |
| 422 | 数据验证失败 | 检查数据格式 |
| 500 | 服务器内部错误 | 联系技术支持 |

---

## 4. 使用示例

### 示例1：适配内容到抖音

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/adapter/adapt \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天分享3个超好用的视频剪辑技巧",
    "platform": "douyin",
    "title": "3个视频剪辑技巧",
    "tags": ["教程", "干货", "分享"]
  }'
```

**响应**:
```json
{
  "code": 200,
  "message": "适配成功",
  "data": {
    "title": "3个视频剪辑技巧",
    "content": "今天分享3个超好用的视频剪辑技巧。",
    "tags": ["#教程", "#干货", "#分享"],
    "preview": "3个视频剪辑技巧\n\n今天分享3个超好用的视频剪辑技巧。\n\n#教程 #干货 #分享",
    "warnings": [],
    "suggestions": []
  }
}
```

### 示例2：获取平台列表

**请求**:
```bash
curl http://localhost:8000/api/v1/adapter/platforms
```

**响应**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "code": "douyin",
      "name": "抖音",
      "title": {
        "max_length": 30,
        "emoji_enabled": true,
        "tips": "标题需要吸引眼球,可使用emoji"
      },
      "content": {
        "max_length": 2000,
        "paragraph_max_length": 500,
        "tips": "正文第一段为钩子,吸引用户停留"
      },
      "tags": {
        "max_count": 5,
        "format": "#{tag}",
        "tips": "标签需要与内容相关"
      },
      "cover": {
        "ratio": "9:16",
        "tips": "竖屏高清图片"
      }
    }
  ]
}
```

---

## 5. 注意事项

1. **编码格式**: 所有请求和响应使用UTF-8编码
2. **时间格式**: 使用ISO 8601格式
3. **认证**: 需要在请求头中携带有效的认证token
4. **限流**: API接口建议每秒不超过10次请求
5. **错误处理**: 客户端应该根据错误码进行相应的错误处理
6. **超时设置**: 建议设置请求超时时间为30秒

---

## 6. 版本历史

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| 1.0 | 2026-02-18 | 平台适配模块负责人 | 初始版本 |

---

**文档结束**
