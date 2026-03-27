# 面向流媒体/自媒体营销的"内容创作AI-Agent"后端架构模块 API 文档

---

**文档版本**：2.0  
**编制日期**：2026年3月  
**编制人**：项目团队  
**审核人**：团队负责人  

---

## 1. 概述

本文档描述后端架构模块提供的所有 API 接口。完整的交互式文档可通过启动服务后访问：

- **Swagger UI**：`http://localhost:8000/docs`
- **ReDoc**：`http://localhost:8000/redoc`

## 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `http://localhost:8000` |
| 认证方式 | Bearer Token (JWT) |
| 数据格式 | JSON |

---

## 1. 系统端点

### `GET /health`
健康检查，用于监控和容器探活。

**响应示例**：
```json
{"status": "healthy"}
```

### `GET /`
根路径，返回系统基本信息。

**响应示例**：
```json
{"message": "欢迎使用内容创作AI-Agent", "version": "1.0.0"}
```

---

## 2. 认证模块 `/api/v1/auth`

### `POST /api/v1/auth/register`
用户注册。

**请求体**：
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**成功响应** (200)：
```json
{"code": 200, "message": "注册成功", "data": {"id": 1}}
```

**错误响应** (400)：用户名已存在 / 邮箱已被注册

### `POST /api/v1/auth/login`
用户登录，返回 JWT 令牌。

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**成功响应** (200)：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {"id": 1, "username": "string", "email": "user@example.com"}
  }
}
```

**错误响应** (401)：用户名或密码错误

---



## 3. 素材管理 `/api/v1/materials`

> 当前实现说明：素材元信息包含 `title/description/category/preview/uploadDate/id`。
> `preview` 推荐保存为可访问的静态资源地址（例如 `http://localhost:8000/uploads/<filename>` 或 `/uploads/<filename>`）。

### `GET /api/v1/materials`

获取素材列表（支持关键字搜索与分类筛选）。

**Query 参数**：

| 参数       | 类型     | 必填 | 默认值  | 说明                |
| -------- | ------ | -- | ---- | ----------------- |
| q        | string | 否  | `""` | 关键字搜索（匹配标题/描述）    |
| category | string | 否  | `""` | 分类筛选（图片/视频/音频/文档） |

**成功响应** (200)：

```json
[
  {
    "id": 1,
    "title": "新春快乐",
    "description": "新春活动海报",
    "category": "图片",
    "preview": "http://localhost:8000/uploads/xxx.jpg",
    "uploadDate": "2026-02-21"
  }
]
```

---

### `POST /api/v1/materials`

创建素材（保存素材元数据）。

**请求体**：

```json
{
  "title": "string",
  "description": "string",
  "category": "图片",
  "preview": "http://localhost:8000/uploads/xxx.jpg"
}
```

**字段说明**：

| 字段          | 类型     | 必填 | 说明                         |
| ----------- | ------ | -- | -------------------------- |
| title       | string | 是  | 素材标题                       |
| description | string | 是  | 素材描述                       |
| category    | string | 是  | 分类：图片/视频/音频/文档             |
| preview     | string | 是  | 预览地址/文件地址（通常来自上传接口返回的路径拼接） |

**成功响应** (200)：

```json
{
  "id": 2,
  "title": "1",
  "description": "1",
  "category": "图片",
  "preview": "http://localhost:8000/uploads/5e34430b5908422c80b2b02087f34704.jpg",
  "uploadDate": "2026-02-21"
}
```

---

### `PUT /api/v1/materials/{material_id}`

更新素材元数据（支持局部更新）。

**Path 参数**：

* `material_id`：素材 ID

**请求体**（可选字段，未提供的不修改）：

```json
{
  "title": "string",
  "description": "string",
  "category": "图片",
  "preview": "http://localhost:8000/uploads/new.jpg"
}
```

**成功响应** (200)：返回更新后的素材对象（同 `POST` 响应结构）。

---

### `DELETE /api/v1/materials/{material_id}`

删除素材元数据。

**Path 参数**：

* `material_id`：素材 ID

**成功响应** (200)：

```json
{"ok": true, "deleted": 1}
```

> 注意：当前删除接口仅删除元数据记录；若需同时删除文件，需要在后端增加“文件清理”逻辑或提供单独的删除文件接口。

---

## 3.1 上传模块 `/api/v1/uploads`

> 用途：上传素材文件（图片/视频/音频/文档），并返回可访问的文件路径。
> 上传成功后，一般流程是：先调用上传接口拿到文件路径，再调用 `POST /materials` 保存元数据。

### `POST /api/v1/uploads`

上传文件（multipart/form-data）。

**请求类型**：`multipart/form-data`

**表单字段**：

| 字段   | 类型   | 必填 | 说明   |
| ---- | ---- | -- | ---- |
| file | file | 是  | 上传文件 |

**成功响应** (200)：当前实现返回一个字符串路径（Swagger 显示 `string`）

```json
"/uploads/5e34430b5908422c80b2b02087f34704.jpg"
```

> 前端处理建议：
>
> * 若后端返回 `/uploads/...` 相对路径，可拼接为 `http://localhost:8000/uploads/...` 用于预览；
> * 或直接将相对路径存入 `preview`，配合前端代理/同域部署实现访问。

---

## 推荐联动流程（上传 → 创建素材）

1. `POST /api/v1/uploads` 上传文件，得到：

   ```json
   "/uploads/xxx.jpg"
   ```
2. 拼接预览地址（示例）：

   * `preview = http://localhost:8000/uploads/xxx.jpg`
3. `POST /api/v1/materials` 保存素材元数据：

   ```json
   {
     "title": "新春快乐",
     "description": "新春活动海报",
     "category": "图片",
     "preview": "http://localhost:8000/uploads/xxx.jpg"
   }
   ```

---


---

## 4. AI 内容生成 `/api/v1/ai`

### `POST /api/v1/ai/generate`
AI 生成内容（待实现）。

---

## 5. 平台适配 `/api/v1/adapter`

### `POST /api/v1/adapter/adapt`
适配内容到指定平台。

**请求体**：
```json
{
  "content": "需要适配的内容",
  "platform": "douyin",
  "title": "标题",
  "tags": ["标签1", "标签2"],
  "auto_format": true
}
```

**支持平台**：`douyin` | `xiaohongshu` | `wechat`

### `GET /api/v1/adapter/platforms`
获取支持的平台列表。

---

## 6. 创作记录 `/api/v1/records`

### `GET /api/v1/records/`
获取创作记录列表（待实现）。

---

## 7. 统计分析 `/api/v1/statistics`

### `GET /api/v1/statistics/`
获取统计数据（待实现）。

---

## 统一错误响应格式

```json
{
  "code": 401,
  "message": "错误描述"
}
```

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / 令牌无效 |
| 422 | 请求体验证失败 |
| 500 | 服务器内部错误 |

## 认证说明

1. 调用 `/api/v1/auth/login` 获取 `token`
2. 在后续请求 Header 中添加：`Authorization: Bearer <token>`
3. 令牌有效期：30 分钟（可配置）

---

**文档说明**：这份API文档为"内容创作AI-Agent"后端架构模块提供了完整的API接口说明，涵盖了认证、素材管理、AI内容生成、平台适配、创作记录和统计分析等核心功能，确保后端API能够高效支持前端开发和系统集成。
