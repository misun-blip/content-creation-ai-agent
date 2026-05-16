/**
 * Property-Based Test: Statistics API Request Construction Correctness
 *
 * Feature: frontend-api-integration, Property 1: API module request construction correctness (Statistics)
 *
 * Validates: Requirements 6.1, 6.2, 6.3
 *
 * Uses fast-check to generate random date strings for start_date/end_date and verifies
 * that getTotalWords, getAvgTime, and exportReport construct correct requests.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import fc from 'fast-check';

// Mock the @/api/index module before importing the statistics functions
vi.mock('@/api/index', () => {
  return {
    default: vi.fn((config) => Promise.resolve(config)),
  };
});

import request from '@/api/index';
import { getTotalWords, getAvgTime, exportReport } from '@/api/statistics';

// Arbitrary for generating date strings in YYYY-MM-DD format
const arbDateString = () =>
  fc.tuple(
    fc.integer({ min: 2000, max: 2099 }),
    fc.integer({ min: 1, max: 12 }),
    fc.integer({ min: 1, max: 28 })
  ).map(([y, m, d]) => `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`);

describe('Feature: frontend-api-integration, Property 1: API module request construction correctness (Statistics)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * **Validates: Requirements 6.1**
   *
   * For any valid start_date and end_date, getTotalWords SHALL send a GET request
   * to /api/v1/statistics/total_words with the correct params.
   */
  it('getTotalWords constructs correct request for any date params', () => {
    fc.assert(
      fc.property(
        arbDateString(),
        arbDateString(),
        (startDate, endDate) => {
          vi.clearAllMocks();

          const params = { start_date: startDate, end_date: endDate };
          getTotalWords(params);

          expect(request).toHaveBeenCalledTimes(1);
          const callArg = request.mock.calls[0][0];

          expect(callArg.url).toBe('/api/v1/statistics/total_words');
          expect(callArg.method).toBe('get');
          expect(callArg.params).toEqual(params);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 6.1**
   *
   * getTotalWords SHALL also work with no params (both start_date and end_date are optional).
   */
  it('getTotalWords constructs correct request with undefined params', () => {
    fc.assert(
      fc.property(
        fc.constant(undefined),
        (params) => {
          vi.clearAllMocks();

          getTotalWords(params);

          expect(request).toHaveBeenCalledTimes(1);
          const callArg = request.mock.calls[0][0];

          expect(callArg.url).toBe('/api/v1/statistics/total_words');
          expect(callArg.method).toBe('get');
          expect(callArg.params).toBeUndefined();
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 6.2**
   *
   * For any valid start_date and end_date, getAvgTime SHALL send a GET request
   * to /api/v1/statistics/avg_time with the correct params.
   */
  it('getAvgTime constructs correct request for any date params', () => {
    fc.assert(
      fc.property(
        arbDateString(),
        arbDateString(),
        (startDate, endDate) => {
          vi.clearAllMocks();

          const params = { start_date: startDate, end_date: endDate };
          getAvgTime(params);

          expect(request).toHaveBeenCalledTimes(1);
          const callArg = request.mock.calls[0][0];

          expect(callArg.url).toBe('/api/v1/statistics/avg_time');
          expect(callArg.method).toBe('get');
          expect(callArg.params).toEqual(params);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 6.2**
   *
   * getAvgTime SHALL also work with no params (both start_date and end_date are optional).
   */
  it('getAvgTime constructs correct request with undefined params', () => {
    fc.assert(
      fc.property(
        fc.constant(undefined),
        (params) => {
          vi.clearAllMocks();

          getAvgTime(params);

          expect(request).toHaveBeenCalledTimes(1);
          const callArg = request.mock.calls[0][0];

          expect(callArg.url).toBe('/api/v1/statistics/avg_time');
          expect(callArg.method).toBe('get');
          expect(callArg.params).toBeUndefined();
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 6.3**
   *
   * For any valid start_date and end_date, exportReport SHALL send a GET request
   * to /api/v1/statistics/export_report with params and responseType: 'blob'.
   */
  it('exportReport constructs correct request with date params and blob responseType', () => {
    fc.assert(
      fc.property(
        arbDateString(),
        arbDateString(),
        (startDate, endDate) => {
          vi.clearAllMocks();

          const params = { start_date: startDate, end_date: endDate };
          exportReport(params);

          expect(request).toHaveBeenCalledTimes(1);
          const callArg = request.mock.calls[0][0];

          expect(callArg.url).toBe('/api/v1/statistics/export_report');
          expect(callArg.method).toBe('get');
          expect(callArg.params).toEqual(params);
          expect(callArg.responseType).toBe('blob');
        }
      ),
      { numRuns: 100 }
    );
  });
});
