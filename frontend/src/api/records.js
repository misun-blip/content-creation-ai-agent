import request from "./index";

// ─────────────────────────────────────────────────────────────
// 创作记录 CRUD
// ─────────────────────────────────────────────────────────────

/**
 * 获取创作记录列表（支持关键词/平台/状态/时间范围/分页筛选）
 * @param {Object} params - 查询参数
 * @param {string} [params.keyword] - 标题关键词
 * @param {string} [params.platform] - 平台筛选
 * @param {string} [params.status] - 状态筛选 draft/published/archived
 * @param {string} [params.start_date] - 开始日期 YYYY-MM-DD
 * @param {string} [params.end_date] - 结束日期 YYYY-MM-DD
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页条数
 */
export function fetchRecords(params) {
  return request.get("/api/v1/records/", { params });
}

/**
 * 创建创作记录
 * @param {Object} data - 记录数据
 * @param {string} data.title - 标题
 * @param {string} data.platform - 平台
 * @param {string} [data.content] - 内容
 * @param {string} [data.status] - 状态
 */
export function createRecord(data) {
  return request.post("/api/v1/records/", data);
}

/**
 * 获取单条创作记录详情
 * @param {number} recordId - 记录ID
 */
export function getRecord(recordId) {
  return request.get(`/api/v1/records/${recordId}`);
}

/**
 * 更新创作记录
 * @param {number} recordId - 记录ID
 * @param {Object} data - 更新数据
 */
export function updateRecord(recordId, data) {
  return request.put(`/api/v1/records/${recordId}`, data);
}

/**
 * 删除创作记录
 * @param {number} recordId - 记录ID
 */
export function deleteRecord(recordId) {
  return request.delete(`/api/v1/records/${recordId}`);
}

// ─────────────────────────────────────────────────────────────
// 版本管理
// ─────────────────────────────────────────────────────────────

/**
 * 获取某条记录的所有版本列表
 * @param {number} recordId - 记录ID
 */
export function fetchVersions(recordId) {
  return request.get(`/api/v1/records/${recordId}/versions`);
}

/**
 * 为某条记录创建新版本
 * @param {number} recordId - 记录ID
 * @param {Object} data - 版本数据
 * @param {string} data.content - 版本内容
 * @param {string} [data.change_note] - 变更说明
 */
export function createVersion(recordId, data) {
  return request.post(`/api/v1/records/${recordId}/versions`, data);
}

/**
 * 获取指定版本详情
 * @param {number} recordId - 记录ID
 * @param {number} versionId - 版本ID
 */
export function getVersion(recordId, versionId) {
  return request.get(`/api/v1/records/${recordId}/versions/${versionId}`);
}

/**
 * 回滚到指定版本
 * @param {number} recordId - 记录ID
 * @param {number} versionId - 版本ID
 */
export function restoreVersion(recordId, versionId) {
  return request.post(`/api/v1/records/${recordId}/versions/${versionId}/restore`);
}

/**
 * 删除指定版本
 * @param {number} recordId - 记录ID
 * @param {number} versionId - 版本ID
 */
export function deleteVersion(recordId, versionId) {
  return request.delete(`/api/v1/records/${recordId}/versions/${versionId}`);
}

// ─────────────────────────────────────────────────────────────
// 导出
// ─────────────────────────────────────────────────────────────

/**
 * 导出创作记录（支持 csv/txt/docx/pdf 格式）
 * @param {string} format - 导出格式 csv|txt|docx|pdf
 * @param {Object} [params] - 筛选参数（同 fetchRecords）
 */
export function exportRecords(format, params) {
  return request.get(`/api/v1/records/export/${format}`, {
    params,
    responseType: "blob",
  });
}
