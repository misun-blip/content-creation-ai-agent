import axios from "axios";
import { ElMessage } from "element-plus";
import { useUserStore } from "@/stores/user";
import router from "@/router";

// 所有具体接口里已经写成 /api/v1/... 形式，这里不再额外添加前缀，
// 让浏览器直接请求 /api/...，再由 Vite 按 vite.config.js 中的 proxy 规则转发到后端。
const request = axios.create({
  baseURL: "",
  timeout: 60000,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
   // blob 类型直接返回完整 response，不做 code 校验
    if (response.config.responseType === "blob") {
      return response;  // ← 加这一段
    }
    const res = response.data;
    if (res.code !== 200) {
      ElMessage.error(res.message || "请求失败");
      return Promise.reject(new Error(res.message || "请求失败"));
    }
    return res;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401: {
          const isLoginRequest = /auth\/login$/i.test(String(error.config?.url || ""));
          if (isLoginRequest) {
            const msg = error.response?.data?.detail || "用户名或密码错误";
            ElMessage.error(typeof msg === "string" ? msg : "用户名或密码错误");
          } else {
            const userStore = useUserStore();
            userStore.logout();
            router.push("/login");
            ElMessage.error("未授权，请重新登录");
          }
          break;
        }
        case 403:
          ElMessage.error("拒绝访问");
          break;
        case 404:
          ElMessage.error("请求的资源不存在");
          break;
        case 500:
          ElMessage.error("服务器错误");
          break;
        default:
          ElMessage.error(error.response.data.message || "请求失败");
      }
    } else {
      const isNetworkError =
        error.code === "ERR_NETWORK" ||
        (error.message && /network|Network Error/i.test(error.message));
      ElMessage.error(
        isNetworkError
          ? "无法连接后端，请确认后端已启动（端口 8000）"
          : "网络错误，请检查网络连接"
      );
    }
    return Promise.reject(error);
  }
);

export default request;
