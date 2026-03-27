<template>
  <div class="topic-generate">
    <div class="page-wrap">
      <el-card class="page-header">
        <template #header>
          <h2>选题生成</h2>
        </template>
        <p class="page-desc">输入关键词，让 AI 结合素材库与平台特性生成推荐选题</p>
      </el-card>

    <el-card class="generate-form">
      <el-form :model="generateForm" :rules="rules" ref="formRef">
        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="generateForm.keywords"
            placeholder="输入核心关键词（如：营销、自媒体），多个关键词用逗号分隔"
            type="textarea"
            :rows="3"
          />
          <p class="form-tip">多个关键词用逗号分隔</p>
        </el-form-item>

        <el-form-item label="行业" prop="industry">
          <el-select
            v-model="generateForm.industry"
            placeholder="选择行业"
            filterable
            style="width: 100%"
          >
            <el-option label="科技" value="科技" />
            <el-option label="教育" value="教育" />
            <el-option label="金融" value="金融" />
            <el-option label="医疗" value="医疗" />
            <el-option label="零售" value="零售" />
            <el-option label="美妆" value="美妆" />
            <el-option label="美食" value="美食" />
            <el-option label="旅行" value="旅行" />
            <el-option label="时尚" value="时尚" />
            <el-option label="母婴" value="母婴" />
            <el-option label="游戏" value="游戏" />
            <el-option label="汽车" value="汽车" />
            <el-option label="房产" value="房产" />
            <el-option label="法律" value="法律" />
            <el-option label="电商" value="电商" />
            <el-option label="文化" value="文化" />
            <el-option label="体育" value="体育" />
            <el-option label="其他" value="通用行业" />
          </el-select>
        </el-form-item>

        <el-form-item label="目标平台" prop="platform">
          <el-select
            v-model="generateForm.platform"
            placeholder="选择目标平台"
            filterable
            style="width: 100%"
          >
            <el-option label="抖音" value="douyin" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="微信视频号" value="wechat" />
            <el-option label="全平台通用" value="all" />
          </el-select>
        </el-form-item>

        <el-form-item prop="count">
          <el-slider
            v-model="generateForm.count"
            :min="1"
            :max="10"
            :step="1"
            show-input
            input-size="small"
            style="width: 250px"
          />
          <span style="margin-left: 15px; color: #606266">
            生成 {{ generateForm.count }} 个选题
          </span>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleGenerate"
            :loading="loading"
            style="width: 100%"
          >
            <el-icon style="margin-right: 5px">
              <MagicStick />
            </el-icon>
            {{ loading ? "AI 检索素材并生成中..." : "生成选题" }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="generate-result">
      <template #header>
        <h3>生成结果</h3>
      </template>
      <div v-if="topics.length > 0" class="topics-list">
        <div v-for="(topic, index) in topics" :key="index" class="topic-item">
          <el-card shadow="hover" class="topic-card">
            <div class="topic-header">
              <span class="topic-index">{{ index + 1 }}</span>
              <span class="topic-platform">
                <el-tag size="small" type="success">
                  {{ getPlatformName(topic.platform || generateForm.platform) }}
                </el-tag>
              </span>
            </div>
            <h4 class="topic-title">{{ topic.title }}</h4>
            <p class="topic-desc">{{ topic.description }}</p>
            <div class="topic-actions">
              <el-button size="small" @click="handleCopy(topic.title)">
                <el-icon>
                  <DocumentCopy />
                </el-icon>
                复制标题
              </el-button>
              <el-button
                size="small"
                type="primary"
                plain
                @click="handleGenerateContent(topic)"
              >
                <el-icon>
                  <EditPen />
                </el-icon>
                去写文案
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
      <el-empty
        v-else
        description="暂无结果，请先生成选题"
        :image-size="80"
      />
    </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { MagicStick, DocumentCopy, EditPen } from "@element-plus/icons-vue";
import { generateTopics as apiGenerateTopics } from "@/api/ai";

const router = useRouter();
const formRef = ref(null);
const loading = ref(false);
const topics = ref([]);

const generateForm = reactive({
  keywords: "",
  industry: "",
  platform: "all",
  count: 5,
});

const rules = {
  keywords: [{ required: true, message: "请输入核心关键词", trigger: "blur" }],
  industry: [{ required: true, message: "请选择行业", trigger: "change" }],
  platform: [{ required: true, message: "请选择平台", trigger: "change" }],
};

const getPlatformName = (platform) => {
  const map = {
    douyin: "抖音",
    xiaohongshu: "小红书",
    wechat: "微信视频号",
    all: "全平台通用",
  };
  return map[platform] || platform;
};

const handleCopy = (text) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      ElMessage.success("标题已复制");
    })
    .catch(() => {
      ElMessage.error("复制失败，请手动复制");
    });
};

const handleGenerateContent = (topic) => {
  router.push({
    path: "/ai/content",
    query: { topic: encodeURIComponent(topic.title) },
  });
};

const handleGenerate = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await apiGenerateTopics({
          keywords: generateForm.keywords,
          industry: generateForm.industry,
          platform: generateForm.platform,
          count: generateForm.count,
        });

        if (res?.code === 200 && res?.data?.topics) {
          topics.value = res.data.topics;
          ElMessage.success("选题生成成功！");
        } else {
          ElMessage.error(res?.message || "后端返回错误");
        }
      } catch (error) {
        console.error("API Error:", error);
        ElMessage.error("接口请求失败，请确认后端已启动。");
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning("请完善表单必填项");
    }
  });
};
</script>

<style scoped>
.topic-generate {
  padding: 20px;
  min-height: 100%;
}
.page-wrap {
  max-width: 900px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
.page-desc {
  color: #606266;
  margin: 8px 0 0;
  font-size: 14px;
  line-height: 1.5;
}
.generate-form {
  margin-bottom: 20px;
}
.generate-result {
  margin-top: 30px;
}
.generate-result :deep(.el-card__body) {
  min-height: 120px;
}
.topics-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.topic-item {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.topic-item:hover {
  transform: translateY(-4px);
}
.topic-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease;
}
.topic-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.topic-index {
  display: inline-block;
  width: 26px;
  height: 26px;
  line-height: 26px;
  text-align: center;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 13px;
  font-weight: bold;
}
.topic-platform .el-tag {
  font-size: 12px;
}
.topic-title {
  margin: 10px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}
.topic-desc {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  flex-grow: 1;
}
.topic-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}
.form-tip {
  margin: 4px 0 0;
  font-size: 12px;
  color: #909399;
}
@media (max-width: 768px) {
  .topic-generate {
    padding: 12px;
  }
  .page-wrap {
    max-width: 100%;
  }
  .topics-list {
    grid-template-columns: 1fr;
  }
}
</style>
