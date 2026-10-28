import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { 
  auditPrompt, 
  synthesizePrompt, 
  validateProductionBoundary, 
  FORBIDDEN_TOKENS, 
  SCENE_PROFILES 
} from "../lib/loreGuard.mjs";

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
    assert.ok(positivePrompt.includes("heavy ink"), "Aesthetic anchor must be injected");
    assert.ok(negativePrompt.includes("medieval fantasy"), "Negative prompt must block medieval fantasy");
  });

  it("synthesizePrompt -> auditPrompt round-trip produces valid audit in varek_defense_line", () => {
    const rawScene = "Miners advancing down the haul drift under heavy steam";
    const synthesized = synthesizePrompt(rawScene, "varek_defense_line");
    const roundTripAudit = auditPrompt(synthesized.positivePrompt, "varek_defense_line");

    assert.equal(roundTripAudit.valid, true, "Synthesized prompt must pass its own profile audit without self-conflicting violations");
    assert.deepEqual(roundTripAudit.violations, []);
    assert.deepEqual(roundTripAudit.missingAnchors, []);
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

  it("passes dialogue-free silent panel (Page 16 folded coat fixture: both pins remain seated, spanner still on shelf)", () => {
    // Script line: "Both pins remain seated; the spanner is still on the shelf. He takes off the borrowed coat... folds the coat, kneels, and places it where he intends to lower her head."
    const coatPrompt = "Oversized borrowed wool miner coat folded into a pillow on wet deck grating where he intends to lower her head. Both coupling pins remain seated, spanner still on shelf. Dilute amber lamp spill, silence, charcoal blacks, heavy ink chiaroscuro";
    const audit = auditPrompt(coatPrompt, { sceneProfile: "fortis_pilot" });

    assert.equal(audit.valid, true, "Folded coat silent still-life fixture must pass with seated pins and spanner on shelf");
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

  it("synthesizePrompt -> auditPrompt round-trip produces valid audit in fortis_pilot", () => {
    const rawBeat = "Beneath the warm return pipe, Ansen watches through the gap";
    const synthesized = synthesizePrompt(rawBeat, "fortis_pilot");
    const roundTripAudit = auditPrompt(synthesized.positivePrompt, "fortis_pilot");

    assert.equal(roundTripAudit.valid, true, "Synthesized FORTIS prompt must pass audit cleanly");
    assert.deepEqual(roundTripAudit.violations, []);
    assert.deepEqual(roundTripAudit.missingAnchors, []);
  });
});

describe("Gate 1: Profile Validation & Production Boundary Contracts", () => {
  it("rejects unknown scene profiles explicitly in auditPrompt", () => {
    assert.throws(
      () => auditPrompt("A scene prompt", "unknown_scifi_profile"),
      /Unknown sceneProfile: "unknown_scifi_profile"/
    );
  });

  it("rejects unknown scene profiles explicitly in synthesizePrompt", () => {
    assert.throws(
      () => synthesizePrompt("A scene beat", { sceneProfile: "cyberpunk_matrix" }),
      /Unknown sceneProfile: "cyberpunk_matrix"/
    );
  });

  it("validateProductionBoundary requires approved, versioned style reference metadata", () => {
    const compliantManifest = {
      id: "FORTIS-P01-02",
      sceneProfile: "fortis_pilot",
      styleReference: "FORTIS_STYLE_V1.0",
      story_beat: "Ansen watches passage through board gap, Nessa sits behind under warm pipe"
    };
    const result = validateProductionBoundary(compliantManifest);

    assert.equal(result.valid, true, "Compliant production manifest must pass");
    assert.equal(result.errors.length, 0);
    assert.equal(result.styleAudit.metadataVerified, true);
    assert.equal(result.styleAudit.styleReference, "FORTIS_STYLE_V1.0");
    assert.ok(result.styleAudit.disclaimer.includes("does not prove rendered image style"));
  });

  it("validateProductionBoundary rejects unapproved or pending_approval style reference", () => {
    const pendingManifest = {
      id: "FORTIS-P01-02",
      sceneProfile: "fortis_pilot",
      styleReference: "pending_approval",
      story_beat: "Ansen watches passage through board gap"
    };
    const result = validateProductionBoundary(pendingManifest);

    assert.equal(result.valid, false, "Pending approval style reference must fail production boundary");
    assert.ok(result.errors.some(e => e.includes("Missing approved, versioned style reference")));
    assert.equal(result.styleAudit.metadataVerified, false);
  });

  it("validateProductionBoundary explicitly disclaims text audit as proof of rendered style", () => {
    const entry = {
      id: "FORTIS-P01-03",
      sceneProfile: "fortis_pilot",
      styleReference: "FORTIS_STYLE_V1.0",
      prompt: "Nessa cradles warm loaf of bread inside worn wool wrap"
    };
    const result = validateProductionBoundary(entry);

    assert.ok(result.styleAudit.disclaimer.includes("human visual review"));
    assert.ok(!result.styleAudit.renderedStyleCertified, "Must not claim automated render certification");
  });
});
