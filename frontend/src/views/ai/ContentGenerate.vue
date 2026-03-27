<template>
  <div class="content-generate">
    <div class="page-wrap">
      <el-card class="page-header">
        <template #header>
          <h2>文案生成与编辑器</h2>
        </template>
        <p class="page-desc">一键生成高质量文案，支持人工二次编辑与质量评估</p>
      </el-card>

    <el-card class="generate-form">
      <el-form :model="generateForm" :rules="rules" ref="formRef">
        <el-form-item label="主题/标题" prop="topic">
          <el-input
            v-model="generateForm.topic"
            placeholder="可从选题页选择选题后自动带入，或直接输入核心主题/完整标题"
            type="textarea"
            :rows="3"
          />
        </el-form-item>

        <el-form-item prop="length">
          <el-slider
            v-model="generateForm.length"
            :min="100"
            :max="1500"
            :step="100"
            show-input
            input-size="small"
            style="width: 250px"
          />
          <span style="margin-left: 15px; color: #606266">
            目标字数：约 {{ generateForm.length }} 字
          </span>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文案风格" prop="style">
              <el-select
                v-model="generateForm.style"
                placeholder="选择文案风格"
                filterable
                style="width: 100%"
              >
                <el-option label="专业严谨" value="专业严谨" />
                <el-option label="轻松活泼" value="轻松活泼" />
                <el-option label="幽默搞笑" value="幽默搞笑" />
                <el-option label="情感共鸣" value="情感共鸣" />
                <el-option label="温暖治愈" value="温暖治愈" />
                <el-option label="干货教程" value="干货教程" />
                <el-option label="故事叙述" value="故事叙述" />
                <el-option label="促销引流" value="促销引流" />
                <el-option label="品牌宣传" value="品牌宣传" />
                <el-option label="口语化" value="口语化" />
                <el-option label="文艺清新" value="文艺清新" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
                <el-option label="通用" value="general" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

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
            {{ loading ? "AI 创作中，请耐心等待..." : "生成文案" }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="generatedContent" class="generate-result">
      <template #header>
        <div class="result-header">
          <h3 class="result-title">✍️ 人工二次编辑区</h3>
          <div class="result-actions">
            <el-button size="small" @click="handleCopy">
              <el-icon><DocumentCopy /></el-icon>
              复制内容
            </el-button>
            <el-button size="small" type="success" :loading="saveRecordLoading" @click="handleSaveRecord">
              <el-icon><DocumentAdd /></el-icon>
              保存至记录
            </el-button>
            <el-button size="small" type="warning" plain @click="handleEvaluate">
              <el-icon><DataAnalysis /></el-icon>
              质量评估
            </el-button>
            <el-button size="small" type="primary" plain @click="handleAdapt">
              <el-icon><Platform /></el-icon>
              去排版适配
            </el-button>
          </div>
        </div>
      </template>

      <div class="editor-container">
        <QuillEditor
          v-model:content="generatedContent"
          contentType="html"
          theme="snow"
          toolbar="full"
        />
      </div>

      <div class="content-stats">
        <span>当前字数：约 {{ plainTextLength }} 字</span>
      </div>
    </el-card>
    <el-dialog v-model="dialogVisible" title="文案质量评估报告" width="500px" class="evaluate-dialog">
      <div class="evaluate-score-wrap">
        <el-progress
          type="dashboard"
          :percentage="evaluateResult.score"
          :color="evaluateResult.score >= 80 ? '#67C23A' : '#F56C6C'"
        >
          <template #default="{ percentage }">
            <span class="evaluate-score-text">{{ percentage }} 分</span>
          </template>
        </el-progress>
      </div>
      <h4 class="evaluate-suggestions-title">优化建议：</h4>
      <ol class="evaluate-suggestions-list">
        <li v-for="(item, index) in evaluateResult.suggestions" :key="index">
          {{ item }}
        </li>
      </ol>
      <el-empty v-if="evaluateResult.suggestions.length === 0" description="暂无建议" :image-size="48" />
      <template #footer>
        <el-button type="primary" @click="dialogVisible = false">我知道了</el-button>
      </template>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  MagicStick,
  DocumentCopy,
  Platform,
  DocumentAdd,
  DataAnalysis,
} from "@element-plus/icons-vue";
import request from "@/api/index";
import { generateContent as apiGenerateContent, evaluateContent as apiEvaluateContent } from "@/api/ai";
import { useAdapterStore } from "@/stores/adapter";

import { QuillEditor } from "@vueup/vue-quill";
import "@vueup/vue-quill/dist/vue-quill.snow.css";

const DRAFT_KEY = "content_generate_draft";

const router = useRouter();
const route = useRoute();
const adapterStore = useAdapterStore();
const formRef = ref(null);
const loading = ref(false);

const generateForm = reactive({
  topic: "",
  length: 500,
  style: "专业严谨",
  platform: "general",
});

const rules = {
  topic: [{ required: true, message: "请输入标题或主题", trigger: "blur" }],
  style: [{ required: true, message: "请选择文案风格", trigger: "change" }],
  platform: [{ required: true, message: "请选择发布平台", trigger: "change" }],
};

const generatedContent = ref("");

function saveDraft() {
  if (!generatedContent.value) return;
  try {
    const draft = {
      generatedContent: generatedContent.value,
      generateForm: {
        topic: generateForm.topic,
        length: generateForm.length,
        style: generateForm.style,
        platform: generateForm.platform,
      },
    };
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  } catch (e) {
    // sessionStorage 可能已满，不阻塞流程
  }
}

function loadDraft() {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

onMounted(() => {
  const topicQuery = route.query.topic;
  if (topicQuery) {
    generateForm.topic = decodeURIComponent(topicQuery);
  }
  const draft = loadDraft();
  if (draft?.generatedContent) {
    generatedContent.value = draft.generatedContent;
    if (!topicQuery && draft.generateForm) {
      generateForm.topic = draft.generateForm.topic ?? generateForm.topic;
      generateForm.length = draft.generateForm.length ?? generateForm.length;
      generateForm.style = draft.generateForm.style ?? generateForm.style;
      generateForm.platform = draft.generateForm.platform ?? generateForm.platform;
    } else if (draft.generateForm) {
      generateForm.length = draft.generateForm.length ?? generateForm.length;
      generateForm.style = draft.generateForm.style ?? generateForm.style;
      generateForm.platform = draft.generateForm.platform ?? generateForm.platform;
    }
  }
});

onBeforeUnmount(() => {
  if (generatedContent.value) saveDraft();
});

const plainTextLength = computed(() => {
  if (!generatedContent.value) return 0;
  return generatedContent.value.replace(/<[^>]+>/g, "").trim().length;
});

const handleCopy = () => {
  if (!generatedContent.value) return;
  let textToCopy = generatedContent.value
    .replace(/<\/p>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .trim();

  navigator.clipboard
    .writeText(textToCopy)
    .then(() => {
      ElMessage.success("内容已复制到剪贴板");
    })
    .catch(() => {
      ElMessage.error("复制失败");
    });
};

const handleGenerate = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const res = await apiGenerateContent({
          topic: generateForm.topic,
          length: generateForm.length,
          style: generateForm.style,
          platform: generateForm.platform,
        });

        if (res?.code === 200 && res?.data?.content != null) {
          const rawText = res.data.content;
          generatedContent.value = rawText
            .split("\n")
            .filter((line) => line.trim() !== "")
            .map((line) => `<p>${line}</p>`)
            .join("");
          saveDraft();
          ElMessage.success("文案初稿生成完毕，请查阅并编辑！");
        } else {
          ElMessage.error(res?.message || "后端返回错误");
        }
      } catch (error) {
        console.error("API Error:", error);
        ElMessage.error("接口请求失败，请检查后端服务是否正常");
      } finally {
        loading.value = false;
      }
    } else {
      ElMessage.warning("请完善表单必填项");
    }
  });
};

// 评估相关的响应式变量
const dialogVisible = ref(false);
const evaluateResult = reactive({
  score: 0,
  suggestions: [],
});

// 触发质量评估
const handleEvaluate = async () => {
  if (!generatedContent.value) {
    ElMessage.warning("请先生成文案！");
    return;
  }

  const plainText = generatedContent.value.replace(/<[^>]+>/g, "").trim();

  try {
    const res = await apiEvaluateContent({
      content: plainText,
      topic: generateForm.topic,
      target_length: generateForm.length,
    });

    if (res?.code === 200) {
      evaluateResult.score = res?.data?.score ?? 0;
      evaluateResult.suggestions = res?.data?.suggestions ?? [];
      dialogVisible.value = true;
    } else {
      ElMessage.error(res?.message || "评估失败");
    }
  } catch (error) {
    console.error("Evaluate Error:", error);
    ElMessage.error("接口请求失败，请检查后端");
  }
};

const saveRecordLoading = ref(false);
const handleSaveRecord = async () => {
  if (!generateForm.topic?.trim()) {
    ElMessage.warning("请先填写主题/标题");
    return;
  }
  const plainText = generatedContent.value
    ? generatedContent.value.replace(/<[^>]+>/g, "").replace(/<\/p>/g, "\n").trim()
    : "";
  saveRecordLoading.value = true;
  try {
    await request.post("/api/v1/records/", {
      title: generateForm.topic.trim(),
      platform: generateForm.platform || "general",
      content: plainText,
    });
    ElMessage.success("已保存至创作记录");
    await ElMessageBox.confirm("是否前往创作记录页面查看？", "提示", {
      confirmButtonText: "前往查看",
      cancelButtonText: "留在此页",
      type: "info",
    }).then(() => {
      router.push("/records");
    }).catch(() => {});
  } catch (err) {
    let msg = err?.response?.data?.detail ?? err?.message ?? "保存失败";
    if (Array.isArray(msg)) msg = msg.map((m) => m?.msg ?? m).filter(Boolean).join("；") || "保存失败";
    else if (typeof msg !== "string") msg = "保存失败，请稍后重试";
    ElMessage.error(msg);
  } finally {
    saveRecordLoading.value = false;
  }
};

const handleAdapt = () => {
  const plainText = generatedContent.value
    ? generatedContent.value
        .replace(/<\/p>/g, "\n")
        .replace(/<[^>]+>/g, "")
        .trim()
    : "";
  adapterStore.setOriginalContent(plainText);
  router.push("/adapter");
};
</script>

<style scoped>
.content-generate {
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
  margin-top: 20px;
}
.result-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  margin-bottom: 0;
}
.result-title {
  margin: 0;
  font-size: 16px;
  flex-shrink: 0;
}
.result-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.editor-container {
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  margin-top: 16px;
}
.evaluate-score-wrap {
  text-align: center;
  margin-bottom: 20px;
}
.evaluate-score-text {
  font-size: 24px;
  font-weight: bold;
}
.evaluate-suggestions-title {
  margin: 0 0 12px;
  font-size: 14px;
  color: #303133;
}
.evaluate-suggestions-list {
  margin: 0;
  padding-left: 22px;
  line-height: 1.8;
  font-size: 14px;
  color: #606266;
}
.evaluate-suggestions-list li {
  margin-bottom: 4px;
}
:deep(.ql-editor) {
  min-height: 450px;
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}
:deep(.ql-toolbar.ql-snow) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  background-color: #f8f9fa;
}
:deep(.ql-container.ql-snow) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}
.content-stats {
  margin-top: 15px;
  font-size: 14px;
  color: #909399;
  text-align: right;
}
@media (max-width: 768px) {
  .content-generate {
    padding: 12px;
  }
  .page-wrap {
    max-width: 100%;
  }
  .result-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
