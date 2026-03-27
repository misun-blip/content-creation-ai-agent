// 数据格式化工具函数

/**
 * 格式化数字，添加千分位分隔符
 * @param {number|string} num - 要格式化的数字
 * @returns {string} 格式化后的数字字符串
 */
export const formatNumber = (num) => {
  return Number(num).toLocaleString();
};

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @param {number} decimals - 小数位数，默认2
 * @returns {string} 格式化后的文件大小字符串
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

/**
 * 格式化百分比
 * @param {number} value - 要格式化的值
 * @param {number} decimals - 小数位数，默认2
 * @returns {string} 格式化后的百分比字符串
 */
export const formatPercent = (value, decimals = 2) => {
  return (value * 100).toFixed(decimals) + "%";
};

/**
 * 格式化金额
 * @param {number|string} amount - 金额
 * @param {string} currency - 货币符号，默认 '¥'
 * @param {number} decimals - 小数位数，默认2
 * @returns {string} 格式化后的金额字符串
 */
export const formatCurrency = (amount, currency = "¥", decimals = 2) => {
  const num = Number(amount);
  return currency + num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

/**
 * 截断文本，超出部分显示省略号
 * @param {string} text - 要截断的文本
 * @param {number} maxLength - 最大长度
 * @returns {string} 截断后的文本
 */
export const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
};

/**
 * 格式化手机号，中间4位显示为星号
 * @param {string} phone - 手机号
 * @returns {string} 格式化后的手机号
 */
export const formatPhone = (phone) => {
  if (!phone || phone.length !== 11) return phone;
  return phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
};

/**
 * 格式化邮箱，部分显示为星号
 * @param {string} email - 邮箱地址
 * @returns {string} 格式化后的邮箱
 */
export const formatEmail = (email) => {
  if (!email) return email;
  const parts = email.split("@");
  if (parts.length !== 2) return email;
  const username = parts[0];
  const domain = parts[1];

  if (username.length <= 3) {
    return username.substring(0, 1) + "***@" + domain;
  } else {
    return username.substring(0, 3) + "***@" + domain;
  }
};

/**
 * 格式化URL，隐藏协议和部分路径
 * @param {string} url - URL地址
 * @returns {string} 格式化后的URL
 */
export const formatUrl = (url) => {
  if (!url) return url;
  // 移除协议
  let formatted = url.replace(/^https?:\/\//, "");
  // 限制长度
  if (formatted.length > 30) {
    formatted =
      formatted.substring(0, 15) +
      "..." +
      formatted.substring(formatted.length - 10);
  }
  return formatted;
};
