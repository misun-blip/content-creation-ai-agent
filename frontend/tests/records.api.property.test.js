/**
 * Property-Based Test: Records API request construction correctness
 *
 * Feature: frontend-api-integration, Property 1: API module request construction correctness (Records)
 *
 * Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as fc from "fast-check";

// Mock the request instance before importing the module
vi.mock("../src/api/index", () => {
  const mockRequest = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  };
  return { default: mockRequest };
});

import request from "../src/api/index";
import {
  fetchRecords,
  createRecord,
  getRecord,
  updateRecord,
  deleteRecord,
  fetchVersions,
  createVersion,
  getVersion,
  restoreVersion,
  deleteVersion,
  exportRecords,
} from "../src/api/records";

describe("Property 1: API module request construction correctness (Records)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * **Validates: Requirements 3.1**
   * fetchRecords sends GET to /api/v1/records/ with filter params
   */
  it("fetchRecords constructs correct GET request with filter params", () => {
    fc.assert(
      fc.property(
        fc.record({
          keyword: fc.string({ minLength: 0, maxLength: 50 }),
          platform: fc.constantFrom("douyin", "xiaohongshu", "wechat", "bilibili"),
          status: fc.constantFrom("draft", "published", "archived"),
          start_date: fc.integer({ min: 946684800000, max: 4102444800000 }).map((ts) => new Date(ts).toISOString().slice(0, 10)),
          end_date: fc.integer({ min: 946684800000, max: 4102444800000 }).map((ts) => new Date(ts).toISOString().slice(0, 10)),
          page: fc.integer({ min: 1, max: 1000 }),
          page_size: fc.integer({ min: 1, max: 100 }),
        }),
        (params) => {
          fetchRecords(params);
          expect(request.get).toHaveBeenCalledWith("/api/v1/records/", { params });
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.2**
   * createRecord sends POST to /api/v1/records/ with record data
   */
  it("createRecord constructs correct POST request with body data", () => {
    fc.assert(
      fc.property(
        fc.record({
          title: fc.string({ minLength: 1, maxLength: 100 }),
          platform: fc.constantFrom("douyin", "xiaohongshu", "wechat", "bilibili"),
          content: fc.string({ minLength: 0, maxLength: 500 }),
          status: fc.constantFrom("draft", "published", "archived"),
        }),
        (data) => {
          createRecord(data);
          expect(request.post).toHaveBeenCalledWith("/api/v1/records/", data);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.3**
   * getRecord sends GET to /api/v1/records/{recordId}
   */
  it("getRecord constructs correct GET request with interpolated recordId", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100000 }), (recordId) => {
        getRecord(recordId);
        expect(request.get).toHaveBeenCalledWith(`/api/v1/records/${recordId}`);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.4**
   * updateRecord sends PUT to /api/v1/records/{recordId} with data
   */
  it("updateRecord constructs correct PUT request with recordId and body", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100000 }),
        fc.record({
          title: fc.string({ minLength: 1, maxLength: 100 }),
          content: fc.string({ minLength: 0, maxLength: 500 }),
        }),
        (recordId, data) => {
          updateRecord(recordId, data);
          expect(request.put).toHaveBeenCalledWith(
            `/api/v1/records/${recordId}`,
            data
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.5**
   * deleteRecord sends DELETE to /api/v1/records/{recordId}
   */
  it("deleteRecord constructs correct DELETE request with recordId", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100000 }), (recordId) => {
        deleteRecord(recordId);
        expect(request.delete).toHaveBeenCalledWith(`/api/v1/records/${recordId}`);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.6**
   * fetchVersions sends GET to /api/v1/records/{recordId}/versions
   */
  it("fetchVersions constructs correct GET request with recordId", () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100000 }), (recordId) => {
        fetchVersions(recordId);
        expect(request.get).toHaveBeenCalledWith(
          `/api/v1/records/${recordId}/versions`
        );
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.7**
   * createVersion sends POST to /api/v1/records/{recordId}/versions with data
   */
  it("createVersion constructs correct POST request with recordId and body", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100000 }),
        fc.record({
          content: fc.string({ minLength: 1, maxLength: 500 }),
          change_note: fc.string({ minLength: 0, maxLength: 200 }),
        }),
        (recordId, data) => {
          createVersion(recordId, data);
          expect(request.post).toHaveBeenCalledWith(
            `/api/v1/records/${recordId}/versions`,
            data
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.8**
   * getVersion sends GET to /api/v1/records/{recordId}/versions/{versionId}
   */
  it("getVersion constructs correct GET request with recordId and versionId", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100000 }),
        fc.integer({ min: 1, max: 100000 }),
        (recordId, versionId) => {
          getVersion(recordId, versionId);
          expect(request.get).toHaveBeenCalledWith(
            `/api/v1/records/${recordId}/versions/${versionId}`
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.9**
   * restoreVersion sends POST to /api/v1/records/{recordId}/versions/{versionId}/restore
   */
  it("restoreVersion constructs correct POST request with recordId and versionId", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100000 }),
        fc.integer({ min: 1, max: 100000 }),
        (recordId, versionId) => {
          restoreVersion(recordId, versionId);
          expect(request.post).toHaveBeenCalledWith(
            `/api/v1/records/${recordId}/versions/${versionId}/restore`
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.10**
   * deleteVersion sends DELETE to /api/v1/records/{recordId}/versions/{versionId}
   */
  it("deleteVersion constructs correct DELETE request with recordId and versionId", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 100000 }),
        fc.integer({ min: 1, max: 100000 }),
        (recordId, versionId) => {
          deleteVersion(recordId, versionId);
          expect(request.delete).toHaveBeenCalledWith(
            `/api/v1/records/${recordId}/versions/${versionId}`
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 3.11**
   * exportRecords sends GET to /api/v1/records/export/{format} with responseType blob
   */
  it("exportRecords constructs correct GET request with format and blob responseType", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("csv", "txt", "docx", "pdf"),
        fc.record({
          keyword: fc.string({ minLength: 0, maxLength: 50 }),
          start_date: fc.integer({ min: 946684800000, max: 4102444800000 }).map((ts) => new Date(ts).toISOString().slice(0, 10)),
          end_date: fc.integer({ min: 946684800000, max: 4102444800000 }).map((ts) => new Date(ts).toISOString().slice(0, 10)),
        }),
        (format, params) => {
          exportRecords(format, params);
          expect(request.get).toHaveBeenCalledWith(
            `/api/v1/records/export/${format}`,
            {
              params,
              responseType: "blob",
            }
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
