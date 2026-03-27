import request from "./index";

// 用户登录
export function login(data) {
  return request({
    url: "/api/v1/auth/login",
    method: "post",
    data,
  });
}

// 用户注册
export function register(data) {
  return request({
    url: "/api/v1/auth/register",
    method: "post",
    data,
  });
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: "/api/v1/auth/me",
    method: "get",
  });
}

// 修改密码
export function changePassword(data) {
  return request({
    url: "/api/v1/auth/password",
    method: "put",
    data,
  });
}

// 更新个人资料（用户名、头像等）
export function updateProfile(data) {
  return request({
    url: "/api/v1/auth/profile",
    method: "put",
    data,
  });
}