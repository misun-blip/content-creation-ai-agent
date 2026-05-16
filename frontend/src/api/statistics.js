// frontend/src/api/statistics.js
import request from '@/api/index';

// 每日创作统计
export const getDailyStats = (params) => {
  return request({
    url: '/api/v1/statistics/daily',
    method: 'get',
    params
  });
};

// 关键词统计（必须存在，且名字完全一致）
export const getKeywordStats = (params) => {
  return request({
    url: '/api/v1/statistics/keywords',
    method: 'get',
    params
  });
};

// 其他接口（可选，先保证前两个存在）
export const getPlatformStats = (params) => {
  return request({
    url: '/api/v1/statistics/platform',
    method: 'get',
    params
  });
};

export const getTypeStats = (params) => {
  return request({
    url: '/api/v1/statistics/type',
    method: 'get',
    params
  });
};

export const getSummaryStats = (params) => {
  return request({
    url: '/api/v1/statistics/summary',
    method: 'get',
    params
  });
};

// 总字数统计
export const getTotalWords = (params) => {
  return request({
    url: '/api/v1/statistics/total_words',
    method: 'get',
    params
  });
};

// 平均创作时间
export const getAvgTime = (params) => {
  return request({
    url: '/api/v1/statistics/avg_time',
    method: 'get',
    params
  });
};

// 导出统计报告
export const exportReport = (params) => {
  return request({
    url: '/api/v1/statistics/export_report',
    method: 'get',
    params,
    responseType: 'blob'
  });
};
