import request from "./index";

/**
 * 生成选题
 * @param {{ keywords: string, industry: string, platform: string, count?: number }} data
 */
export function generateTopics(data) {
  return request.post("/api/v1/ai/topics", data);
}

/**
 * 生成文案
 * @param {{ topic: string, length?: number, style?: string, platform?: string }} data
 */
export function generateContent(data) {
  return request.post("/api/v1/ai/content", data);
}

/**
 * 内容质量评估
 * @param {{ content: string }} data
 */
export function evaluateContent(data) {
  return request.post("/api/v1/ai/evaluate", data);
}
