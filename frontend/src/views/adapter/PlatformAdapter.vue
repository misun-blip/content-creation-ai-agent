<template>
  <div class="platform-adapter">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="8" :lg="8">
        <PlatformSelector />
        <ContentEditor @adapt="handleAdapt" />
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <PreviewPanel />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import PlatformSelector from '@/components/adapter/PlatformSelector.vue';
import ContentEditor from '@/components/adapter/ContentEditor.vue';
import PreviewPanel from '@/components/adapter/PreviewPanel.vue';
import { ElMessage } from 'element-plus';

const handleAdapt = (result) => {
  console.log('适配结果:', result);
  
  // 显示成功提示
  if (result.warnings && result.warnings.length > 0) {
    ElMessage.warning({
      message: '适配成功，但存在警告',
      duration: 3000
    });
  } else {
    ElMessage.success({
      message: '适配成功',
      duration: 2000
    });
  }
};
</script>

<style scoped>
.platform-adapter {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background-color: #f5f5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .platform-adapter {
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .platform-adapter {
    padding: 5px;
  }
}
</style>
