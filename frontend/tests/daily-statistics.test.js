/**
 * Unit Tests: DailyStatistics statistics integration
 *
 * Validates: Requirements 7.1, 7.2, 7.6
 *
 * Tests that DailyStatistics.vue:
 * - Calls getTotalWords and getAvgTime on mount
 * - Uses fallback values (0 for total_words, 1 for avg_time) when API fails
 * - Calls exportReport with date range params when export button is clicked
 *
 * @vitest-environment happy-dom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';

// Mock echarts before anything else
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    dispose: vi.fn(),
    resize: vi.fn(),
  })),
}));

// Mock the statistics API module
vi.mock('@/api/statistics', () => ({
  getDailyStats: vi.fn(() => Promise.resolve({ code: 200, data: {} })),
  getPlatformStats: vi.fn(() => Promise.resolve({ code: 200, data: [] })),
  getTypeStats: vi.fn(() => Promise.resolve({ code: 200, data: [] })),
  getKeywordStats: vi.fn(() => Promise.resolve({ code: 200, data: [] })),
  getTotalWords: vi.fn(() => Promise.resolve({ code: 200, data: 5000 })),
  getAvgTime: vi.fn(() => Promise.resolve({ code: 200, data: 30 })),
  exportReport: vi.fn(() => Promise.resolve({ data: new Blob(['test'], { type: 'text/csv' }) })),
}));

// Mock the download utility
vi.mock('@/utils/download', () => ({
  downloadBlob: vi.fn(),
}));

// Mock the KeywordTable component
vi.mock('@/components/Statistics/KeywordTable.vue', () => ({
  default: {
    name: 'KeywordTable',
    template: '<div class="mock-keyword-table"></div>',
    props: ['keywords', 'startDate', 'endDate'],
  },
}));

// Mock element-plus components and icons
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

import { getTotalWords, getAvgTime, exportReport } from '@/api/statistics';
import { downloadBlob } from '@/utils/download';
import { ElMessage } from 'element-plus';

describe('DailyStatistics statistics integration', () => {
  let DailyStatistics;

  beforeEach(async () => {
    vi.clearAllMocks();
    // Dynamically import after mocks are set up
    const mod = await import('@/views/statistics/DailyStatistics.vue');
    DailyStatistics = mod.default;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * Validates: Requirement 7.1
   * WHEN the statistics page loads, THE DailyStatistics view SHALL call
   * the Statistics_API getTotalWords function
   */
  it('calls getTotalWords on mount', async () => {
    const wrapper = mount(DailyStatistics, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot /><slot name="header" /></div>' },
          'el-select': { template: '<div><slot /></div>' },
          'el-option': { template: '<div />' },
          'el-date-picker': { template: '<div />' },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'Search': true,
          'Download': true,
          'Document': true,
          'Calendar': true,
          'Timer': true,
          'TrendCharts': true,
        },
      },
    });

    await flushPromises();

    expect(getTotalWords).toHaveBeenCalled();
    expect(getTotalWords).toHaveBeenCalledWith(
      expect.objectContaining({
        start_date: expect.any(String),
        end_date: expect.any(String),
      })
    );

    wrapper.unmount();
  });

  /**
   * Validates: Requirement 7.2
   * WHEN the statistics page loads, THE DailyStatistics view SHALL call
   * the Statistics_API getAvgTime function
   */
  it('calls getAvgTime on mount', async () => {
    const wrapper = mount(DailyStatistics, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot /><slot name="header" /></div>' },
          'el-select': { template: '<div><slot /></div>' },
          'el-option': { template: '<div />' },
          'el-date-picker': { template: '<div />' },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'Search': true,
          'Download': true,
          'Document': true,
          'Calendar': true,
          'Timer': true,
          'TrendCharts': true,
        },
      },
    });

    await flushPromises();

    expect(getAvgTime).toHaveBeenCalled();
    expect(getAvgTime).toHaveBeenCalledWith(
      expect.objectContaining({
        start_date: expect.any(String),
        end_date: expect.any(String),
      })
    );

    wrapper.unmount();
  });

  /**
   * Validates: Requirement 7.6
   * IF the Statistics_API request for total words fails, THEN THE DailyStatistics
   * view SHALL display 0 as the fallback value
   */
  it('uses fallback value 0 for totalWords when getTotalWords API fails', async () => {
    getTotalWords.mockRejectedValueOnce(new Error('Network error'));

    const wrapper = mount(DailyStatistics, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot /><slot name="header" /></div>' },
          'el-select': { template: '<div><slot /></div>' },
          'el-option': { template: '<div />' },
          'el-date-picker': { template: '<div />' },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'Search': true,
          'Download': true,
          'Document': true,
          'Calendar': true,
          'Timer': true,
          'TrendCharts': true,
        },
      },
    });

    await flushPromises();

    // The component should display '0字' as fallback for total words
    expect(wrapper.text()).toContain('0字');

    wrapper.unmount();
  });

  /**
   * Validates: Requirement 7.6 (fallback for avg_time)
   * IF the Statistics_API request for avg_time fails, THEN THE DailyStatistics
   * view SHALL display 1 as the fallback value
   */
  it('uses fallback value 1 for avgCreationTime when getAvgTime API fails', async () => {
    getAvgTime.mockRejectedValueOnce(new Error('Network error'));

    const wrapper = mount(DailyStatistics, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot /><slot name="header" /></div>' },
          'el-select': { template: '<div><slot /></div>' },
          'el-option': { template: '<div />' },
          'el-date-picker': { template: '<div />' },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'Search': true,
          'Download': true,
          'Document': true,
          'Calendar': true,
          'Timer': true,
          'TrendCharts': true,
        },
      },
    });

    await flushPromises();

    // The component should display '1分钟' as fallback for avg creation time
    expect(wrapper.text()).toContain('1分钟');

    wrapper.unmount();
  });

  /**
   * Validates: Requirement 7.1, 7.2 (combined - export button)
   * WHEN a user clicks the export report button, THE DailyStatistics view SHALL
   * call the Statistics_API exportReport function with the current date range params
   */
  it('calls exportReport with date range params when export button is clicked', async () => {
    const wrapper = mount(DailyStatistics, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot /><slot name="header" /></div>' },
          'el-select': { template: '<div><slot /></div>' },
          'el-option': { template: '<div />' },
          'el-date-picker': { template: '<div />' },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>', props: ['type'] },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'Search': true,
          'Download': true,
          'Document': true,
          'Calendar': true,
          'Timer': true,
          'TrendCharts': true,
        },
      },
    });

    await flushPromises();

    // Clear all mock calls from mount so we can isolate the export call
    exportReport.mockClear();
    getTotalWords.mockClear();
    getAvgTime.mockClear();

    // Find the export button - it contains "导出报告" text
    const buttons = wrapper.findAll('button');
    const exportButton = buttons.find((btn) => btn.text().includes('导出报告'));
    expect(exportButton).toBeTruthy();

    await exportButton.trigger('click');
    await flushPromises();

    expect(exportReport).toHaveBeenCalled();
    expect(exportReport).toHaveBeenCalledWith(
      expect.objectContaining({
        start_date: expect.any(String),
        end_date: expect.any(String),
      })
    );

    wrapper.unmount();
  });
});
