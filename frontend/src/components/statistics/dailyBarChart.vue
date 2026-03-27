<template>
  <div class="chart-container" ref="chartRef"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import { getDailyStats } from '@/api/statistics';

const props = defineProps({
  startDate: { type: String, required: true },
  endDate: { type: String, required: true }
});

const chartRef = ref(null);
let myChart = null;

const fetchData = async () => {
  try {
    // 直接调用项目封装好的接口，自动带 Token
    const res = await getDailyStats({
      start_date: props.startDate,
      end_date: props.endDate
    });
    renderChart(res.data);
  } catch (error) {
    console.error('获取每日统计失败:', error);
  }
};

const renderChart = (data) => {
  if (!myChart) {
    myChart = echarts.init(chartRef.value);
  }

  const xAxisData = data.map(item => item.date) || [];
  const seriesData = data.map(item => item.count) || [];

  const option = {
    title: { text: '每日创作数量统计', left: 'center' },
    tooltip: { trigger: 'axis', formatter: '{b}：{c} 篇' },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLabel: { rotate: 30 }
    },
    yAxis: { type: 'value', name: '创作数量（篇）', min: 0 },
    series: [{
      name: '创作数',
      type: 'bar',
      data: seriesData,
      itemStyle: { color: '#409EFF' },
      barWidth: '60%'
    }]
  };

  myChart.setOption(option);
};

onMounted(() => {
  fetchData();
  window.addEventListener('resize', () => myChart?.resize());
});

watch([() => props.startDate, () => props.endDate], () => {
  fetchData();
});

onUnmounted(() => {
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }
  window.removeEventListener('resize', () => myChart?.resize());
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
  background: #fff;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>
