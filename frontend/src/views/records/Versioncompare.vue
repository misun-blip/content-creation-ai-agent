<template>
  <div class="version-compare">
    <el-page-header @back="$router.back()" content="版本对比" />

    <el-card class="mt-16" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>{{ record?.title }}</span>
          <el-tag :type="getPlatformType(record?.platform)" size="small">
            {{ getPlatformName(record?.platform) }}
          </el-tag>
        </div>
      </template>

      <!-- 版本选择器 -->
      <el-row :gutter="16" class="version-selectors">
        <el-col :span="12">
          <div class="selector-label">基准版本（左）</div>
          <el-select v-model="leftVersionId" placeholder="选择版本" style="width: 100%" @change="updateCompare">
            <el-option
              v-for="v in versions"
              :key="v.id"
              :label="`v${v.version_number} — ${v.change_note || '无备注'}`"
              :value="v.id"
            />
          </el-select>
        </el-col>
        <el-col :span="12">
          <div class="selector-label">对比版本（右）</div>
          <el-select v-model="rightVersionId" placeholder="选择版本" style="width: 100%" @change="updateCompare">
            <el-option
              v-for="v in versions"
              :key="v.id"
              :label="`v${v.version_number} — ${v.change_note || '无备注'}`"
              :value="v.id"
            />
          </el-select>
        </el-col>
      </el-row>

      <!-- 对比展示 -->
      <el-row v-if="leftVersion && rightVersion" :gutter="16" class="compare-area">
        <el-col :span="12">
          <div class="version-pane left-pane">
            <div class="pane-header">
              <span class="version-number">v{{ leftVersion.version_number }}</span>
              <span class="version-time">{{ formatDate(leftVersion.created_at) }}</span>
              <el-tag size="small" type="info">{{ leftVersion.change_note || '无备注' }}</el-tag>
            </div>
            <div class="pane-content">
              <p
                v-for="(line, idx) in leftLines"
                :key="idx"
                :class="getDiffClass(line, idx, 'left')"
              >{{ line || '&nbsp;' }}</p>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="version-pane right-pane">
            <div class="pane-header">
              <span class="version-number">v{{ rightVersion.version_number }}</span>
              <span class="version-time">{{ formatDate(rightVersion.created_at) }}</span>
              <el-tag size="small" type="success">{{ rightVersion.change_note || '无备注' }}</el-tag>
            </div>
            <div class="pane-content">
              <p
                v-for="(line, idx) in rightLines"
                :key="idx"
                :class="getDiffClass(line, idx, 'right')"
              >{{ line || '&nbsp;' }}</p>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 无数据提示 -->
      <el-empty v-else description="请在左右两侧各选择一个版本进行对比" />
    </el-card>

    <!-- 时间线 -->
    <el-card class="mt-16">
      <template #header><span>版本时间线</span></template>
      <el-timeline>
        <el-timeline-item
          v-for="v in versions"
          :key="v.id"
          :timestamp="formatDate(v.created_at)"
          placement="top"
          :type="v.id === leftVersionId || v.id === rightVersionId ? 'primary' : 'info'"
          :hollow="v.id !== leftVersionId && v.id !== rightVersionId"
        >
          <div class="timeline-item">
            <span class="tl-version">v{{ v.version_number }}</span>
            <span class="tl-note">{{ v.change_note || '无备注' }}</span>
            <div class="tl-actions">
              <el-button size="small" plain @click="leftVersionId = v.id; updateCompare()">设为左</el-button>
              <el-button size="small" plain @click="rightVersionId = v.id; updateCompare()">设为右</el-button>
              <el-button size="small" type="warning" plain @click="handleRestore(v)">回滚</el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/api/index";

const route = useRoute();
const router = useRouter();
const recordId = computed(() => route.params.id);

const loading = ref(false);
const record = ref(null);
const versions = ref([]);
const leftVersionId = ref(null);
const rightVersionId = ref(null);

const leftVersion = computed(() => versions.value.find((v) => v.id === leftVersionId.value));
const rightVersion = computed(() => versions.value.find((v) => v.id === rightVersionId.value));

const leftLines = computed(() => leftVersion.value?.content?.split("\n") || []);
const rightLines = computed(() => rightVersion.value?.content?.split("\n") || []);

// 简单行级差异高亮（不同则高亮）
const getDiffClass = (line, idx, side) => {
  if (!leftVersion.value || !rightVersion.value) return "";
  const l = leftLines.value[idx] ?? "";
  const r = rightLines.value[idx] ?? "";
  if (l === r) return "";
  return side === "left" ? "line-removed" : "line-added";
};

const updateCompare = () => {};

const fetchData = async () => {
  loading.value = true;
  try {
    const [recRes, verRes] = await Promise.all([
      request.get(`/api/v1/records/${recordId.value}`),
      request.get(`/api/v1/records/${recordId.value}/versions`),
    ]);
    record.value = recRes.data;
    versions.value = verRes.data || [];
    // 默认选最后两个版本
    if (versions.value.length >= 2) {
      leftVersionId.value = versions.value[versions.value.length - 2].id;
      rightVersionId.value = versions.value[versions.value.length - 1].id;
    } else if (versions.value.length === 1) {
      leftVersionId.value = versions.value[0].id;
    }
  } finally {
    loading.value = false;
  }
};

const handleRestore = async (version) => {
  await ElMessageBox.confirm(`确定回滚到 v${version.version_number}？`, "确认", { type: "warning" });
  await request.post(`/api/v1/records/${recordId.value}/versions/${version.id}/restore`);
  ElMessage.success("回滚成功");
  await fetchData();
};

const getPlatformName = (p) =>
  ({ douyin: "抖音", xiaohongshu: "小红书", wechat: "微信", bilibili: "B站" }[p] || p || "");

const getPlatformType = (p) =>
  ({ douyin: "danger", xiaohongshu: "warning", wechat: "success", bilibili: "info" }[p] || "");

const formatDate = (dt) => {
  if (!dt) return "-";
  return new Date(dt).toLocaleString("zh-CN", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
};

onMounted(fetchData);
</script>

<style scoped>
.version-compare {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.mt-16 { margin-top: 16px; }

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 16px;
}

.version-selectors {
  margin-bottom: 16px;
}
.selector-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  font-weight: 600;
}

.compare-area {
  margin-top: 8px;
}

.version-pane {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}
.pane-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}
.version-number {
  font-weight: 700;
  color: #409eff;
}
.version-time {
  font-size: 12px;
  color: #999;
  flex: 1;
}
.pane-content {
  padding: 14px;
  font-size: 13px;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
  font-family: "Courier New", monospace;
}
.pane-content p {
  margin: 0;
  padding: 1px 4px;
  border-radius: 2px;
  white-space: pre-wrap;
  word-break: break-all;
}

.line-removed {
  background-color: #ffeef0;
  color: #cb2431;
}
.line-added {
  background-color: #e6ffed;
  color: #22863a;
}

/* 时间线 */
.timeline-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.tl-version {
  font-weight: 700;
  color: #409eff;
  min-width: 32px;
}
.tl-note {
  flex: 1;
  color: #555;
  font-size: 13px;
}
.tl-actions {
  display: flex;
  gap: 6px;
}
</style>