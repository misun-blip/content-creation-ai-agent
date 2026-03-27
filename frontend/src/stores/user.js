import { defineStore } from "pinia";
import { 
  login as loginApi, 
  register as registerApi,
  getUserInfo as getUserInfoApi,
  updateProfile as updateProfileApi,
  changePassword as changePasswordApi
} from "@/api/auth";
import { uploadFile as uploadFileApi } from "@/api/materials";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    userInfo: JSON.parse(localStorage.getItem("userInfo") || "{}"),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.userInfo.username || "",
    avatar: (state) => state.userInfo.avatar || "",
  },

  actions: {
    // 登录
    async login(credentials) {
      try {
        const res = await loginApi(credentials);
        this.token = res.data.token;
        this.userInfo = res.data.user;
        localStorage.setItem("token", this.token);
        localStorage.setItem("userInfo", JSON.stringify(this.userInfo));
        return res;
      } catch (error) {
        // 401 或其它业务错误：直接抛出，由登录页展示后端返回的提示
        if (error.response?.status === 401 || error.response?.status === 400) {
          throw error;
        }
        // 仅当网络不可达时使用模拟登录，便于本地演示
        if (error.code === "ERR_NETWORK" || !error.response) {
          console.warn("后端不可用，使用模拟登录");
          const mockToken = "mock-token-" + Date.now();
          const mockUserInfo = {
            id: 1,
            username: credentials.username,
            email: credentials.username.includes("@")
              ? credentials.username
              : `${credentials.username}@example.com`,
            avatar: null,
          };
          this.token = mockToken;
          this.userInfo = mockUserInfo;
          localStorage.setItem("token", this.token);
          localStorage.setItem("userInfo", JSON.stringify(this.userInfo));
          return {
            code: 200,
            message: "登录成功（演示模式）",
            data: { token: mockToken, user: mockUserInfo },
          };
        }
        throw error;
      }
    },

    // 注册：只调用后端，不做模拟；错误由调用方（注册页）展示
    async register(userData) {
      const res = await registerApi(userData);
      return res;
    },

    // 获取当前用户信息
    async getUserInfo() {
      try {
        const res = await getUserInfoApi();
        this.userInfo = res.data;
        localStorage.setItem("userInfo", JSON.stringify(this.userInfo));
        return res;
      } catch (error) {
        console.error("获取用户信息失败:", error);
        throw error;
      }
    },

    // 更新个人资料（用户名、头像）
    async updateProfile(profileData) {
      try {
        const res = await updateProfileApi(profileData);
        // 后端返回新的token和用户信息
        if (res.data.token) {
          this.token = res.data.token;
          localStorage.setItem("token", this.token);
        }
        if (res.data.user) {
          this.userInfo = res.data.user;
          localStorage.setItem("userInfo", JSON.stringify(this.userInfo));
        }
        return res;
      } catch (error) {
        console.error("更新个人资料失败:", error);
        throw error;
      }
    },

    // 修改密码
    async changePassword(passwordData) {
      try {
        const res = await changePasswordApi(passwordData);
        return res;
      } catch (error) {
        console.error("修改密码失败:", error);
        throw error;
      }
    },

    // 上传头像
    async uploadAvatar(file) {
      try {
        const res = await uploadFileApi(file);
        // 获取上传后的URL
        const avatarUrl = res?.data?.url || res?.url;
        if (!avatarUrl) {
          throw new Error("上传失败，未返回文件URL");
        }
        return avatarUrl;
      } catch (error) {
        console.error("上传头像失败:", error);
        throw error;
      }
    },

    // 登出
    logout() {
      this.token = "";
      this.userInfo = {};
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
    },
  },
});
