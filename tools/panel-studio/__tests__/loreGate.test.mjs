import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { auditPrompt, synthesizePrompt, FORBIDDEN_TOKENS } from "../lib/loreGuard.mjs";

describe("Gate 1: Lore Invariant & Anti-Slop Enforcement", () => {
  it("catches forbidden fantasy tokens under adversarial injection", () => {
    const poisonedPrompt = "A knight in shining armor holding a crude wooden shield and a magic glow sword";
    const audit = auditPrompt(poisonedPrompt);

    assert.equal(audit.valid, false, "Audit must fail poisoned prompt");
    assert.ok(audit.violations.includes("knight in shining armor"));
    assert.ok(audit.violations.includes("wooden shield"));
    assert.ok(audit.violations.includes("magic glow"));
  });

  it("fails prompts that omit required Thulan canonical anchors", () => {
    const genericPrompt = "An empty dark underground mine corridor with lanterns";
    const audit = auditPrompt(genericPrompt);

    assert.equal(audit.valid, false, "Prompt without mastercraft anchors must fail");
    assert.ok(audit.missingAnchors.length > 0);
  });

  it("passes compliant canonical Thulan prompt", () => {
    const canonicalPrompt = "A sloped bronze ballistic mantlet anchored by hydraulic shock pistons, heavy ink chiaroscuro, Dark Horse comic illustration";
    const audit = auditPrompt(canonicalPrompt);

    assert.equal(audit.valid, true, "Canonical prompt must pass audit");
    assert.equal(audit.violations.length, 0);
    assert.equal(audit.missingAnchors.length, 0);
  });

  it("synthesizePrompt strips forbidden tokens and injects canonical anchors", () => {
    const rawScene = "The warrior advances with a wooden shield against the miners";
    const { positivePrompt, negativePrompt } = synthesizePrompt(rawScene);

    assert.ok(!positivePrompt.includes("wooden shield"), "Forbidden token must be stripped");
    assert.ok(positivePrompt.includes("sloped bronze"), "Canonical anchor must be injected");
    assert.ok(positivePrompt.includes("Dark Horse comic"), "Aesthetic anchor must be injected");
    assert.ok(negativePrompt.includes("medieval fantasy"), "Negative prompt must block medieval fantasy");
  });
});
