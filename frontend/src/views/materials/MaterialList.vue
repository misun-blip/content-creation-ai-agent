<template>
  <div class="material-list">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <span>素材库管理</span>
          <el-button type="primary" @click="handleAddMaterial">
            <el-icon><Plus /></el-icon>
            上传素材
          </el-button>
        </div>
      </template>

      <div class="header-filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索素材（标题/描述）"
          style="width: 300px; margin-right: 10px"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="categoryFilter"
          placeholder="按分类筛选"
          style="width: 150px; margin-right: 10px"
          clearable
        >
          <el-option label="全部" value="" />
          <el-option label="图片" value="图片" />
          <el-option label="视频" value="视频" />
          <el-option label="音频" value="音频" />
          <el-option label="文档" value="文档" />
        </el-select>

        <el-button type="primary" plain @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>

        <el-button style="margin-left: 8px" @click="handleResetFilters">
          重置
        </el-button>

        <el-button style="margin-left: 8px" :loading="loading" @click="loadMaterials">
          刷新
        </el-button>
      </div>
    </el-card>

    <el-card class="material-grid" v-loading="loading">
      <div class="grid-content">
        <div v-for="material in pagedMaterials" :key="material.id" class="material-item">
          <el-card shadow="hover" class="material-card">
            <div class="material-preview">
              <el-image
                :src="normalizePreview(material.preview)"
                fit="cover"
                style="width: 100%; height: 150px"
                :preview-src-list="[normalizePreview(material.preview)]"
                preview-teleported
              />
            </div>

            <div class="material-info">
              <h4 class="material-title">{{ material.title }}</h4>
              <p class="material-desc">{{ material.description }}</p>

              <div class="material-meta">
                <el-tag size="small">{{ material.category }}</el-tag>
                <span class="material-date">{{ material.uploadDate }}</span>
              </div>

              <div class="material-actions">
                <el-button size="small" @click="handleEditMaterial(material.id)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>

                <el-button size="small" type="danger" @click="handleDeleteMaterial(material.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="pagedMaterials.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无素材" />
      </div>
    </el-card>

    <el-pagination
      v-if="filteredMaterials.length > 0"
      layout="prev, pager, next"
      :total="filteredMaterials.length"
      :page-size="pageSize"
      :current-page="currentPage"
      @current-change="handlePageChange"
      style="margin-top: 20px; text-align: center"
    />

    <!-- 新增/编辑弹窗（共用） -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑素材' : '上传素材'"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px" status-icon>
        <el-form-item label="类型" prop="category">
          <el-select v-model="form.category" placeholder="请选择类型">
            <el-option label="图片" value="图片" />
            <el-option label="视频" value="视频" />
            <el-option label="音频" value="音频" />
            <el-option label="文档" value="文档" />
          </el-select>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="例如：春季营销活动海报" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="简单描述一下这个素材..."
          />
        </el-form-item>

        <!-- 文件：新增必填；编辑可选（如果你想支持换图/换文件） -->
        <el-form-item :label="isEditMode ? '更换文件' : '文件'" prop="file">
          <el-upload
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.ppt,.pptx"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                {{
                  isEditMode
                    ? "编辑时可不选文件；若选择则会先上传并更新 preview"
                    : "将上传到后端 /api/v1/uploads，然后保存到 /api/v1/materials"
                }}
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="form.fileName" label="已选文件">
          <div style="color: #666">{{ form.fileName }}</div>
        </el-form-item>

        <!-- 预览：新增时用本地 blob；编辑时展示当前 preview（或选择新文件后的 blob） -->
        <el-form-item v-if="previewForDialog" label="预览">
          <el-image
            :src="previewForDialog"
            fit="cover"
            style="width: 240px; height: 150px; border-radius: 8px"
            :preview-src-list="[previewForDialog]"
            preview-teleported
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button :disabled="saving" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitMaterial">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Search, Edit, Delete } from "@element-plus/icons-vue";
import {
  fetchMaterials,
  createMaterial,
  updateMaterial,
  deleteMaterial,
  uploadFile,
} from "@/api/materials";

const API_BASE = import.meta.env.VITE_APP_API_BASE_URL || "http://localhost:8000";

const searchQuery = ref("");
const categoryFilter = ref("");

const currentPage = ref(1);
const pageSize = ref(12);

const loading = ref(false);
const saving = ref(false);

// 列表数据（来自后端）
const materials = ref([]);

// --- 编辑模式状态 ---
const dialogVisible = ref(false);
const isEditMode = ref(false);
const editingId = ref(null);

// 表单
const formRef = ref(null);
const form = reactive({
  title: "",
  description: "",
  category: "",
  file: null,
  fileName: "",
  preview: "", // 本地预览 blob（新增/换图）
  existingPreview: "", // 编辑时已有 preview
});

function normalizePreview(p) {
  if (!p) return "";
  // 已经是完整 URL
  if (p.startsWith("http")) return p;
  // 相对路径（/uploads/xxx）
  if (p.startsWith("/")) return `${API_BASE}${p}`;
  // 兜底
  return p;
}

const filteredMaterials = computed(() => materials.value);

const pagedMaterials = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredMaterials.value.slice(start, end);
});

async function loadMaterials() {
  loading.value = true;
  try {
    const params = {
      q: searchQuery.value.trim(),
      category: categoryFilter.value || "",
    };
    const data = await fetchMaterials(params);
    materials.value = Array.isArray(data) ? data : (data?.data != null ? data.data : []);
  } catch (e) {
    console.error(e);
    ElMessage.error("拉取素材列表失败，请检查后端是否启动/接口是否存在");
  } finally {
    loading.value = false;
  }
}

const handleSearch = async () => {
  currentPage.value = 1;
  await loadMaterials();
  ElMessage.success("已应用筛选条件");
};

const handleResetFilters = async () => {
  searchQuery.value = "";
  categoryFilter.value = "";
  currentPage.value = 1;
  await loadMaterials();
};

const handlePageChange = (page) => {
  currentPage.value = page;
};

function resetForm() {
  form.title = "";
  form.description = "";
  form.category = "";
  form.file = null;
  form.fileName = "";
  form.existingPreview = "";
  if (form.preview) URL.revokeObjectURL(form.preview);
  form.preview = "";
}

const handleAddMaterial = () => {
  isEditMode.value = false;
  editingId.value = null;
  resetForm();
  dialogVisible.value = true;
};

const handleEditMaterial = (id) => {
  const target = materials.value.find((m) => m.id === id);
  if (!target) {
    ElMessage.error("未找到要编辑的素材");
    return;
  }

  isEditMode.value = true;
  editingId.value = id;

  resetForm();
  form.title = target.title || "";
  form.description = target.description || "";
  form.category = target.category || "";
  form.existingPreview = target.preview || "";

  dialogVisible.value = true;
};

const handleDeleteMaterial = (id) => {
  ElMessageBox.confirm("确定要删除这个素材吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        await deleteMaterial(id);
        ElMessage.success("删除成功");
        await loadMaterials();
        if (pagedMaterials.value.length === 0 && currentPage.value > 1) {
          currentPage.value -= 1;
        }
      } catch (e) {
        console.error(e);
        ElMessage.error("删除失败");
      }
    })
    .catch(() => {});
};

// --- 文件选择/预览 ---
const handleFileChange = (uploadFile) => {
  const raw = uploadFile.raw;
  form.file = raw;
  form.fileName = raw?.name || "";

  // 仅图片做本地预览
  if (raw && form.category === "图片") {
    if (form.preview) URL.revokeObjectURL(form.preview);
    form.preview = URL.createObjectURL(raw);
  } else {
    if (form.preview) URL.revokeObjectURL(form.preview);
    form.preview = "";
  }
};

const handleFileRemove = () => {
  form.file = null;
  form.fileName = "";
  if (form.preview) URL.revokeObjectURL(form.preview);
  form.preview = "";
};

// 弹窗预览：优先本地 blob，否则用已有 preview
const previewForDialog = computed(() => {
  if (form.category !== "图片") return "";
  if (form.preview) return form.preview; // 新选文件
  if (form.existingPreview) return normalizePreview(form.existingPreview); // 编辑已有
  return "";
});

// --- 动态校验规则：新增必须选文件；编辑不必选 ---
const formRules = computed(() => {
  const base = {
    category: [{ required: true, message: "请选择类型", trigger: "change" }],
    title: [{ required: true, message: "请输入标题", trigger: "blur" }],
    description: [{ required: true, message: "请输入描述", trigger: "blur" }],
  };
  if (!isEditMode.value) {
    base.file = [{ required: true, message: "请选择文件", trigger: "change" }];
  }
  return base;
});

// --- 上传到后端：返回 "/uploads/xxx" 或 {url:"/uploads/xxx"} 都兼容 ---
async function uploadToBackend(file) {
  const res = await uploadFile(file);
  const data = res?.data != null ? res.data : res;
  const urlPath = typeof data === "string" ? data : data?.url;

  if (!urlPath) throw new Error("Upload response missing url");
  return urlPath;
}

const submitMaterial = async () => {
  if (!formRef.value) return;

  saving.value = true;
  try {
    // ✅ 推荐：不传 callback，直接 await
    await formRef.value.validate();

    if (isEditMode.value) {
      // 编辑：允许不选文件
      let newPreview = null;

      // 如果编辑时选择了新文件：先上传拿到 url，再更新 preview
      if (form.file) {
        const urlPath = await uploadToBackend(form.file);
        newPreview = `${API_BASE}${urlPath}`; // 存完整 URL（与你现有后端返回一致）
      }

      const payload = {
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
      };

      if (newPreview) payload.preview = newPreview;

      await updateMaterial(editingId.value, payload);

      dialogVisible.value = false;
      ElMessage.success("编辑成功");
      await loadMaterials();
      return;
    }

    // 新增：必须有文件
    const urlPath = await uploadToBackend(form.file);
    const previewUrl = `${API_BASE}${urlPath}`;

    await createMaterial({
      title: form.title.trim(),
      description: form.description.trim(),
      category: form.category,
      preview: previewUrl,
    });

    dialogVisible.value = false;
    currentPage.value = 1;
    ElMessage.success("已保存到后端素材库");
    await loadMaterials();
  } catch (e) {
    const status = e?.response?.status;
    const data = e?.response?.data;
    console.error("save error:", status, data, e);
    ElMessage.error(
      `保存失败：${status || ""} ${typeof data === "string" ? data : JSON.stringify(data || {})}`
    );
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await loadMaterials();
});
</script>

<style scoped>
.material-list {
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

.material-grid {
  margin-bottom: 20px;
}

.grid-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.material-item {
  transition: all 0.3s;
}

.material-item:hover {
  transform: translateY(-5px);
}

.material-card {
  height: 100%;
}

.material-preview {
  margin-bottom: 15px;
}

.material-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: bold;
}

.material-desc {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #999;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.material-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 12px;
  color: #999;
}

.material-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}
</style>