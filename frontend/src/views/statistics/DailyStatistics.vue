<template>
  <div class="daily-statistics">
    <el-card class="page-header">
      <template #header>
        <h2>统计分析</h2>
      </template>
      <p class="page-desc">查看你的创作数据和统计分析（基于真实创作记录）</p>
    </el-card>

    <el-card class="filter-form">
      <div class="filter-content">
        <el-select
          v-model="timeRange"
          placeholder="选择时间范围"
          style="width: 150px; margin-right: 10px"
          @change="handleTimeRangeChange"
        >
          <el-option label="今日" value="today" />
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
          <el-option label="本年" value="year" />
          <el-option label="自定义" value="custom" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 250px; margin-right: 10px"
          v-if="timeRange === 'custom'"
        />
        <el-button type="primary" plain @click="handleSearch">
          <el-icon><Search /></el-icon>
          刷新数据
        </el-button>
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>每日创作数量</h3>
          </template>
          <div class="chart-container">
            <div id="creationChart" style="width: 100%; height: 300px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>创作平台分布</h3>
          </template>
          <div class="chart-container">
            <div id="platformChart" style="width: 100%; height: 300px"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>创作类型分布</h3>
          </template>
          <div class="chart-container">
            <div id="typeChart" style="width: 100%; height: 300px"></div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <h3>热门关键词</h3>
          </template>
          <div class="table-container">
            <KeywordTable 
              :keywords="keywordList"
              :start-date="dateRange[0] || formatDate(new Date())" 
              :end-date="dateRange[1] || formatDate(new Date())" 
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="stats-summary" style="margin-top: 20px">
      <template #header>
        <h3>数据概览</h3>
      </template>
      <div class="summary-grid">
        <div class="summary-item">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-content">
              <el-icon class="summary-icon" color="#409EFF"
                ><Document
              /></el-icon>
              <div class="summary-info">
                <div class="summary-value">{{ totalCreations }}</div>
                <div class="summary-label">总创作数</div>
              </div>
            </div>
          </el-card>
        </div>
        <div class="summary-item">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-content">
              <el-icon class="summary-icon" color="#67C23A"
                ><Calendar
              /></el-icon>
              <div class="summary-info">
                <div class="summary-value">{{ todayCreations }}</div>
                <div class="summary-label">今日创作</div>
              </div>
            </div>
          </el-card>
        </div>
        <div class="summary-item">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-content">
              <el-icon class="summary-icon" color="#E6A23C"><Timer /></el-icon>
              <div class="summary-info">
                <div class="summary-value">{{ avgCreationTime }}分钟</div>
                <div class="summary-label">平均创作时长</div>
              </div>
            </div>
          </el-card>
        </div>
        <div class="summary-item">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-content">
              <el-icon class="summary-icon" color="#F56C6C"
                ><TrendCharts
              /></el-icon>
              <div class="summary-info">
                <div class="summary-value">{{ totalWords }}字</div>
                <div class="summary-label">总字数</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import * as echarts from 'echarts';
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, Download, Document, Calendar, Timer, TrendCharts } from '@element-plus/icons-vue';
import { getDailyStats, getPlatformStats, getTypeStats, getKeywordStats, getTotalWords, getAvgTime, exportReport } from '@/api/statistics';
import { downloadBlob } from '@/utils/download';
import KeywordTable from '@/components/Statistics/KeywordTable.vue';

// 响应式数据（全部基于真实记录）
const timeRange = ref('month');
const dateRange = ref([]);
const totalCreations = ref(0);
const todayCreations = ref(0);
const avgCreationTime = ref(1); // 若需真实值，需后端补充record的耗时字段
const totalWords = ref(0); // 若需真实值，需后端统计content字数
const keywordList = ref([]); // 真实关键词列表

// 图表实例（避免内存泄漏）
let creationChart = null;
let platformChart = null;
let typeChart = null;

// 工具函数：格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

// 核心修改：时间范围处理（实时计算，不再固定2026-02-24）
const handleTimeRangeChange = () => {
  const now = new Date(); // 实时当前时间
  let startDate = '';
  let endDate = formatDate(now); // 截止到今天
  
  switch (timeRange.value) {
    case 'today':
      // 今日：0点到现在
      startDate = endDate = formatDate(now);
      break;
    case 'week':
      // 本周：周一到周日（实时）
      const weekDay = now.getDay() || 7; // 周日返回7
      const monday = new Date(now);
      monday.setDate(now.getDate() - weekDay + 1);
      startDate = formatDate(monday);
      endDate = formatDate(now);
      break;
    case 'month':
      // 本月：1号到现在
      const monthFirstDay = new Date(now.getFullYear(), now.getMonth(), 1);
      startDate = formatDate(monthFirstDay);
      endDate = formatDate(now);
      break;
    case 'year':
      // 本年：1月1号到现在
      const yearFirstDay = new Date(now.getFullYear(), 0, 1);
      startDate = formatDate(yearFirstDay);
      endDate = formatDate(now);
      break;
    case 'custom':
      return;
  }
  
  if (startDate && endDate) {
    dateRange.value = [startDate, endDate];
  }
};

const initCreationChart = (dailyData) => {
  if (creationChart) {
    creationChart.dispose();
  }
  
  const chartDom = document.getElementById('creationChart');
  if (!chartDom) return;
  
  creationChart = echarts.init(chartDom);
  const xData = Object.keys(dailyData || {});
  const yData = Object.values(dailyData || {});
  
  // 1. 总创作数/今日创作数：统计篇数（动态）
  totalCreations.value = yData.reduce((sum, val) => sum + val, 0);
  // 今日创作数：取实时今天的日期对应数据
  todayCreations.value = dailyData[formatDate(new Date())] || 0;
  
  creationChart.setOption({
    title: { text: '每日创作数量（篇）', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { 
      type: 'category', 
      data: xData,
      axisLabel: { rotate: 30 }
    },
    yAxis: { type: 'value', min: 0, integer: true }, // 篇数是整数
    series: [{
      name: '创作篇数',
      type: 'bar',
      data: yData,
      itemStyle: { color: '#409EFF' }
    }]
  });
  
  window.addEventListener('resize', () => creationChart.resize());
};

// 初始化平台分布图表（真实数据 + 中文映射）
const initPlatformChart = (platformData) => {
  if (platformChart) {
    platformChart.dispose();
  }
  
  const chartDom = document.getElementById('platformChart');
  if (!chartDom) return;
  
  platformChart = echarts.init(chartDom);
  
  // 关键：在这里做英文到中文的映射
  const platformMap = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "wechat": "微信",
    "general": "通用",
    "未分类": "未分类"
  };
  
  const pieData = platformData.map(item => ({ 
    name: platformMap[item.platform] || item.platform, // 替换为中文
    value: item.count 
  }));
  
  platformChart.setOption({
    title: { text: '创作平台分布', left: 'center' },
    tooltip: { 
      trigger: 'item', 
      formatter: '{b}: {c} 条 ({d}%)' 
    },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      name: '平台数量',
      type: 'pie',
      radius: ['40%', '70%'],
      data: pieData,
      label: { show: true, formatter: '{b}: {c}条' }
    }]
  });
  
  window.addEventListener('resize', () => platformChart.resize());
};

// 初始化创作类型图表（真实数据）
const initTypeChart = (typeData) => {
  if (typeChart) {
    typeChart.dispose();
  }
  
  const chartDom = document.getElementById('typeChart');
  if (!chartDom) return;
  
  typeChart = echarts.init(chartDom);
  const pieData = typeData.map(item => ({ 
    name: item.type || '未分类', 
    value: item.count 
  }));
  
  typeChart.setOption({
    title: { text: '创作类型分布', left: 'center' },
    tooltip: { 
      trigger: 'item', 
      formatter: '{b}: {c} 条 ({d}%)' 
    },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      name: '类型数量',
      type: 'pie',
      radius: ['40%', '70%'],
      data: pieData,
      label: { show: true, formatter: '{b}: {c}条' }
    }]
  });
  
  window.addEventListener('resize', () => typeChart.resize());
};

// 获取所有真实统计数据（实时参数）
const fetchAllStats = async () => {
  try {
    // 核心修改：强制使用一个能覆盖你所有记录的时间范围
    const params = { 
      start_date: "2026-02-01", // 覆盖你最早的记录
      end_date: formatDate(new Date()) // 到今天
    };

    // 1. 每日创作篇数
    const dailyRes = await getDailyStats(params);
    if (dailyRes && dailyRes.code === 200) {
      initCreationChart(dailyRes.data);
    }

    // 2. 单独请求真实总字数
    try {
      const wordCountRes = await getTotalWords(params);
      if (wordCountRes && wordCountRes.code === 200) {
        totalWords.value = wordCountRes.data;
      } else {
        totalWords.value = 0;
      }
    } catch {
      totalWords.value = 0;
      ElMessage.error('获取总字数失败');
    }

    // 3. 平台分布（动态篇数）
    const platformRes = await getPlatformStats(params);
    if (platformRes && platformRes.code === 200) {
      initPlatformChart(platformRes.data);
    }

    // 4. 创作类型（动态篇数）
    const typeRes = await getTypeStats(params);
    if (typeRes && typeRes.code === 200) {
      initTypeChart(typeRes.data);
    }

    // 5. 关键词
    const keywordRes = await getKeywordStats(params);
    if (keywordRes && keywordRes.code === 200) {
      keywordList.value = keywordRes.data;
    }

    // 6. 获取真实平均创作时长
    try {
      const avgTimeRes = await getAvgTime(params);
      if (avgTimeRes && avgTimeRes.code === 200) {
        avgCreationTime.value = avgTimeRes.data;
      } else {
        avgCreationTime.value = 1;
      }
    } catch {
      avgCreationTime.value = 1;
      ElMessage.error('获取平均创作时长失败');
    }

    ElMessage.success('实时创作数据加载成功');
  } catch (error) {
    console.error('统计数据获取失败：', error);
    ElMessage.error('加载实时数据失败，请检查后端接口');
  }
};

// 刷新数据
const handleSearch = () => {
  fetchAllStats();
};

// 导出报告（实时参数）
const handleExport = async () => {
  try {
    // 核心修改：导出参数也用实时时间范围
    const params = {
      start_date: dateRange.value[0] || formatDate(new Date(new Date().getFullYear(), new Date().getMonth(), 1)),
      end_date: dateRange.value[1] || formatDate(new Date())
    };

    // 调用统计API导出接口
    const response = await exportReport(params);

    // 触发浏览器下载
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data]);
    downloadBlob(blob, `创作统计报告_${formatDate(new Date())}.csv`);

    ElMessage.success('报告导出成功');
  } catch (error) {
    console.error('导出失败：', error);
    ElMessage.error('导出报告失败');
  }
};

// 生命周期钩子
onMounted(() => {
  handleTimeRangeChange(); // 初始化实时时间范围
  fetchAllStats();
  console.log("统计分析页面（实时数据模式）加载完成");
});

onUnmounted(() => {
  // 销毁图表实例，避免内存泄漏
  creationChart?.dispose();
  platformChart?.dispose();
  typeChart?.dispose();
});
</script>

<style scoped>
.daily-statistics {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-desc {
  color: #999;
  margin-top: 5px;
}

.filter-form {
  margin-bottom: 20px;
}

.filter-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.stats-card {
  margin-bottom: 20px;
}

.chart-container {
  position: relative;
  height: 300px;
  background-color: #f9f9f9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.table-container {
  padding: 10px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.summary-item {
  transition: all 0.3s;
}

.summary-item:hover {
  transform: translateY(-5px);
}

.summary-card {
  height: 100%;
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.summary-icon {
  font-size: 48px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-content > * {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .el-row {
    display: flex;
    flex-direction: column;
  }

  .el-col {
    width: 100% !important;
  }
}
</style>
