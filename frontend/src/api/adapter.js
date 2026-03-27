import request from "./index";

/**
 * 适配内容到指定平台
 * @param {Object} data - 适配请求数据
 * @param {string} data.content - 原始内容
 * @param {string} data.platform - 目标平台(douyin/xiaohongshu/wechat)
 * @param {string} [data.title] - 标题
 * @param {Array<string>} [data.tags] - 标签列表
 * @param {boolean} [data.auto_format] - 是否自动排版，默认true
 * @returns {Promise<Object>} 适配结果
 */
export const adaptContent = async (data) => {
  return request({
    url: "/api/v1/adapter/adapt",
    method: "post",
    data,
  });
};

/**
 * 获取支持的平台列表
 * @returns {Promise<Object>} 平台列表
 */
export const getPlatforms = async () => {
  return request({
    url: "/api/v1/adapter/platforms",
    method: "get",
  });
};
