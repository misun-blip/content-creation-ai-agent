import request from "./index";

/**
 * 获取标签列表（支持按名称搜索）
 * @param {Object} [params] - 查询参数
 * @param {string} [params.q] - 搜索关键词
 * @returns {Promise} 标签列表
 */
export function fetchTags(params) {
  return request.get("/api/v1/tags", { params });
}

/**
 * 创建标签
 * @param {Object} data - 标签数据
 * @param {string} data.name - 标签名称
 * @returns {Promise} 创建的标签
 */
export function createTag(data) {
  return request.post("/api/v1/tags", data);
}

/**
 * 获取单个标签
 * @param {number} tagId - 标签 ID
 * @returns {Promise} 标签详情
 */
export function getTag(tagId) {
  return request.get(`/api/v1/tags/${tagId}`);
}

/**
 * 删除标签
 * @param {number} tagId - 标签 ID
 * @returns {Promise} 删除结果
 */
export function deleteTag(tagId) {
  return request.delete(`/api/v1/tags/${tagId}`);
}
