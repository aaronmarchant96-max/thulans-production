import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { validateAspectRatio, validateFileBuffer } from "../lib/assetBoundary.mjs";

describe("Gate 3: Asset Boundary & 16:9 Cinema Aspect Gate", () => {
  it("passes canonical 16:9 resolutions", () => {
    const validDims = [
      [1920, 1080],
      [3840, 2160],
      [1280, 720],
      [2560, 1440]
    ];

    for (const [w, h] of validDims) {
      const res = validateAspectRatio(w, h);
      assert.equal(res.valid, true, `${w}x${h} must pass 16:9 gate`);
    }
  });

  it("catches non-16:9 aspect ratios (square, portrait, 4:3)", () => {
    const invalidDims = [
      [1080, 1080], // 1:1 square
      [1080, 1920], // 9:16 vertical mobile
      [1024, 768],  // 4:3 legacy
      [800, 600]    // 4:3
    ];

    for (const [w, h] of invalidDims) {
      const res = validateAspectRatio(w, h);
      assert.equal(res.valid, false, `${w}x${h} must fail 16:9 gate`);
      assert.ok(res.error, "Error message must report deviation");
    }
  });

  it("validates file buffer payload size and catches empty/corrupt files", () => {
    const emptyBuffer = Buffer.alloc(0);
    const tinyBuffer = Buffer.alloc(256);
    const validBuffer = Buffer.alloc(2048);

    assert.equal(validateFileBuffer(emptyBuffer).valid, false, "Empty buffer must fail");
    assert.equal(validateFileBuffer(tinyBuffer, 1024).valid, false, "Tiny buffer under 1KB must fail");
    assert.equal(validateFileBuffer(validBuffer, 1024).valid, true, "2KB buffer must pass");
  });
});
