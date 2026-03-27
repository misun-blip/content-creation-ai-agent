import request from "./index";

// 模拟数据
const mockData = {
  stats: {
    totalMaterials: 128,
    totalCreations: 56,
    aiGenerations: 34,
    platformAdapts: 12
  },
  trend: {
    xAxis: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    data: [12, 19, 15, 25, 22, 30, 35, 42, 38, 45, 52, 60]
  },
  platform: [
    { value: 55, name: "抖音" },
    { value: 30, name: "小红书" },
    { value: 10, name: "微信" },
    { value: 8, name: "B站" },
    { value: 7, name: "微博" }
  ],
  type: {
    xAxis: ["文案", "方案", "教程", "分析", "指南", "故事", "评论"],
    data: [40, 20, 15, 15, 10, 8, 12]
  },
  activities: [
    {
      title: "生成了新的选题：2024年营销热点趋势分析",
      time: "10分钟前",
      icon: "MagicStick",
      color: "#E6A23C"
    },
    {
      title: "上传了新素材：春季营销活动海报",
      time: "2小时前",
      icon: "Upload",
      color: "#409EFF"
    },
    {
      title: "生成了新的文案：小红书爆款笔记分析",
      time: "4小时前",
      icon: "EditPen",
      color: "#67C23A"
    },
    {
      title: "适配了文案到抖音平台",
      time: "6小时前",
      icon: "Platform",
      color: "#F56C6C"
    },
    {
      title: "查看了统计分析报告",
      time: "昨天",
      icon: "Document",
      color: "#909399"
    }
  ],
  tags: [
    { name: "营销", type: "" },
    { name: "热点", type: "success" },
    { name: "爆款", type: "warning" },
    { name: "短视频", type: "danger" },
    { name: "运营", type: "info" },
    { name: "内容创作", type: "" },
    { name: "流量", type: "success" },
    { name: "转化", type: "warning" },
    { name: "品牌", type: "info" },
    { name: "增长", type: "success" }
  ]
};

// 获取主页面统计数据
export function getDashboardStats() {
  return request({
    url: "/api/v1/dashboard/stats",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.stats
    };
  });
}

// 获取创作趋势数据
export function getCreationTrend() {
  return request({
    url: "/api/v1/dashboard/trend",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.trend
    };
  });
}

// 获取平台分布数据
export function getPlatformDistribution() {
  return request({
    url: "/api/v1/dashboard/platform",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.platform
    };
  });
}

// 获取创作类型数据
export function getCreationType() {
  return request({
    url: "/api/v1/dashboard/type",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.type
    };
  });
}

// 获取最近活动
export function getRecentActivities() {
  return request({
    url: "/api/v1/dashboard/activities",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.activities
    };
  });
}

// 获取热门标签
export function getHotTags() {
  return request({
    url: "/api/v1/dashboard/tags",
    method: "get",
  }).catch(() => {
    // API调用失败时返回模拟数据
    return {
      code: 200,
      message: "成功",
      data: mockData.tags
    };
  });
}
