<template>
  <div class="profile">
    <el-card v-loading="loading" class="profile-card">
      <template #header>
        <h3>个人信息</h3>
      </template>

      <template v-if="!userStore.isLoggedIn">
        <el-empty description="请先登录">
          <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
        </el-empty>
      </template>

      <template v-else>
        <el-form :model="userInfo" label-width="100px" class="profile-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="用户名">
                <el-input v-model="userInfo.username" placeholder="请输入用户名" />
              </el-form-item>

              <el-form-item label="邮箱">
                <el-input v-model="userInfo.email" disabled />
              </el-form-item>

              <el-form-item label="注册时间">
                <el-input v-model="userInfo.registerTime" disabled />
              </el-form-item>

              <el-form-item label="最后登录">
                <el-input v-model="userInfo.lastLogin" disabled />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <div class="avatar-section" @click="triggerAvatarSelect">
                <el-avatar :size="100" :src="avatarPreview" class="user-avatar">
                  <span v-if="!avatarPreview">{{ (userInfo.username || '').charAt(0).toUpperCase() || 'U' }}</span>
                </el-avatar>
                <el-button type="primary" size="small" class="avatar-upload-btn" :loading="avatarUploading">
                  <el-icon><Upload /></el-icon>
                  {{ avatarUploading ? '上传中...' : '点击更换头像' }}
                </el-button>
                <input
                  ref="avatarInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleAvatarFileChange"
                />
              </div>

              <el-form-item label="用户ID">
                <el-input :model-value="String(userInfo.id || '')" disabled />
              </el-form-item>

              <el-form-item label="账号状态">
                <el-tag type="success">活跃</el-tag>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="saveBasicProfile" :loading="savingProfile">
                  保存基本信息
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </template>
    </el-card>

    <el-card v-if="userStore.isLoggedIn" class="profile-card security-card">
      <template #header>
        <h3>账号安全</h3>
      </template>

      <div class="security-section">
        <el-table :data="securityItems" style="width: 100%">
          <el-table-column prop="item" label="安全项" width="180" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'enabled' ? 'success' : 'info'">
                {{ scope.row.status === 'enabled' ? '已开启' : '未开启' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="action" label="操作" width="140">
            <template #default="scope">
              <el-button
                v-if="scope.row.key === 'password'"
                type="primary"
                size="small"
                @click="openPasswordDialog"
              >
                修改密码
              </el-button>
              <el-button v-else type="primary" size="small" disabled>
                {{ scope.row.action }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 修改密码弹窗 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
      @close="resetPasswordForm"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSubmitting" @click="submitPasswordChange">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getUserInfo, changePassword, updateProfile } from '@/api/auth'
import { uploadFile } from '@/api/materials'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const savingProfile = ref(false)
const passwordDialogVisible = ref(false)
const passwordSubmitting = ref(false)
const passwordFormRef = ref(null)
const avatarInputRef = ref(null)
const avatarUploading = ref(false)

// 用户信息：优先从 store 初始化，再从 /me 拉取
const userInfo = ref({
  id: '',
  username: userStore.userInfo?.username || '',
  email: userStore.userInfo?.email || '',
  avatar: '',
  registerTime: '加载中...',
  lastLogin: '暂无',
  status: 'active',
})

// 统一构造文件完整访问 URL（后端返回的是 /uploads/xxx.jpg 相对路径）
const apiBase = import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000'
const avatarPreview = computed(() => {
  const raw = userInfo.value.avatar
  if (!raw) return ''
  if (/^https?:\/\//i.test(raw)) return raw
  return apiBase.replace(/\/$/, '') + raw
})

function formatDateTime(isoStr) {
  if (!isoStr) return '暂无'
  try {
    const d = new Date(isoStr)
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

async function fetchUserInfo() {
  if (!userStore.token) return
  loading.value = true
  try {
    const res = await getUserInfo()
    if (res?.code === 200 && res?.data) {
      const d = res.data
      userInfo.value = {
        id: d.id,
        username: d.username ?? userStore.userInfo?.username ?? '',
        email: d.email ?? userStore.userInfo?.email ?? '',
        avatar: d.avatar ?? '',
        registerTime: formatDateTime(d.created_at),
        lastLogin: d.last_login ? formatDateTime(d.last_login) : '暂无',
        status: 'active',
      }
      userStore.userInfo = { ...userStore.userInfo, ...d }
      localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
    }
  } catch (err) {
    if (err?.response?.status === 401) {
      userStore.logout()
      ElMessage.warning('登录已过期，请重新登录')
      router.push('/login')
      return
    }
    ElMessage.error('获取用户信息失败')
    // 非 401 时保留 store 中的用户名、邮箱、ID，仅将时间类显示为 —（mock 时用 — 更友好）
    const isMock = String(userStore.token || '').startsWith('mock-')
    const fallbackTime = isMock ? '—' : '获取失败'
    userInfo.value = {
      ...userInfo.value,
      username: userStore.userInfo?.username ?? userInfo.value.username ?? '',
      email: userStore.userInfo?.email ?? userInfo.value.email ?? '',
      id: userStore.userInfo?.id ?? userInfo.value.id ?? '',
      registerTime: fallbackTime,
      lastLogin: fallbackTime,
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) return
  userInfo.value.username = userStore.userInfo?.username ?? ''
  userInfo.value.email = userStore.userInfo?.email ?? ''
  userInfo.value.id = userStore.userInfo?.id ?? ''
  fetchUserInfo()
})

async function applyProfileUpdate({ username, avatar }) {
  const payload = {}
  if (username != null) payload.username = username
  if (avatar != null) payload.avatar = avatar
  const res = await updateProfile(payload)
  if (res?.code === 200 && res?.data) {
    const { token, user } = res.data
    if (token) {
      userStore.token = token
      localStorage.setItem('token', token)
    }
    if (user) {
      userInfo.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        avatar: user.avatar || '',
        registerTime: formatDateTime(user.created_at),
        lastLogin: user.last_login ? formatDateTime(user.last_login) : userInfo.value.lastLogin,
        status: 'active',
      }
      userStore.userInfo = { ...userStore.userInfo, ...user }
      localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
    }
  }
  return res
}

async function saveBasicProfile() {
  if (!userStore.isLoggedIn) return
  savingProfile.value = true
  try {
    await applyProfileUpdate({
      username: userInfo.value.username,
      avatar: userInfo.value.avatar,
    })
    ElMessage.success('个人信息已更新')
  } catch (err) {
    if (err?.response?.status === 400) {
      const msg = err.response.data?.detail || '更新失败'
      ElMessage.error(msg)
    } else if (err?.response?.status === 401) {
      userStore.logout()
      ElMessage.warning('登录已过期，请重新登录')
      router.push('/login')
    } else {
      ElMessage.error('更新个人信息失败')
    }
  } finally {
    savingProfile.value = false
  }
}

function triggerAvatarSelect() {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  avatarInputRef.value?.click()
}

async function handleAvatarFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  // 重置 input，避免同一文件无法再次触发 change
  event.target.value = ''

  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请选择图片文件作为头像')
    return
  }

  avatarUploading.value = true
  try {
    const res = await uploadFile(file)
    const url = res?.data?.url || res?.data?.data?.url
    if (!url) {
      ElMessage.error('上传失败：未获取到文件地址')
      return
    }
    userInfo.value.avatar = url
    await applyProfileUpdate({ avatar: url })
    ElMessage.success('头像已更新')
  } catch (err) {
    if (err?.response?.status === 401) {
      userStore.logout()
      ElMessage.warning('登录已过期，请重新登录')
      router.push('/login')
      return
    }
    ElMessage.error('头像上传失败')
  } finally {
    avatarUploading.value = false
  }
}

// 安全项（仅「修改密码」可点击）
const securityItems = ref([
  { key: 'password', item: '密码保护', status: 'enabled', action: '修改' },
  { key: 'email', item: '邮箱验证', status: 'enabled', action: '验证' },
  { key: 'phone', item: '手机绑定', status: 'disabled', action: '绑定' },
  { key: '2fa', item: '两步验证', status: 'disabled', action: '开启' },
])

// 修改密码
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) callback(new Error('两次输入不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

function openPasswordDialog() {
  passwordDialogVisible.value = true
}

function resetPasswordForm() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordFormRef.value?.resetFields()
}

/** 将后端 detail（可能为字符串或数组）转为单行提示文案 */
function getErrorMessage(err) {
  const detail = err?.response?.data?.detail
  if (detail == null) return err?.message || '修改失败'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const first = detail[0]
    if (first && typeof first === 'object' && first.msg != null) return first.msg
    return detail.map((x) => (typeof x === 'string' ? x : x?.msg)).filter(Boolean).join('；') || '修改失败'
  }
  return String(detail)
}

async function submitPasswordChange() {
  if (!passwordFormRef.value) return
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }
  passwordSubmitting.value = true
  try {
    await changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
    })
    ElMessage.success('密码已修改，请重新登录')
    passwordDialogVisible.value = false
    resetPasswordForm()
    userStore.logout()
    router.push('/login')
  } catch (err) {
    if (err?.response?.status === 401) {
      userStore.logout()
      ElMessage.warning('登录已过期，请重新登录')
      passwordDialogVisible.value = false
      resetPasswordForm()
      router.push('/login')
      return
    }
    ElMessage.error(getErrorMessage(err))
  } finally {
    passwordSubmitting.value = false
  }
}
</script>

<style scoped>
.profile {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  margin-bottom: 20px;
}

.profile-card.security-card {
  margin-top: 20px;
}

.profile-form {
  margin-top: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background-color: var(--el-fill-color-light);
}

.user-avatar {
  margin-bottom: 15px;
}

.avatar-upload-btn {
  margin-top: 10px;
}

.security-section {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .profile {
    padding: 10px;
  }

  .el-form-item {
    margin-bottom: 15px;
  }

  .el-col {
    margin-bottom: 20px;
  }
}
</style>
