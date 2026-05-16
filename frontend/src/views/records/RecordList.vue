<template>
  <div class="record-list">
    <!-- 页面标题 -->
    <el-card class="page-header">
      <template #header>
        <h2>创作记录</h2>
      </template>
      <p class="page-desc">查看和管理你的所有创作记录</p>
    </el-card>

    <!-- 检索区域 -->
    <el-card class="filter-form">
      <div class="filter-content">
        <el-input
          v-model="searchQuery"
          placeholder="搜索标题关键词"
          prefix-icon="Search"
          style="width: 260px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select
          v-model="platformFilter"
          placeholder="按平台筛选"
          style="width: 150px"
          clearable
        >
          <el-option label="抖音" value="douyin" />
          <el-option label="小红书" value="xiaohongshu" />
          <el-option label="微信" value="wechat" />
          <el-option label="B站" value="bilibili" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 260px"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" :loading="loading" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-dropdown @command="handleExport" trigger="click">
          <el-button type="success">
            <el-icon><Download /></el-icon>
            导出
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="csv">CSV</el-dropdown-item>
              <el-dropdown-item command="txt">TXT</el-dropdown-item>
              <el-dropdown-item command="docx">Word</el-dropdown-item>
              <el-dropdown-item command="pdf">PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" plain @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          新建记录
        </el-button>
      </div>
    </el-card>

    <!-- 记录表格 -->
    <el-card class="records-table">
      <template #header>
        <div class="table-header">
          <h3>创作列表</h3>
          <span class="total-tip">共 {{ total }} 条记录</span>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="records"
        style="width: 100%"
        border
        stripe
        row-key="id"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="title" label="标题" min-width="170">
          <template #default="{ row }">
            <el-link type="primary" @click="openDetailDialog(row)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getPlatformType(row.platform)" size="small">
              {{ getPlatformName(row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version_count" label="版本数" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.version_count" type="info" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="openDetailDialog(row)">
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button size="small" type="warning" @click="openVersionDialog(row)">
              <el-icon><Clock /></el-icon>版本
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchRecords"
          @current-change="fetchRecords"
        />
      </div>
    </el-card>

    <!-- ── 新建/编辑记录 Dialog ── -->
    <el-dialog
      v-model="createDialogVisible"
      :title="editingRecord ? '编辑记录' : '新建创作记录'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="recordForm" label-width="80px" :rules="recordRules" ref="recordFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="recordForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="平台" prop="platform">
          <el-select v-model="recordForm.platform" placeholder="请选择平台" style="width: 100%">
            <el-option label="抖音" value="douyin" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="微信" value="wechat" />
            <el-option label="B站" value="bilibili" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="recordForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入创作内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRecord">
          {{ editingRecord ? '保存修改' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ── 记录详情 Dialog ── -->
    <el-dialog
      v-model="detailDialogVisible"
      title="创作记录详情"
      width="700px"
      destroy-on-close
    >
      <template v-if="currentRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="平台">
            <el-tag :type="getPlatformType(currentRecord.platform)" size="small">
              {{ getPlatformName(currentRecord.platform) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="2">{{ currentRecord.title }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentRecord.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentRecord.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 当前内容：独立区块，支持鼠标滚轮查看完整内容 -->
        <div class="content-section">
          <div class="content-section-label">当前内容</div>
          <div class="content-scroll-box">
            <template v-if="currentRecord.content">{{ currentRecord.content }}</template>
            <span v-else class="content-empty">（无内容）</span>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="startEdit(currentRecord)">编辑</el-button>
        <el-button type="warning" @click="openVersionDialog(currentRecord)">版本历史</el-button>
      </template>
    </el-dialog>

    <!-- ── 版本管理 Dialog ── -->
    <el-dialog
      v-model="versionDialogVisible"
      title="版本历史"
      width="800px"
      destroy-on-close
    >
      <div v-if="currentRecord" class="version-panel">
        <!-- 时间线 -->
        <el-timeline>
          <el-timeline-item
            v-for="v in versions"
            :key="v.id"
            :timestamp="formatDate(v.created_at)"
            placement="top"
            :type="compareSelection.includes(v.version_number) ? 'primary' : ''"
          >
            <el-card shadow="never" class="version-card">
              <div class="version-card-header">
                <span class="version-tag">v{{ v.version_number }}</span>
                <span class="version-note">{{ v.change_note || '无备注' }}</span>
                <div class="version-actions">
                  <el-checkbox
                    v-model="compareSelection"
                    :label="v.version_number"
                    :disabled="compareSelection.length >= 2 && !compareSelection.includes(v.version_number)"
                    size="small"
                  >
                    对比
                  </el-checkbox>
                  <el-button
                    v-if="v.version_number !== versions[versions.length - 1]?.version_number"
                    size="small"
                    type="warning"
                    plain
                    @click="handleRestore(v)"
                  >
                    回滚至此版本
                  </el-button>
                </div>
              </div>
              <div class="version-content-preview">{{ truncate(v.content, 120) }}</div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <!-- 版本对比区域 -->
        <div v-if="compareSelection.length === 2" class="compare-panel">
          <el-divider>版本对比</el-divider>
          <el-row :gutter="16">
            <el-col :span="12">
              <div class="compare-label">v{{ compareSelection[0] }}</div>
              <div class="compare-content">{{ getVersionContent(compareSelection[0]) }}</div>
            </el-col>
            <el-col :span="12">
              <div class="compare-label">v{{ compareSelection[1] }}</div>
              <div class="compare-content">{{ getVersionContent(compareSelection[1]) }}</div>
            </el-col>
          </el-row>
        </div>

        <!-- 新增版本 -->
        <el-divider>保存新版本</el-divider>
        <el-form :model="newVersionForm" label-width="80px">
          <el-form-item label="内容">
            <el-input
              v-model="newVersionForm.content"
              type="textarea"
              :rows="4"
              placeholder="输入新版本内容"
            />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="newVersionForm.change_note" placeholder="本次修改说明（可选）" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="submitNewVersion">
              保存新版本
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="versionDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Download, View, Delete, Plus, Clock, ArrowDown } from "@element-plus/icons-vue";
import {
  fetchRecords as apiFetchRecords,
  createRecord,
  getRecord,
  updateRecord,
  deleteRecord,
  fetchVersions as apiFetchVersions,
  createVersion,
  restoreVersion,
  exportRecords,
} from "@/api/records";
import { downloadBlob } from "@/utils/download";

// ── 状态 ──────────────────────────────────────────────────────
const loading = ref(false);
const submitting = ref(false);
const records = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

const searchQuery = ref("");
const platformFilter = ref("");
const dateRange = ref([]);

// Dialog 状态
const createDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const versionDialogVisible = ref(false);
const currentRecord = ref(null);
const editingRecord = ref(null);

// 表单
const recordFormRef = ref(null);
const recordForm = reactive({ title: "", platform: "", content: "" });
const recordRules = {
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  platform: [{ required: true, message: "请选择平台", trigger: "change" }],
};

// 版本
const versions = ref([]);
const compareSelection = ref([]);
const newVersionForm = reactive({ content: "", change_note: "" });

// ── API 调用 ───────────────────────────────────────────────────

const fetchRecords = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    };
    if (searchQuery.value) params.keyword = searchQuery.value;
    if (platformFilter.value) params.platform = platformFilter.value;
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0];
      params.end_date = dateRange.value[1];
    }
    const res = await apiFetchRecords(params);
    // 前端兜底：按 id 升序排列
    const items = res.data?.items || [];
    items.sort((a, b) => a.id - b.id);
    records.value = items;
    total.value = res.data?.total || 0;
  } catch (e) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false;
  }
};

const fetchVersions = async (recordId) => {
  const res = await apiFetchVersions(recordId);
  versions.value = res.data || [];
};

// ── 搜索 & 重置 ───────────────────────────────────────────────
const handleSearch = () => {
  currentPage.value = 1;
  fetchRecords();
};

const handleReset = () => {
  searchQuery.value = "";
  platformFilter.value = "";
  dateRange.value = [];
  currentPage.value = 1;
  fetchRecords();
};

// ── 导出 ──────────────────────────────────────────────────────
const EXPORT_FORMATS = {
  csv:  { extension: '.csv',  mimeType: 'text/csv' },
  txt:  { extension: '.txt',  mimeType: 'text/plain' },
  docx: { extension: '.docx', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
  pdf:  { extension: '.pdf',  mimeType: 'application/pdf' },
};

const handleExport = async (format) => {
  try {
    const params = {};
    if (searchQuery.value) params.keyword = searchQuery.value;
    if (platformFilter.value) params.platform = platformFilter.value;
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0];
      params.end_date = dateRange.value[1];
    }
    const res = await exportRecords(format, params);
    // 从响应头取文件名，取不到则用默认名
    const disposition = res.headers?.["content-disposition"] || "";
    const match = disposition.match(/filename="?([^"]+)"?/);
    const formatMeta = EXPORT_FORMATS[format] || EXPORT_FORMATS.csv;
    const filename = match ? match[1] : `records_${Date.now()}${formatMeta.extension}`;
    const blob = new Blob([res.data], { type: formatMeta.mimeType });
    downloadBlob(blob, filename);
    ElMessage.success("导出成功");
  } catch (e) {
    ElMessage.error("导出失败，请稍后重试");
  }
};

// ── 新建 / 编辑 ────────────────────────────────────────────────
const openCreateDialog = () => {
  editingRecord.value = null;
  Object.assign(recordForm, { title: "", platform: "", content: "" });
  createDialogVisible.value = true;
};

const startEdit = (record) => {
  editingRecord.value = record;
  Object.assign(recordForm, {
    title: record.title,
    platform: record.platform,
    content: record.content || "",
  });
  detailDialogVisible.value = false;
  createDialogVisible.value = true;
};

const submitRecord = async () => {
  await recordFormRef.value?.validate();
  submitting.value = true;
  try {
    if (editingRecord.value) {
      await updateRecord(editingRecord.value.id, recordForm);
      ElMessage.success("更新成功");
    } else {
      await createRecord(recordForm);
      ElMessage.success("创建成功");
    }
    createDialogVisible.value = false;
    fetchRecords();
  } finally {
    submitting.value = false;
  }
};

// ── 详情 ──────────────────────────────────────────────────────
const openDetailDialog = async (row) => {
  const res = await getRecord(row.id);
  currentRecord.value = res.data;
  detailDialogVisible.value = true;
};

// ── 版本 ──────────────────────────────────────────────────────
const openVersionDialog = async (row) => {
  currentRecord.value = row;
  compareSelection.value = [];
  newVersionForm.content = row.content || "";
  newVersionForm.change_note = "";
  await fetchVersions(row.id);
  versionDialogVisible.value = true;
};

const submitNewVersion = async () => {
  if (!newVersionForm.content.trim()) {
    ElMessage.warning("请输入版本内容");
    return;
  }
  submitting.value = true;
  try {
    await createVersion(currentRecord.value.id, newVersionForm);
    ElMessage.success("版本保存成功");
    await fetchVersions(currentRecord.value.id);
    newVersionForm.content = "";
    newVersionForm.change_note = "";
    fetchRecords();
  } finally {
    submitting.value = false;
  }
};

const handleRestore = async (version) => {
  await ElMessageBox.confirm(
    `确定回滚到 v${version.version_number}？将基于该版本内容创建新版本。`,
    "确认回滚",
    { type: "warning" }
  );
  await restoreVersion(currentRecord.value.id, version.id);
  ElMessage.success("回滚成功");
  await fetchVersions(currentRecord.value.id);
  fetchRecords();
};

// ── 删除 ──────────────────────────────────────────────────────
const handleDelete = async (row) => {
  await ElMessageBox.confirm(
    `确定删除「${row.title}」及其所有版本？此操作不可恢复。`,
    "确认删除",
    { type: "warning", confirmButtonText: "删除", confirmButtonClass: "el-button--danger" }
  );
  await deleteRecord(row.id);
  ElMessage.success("删除成功");
  fetchRecords();
};

// ── 工具函数 ─────────────────────────────────────────────────
const getPlatformName = (p) =>
  ({ douyin: "抖音", xiaohongshu: "小红书", wechat: "微信", bilibili: "B站" }[p] || p);

const getPlatformType = (p) =>
  ({ douyin: "danger", xiaohongshu: "warning", wechat: "success", bilibili: "info" }[p] || "");

const formatDate = (dt) => {
  if (!dt) return "-";
  return new Date(dt).toLocaleString("zh-CN", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
};

const truncate = (str, len) =>
  str && str.length > len ? str.slice(0, len) + "…" : str || "";

const getVersionContent = (versionNumber) => {
  const v = versions.value.find((v) => v.version_number === versionNumber);
  return v?.content || "";
};

// ── 初始化 ───────────────────────────────────────────────────
onMounted(fetchRecords);
</script>

<style scoped>
.record-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  /* background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); */
  color: black;
}
.page-header :deep(.el-card__header) h2 {
  color: black;
  margin: 0;
}
.page-desc {
  color:black;
  margin: 0;
}

.filter-content {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.table-header h3 {
  margin: 0;
}
.total-tip {
  font-size: 13px;
  color: #999;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* ── 详情弹窗：当前内容区域 ── */
.content-section {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.content-section-label {
  padding: 8px 12px;
  background: #f5f7fa;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

/* 核心：固定最大高度 + overflow-y:auto，支持鼠标滚轮查看全部内容 */
.content-scroll-box {
  max-height: 100px;
  overflow-y: auto;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
}

.content-empty {
  color: #c0c4cc;
  font-style: italic;
}

/* 滚动条美化 */
.content-scroll-box::-webkit-scrollbar {
  width: 6px;
}
.content-scroll-box::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}
.content-scroll-box::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}
.content-scroll-box::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* ── 版本面板 ── */
.version-panel {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 4px;
}

.version-card {
  margin-bottom: 4px;
}
.version-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.version-tag {
  font-weight: 700;
  color: #409eff;
  font-size: 14px;
  min-width: 28px;
}
.version-note {
  flex: 1;
  color: #666;
  font-size: 13px;
}
.version-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.version-content-preview {
  font-size: 13px;
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
}

.compare-panel {
  margin-top: 8px;
}
.compare-label {
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}
.compare-content {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  min-height: 120px;
}

@media (max-width: 768px) {
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-content > * {
    width: 100% !important;
  }
}
</style>