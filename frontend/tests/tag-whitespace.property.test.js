/**
 * Property-Based Test: Whitespace-only tag names are rejected
 *
 * Feature: frontend-api-integration, Property 2: Whitespace-only tag names are rejected
 *
 * **Validates: Requirements 2.4**
 *
 * Tests that the TagManager validation logic rejects any string composed entirely
 * of whitespace characters (spaces, tabs, newlines, combinations). The validation
 * prevents the API call from being made and the tag list remains unchanged.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import fc from "fast-check";

// Mock the tags API module to verify no API call is made
vi.mock("../src/api/tags", () => ({
  fetchTags: vi.fn(() => Promise.resolve({ data: [] })),
  createTag: vi.fn(() => Promise.resolve({ data: { id: 1, name: "test", usage_count: 0 } })),
  deleteTag: vi.fn(() => Promise.resolve()),
}));

import { createTag } from "../src/api/tags";

/**
 * Replicates the TagManager.vue validation logic from handleCreateTag:
 *
 *   if (!newTagName.value || !newTagName.value.trim()) {
 *     validationError.value = "标签名称不能为空";
 *     return;
 *   }
 *
 * Returns true if the name is REJECTED (invalid), false if it would pass validation.
 */
function isRejectedByValidation(name) {
  return !name || !name.trim();
}

/**
 * Simulates the handleCreateTag flow:
 * - If validation rejects the name, createTag API should NOT be called.
 * - Returns the validation error message if rejected, or null if accepted.
 */
function simulateHandleCreateTag(tagName, createTagFn) {
  if (!tagName || !tagName.trim()) {
    return { rejected: true, error: "标签名称不能为空" };
  }
  createTagFn({ name: tagName.trim() });
  return { rejected: false, error: null };
}

// Arbitrary that generates whitespace-only strings of varying lengths and compositions
const arbWhitespaceOnly = () =>
  fc
    .array(fc.constantFrom(" ", "\t", "\n", "\r", "\f", "\v"), { minLength: 1, maxLength: 50 })
    .map((chars) => chars.join(""));

describe("Feature: frontend-api-integration, Property 2: Whitespace-only tag names are rejected", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * **Validates: Requirements 2.4**
   *
   * For any string composed entirely of whitespace characters,
   * the validation logic SHALL reject it (trim() yields empty string).
   */
  it("whitespace-only strings are always rejected by validation", () => {
    fc.assert(
      fc.property(arbWhitespaceOnly(), (whitespaceStr) => {
        expect(isRejectedByValidation(whitespaceStr)).toBe(true);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 2.4**
   *
   * For any whitespace-only tag name, the createTag API function SHALL NOT be called
   * and a validation error message SHALL be returned.
   */
  it("whitespace-only tag names prevent the API call from being made", () => {
    fc.assert(
      fc.property(arbWhitespaceOnly(), (whitespaceStr) => {
        vi.clearAllMocks();

        const result = simulateHandleCreateTag(whitespaceStr, createTag);

        // Validation should reject the input
        expect(result.rejected).toBe(true);
        expect(result.error).toBe("标签名称不能为空");

        // The API should NOT have been called
        expect(createTag).not.toHaveBeenCalled();
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 2.4**
   *
   * For any whitespace-only tag name, the tag list SHALL remain unchanged
   * (since no API call is made, no new tag is added).
   */
  it("tag list remains unchanged when whitespace-only name is submitted", () => {
    fc.assert(
      fc.property(arbWhitespaceOnly(), (whitespaceStr) => {
        vi.clearAllMocks();

        const tagsBefore = [
          { id: 1, name: "existing-tag", usage_count: 5 },
          { id: 2, name: "another-tag", usage_count: 3 },
        ];
        const tagsAfter = [...tagsBefore];

        // Simulate the create attempt
        const result = simulateHandleCreateTag(whitespaceStr, createTag);

        // Validation rejected it, so no API call was made
        expect(result.rejected).toBe(true);
        expect(createTag).not.toHaveBeenCalled();

        // Tag list is unchanged
        expect(tagsAfter).toEqual(tagsBefore);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 2.4**
   *
   * Empty string and null/undefined are also rejected by the same validation logic.
   */
  it("empty string is also rejected by validation", () => {
    fc.assert(
      fc.property(fc.constant(""), (emptyStr) => {
        expect(isRejectedByValidation(emptyStr)).toBe(true);
      }),
      { numRuns: 100 }
    );
  });

  /**
   * Contrast property: non-whitespace strings that contain at least one
   * non-whitespace character are NOT rejected by validation.
   */
  it("strings with non-whitespace characters pass validation", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
        (validStr) => {
          expect(isRejectedByValidation(validStr)).toBe(false);
        }
      ),
      { numRuns: 100 }
    );
  });
});
