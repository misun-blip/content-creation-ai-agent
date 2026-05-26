/**
 * Property-Based Test: Tags API request construction correctness
 *
 * Feature: frontend-api-integration, Property 1: API module request construction correctness (Tags)
 *
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4
 *
 * Uses fast-check to generate random positive integers for tagId and random non-empty
 * strings for query parameter. Mocks the request instance and verifies URL path,
 * HTTP method, and params are correctly constructed for each function.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as fc from "fast-check";

// Mock the @/api/index module before importing the tags module
vi.mock("@/api/index", () => {
  const mockRequest = {
    get: vi.fn().mockResolvedValue({}),
    post: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  };
  return { default: mockRequest };
});

import request from "@/api/index";
import { fetchTags, createTag, getTag, deleteTag } from "@/api/tags";

describe("Feature: frontend-api-integration, Property 1: API module request construction correctness (Tags)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetchTags sends GET to /api/v1/tags with correct params for any query string", () => {
    /** Validates: Requirements 1.1 */
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        (query) => {
          vi.clearAllMocks();
          const params = { q: query };
          fetchTags(params);

          expect(request.get).toHaveBeenCalledTimes(1);
          expect(request.get).toHaveBeenCalledWith("/api/v1/tags", { params });
        }
      ),
      { numRuns: 100 }
    );
  });

  it("fetchTags sends GET to /api/v1/tags with no params when called without arguments", () => {
    /** Validates: Requirements 1.1 */
    fetchTags();

    expect(request.get).toHaveBeenCalledTimes(1);
    expect(request.get).toHaveBeenCalledWith("/api/v1/tags", { params: undefined });
  });

  it("createTag sends POST to /api/v1/tags with correct body for any non-empty tag name", () => {
    /** Validates: Requirements 1.2 */
    fc.assert(
      fc.property(
        fc.string({ minLength: 1 }),
        (name) => {
          vi.clearAllMocks();
          const data = { name };
          createTag(data);

          expect(request.post).toHaveBeenCalledTimes(1);
          expect(request.post).toHaveBeenCalledWith("/api/v1/tags", data);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("getTag sends GET to /api/v1/tags/{tagId} for any positive integer tagId", () => {
    /** Validates: Requirements 1.3 */
    fc.assert(
      fc.property(
        fc.integer({ min: 1 }),
        (tagId) => {
          vi.clearAllMocks();
          getTag(tagId);

          expect(request.get).toHaveBeenCalledTimes(1);
          expect(request.get).toHaveBeenCalledWith(`/api/v1/tags/${tagId}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("deleteTag sends DELETE to /api/v1/tags/{tagId} for any positive integer tagId", () => {
    /** Validates: Requirements 1.4 */
    fc.assert(
      fc.property(
        fc.integer({ min: 1 }),
        (tagId) => {
          vi.clearAllMocks();
          deleteTag(tagId);

          expect(request.delete).toHaveBeenCalledTimes(1);
          expect(request.delete).toHaveBeenCalledWith(`/api/v1/tags/${tagId}`);
        }
      ),
      { numRuns: 100 }
    );
  });
});
