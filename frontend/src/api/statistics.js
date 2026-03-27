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
