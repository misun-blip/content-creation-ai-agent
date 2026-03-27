// 日期处理工具函数

/**
 * 格式化日期为指定格式
 * @param {Date|string|number} date - 日期对象、字符串或时间戳
 * @param {string} format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date, format = "YYYY-MM-DD HH:mm:ss") => {
  const d = new Date(date);

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return format
    .replace("YYYY", year)
    .replace("MM", month)
    .replace("DD", day)
    .replace("HH", hours)
    .replace("mm", minutes)
    .replace("ss", seconds);
};

/**
 * 获取相对时间描述
 * @param {Date|string|number} date - 日期对象、字符串或时间戳
 * @returns {string} 相对时间描述，如 "3分钟前"、"1小时前"
 */
export const getRelativeTime = (date) => {
  const now = new Date();
  const target = new Date(date);
  const diff = now - target;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) {
    return "刚刚";
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    return formatDate(date, "YYYY-MM-DD");
  }
};

/**
 * 获取今天的开始时间
 * @returns {Date} 今天00:00:00的Date对象
 */
export const getTodayStart = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
};

/**
 * 获取今天的结束时间
 * @returns {Date} 今天23:59:59的Date对象
 */
export const getTodayEnd = () => {
  const today = new Date();
  today.setHours(23, 59, 59, 999);
  return today;
};

/**
 * 获取本周的开始时间
 * @returns {Date} 本周一00:00:00的Date对象
 */
export const getWeekStart = () => {
  const today = new Date();
  const day = today.getDay() || 7; // 调整为周一为1，周日为7
  const diff = today.getDate() - day + 1;
  const weekStart = new Date(today.setDate(diff));
  weekStart.setHours(0, 0, 0, 0);
  return weekStart;
};

/**
 * 获取本月的开始时间
 * @returns {Date} 本月1号00:00:00的Date对象
 */
export const getMonthStart = () => {
  const today = new Date();
  const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
  monthStart.setHours(0, 0, 0, 0);
  return monthStart;
};
