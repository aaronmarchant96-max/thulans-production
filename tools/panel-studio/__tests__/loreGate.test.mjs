import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { auditPrompt, synthesizePrompt, FORBIDDEN_TOKENS, SCENE_PROFILES } from "../lib/loreGuard.mjs";

describe("Gate 1: Lore Invariant & Anti-Slop Enforcement (Episode 001 / Varek Baseline)", () => {
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

describe("Gate 1: FORTIS Pilot Multi-Scene Guard", () => {
  it("passes shelter panel with loose wooden boards without false-positive tripwire", () => {
    const shelterPrompt = "Beneath a warm return pipe, behind two loose wooden boards, Ansen watches a passage through a gap. Nessa sits behind him, skirt tucked from floor water.";
    const audit = auditPrompt(shelterPrompt, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, true, "Shelter wooden boards must pass under fortis_pilot");
    assert.equal(audit.violations.length, 0);
    assert.equal(audit.missingAnchors.length, 0);
  });

  it("passes bread reveal panel with quiet intimacy and no forced bronze anchors", () => {
    const breadPrompt = "Nessa draws a small warm loaf of bread from beneath her shawl, coarse hands cradling the crust, Ansen turning toward her in the dark";
    const audit = auditPrompt(breadPrompt, "fortis_pilot");

    assert.equal(audit.valid, true, "Bread scene must pass under fortis_pilot without bronze/hydraulic anchors");
    assert.equal(audit.violations.length, 0);
    assert.equal(audit.missingAnchors.length, 0);
  });

  it("passes dialogue-free silent panel (Page 16 folded coat fixture)", () => {
    const coatPrompt = "Oversized wool miner coat folded into a pillow on wet deck grating, heavy dropped spanner and removed coupling pin beside it in darkness";
    const audit = auditPrompt(coatPrompt, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, true, "Folded coat silent still-life must pass");
    assert.equal(audit.violations.length, 0);
    assert.equal(audit.missingAnchors.length, 0);
  });

  it("passes mechanical scene with Frame 9 controls, stops and shutoff", () => {
    const mechPrompt = "Frame 9 handler station, hydraulic shutoff valve, lever control, powered gauntlet iron cuff stop, and service ledger on wall";
    const audit = auditPrompt(mechPrompt, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, true, "Mechanical scene must pass without requiring sloped bronze armor");
    assert.equal(audit.violations.length, 0);
    assert.equal(audit.missingAnchors.length, 0);
  });

  it("catches forbidden fantasy tokens under FORTIS profile", () => {
    const poisonedFortis = "Ansen holding a magic glow sword and wearing a flowing cape inside the shelter";
    const audit = auditPrompt(poisonedFortis, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, false, "FORTIS audit must reject fantasy tokens");
    assert.ok(audit.violations.includes("magic glow"));
    assert.ok(audit.violations.includes("sword"));
    assert.ok(audit.violations.includes("flowing cape"));
  });

  it("catches visual slop tokens under FORTIS profile (anime, glossy CGI, neon)", () => {
    const slopPrompt = "Anime faces, glossy cgi render of Nessa with neon glow eyes";
    const audit = auditPrompt(slopPrompt, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, false, "FORTIS audit must reject visual slop");
    assert.ok(audit.violations.includes("anime faces"));
    assert.ok(audit.violations.includes("glossy cgi"));
    assert.ok(audit.violations.includes("neon glow"));
  });

  it("synthesizePrompt generates compliant FORTIS prompts with European graphic novel ink preset", () => {
    const rawBeat = "Nessa draws bread from blouse, Ansen turns to watch with a wooden shield";
    const { positivePrompt, negativePrompt, profile } = synthesizePrompt(rawBeat, { sceneProfile: "fortis_pilot" });

    assert.equal(profile, "fortis_pilot");
    assert.ok(!positivePrompt.includes("wooden shield"), "Forbidden token must be stripped");
    assert.ok(positivePrompt.includes("European graphic-novel ink"), "FORTIS aesthetic preset must be injected");
    assert.ok(positivePrompt.includes("near-monochrome charcoal"), "FORTIS palette preset must be injected");
    assert.ok(!positivePrompt.includes("sloped bronze"), "Varek-specific anchor must NOT be injected into FORTIS");
    assert.ok(negativePrompt.includes("glossy CGI"), "Negative prompt must block glossy CGI");
    assert.ok(negativePrompt.includes("medieval fantasy"), "Negative prompt must block medieval fantasy");
  });
});
