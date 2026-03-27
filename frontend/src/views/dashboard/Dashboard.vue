<template>
  <div class="dashboard">
    <!-- 加载状态 -->
    <el-skeleton :loading="loading" animated>
      <!-- 快捷操作面板 -->
      <el-card class="quick-actions" shadow="hover">
        <template #header>
          <h3>快捷操作</h3>
        </template>
        <div class="actions-grid">
          <el-button
            type="primary"
            @click="handleCreateTopic"
            class="action-btn"
          >
            <el-icon><MagicStick /></el-icon>
            <span>生成选题</span>
          </el-button>
          <el-button
            type="success"
            @click="handleCreateContent"
            class="action-btn"
          >
            <el-icon><EditPen /></el-icon>
            <span>生成文案</span>
          </el-button>
          <el-button
            type="warning"
            @click="handlePlatformAdapt"
            class="action-btn"
          >
            <el-icon><Platform /></el-icon>
            <span>平台适配</span>
          </el-button>
          <el-button
            type="info"
            @click="handleUploadMaterial"
            class="action-btn"
          >
            <el-icon><Upload /></el-icon>
            <span>上传素材</span>
          </el-button>
        </div>
      </el-card>

      <!-- 统计卡片 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#409EFF"><Document /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalMaterials }}</div>
                <div class="stat-label">总素材数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#67C23A"><EditPen /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalCreations }}</div>
                <div class="stat-label">创作记录</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#E6A23C"
                ><MagicStick
              /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.aiGenerations }}</div>
                <div class="stat-label">AI生成</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <el-icon class="stat-icon" color="#F56C6C"><Platform /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ stats.platformAdapts }}</div>
                <div class="stat-label">平台适配</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <h3>创作趋势</h3>
            </template>
            <div ref="trendChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <h3>平台分布</h3>
            </template>
            <div ref="platformChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <h3>创作类型</h3>
            </template>
            <div ref="typeChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="recent-activities" shadow="hover">
            <template #header>
              <h3>最近活动</h3>
            </template>
            <div class="activities-list">
              <div
                v-for="(activity, index) in recentActivities"
                :key="index"
                class="activity-item"
              >
                <div class="activity-icon">
                  <el-icon :color="activity.color">
                    <component :is="iconMap[activity.icon] || MagicStick" />
                  </el-icon>
                </div>
                <div class="activity-content">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
              <div
                v-if="recentActivities.length === 0"
                class="empty-activities"
              >
                <el-empty description="暂无活动记录" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 热门标签 -->
      <el-card class="hot-tags" shadow="hover" style="margin-top: 20px">
        <template #header>
          <h3>热门标签</h3>
        </template>
        <div class="tag-cloud">
          <el-tag
            v-for="tag in hotTags"
            :key="tag.name"
            :type="tag.type"
            effect="plain"
            class="tag-item"
            @click="handleTagClick(tag.name)"
          >
            {{ tag.name }}
          </el-tag>
          <div v-if="hotTags.length === 0" class="empty-tags">
            <el-empty description="暂无热门标签" />
          </div>
        </div>
      </el-card>
    </el-skeleton>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElEmpty, ElSkeleton } from "element-plus";
import * as echarts from "echarts";
import {
  MagicStick,
  EditPen,
  Platform,
  Upload,
  Document,
  Calendar,
  Timer,
  TrendCharts,
} from "@element-plus/icons-vue";

// 图标映射
const iconMap = {
  MagicStick,
  EditPen,
  Platform,
  Upload,
  Document
};
import {
  getDashboardStats,
  getCreationTrend,
  getPlatformDistribution,
  getCreationType,
  getRecentActivities,
  getHotTags,
} from "@/api/dashboard";

const router = useRouter();

// 加载状态
const loading = ref(true);

// 统计数据
const stats = ref({
  totalMaterials: 0,
  totalCreations: 0,
  aiGenerations: 0,
  platformAdapts: 0,
});

// 图表引用
const trendChartRef = ref(null);
const platformChartRef = ref(null);
const typeChartRef = ref(null);

// 图表实例
let trendChart = null;
let platformChart = null;
let typeChart = null;

// 热门标签
const hotTags = ref([]);

// 最近活动
const recentActivities = ref([]);

// 图表数据
const chartData = ref({
  trend: {
    xAxis: ["1月", "2月", "3月", "4月", "5月", "6月"],
    data: [0, 0, 0, 0, 0, 0],
  },
  platform: [
    { value: 0, name: "抖音" },
    { value: 0, name: "小红书" },
    { value: 0, name: "微信" },
    { value: 0, name: "B站" },
  ],
  type: {
    xAxis: ["文案", "方案", "教程", "分析", "指南"],
    data: [0, 0, 0, 0, 0],
  },
});

// 快捷操作
const handleCreateTopic = () => {
  router.push("/ai/topics");
};

const handleCreateContent = () => {
  router.push("/ai/content");
};

const handlePlatformAdapt = () => {
  router.push("/adapter");
};

const handleUploadMaterial = () => {
  router.push("/materials");
};

// 标签点击
const handleTagClick = (tag) => {
  console.log("点击标签:", tag);
  // 实际项目中可以根据标签筛选内容
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await getDashboardStats();
    stats.value = res.data;
  } catch (error) {
    ElMessage.error("获取统计数据失败");
    console.error("获取统计数据失败:", error);
  }
};

// 获取创作趋势数据
const fetchTrendData = async () => {
  try {
    const res = await getCreationTrend();
    chartData.value.trend = res.data;
  } catch (error) {
    console.error("获取创作趋势数据失败:", error);
  }
};

// 获取平台分布数据
const fetchPlatformData = async () => {
  try {
    const res = await getPlatformDistribution();
    chartData.value.platform = res.data;
  } catch (error) {
    console.error("获取平台分布数据失败:", error);
  }
};

// 获取创作类型数据
const fetchTypeData = async () => {
  try {
    const res = await getCreationType();
    chartData.value.type = res.data;
  } catch (error) {
    console.error("获取创作类型数据失败:", error);
  }
};

// 获取最近活动
const fetchRecentActivities = async () => {
  try {
    const res = await getRecentActivities();
    recentActivities.value = res.data;
  } catch (error) {
    console.error("获取最近活动失败:", error);
  }
};

// 获取热门标签
const fetchHotTags = async () => {
  try {
    const res = await getHotTags();
    hotTags.value = res.data;
  } catch (error) {
    console.error("获取热门标签失败:", error);
  }
};

// 初始化图表
const initCharts = () => {
  // 确保DOM元素存在
  if (!trendChartRef.value && !platformChartRef.value && !typeChartRef.value) {
    console.error("图表容器不存在");
    return;
  }

  // 创作趋势图表
  if (trendChartRef.value) {
    try {
      trendChart = echarts.init(trendChartRef.value);
      const trendOption = {
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            return `${params[0].name}<br/>${params[0].seriesName}: ${params[0].value} 篇`;
          },
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          borderColor: "#409EFF",
          borderWidth: 1,
          textStyle: {
            color: "#333",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: chartData.value.trend.xAxis || [],
          axisLine: {
            lineStyle: {
              color: "#999",
            },
          },
          axisLabel: {
            color: "#666",
          },
        },
        yAxis: {
          type: "value",
          axisLine: {
            show: false,
          },
          axisLabel: {
            color: "#666",
          },
          splitLine: {
            lineStyle: {
              color: "#f0f0f0",
            },
          },
        },
        series: [
          {
            name: "创作数",
            type: "line",
            data: chartData.value.trend.data || [],
            smooth: true,
            symbol: "circle",
            symbolSize: 8,
            lineStyle: {
              color: "#409EFF",
              width: 3,
            },
            itemStyle: {
              color: "#409EFF",
              borderColor: "#fff",
              borderWidth: 2,
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: "rgba(64, 158, 255, 0.5)",
                },
                {
                  offset: 1,
                  color: "rgba(64, 158, 255, 0.1)",
                },
              ]),
            },
            emphasis: {
              itemStyle: {
                color: "#409EFF",
                borderColor: "#fff",
                borderWidth: 3,
                shadowBlur: 10,
                shadowColor: "rgba(64, 158, 255, 0.5)",
              },
            },
          },
        ],
      };
      trendChart.setOption(trendOption);
      trendChart.on("click", handleChartClick);
      trendChart.on("mouseover", handleChartMouseOver);
    } catch (error) {
      console.error("初始化创作趋势图表失败:", error);
    }
  }

  // 平台分布图表
  if (platformChartRef.value) {
    try {
      platformChart = echarts.init(platformChartRef.value);
      const platformOption = {
        tooltip: {
          trigger: "item",
          formatter: "{b}: {c} ({d}%)",
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          borderColor: "#67C23A",
          borderWidth: 1,
          textStyle: {
            color: "#333",
          },
        },
        legend: {
          orient: "vertical",
          left: "left",
          textStyle: {
            color: "#666",
          },
        },
        series: [
          {
            name: "平台分布",
            type: "pie",
            radius: ["40%", "70%"],
            center: ["60%", "50%"],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: "#fff",
              borderWidth: 2,
            },
            label: {
              show: false,
              position: "center",
            },
            emphasis: {
              label: {
                show: true,
                fontSize: "18",
                fontWeight: "bold",
                color: "#333",
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            labelLine: {
              show: false,
            },
            data: chartData.value.platform || [],
          },
        ],
      };
      platformChart.setOption(platformOption);
      platformChart.on("click", handleChartClick);
      platformChart.on("mouseover", handleChartMouseOver);
    } catch (error) {
      console.error("初始化平台分布图表失败:", error);
    }
  }

  // 创作类型图表
  if (typeChartRef.value) {
    try {
      typeChart = echarts.init(typeChartRef.value);
      const typeOption = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
          formatter: function (params) {
            return `${params[0].name}<br/>${params[0].seriesName}: ${params[0].value} 篇`;
          },
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          borderColor: "#E6A23C",
          borderWidth: 1,
          textStyle: {
            color: "#333",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: chartData.value.type.xAxis || [],
          axisLine: {
            lineStyle: {
              color: "#999",
            },
          },
          axisLabel: {
            color: "#666",
            rotate: 30,
          },
        },
        yAxis: {
          type: "value",
          axisLine: {
            show: false,
          },
          axisLabel: {
            color: "#666",
          },
          splitLine: {
            lineStyle: {
              color: "#f0f0f0",
            },
          },
        },
        series: [
          {
            name: "数量",
            type: "bar",
            data: chartData.value.type.data || [],
            barWidth: "60%",
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {
                  offset: 0,
                  color: "#67C23A",
                },
                {
                  offset: 1,
                  color: "#85ce61",
                },
              ]),
              borderRadius: [4, 4, 0, 0],
            },
            emphasis: {
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  {
                    offset: 0,
                    color: "#85ce61",
                  },
                  {
                    offset: 1,
                    color: "#a9e388",
                  },
                ]),
              },
            },
          },
        ],
      };
      typeChart.setOption(typeOption);
      typeChart.on("click", handleChartClick);
      typeChart.on("mouseover", handleChartMouseOver);
    } catch (error) {
      console.error("初始化创作类型图表失败:", error);
    }
  }
};

// 更新图表数据
const updateCharts = () => {
  if (trendChart) {
    trendChart.setOption({
      xAxis: {
        data: chartData.value.trend.xAxis,
      },
      series: [
        {
          data: chartData.value.trend.data,
        },
      ],
    });
  }

  if (platformChart) {
    platformChart.setOption({
      series: [
        {
          data: chartData.value.platform,
        },
      ],
    });
  }

  if (typeChart) {
    typeChart.setOption({
      xAxis: {
        data: chartData.value.type.xAxis,
      },
      series: [
        {
          data: chartData.value.type.data,
        },
      ],
    });
  }
};

// 加载所有数据
const loadAllData = async () => {
  loading.value = true;
  try {
    // 并行请求所有数据
    await Promise.all([
      fetchStats(),
      fetchTrendData(),
      fetchPlatformData(),
      fetchTypeData(),
      fetchRecentActivities(),
      fetchHotTags(),
    ]);
    // 确保DOM已经渲染完成
    setTimeout(() => {
      // 初始化或更新图表
      if (trendChart || platformChart || typeChart) {
        updateCharts();
      } else {
        initCharts();
      }
    }, 100);
  } catch (error) {
    ElMessage.error("数据加载失败");
    console.error("数据加载失败:", error);
  } finally {
    loading.value = false;
  }
};

// 刷新数据
const refreshData = () => {
  loadAllData();
};

// 图表点击事件
const handleChartClick = (params) => {
  console.log("图表点击:", params);
  // 实际项目中可以根据点击的数据进行相应操作
};

// 图表鼠标悬停事件
const handleChartMouseOver = (params) => {
  console.log("图表鼠标悬停:", params);
  // 可以添加自定义的提示信息
};

// 监听窗口大小变化
const handleResize = () => {
  trendChart?.resize();
  platformChart?.resize();
  typeChart?.resize();
};

onMounted(() => {
  // 加载数据
  loadAllData();
  // 监听窗口大小变化
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  // 销毁图表实例
  trendChart?.dispose();
  platformChart?.dispose();
  typeChart?.dispose();
  // 移除事件监听
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

/* 快捷操作 */
.quick-actions {
  margin-bottom: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 10px;
  height: 100px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

/* 统计卡片 */
.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-value {
  transform: scale(1.05);
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

/* 图表 */
.chart-card {
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.chart-container {
  width: 100%;
  height: 300px;
}

/* 最近活动 */
.recent-activities {
  transition: all 0.3s ease;
}

.recent-activities:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background-color: #f5f7fa;
}

.activity-icon {
  font-size: 20px;
  margin-top: 2px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: #999;
}

/* 热门标签 */
.hot-tags {
  transition: all 0.3s ease;
}

.hot-tags:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 10px 0;
}

.tag-item {
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 6px 12px;
  font-size: 14px;
}

.tag-item:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .el-row {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .el-col {
    padding-left: 10px !important;
    padding-right: 10px !important;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .action-btn {
    padding: 15px 10px;
    height: 90px;
  }

  .chart-container {
    height: 250px;
  }

  .activity-item {
    padding: 8px;
  }

  .tag-cloud {
    gap: 8px;
  }

  .tag-item {
    font-size: 12px;
    padding: 4px 8px;
  }

  .stat-content {
    gap: 10px;
  }

  .stat-icon {
    font-size: 36px;
  }

  .stat-value {
    font-size: 24px;
  }

  .stat-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 5px;
  }

  .quick-actions {
    margin-bottom: 10px;
  }

  .el-card {
    margin-bottom: 10px;
  }

  .chart-container {
    height: 200px;
  }

  .activity-title {
    font-size: 12px;
  }

  .activity-time {
    font-size: 10px;
  }

  .tag-item {
    font-size: 10px;
    padding: 2px 6px;
  }

  .stat-icon {
    font-size: 28px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 10px;
  }
}
</style>
