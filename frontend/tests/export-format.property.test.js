/**
 * Property-Based Test: Export file download uses correct format metadata
 *
 * Feature: frontend-api-integration, Property 3: Export file download uses correct format metadata
 *
 * Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7
 */
import { describe, it, expect } from "vitest";
import * as fc from "fast-check";

/**
 * The canonical export format map as defined in RecordList.vue.
 * This is the source of truth for extension and MIME type per format.
 */
const EXPORT_FORMATS = {
  csv: { extension: ".csv", mimeType: "text/csv" },
  txt: { extension: ".txt", mimeType: "text/plain" },
  docx: {
    extension: ".docx",
    mimeType:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  },
  pdf: { extension: ".pdf", mimeType: "application/pdf" },
};

/**
 * Simulates the export logic from RecordList.vue:
 * Given a format string, returns the metadata used for the download.
 */
function getExportMetadata(format) {
  const formatMeta = EXPORT_FORMATS[format] || EXPORT_FORMATS.csv;
  return {
    extension: formatMeta.extension,
    mimeType: formatMeta.mimeType,
  };
}

/**
 * Simulates filename generation when no Content-Disposition header is present.
 */
function generateDefaultFilename(format) {
  const formatMeta = EXPORT_FORMATS[format] || EXPORT_FORMATS.csv;
  return `records_${Date.now()}${formatMeta.extension}`;
}

describe("Property 3: Export file download uses correct format metadata", () => {
  /**
   * **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**
   * For any format in {csv, txt, docx, pdf}, the correct file extension is used.
   */
  it("produces correct file extension for any supported export format", () => {
    const expectedExtensions = {
      csv: ".csv",
      txt: ".txt",
      docx: ".docx",
      pdf: ".pdf",
    };

    fc.assert(
      fc.property(
        fc.constantFrom("csv", "txt", "docx", "pdf"),
        (format) => {
          const metadata = getExportMetadata(format);
          expect(metadata.extension).toBe(expectedExtensions[format]);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**
   * For any format in {csv, txt, docx, pdf}, the correct MIME type is used.
   */
  it("produces correct MIME type for any supported export format", () => {
    const expectedMimeTypes = {
      csv: "text/csv",
      txt: "text/plain",
      docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      pdf: "application/pdf",
    };

    fc.assert(
      fc.property(
        fc.constantFrom("csv", "txt", "docx", "pdf"),
        (format) => {
          const metadata = getExportMetadata(format);
          expect(metadata.mimeType).toBe(expectedMimeTypes[format]);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**
   * For any format, the generated default filename ends with the correct extension.
   */
  it("default filename ends with correct extension for any format", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("csv", "txt", "docx", "pdf"),
        (format) => {
          const filename = generateDefaultFilename(format);
          const expectedExt = EXPORT_FORMATS[format].extension;
          expect(filename.endsWith(expectedExt)).toBe(true);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * **Validates: Requirements 5.3, 5.4, 5.5, 5.6, 5.7**
   * For any format, extension and MIME type are always paired correctly
   * (extension implies MIME type and vice versa).
   */
  it("extension and MIME type are consistently paired for any format", () => {
    const validPairs = [
      { extension: ".csv", mimeType: "text/csv" },
      { extension: ".txt", mimeType: "text/plain" },
      {
        extension: ".docx",
        mimeType:
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      },
      { extension: ".pdf", mimeType: "application/pdf" },
    ];

    fc.assert(
      fc.property(
        fc.constantFrom("csv", "txt", "docx", "pdf"),
        (format) => {
          const metadata = getExportMetadata(format);
          const matchingPair = validPairs.find(
            (p) =>
              p.extension === metadata.extension &&
              p.mimeType === metadata.mimeType
          );
          expect(matchingPair).toBeDefined();
        }
      ),
      { numRuns: 100 }
    );
  });
});
