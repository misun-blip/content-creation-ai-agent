// 全局错误处理工具
import { ElMessage } from "element-plus";

/**
 * 初始化全局错误处理
 * @param {Object} app - Vue应用实例
 */
export const setupErrorHandler = (app) => {
  // 全局错误捕获
  app.config.errorHandler = (err, instance, info) => {
    console.error("Vue Error:", err);
    console.error("Error Info:", info);

    // 显示错误提示
    ElMessage.error({
      message: "系统出现错误，请稍后重试",
      duration: 3000,
    });

    // 可以在这里添加错误上报逻辑
    // reportError(err, info)
  };

  // 未捕获的Promise错误
  window.addEventListener("unhandledrejection", (event) => {
    console.error("Unhandled Rejection:", event.reason);

    // 显示错误提示
    ElMessage.error({
      message: "操作失败，请稍后重试",
      duration: 3000,
    });

    // 阻止默认行为
    event.preventDefault();
  });

  // 未捕获的同步错误
  window.addEventListener("error", (event) => {
    console.error("Uncaught Error:", event.error);

    // 显示错误提示
    ElMessage.error({
      message: "系统出现错误，请刷新页面重试",
      duration: 3000,
    });

    // 阻止默认行为
    // event.preventDefault()
  });
};

/**
 * 处理API错误
 * @param {Error} error - API错误对象
 * @returns {string} 错误信息
 */
export const handleApiError = (error) => {
  let errorMessage = "网络请求失败，请稍后重试";

  if (error.response) {
    // 服务器返回错误状态码
    const status = error.response.status;
    const data = error.response.data;

    switch (status) {
      case 400:
        errorMessage = data.message || "请求参数错误";
        break;
      case 401:
        errorMessage = "未授权，请重新登录";
        // 可以在这里添加跳转到登录页面的逻辑
        break;
      case 403:
        errorMessage = "拒绝访问";
        break;
      case 404:
        errorMessage = "请求的资源不存在";
        break;
      case 500:
        errorMessage = "服务器内部错误";
        break;
      default:
        errorMessage = data.message || `请求失败（${status}）`;
    }
  } else if (error.request) {
    // 请求已发送但没有收到响应
    errorMessage = "服务器无响应，请检查网络连接";
  } else {
    // 请求配置出错
    errorMessage = error.message || "请求配置错误";
  }

  // 显示错误提示
  ElMessage.error({
    message: errorMessage,
    duration: 3000,
  });

  return errorMessage;
};

/**
 * 处理表单验证错误
 * @param {Object} error - 表单验证错误对象
 */
export const handleValidationError = (error) => {
  if (error && error.message) {
    ElMessage.warning({
      message: error.message,
      duration: 3000,
    });
  }
};
