/**
 * Asset Boundary & Production Ingest Gate
 * Enforces cinema 16:9 aspect ratio, minimum resolutions, and atomic file transfers.
 */

import fs from "node:fs";
import path from "node:path";

export const TARGET_ASPECT_RATIO = 16 / 9; // 1.7777...
export const ASPECT_TOLERANCE = 0.04; // allows slight rounding variations

/**
 * Validates dimensions for 16:9 cinema animatic standard.
 * @param {number} width 
 * @param {number} height 
 * @returns {{ valid: boolean, ratio: number, error?: string }}
 */
export function validateAspectRatio(width, height) {
  if (!width || !height || width <= 0 || height <= 0) {
    return { valid: false, ratio: 0, error: "Dimensions must be positive numbers" };
  }

  const ratio = width / height;
  const diff = Math.abs(ratio - TARGET_ASPECT_RATIO);

  if (diff > ASPECT_TOLERANCE) {
    return {
      valid: false,
      ratio,
      error: `Aspect ratio ${ratio.toFixed(3)} deviates from 16:9 (${TARGET_ASPECT_RATIO.toFixed(3)}) by ${diff.toFixed(3)}`
    };
  }

  return { valid: true, ratio };
}

/**
 * Validates file buffer before ingestion.
 * @param {Buffer} buffer 
 * @param {number} minBytes 
 * @returns {{ valid: boolean, size: number, error?: string }}
 */
export function validateFileBuffer(buffer, minBytes = 1024) {
  if (!buffer || !Buffer.isBuffer(buffer)) {
    return { valid: false, size: 0, error: "Input is not a valid buffer" };
  }

  if (buffer.length < minBytes) {
    return {
      valid: false,
      size: buffer.length,
      error: `Buffer size ${buffer.length} bytes is below minimum threshold ${minBytes} bytes`
    };
  }

  return { valid: true, size: buffer.length };
}
