import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "@/stores/user";
import DailyStatistics from '@/views/statistics/DailyStatistics.vue';
import { ElMessage } from "element-plus";

// 路由配置
const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/Login.vue"),
    meta: {
      requiresAuth: false,
      title: "登录",
    },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/auth/Register.vue"),
    meta: {
      requiresAuth: false,
      title: "注册",
    },
  },
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "",
        name: "Dashboard",
        component: () => import("@/views/dashboard/Dashboard.vue"),
        meta: {
          title: "首页",
          transition: "fade",
        },
      },
      {
        path: "/records/:id/versions",
        name: "VersionCompare",
        component: () => import("@/views/records/VersionCompare.vue"),
        meta: { title: "版本对比", requiresAuth: true },
      },
      {
        path: "materials",
        name: "Materials",
        component: () => import("@/views/materials/MaterialList.vue"),
        meta: {
          title: "素材库",
          transition: "slide-left",
        },
      },
      {
        path: "ai/topics",
        name: "TopicGenerate",
        component: () => import("@/views/ai/TopicGenerate.vue"),
        meta: {
          title: "选题生成",
          transition: "slide-left",
        },
      },
      {
        path: "ai/content",
        name: "ContentGenerate",
        component: () => import("@/views/ai/ContentGenerate.vue"),
        meta: {
          title: "文案生成",
          transition: "slide-left",
        },
      },
      {
        path: "adapter",
        name: "PlatformAdapter",
        component: () => import("@/views/adapter/PlatformAdapter.vue"),
        meta: {
          title: "平台适配",
          transition: "slide-left",
        },
      },
      {
        path: "records",
        name: "Records",
        component: () => import("@/views/records/RecordList.vue"),
        meta: {
          title: "创作记录",
          transition: "slide-left",
        },
      },
      {
        path: "tags",
        name: "TagManager",
        component: () => import("@/views/tags/TagManager.vue"),
        meta: {
          title: "标签管理",
          transition: "slide-left",
        },
      },
      {
        path: "statistics",
        name: "Statistics",
        component: () => import("@/views/statistics/DailyStatistics.vue"),
        meta: {
          title: "统计分析",
          transition: "slide-left",
        },
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/views/user/Profile.vue"),
        meta: {
          title: "个人信息",
          transition: "slide-left",
        },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("@/views/404.vue"),
    meta: {
      requiresAuth: false,
      title: "404",
    },
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title
    ? `${to.meta.title} - 内容创作AI-Agent`
    : "内容创作AI-Agent";

  // 权限验证
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.token) {
    ElMessage.warning("请先登录");
    next("/login");
  } else if (
    (to.path === "/login" || to.path === "/register") &&
    userStore.token
  ) {
    // 已登录用户访问登录/注册页面，重定向到首页
    next("/");
  } else {
    next();
  }
});

// 路由后置守卫
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等逻辑
  console.log(`访问页面: ${to.path}`);
});

export default router;
