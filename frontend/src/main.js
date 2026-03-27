import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import App from "./App.vue";
import router from "./router";
import { setupErrorHandler } from "./utils/errorHandler";

const app = createApp(App);

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 集成Pinia状态管理
const pinia = createPinia();
app.use(pinia);

// 集成路由
app.use(router);

// 集成Element Plus
app.use(ElementPlus);

// 设置全局错误处理
setupErrorHandler(app);

app.mount("#app");
