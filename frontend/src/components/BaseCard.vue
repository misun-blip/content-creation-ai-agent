<template>
  <el-card
    :shadow="shadow"
    :body-style="bodyStyle"
    :header-style="headerStyle"
    class="base-card"
  >
    <template #header v-if="$slots.header">
      <div class="card-header">
        <slot name="header"></slot>
      </div>
    </template>
    <div class="card-body">
      <slot></slot>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps } from "vue";

const props = defineProps({
  shadow: {
    type: String,
    default: "hover",
  },
  bodyStyle: {
    type: Object,
    default: () => ({}),
  },
  headerStyle: {
    type: Object,
    default: () => ({}),
  },
});
</script>

<style scoped>
.base-card {
  transition: all 0.3s ease;
}

.base-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-body {
  padding: 20px;
}
</style>
