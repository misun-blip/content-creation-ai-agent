<template>
  <el-card class="preview-panel">
    <template #header>
      <div class="panel-header">
        <span>预览效果</span>
        <el-button-group v-if="adaptedResult">
          <el-button 
            size="small" 
            @click="handleCopy"
            :icon="DocumentCopy"
          >
            复制
          </el-button>
          <el-dropdown @command="handleExport" trigger="click">
            <el-button size="small" :icon="Download">
              导出
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="txt">
                  <el-icon><Document /></el-icon>
                  纯文本 (TXT)
                </el-dropdown-item>
                <el-dropdown-item command="md">
                  <el-icon><EditPen /></el-icon>
                  Markdown (MD)
                </el-dropdown-item>
                <el-dropdown-item command="json">
                  <el-icon><DataAnalysis /></el-icon>
                  JSON
                </el-dropdown-item>
                <el-dropdown-item command="html">
                  <el-icon><Monitor /></el-icon>
                  HTML
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </template>
    
    <div v-if="adaptedResult" class="preview-content">
      <div class="preview-section">
        <div class="preview-title">
          <el-icon><EditPen /></el-icon>
          <span class="label">标题</span>
        </div>
        <div class="preview-value">{{ adaptedResult.title }}</div>
      </div>
      
      <el-divider />
      
      <div class="preview-section">
        <div class="preview-title">
          <el-icon><Document /></el-icon>
          <span class="label">正文</span>
        </div>
        <div class="preview-value preview-body">{{ adaptedResult.content }}</div>
      </div>
      
      <el-divider v-if="adaptedResult.tags && adaptedResult.tags.length > 0" />
      
      <div 
        v-if="adaptedResult.tags && adaptedResult.tags.length > 0" 
        class="preview-section"
      >
        <div class="preview-title">
          <el-icon><PriceTag /></el-icon>
          <span class="label">标签</span>
        </div>
        <div class="preview-value">
          <el-tag
            v-for="(tag, index) in adaptedResult.tags"
            :key="index"
            type="info"
            class="tag-item"
            size="small"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
      
      <el-divider />
      
      <div v-if="adaptedResult.warnings && adaptedResult.warnings.length > 0" class="preview-section">
        <div class="preview-title warning-title">
          <el-icon><WarningFilled /></el-icon>
          <span class="label">警告</span>
        </div>
        <div class="preview-value">
          <el-alert
            v-for="(warning, index) in adaptedResult.warnings"
            :key="index"
            type="warning"
            :closable="false"
            class="warning-item"
            show-icon
          >
            {{ warning }}
          </el-alert>
        </div>
      </div>
      
      <div v-if="adaptedResult.suggestions && adaptedResult.suggestions.length > 0" class="preview-section">
        <div class="preview-title suggestion-title">
          <el-icon><InfoFilled /></el-icon>
          <span class="label">建议</span>
        </div>
        <div class="preview-value">
          <el-alert
            v-for="(suggestion, index) in adaptedResult.suggestions"
            :key="index"
            type="info"
            :closable="false"
            class="suggestion-item"
            show-icon
          >
            {{ suggestion }}
          </el-alert>
        </div>
      </div>
      
      <el-divider />
      
      <div class="preview-section">
        <div class="preview-title">
          <el-icon><View /></el-icon>
          <span class="label">完整预览</span>
        </div>
        <div class="preview-value preview-full">
          {{ adaptedResult.preview }}
        </div>
      </div>
      
      <el-divider v-if="originalImages && originalImages.length > 0" />

      <div v-if="originalImages && originalImages.length > 0" class="preview-section">
        <div class="preview-title">
          <el-icon><Picture /></el-icon>
          <span class="label">附带配图 (AI 生成或知识库素材)</span>
        </div>
        <div class="image-gallery">
          <el-row :gutter="10">
            <el-col :span="8" v-for="(img, index) in originalImages" :key="index">
              <el-card shadow="hover" :body-style="{ padding: '0px' }" class="image-card">
                <el-image 
                  :src="img.url" 
                  fit="cover" 
                  class="preview-image"
                  :preview-src-list="originalImages.map(i => i.url)"
                  :initial-index="index"
                >
                  <template #placeholder>
                    <div class="image-slot">加载中...</div>
                  </template>
                </el-image>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
    
    <el-empty 
      v-else 
      description="暂无预览内容" 
      :image-size="200"
    >
      <template #description>
        <p class="empty-text">请输入内容并点击"一键适配"按钮</p>
        <p class="empty-tip">适配后的内容将显示在这里</p>
      </template>
    </el-empty>
  </el-card>
</template>

<script setup>
import { computed } from 'vue';
import { useAdapterStore } from '@/stores/adapter';
import { ElMessage } from 'element-plus';
import { 
  DocumentCopy, 
  Download, 
  EditPen, 
  Document, 
  PriceTag, 
  WarningFilled, 
  InfoFilled, 
  View,
  ArrowDown,
  DataAnalysis,
  Monitor,
  Picture
} from '@element-plus/icons-vue';

const adapterStore = useAdapterStore();

const adaptedResult = computed(() => adapterStore.adaptedResult);
const originalImages = computed(() => adapterStore.originalImages);

const handleCopy = () => {
  if (!adaptedResult.value) return;
  
  const text = `${adaptedResult.value.title}\n\n${adaptedResult.value.content}\n\n${(adaptedResult.value.tags || []).join(' ')}`;
  
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制');
  });
};

const handleExport = (format) => {
  if (!adaptedResult.value) return;
  
  const result = adaptedResult.value;
  const timestamp = Date.now();
  const platform = adapterStore.selectedPlatform;
  
  let content, filename, mimeType;
  
  switch (format) {
    case 'txt':
      content = `${result.title}\n\n${result.content}\n\n${(result.tags || []).join(' ')}`;
      filename = `content_${platform}_${timestamp}.txt`;
      mimeType = 'text/plain;charset=utf-8';
      break;
      
    case 'md':
      content = `# ${result.title}\n\n${result.content}\n\n${(result.tags || []).map(tag => `**${tag}**`).join(' ')}`;
      filename = `content_${platform}_${timestamp}.md`;
      mimeType = 'text/markdown;charset=utf-8';
      break;
      
    case 'json':
      content = JSON.stringify(result, null, 2);
      filename = `content_${platform}_${timestamp}.json`;
      mimeType = 'application/json;charset=utf-8';
      break;
      
    case 'html':
      content = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${result.title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      line-height: 1.6;
    }
    h1 {
      color: #333;
      border-bottom: 2px solid #eee;
      padding-bottom: 10px;
    }
    .content {
      color: #555;
      white-space: pre-wrap;
    }
    .tags {
      margin-top: 20px;
    }
    .tag {
      display: inline-block;
      background: #f0f0f0;
      padding: 4px 12px;
      margin: 4px;
      border-radius: 12px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <h1>${result.title}</h1>
  <div class="content">${result.content}</div>
  <div class="tags">
    ${(result.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('')}
  </div>
</body>
</html>`;
      filename = `content_${platform}_${timestamp}.html`;
      mimeType = 'text/html;charset=utf-8';
      break;
      
    default:
      ElMessage.error('不支持的导出格式');
      return;
  }
  
  try {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    
    ElMessage.success(`已导出为 ${format.toUpperCase()} 格式`);
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败，请重试');
  }
};
</script>

<style scoped>
.preview-panel {
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-content {
  padding: 20px;
}

.preview-section {
  margin-bottom: 20px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.preview-title .el-icon {
  color: #409eff;
}

.preview-title .label {
  color: #606266;
}

.preview-value {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.preview-body {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #333;
  font-size: 14px;
}

.preview-full {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #606266;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  background-color: #f9f9f9;
  border-radius: 6px;
  border-left: 3px solid #909399;
}

.tag-item {
  margin: 5px;
}

.warning-item,
.suggestion-item {
  margin-bottom: 10px;
}

.warning-title {
  color: #e6a23c;
}

.warning-title .el-icon {
  color: #e6a23c;
}

.suggestion-title {
  color: #409eff;
}

.suggestion-title .el-icon {
  color: #409eff;
}

.empty-text {
  color: #909399;
  margin-bottom: 8px;
}

.empty-tip {
  color: #c0c4cc;
  font-size: 13px;
}

.image-gallery {
  margin-top: 10px;
}
.image-card {
  border-radius: 6px;
  overflow: hidden;
  height: 150px;
  border: none;
  background-color: #f5f7fa;
}
.preview-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s;
}
.preview-image:hover {
  transform: scale(1.05);
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-content {
    padding: 10px;
  }
  
  .preview-title {
    font-size: 13px;
  }
  
  .preview-value {
    padding: 8px;
    font-size: 13px;
  }
}
</style>
