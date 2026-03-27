<template>
  <el-table :data="keywords" border stripe>
    <el-table-column prop="keyword" label="关键词" />
    <el-table-column prop="count" label="出现次数" />
    <el-table-column prop="count" label="占比" width="100">
      <template #default="scope">
        {{ totalCount > 0 ? (scope.row.count / totalCount * 100).toFixed(1) + '%' : '0%' }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { computed, defineProps } from 'vue';

// 接收父组件传的真实数据
const props = defineProps({
  keywords: {
    type: Array,
    required: true,
    default: () => []
  },
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' }
});

// 计算总次数（用于占比）
const totalCount = computed(() => {
  return props.keywords.reduce((sum, item) => sum + item.count, 0);
});
</script>
