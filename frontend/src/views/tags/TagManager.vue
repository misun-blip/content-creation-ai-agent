<template>
  <div class="tag-manager">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <span>标签管理</span>
        </div>
      </template>

      <div class="header-filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索标签名称"
          style="width: 300px; margin-right: 10px"
          @keyup.enter="handleSearch"
          clearable
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-button type="primary" plain @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
    </el-card>

    <el-card class="create-section">
      <div class="create-form">
        <el-input
          v-model="newTagName"
          placeholder="输入新标签名称"
          style="width: 300px; margin-right: 10px"
          @keyup.enter="handleCreateTag"
          clearable
        />
        <el-button type="primary" @click="handleCreateTag" :loading="creating">
          <el-icon><Plus /></el-icon>
          创建标签
        </el-button>
      </div>
      <div v-if="validationError" class="validation-error">
        <el-text type="danger">{{ validationError }}</el-text>
      </div>
    </el-card>

    <el-card class="tag-table" v-loading="loading">
      <el-table :data="tags" style="width: 100%" empty-text="暂无标签">
        <el-table-column prop="name" label="标签名称" min-width="200" />
        <el-table-column prop="usage_count" label="使用次数" width="120" sortable />
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleDeleteTag(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus, Delete } from "@element-plus/icons-vue";
import { fetchTags, createTag, deleteTag } from "@/api/tags";

const searchQuery = ref("");
const newTagName = ref("");
const validationError = ref("");
const loading = ref(false);
const creating = ref(false);
const tags = ref([]);

async function loadTags() {
  loading.value = true;
  try {
    const params = {};
    if (searchQuery.value.trim()) {
      params.q = searchQuery.value.trim();
    }
    const res = await fetchTags(params);
    const data = res?.data != null ? res.data : res;
    const list = Array.isArray(data) ? data : [];
    // Sort by usage_count descending
    list.sort((a, b) => (b.usage_count || 0) - (a.usage_count || 0));
    tags.value = list;
  } catch (e) {
    console.error(e);
    // Network errors are already handled by the interceptor
    // Retain current UI state
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  loadTags();
}

async function handleCreateTag() {
  validationError.value = "";

  // Validate: not empty or whitespace-only
  if (!newTagName.value || !newTagName.value.trim()) {
    validationError.value = "标签名称不能为空";
    return;
  }

  creating.value = true;
  try {
    await createTag({ name: newTagName.value.trim() });
    ElMessage.success("标签创建成功");
    newTagName.value = "";
    await loadTags();
  } catch (e) {
    // Handle duplicate tag name (400 response)
    if (e?.response?.status === 400) {
      ElMessage.error("该标签已存在");
    }
    // Other errors are handled by the global interceptor
  } finally {
    creating.value = false;
  }
}

async function handleDeleteTag(tag) {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签「${tag.name}」吗？`,
      "确认删除",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await deleteTag(tag.id);
    ElMessage.success("标签已删除");
    await loadTags();
  } catch (e) {
    // User cancelled the dialog - ElMessageBox.confirm throws on cancel
    if (e === "cancel" || e?.toString?.().includes("cancel")) {
      return;
    }
    // Network/API errors are handled by the global interceptor
    // Retain UI state
  }
}

onMounted(() => {
  loadTags();
});
</script>

<style scoped>
.tag-manager {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-filters {
  margin-top: 15px;
  display: flex;
  align-items: center;
}

.create-section {
  margin-bottom: 20px;
}

.create-form {
  display: flex;
  align-items: center;
}

.validation-error {
  margin-top: 8px;
}

.tag-table {
  margin-bottom: 20px;
}
</style>
