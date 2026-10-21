import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { validateBadgeSyntax, renderBadgeSvg } from "../lib/badgeCompositor.mjs";

describe("Gate 2: Tactical Badge & Caption Plate Validator", () => {
  it("passes canonical tactical badges", () => {
    const validBadges = [
      "THE WELDED / EASTSHAFT-6A112",
      "THE THROAT / LIFT-SECTOR-01",
      "THIRD BELL / PRESSURE-RUPTURE-9",
      "THE ELEVENTH BELL / HOIST-GEAR-7"
    ];

    for (const badge of validBadges) {
      const res = validateBadgeSyntax(badge);
      assert.equal(res.valid, true, `Badge "${badge}" should pass`);
    }
  });

  it("catches malformed, lowercase, or non-sector badges", () => {
    const invalidBadges = [
      "the welded / eastshaft",      // lowercase
      "THE WELDED - SECTOR 1",       // missing slash format
      "THE WELDED /",                // missing sector
      "/ EASTSHAFT-12",              // missing title
      "",                            // empty
      null                           // non-string
    ];

    for (const badge of invalidBadges) {
      const res = validateBadgeSyntax(badge);
      assert.equal(res.valid, false, `Badge "${badge}" should fail`);
      assert.ok(res.error, "Error message must be provided");
    }
  });

  it("renders valid SVG overlay containing title and sector callsign", () => {
    const svg = renderBadgeSvg("THE WELDED / EASTSHAFT-6A112", 1920, 1080);
    assert.ok(svg.includes("THE WELDED"), "SVG must include title");
    assert.ok(svg.includes("EASTSHAFT-6A112"), "SVG must include sector callsign");
    assert.ok(svg.includes("<rect"), "SVG must include frame rectangles");
  });
});
