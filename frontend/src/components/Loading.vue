<template>
  <div class="loading-container" :class="{ fullscreen: fullscreen }">
    <div class="loading-content">
      <el-spinner :size="size" :type="type" />
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  fullscreen: {
    type: Boolean,
    default: false,
  },
  size: {
    type: Number,
    default: 40,
  },
  type: {
    type: String,
    default: "snake",
  },
  text: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.loading-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-text {
  font-size: 14px;
  color: #606266;
  margin: 0;
}
</style>
