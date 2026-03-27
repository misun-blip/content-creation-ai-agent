<template>
  <el-container class="main-layout">
    <el-aside width="200px">
      <div class="logo">
        <h3>内容创作AI-Agent</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/materials">
          <el-icon><Folder /></el-icon>
          <span>素材库</span>
        </el-menu-item>
        <el-menu-item index="/ai/topics">
          <el-icon><MagicStick /></el-icon>
          <span>选题生成</span>
        </el-menu-item>
        <el-menu-item index="/ai/content">
          <el-icon><EditPen /></el-icon>
          <span>文案生成</span>
        </el-menu-item>
        <el-menu-item index="/adapter">
          <el-icon><Platform /></el-icon>
          <span>平台适配</span>
        </el-menu-item>
        <el-menu-item index="/records">
          <el-icon><Document /></el-icon>
          <span>创作记录</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-content">
          <span class="welcome-text">欢迎，{{ userStore.username }}</span>
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              <el-icon><User /></el-icon>
              用户中心
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided
                  >退出登录</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);

const handleCommand = async (command) => {
  if (command === "logout") {
    try {
      await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      });

      userStore.logout();
      ElMessage.success("退出成功");
      router.push("/login");
    } catch (error) {
      // 用户取消
    }
  } else if (command === "profile") {
    router.push("/profile");
  }
};
</script>

<style scoped>
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: row;
}

.logo {
  padding: 20px;
  text-align: center;
  background-color: #545c64;
}

.logo h3 {
  margin: 0;
  color: #fff;
  font-size: 16px;
}

.el-aside {
  background-color: #545c64;
  height: 100%;
  transition: all 0.3s ease;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  justify-content: space-between;
}

.welcome-text {
  color: #333;
  font-size: 14px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-main {
  background-color: #f5f5f5;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .el-aside {
    width: 180px !important;
  }

  .logo h3 {
    font-size: 14px;
  }

  .el-menu-item {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .el-aside {
    width: 60px !important;
  }

  .logo h3 {
    display: none;
  }

  .el-menu-item {
    justify-content: center;
  }

  .el-menu-item span {
    display: none;
  }

  .el-main {
    padding: 10px;
  }

  .welcome-text {
    font-size: 12px;
  }

  .header-content {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .el-header {
    padding: 0 10px;
  }

  .welcome-text {
    display: none;
  }

  .el-main {
    padding: 5px;
  }
}
</style>
