<template>
  <el-card class="platform-selector">
    <template #header>
      <div class="card-header">
        <span>选择平台</span>
        <el-tooltip content="切换平台会清空适配结果" placement="top">
          <el-icon><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </template>
    
    <el-radio-group 
      v-model="selectedPlatform" 
      @change="handlePlatformChange"
      class="platform-buttons"
    >
      <el-radio-button 
        v-for="platform in platforms" 
        :key="platform.code"
        :label="platform.code"
        class="platform-button"
      >
        <el-icon>
          <component :is="getPlatformIcon(platform.code)" />
        </el-icon>
        <span>{{ platform.name }}</span>
      </el-radio-button>
    </el-radio-group>
    
    <el-divider />
    
    <div v-if="selectedPlatformConfig" class="platform-info">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="标题限制">
          <el-tag size="small" type="info">
            最多{{ selectedPlatformConfig.title.max_length }}字符
          </el-tag>
          <el-tag v-if="selectedPlatformConfig.title.emoji_enabled" size="small" type="success">
            支持Emoji
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="正文限制">
          <el-tag size="small" type="info">
            最多{{ selectedPlatformConfig.content.max_length }}字符
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="段落限制">
          <el-tag size="small" type="info">
            每段≤{{ selectedPlatformConfig.content.paragraph_max_length }}字符
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标签数量">
          <el-tag 
            size="small" 
            :type="selectedPlatformConfig.tags.max_count > 0 ? 'success' : 'danger'"
          >
            {{ selectedPlatformConfig.tags.max_count > 0 ? `最多${selectedPlatformConfig.tags.max_count}个` : '不支持' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="封面比例">
          <el-tag size="small" type="info">
            {{ selectedPlatformConfig.cover.ratio }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="平台提示" :span="2">
          <el-text size="small" type="info">
            {{ selectedPlatformConfig.title.tips }}
          </el-text>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-card>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAdapterStore } from '@/stores/adapter';
import { ElMessageBox } from 'element-plus';
import { 
  VideoCamera as DouyinIcon,
  ChatDotRound as XiaohongshuIcon,
  ChatLineSquare as WechatIcon,
  InfoFilled
} from '@element-plus/icons-vue';

const adapterStore = useAdapterStore();

const selectedPlatform = computed({
  get: () => adapterStore.selectedPlatform,
  set: (value) => adapterStore.setPlatform(value)
});

const platforms = computed(() => adapterStore.platforms);

const selectedPlatformConfig = computed(() => {
  return platforms.value.find(p => p.code === selectedPlatform.value);
});

const handlePlatformChange = async (value) => {
  console.log('平台切换:', value);
  
  // 检查是否有适配结果
  if (adapterStore.adaptedResult) {
    try {
      await ElMessageBox.confirm(
        '切换平台将清空当前的适配结果，是否继续？',
        '确认切换',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      );
      // 用户确认，清空适配结果
      adapterStore.clearAdaptedResult();
      adapterStore.setPlatform(value);
    } catch {
      // 用户取消，恢复原来的选择
      console.log('用户取消了平台切换');
      // 不需要做任何操作，因为selectedPlatform的setter没有被调用
    }
  } else {
    // 没有适配结果，直接切换
    adapterStore.setPlatform(value);
  }
};

const getPlatformIcon = (platformCode) => {
  const iconMap = {
    douyin: DouyinIcon,
    xiaohongshu: XiaohongshuIcon,
    wechat: WechatIcon
  };
  return iconMap[platformCode] || InfoFilled;
};

onMounted(() => {
  adapterStore.fetchPlatforms();
});
</script>

<style scoped>
.platform-selector {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
}

.platform-button {
  flex: 1;
  min-width: 120px;
}

.platform-button .el-icon {
  margin-right: 5px;
}

.platform-info {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .platform-buttons {
    flex-direction: column;
  }
  
  .platform-button {
    width: 100%;
  }
}
</style>
