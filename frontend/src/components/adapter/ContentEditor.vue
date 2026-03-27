<template>
  <el-card class="content-editor">
    <template #header>
      <div class="card-header">
        <span>内容编辑</span>
        <el-button 
          type="text" 
          size="small" 
          @click="handleClear"
          :disabled="!hasContent"
        >
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </template>
    
    <el-form :model="formData" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="请输入标题（可选）"
          maxlength="30"
          show-word-limit
          clearable
          @input="handleTitleInput"
        >
          <template #prefix>
            <el-icon><EditPen /></el-icon>
          </template>
        </el-input>
        <div v-if="selectedPlatformConfig" class="form-tip">
          <el-text size="small" type="info">
            {{ selectedPlatformConfig.title.tips }}
          </el-text>
        </div>
      </el-form-item>
      
      <el-form-item label="正文" prop="content">
        <el-input
          v-model="formData.content"
          type="textarea"
          :rows="10"
          placeholder="请输入正文内容"
          @input="handleContentChange"
          show-word-limit
          :maxlength="selectedPlatformConfig?.content?.max_length || 2000"
        >
          <template #prefix>
            <el-icon><Document /></el-icon>
          </template>
        </el-input>
        <div v-if="selectedPlatformConfig" class="form-tip">
          <el-text size="small" type="info">
            {{ selectedPlatformConfig.content.tips }}
          </el-text>
        </div>
      </el-form-item>
      
      <el-form-item 
        v-if="selectedPlatformConfig?.tags?.max_count > 0" 
        label="标签"
        prop="tags"
      >
        <el-select
          v-model="formData.tags"
          multiple
          filterable
          allow-create
          placeholder="请选择或输入标签"
          style="width: 100%"
          :max-collapse-tags="selectedPlatformConfig.tags.max_count"
        >
          <el-option
            v-for="tag in commonTags"
            :key="tag"
            :label="tag"
            :value="tag"
          />
        </el-select>
        <div class="form-tip">
          <el-text size="small" type="info">
            {{ selectedPlatformConfig.tags.tips }}
          </el-text>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          @click="handleAdapt"
          :loading="loading"
          :disabled="!hasContent"
          style="width: 100%"
          size="large"
        >
          <el-icon><MagicStick /></el-icon>
          {{ loading ? '适配中...' : '一键适配' }}
        </el-button>
        <el-button
          @click="handleReset"
          :disabled="!hasContent"
          size="large"
        >
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useAdapterStore } from '@/stores/adapter';
import { ElMessage } from 'element-plus';
import { 
  EditPen, 
  Document, 
  Delete, 
  MagicStick, 
  RefreshLeft 
} from '@element-plus/icons-vue';

const emit = defineEmits(['adapt']);

const adapterStore = useAdapterStore();

const formRef = ref(null);

const formData = reactive({
  title: '',
  content: '',
  tags: []
});

const loading = computed(() => adapterStore.loading);

const selectedPlatformConfig = computed(() => adapterStore.selectedPlatformConfig);

const hasContent = computed(() => {
  return formData.title.trim() || formData.content.trim();
});

const commonTags = [
  '热点', '推荐', '分享', '干货', '教程',
  '生活', '美食', '旅行', '科技', '娱乐',
  '职场', '学习', '成长', '励志', '情感'
];

const rules = {
  content: [
    { 
      required: true, 
      message: '请输入正文内容', 
      trigger: 'blur' 
    },
    {
      min: 1,
      message: '内容不能为空',
      trigger: 'blur'
    }
  ],
};

// 防抖相关变量
let contentDebounceTimer = null;
let titleDebounceTimer = null;
const DEBOUNCE_DELAY = 300; // 防抖延迟时间（毫秒）

const handleContentChange = () => {
  // 清除之前的定时器
  if (contentDebounceTimer) {
    clearTimeout(contentDebounceTimer);
  }
  
  // 设置新的定时器
  contentDebounceTimer = setTimeout(() => {
    adapterStore.setOriginalContent(formData.content);
  }, DEBOUNCE_DELAY);
};

const handleTitleInput = () => {
  // 清除之前的定时器
  if (titleDebounceTimer) {
    clearTimeout(titleDebounceTimer);
  }
  
  // 设置新的定时器（标题输入处理逻辑可以在这里添加）
  titleDebounceTimer = setTimeout(() => {
    // 标题输入时的处理逻辑
    // 例如：实时验证、字数统计等
  }, DEBOUNCE_DELAY);
};

const handleAdapt = async () => {
  if (!formData.content || !formData.content.trim()) {
    ElMessage.warning('请输入正文内容');
    return;
  }
  
  try {
    const result = await adapterStore.adaptContent(
      formData.content,
      adapterStore.selectedPlatform,
      formData.title || null,
      formData.tags || null,
      true
    );
    
    emit('adapt', result);
  } catch (error) {
    ElMessage.error('适配失败: ' + (error.message || '未知错误'));
  }
};

const handleReset = () => {
  formData.title = '';
  formData.content = '';
  formData.tags = [];
  adapterStore.clearAdaptedResult();
  adapterStore.clearError();
  
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

const handleClear = () => {
  handleReset();
  ElMessage.info('已清空表单');
};

onMounted(() => {
  if (adapterStore.originalContent && adapterStore.originalContent.trim()) {
    formData.content = adapterStore.originalContent;
  }
});

// 组件卸载时清除定时器
onUnmounted(() => {
  if (contentDebounceTimer) {
    clearTimeout(contentDebounceTimer);
  }
  if (titleDebounceTimer) {
    clearTimeout(titleDebounceTimer);
  }
});
</script>

<style scoped>
.content-editor {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-top: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .el-button {
    width: 100%;
    margin-bottom: 10px;
  }
}
</style>
