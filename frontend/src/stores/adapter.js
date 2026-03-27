import { defineStore } from 'pinia';
import { adaptContent, getPlatforms } from '@/api/adapter';

/**
 * 平台适配状态管理
 */
export const useAdapterStore = defineStore('adapter', {
  state: () => ({
    // 平台列表
    platforms: [],
    // 选中的平台
    selectedPlatform: 'douyin',
    // 原始内容
    originalContent: '',
    // 适配结果
    adaptedResult: null,
    // 加载状态
    loading: false,
    // 错误信息
    error: null,
    // 错误类型
    errorType: null, // 'network', 'validation', 'server', 'unknown'
    // 重试次数
    retryCount: 0,
    // 最大重试次数
    maxRetries: 3,
  }),

  getters: {
    /**
     * 获取当前选中平台的配置
     */
    selectedPlatformConfig: (state) => {
      return state.platforms.find(p => p.code === state.selectedPlatform);
    },
    
    /**
     * 是否有错误
     */
    hasError: (state) => {
      return state.error !== null;
    },
    
    /**
     * 是否可以重试
     */
    canRetry: (state) => {
      return state.retryCount < state.maxRetries;
    },
    
    /**
     * 获取用户友好的错误消息
     */
    userFriendlyError: (state) => {
      if (!state.error) return '';
      
      switch (state.errorType) {
        case 'network':
          return '网络连接失败，请检查您的网络设置';
        case 'validation':
          return '输入数据验证失败，请检查您的输入';
        case 'server':
          return '服务器错误，请稍后重试';
        default:
          return state.error || '发生未知错误';
      }
    },
  },

  actions: {
    /**
     * 获取平台列表
     */
    async fetchPlatforms() {
      try {
        this.loading = true;
        this.error = null;
        this.errorType = null;
        
        const response = await getPlatforms();
        this.platforms = response.data || [];
        
        // 重置重试计数
        this.retryCount = 0;
      } catch (error) {
        this.error = error.message || '获取平台列表失败';
        this.errorType = this._classifyError(error);
        this.retryCount++;
        
        console.error('获取平台列表失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 适配内容
     * @param {string} content - 原始内容
     * @param {string} platform - 目标平台
     * @param {string} [title] - 标题
     * @param {Array<string>} [tags] - 标签列表
     * @param {boolean} [autoFormat] - 是否自动排版
     */
    async adaptContent(content, platform, title = null, tags = null, autoFormat = true) {
      try {
        this.loading = true;
        this.error = null;
        this.errorType = null;
        
        const response = await adaptContent({
          content,
          platform,
          title,
          tags,
          auto_format: autoFormat
        });
        
        this.adaptedResult = response.data;
        
        // 重置重试计数
        this.retryCount = 0;
        
        return response.data;
      } catch (error) {
        this.error = error.message || '内容适配失败';
        this.errorType = this._classifyError(error);
        this.retryCount++;
        
        console.error('内容适配失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 重试上一次操作
     */
    async retryLastOperation() {
      if (!this.canRetry) {
        throw new Error('已达到最大重试次数');
      }
      
      // 根据当前状态决定重试哪个操作
      if (this.originalContent) {
        return this.adaptContent(
          this.originalContent,
          this.selectedPlatform
        );
      } else {
        return this.fetchPlatforms();
      }
    },

    /**
     * 设置选中的平台
     * @param {string} platform - 平台代码
     */
    setPlatform(platform) {
      this.selectedPlatform = platform;
      // 清空之前的适配结果
      this.adaptedResult = null;
    },

    /**
     * 设置原始内容
     * @param {string} content - 原始内容
     */
    setOriginalContent(content) {
      this.originalContent = content;
    },

    /**
     * 清空适配结果
     */
    clearAdaptedResult() {
      this.adaptedResult = null;
    },

    /**
     * 清空错误
     */
    clearError() {
      this.error = null;
      this.errorType = null;
      this.retryCount = 0;
    },
    
    /**
     * 分类错误类型
     * @private
     */
    _classifyError(error) {
      if (!error) return 'unknown';
      
      // 网络错误
      if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
        return 'network';
      }
      
      // HTTP状态码错误
      if (error.response) {
        const status = error.response.status;
        if (status >= 400 && status < 500) {
          return 'validation';
        } else if (status >= 500) {
          return 'server';
        }
      }
      
      // 默认未知错误
      return 'unknown';
    },
  },
});
