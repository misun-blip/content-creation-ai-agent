<template>
  <div class="not-found">
    <el-card class="not-found-card">
      <div class="not-found-content">
        <div class="not-found-code">404</div>
        <h2>页面不存在</h2>
        <p>抱歉，您访问的页面不存在或已被移除</p>
        <div class="not-found-actions">
          <el-button type="primary" @click="handleGoHome">
            <el-icon><House /></el-icon>
            返回首页
          </el-button>
          <el-button @click="handleGoBack">
            <el-icon><ArrowLeft /></el-icon>
            返回上一页
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { House, ArrowLeft } from "@element-plus/icons-vue";

const router = useRouter();

const handleGoHome = () => {
  router.push("/");
};

const handleGoBack = () => {
  router.back();
};
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.not-found-card {
  width: 100%;
  max-width: 600px;
  text-align: center;
  padding: 40px 20px;
}

.not-found-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 20px;
}

.not-found-content h2 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #303133;
}

.not-found-content p {
  font-size: 16px;
  color: #909399;
  margin-bottom: 30px;
}

.not-found-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

@media (max-width: 768px) {
  .not-found-code {
    font-size: 80px;
  }

  .not-found-content h2 {
    font-size: 20px;
  }

  .not-found-content p {
    font-size: 14px;
  }

  .not-found-actions {
    flex-direction: column;
    align-items: center;
  }

  .not-found-actions .el-button {
    width: 200px;
  }
}
</style>
