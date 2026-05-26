/**
 * 文件下载工具函数
 */

/**
 * 通过 Blob 触发浏览器文件下载
 * @param {Blob} blob - 文件数据
 * @param {string} filename - 建议的文件名
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
