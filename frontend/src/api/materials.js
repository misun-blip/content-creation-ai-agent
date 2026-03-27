import request from "./index";

/**
 * 获取素材列表（支持 q、category、tag）
 */
export function fetchMaterials(params) {
  return request.get("/api/v1/materials", { params });
}

/**
 * 获取素材分类列表
 */
export function fetchCategories() {
  return request.get("/api/v1/materials/categories");
}

/**
 * 创建素材
 */
export function createMaterial(data) {
  return request.post("/api/v1/materials", data);
}

/**
 * 更新素材
 */
export function updateMaterial(id, data) {
  return request.put(`/api/v1/materials/${id}`, data);
}

/**
 * 删除素材
 */
export function deleteMaterial(id) {
  return request.delete(`/api/v1/materials/${id}`);
}

/**
 * 设置素材标签
 */
export function setMaterialTags(id, tagIds) {
  return request.put(`/api/v1/materials/${id}/tags`, { tag_ids: tagIds });
}

/**
 * 上传文件
 */
export function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/api/v1/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
