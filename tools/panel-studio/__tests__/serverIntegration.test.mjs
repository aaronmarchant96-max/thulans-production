import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { server } from "../server.mjs";

describe("Panel Studio Server & UI API Integration", () => {
  let baseUrl;

  before(async () => {
    await new Promise((resolve) => {
      server.listen(0, () => {
        const address = server.address();
        baseUrl = `http://localhost:${address.port}`;
        resolve();
      });
    });
  });

  after(async () => {
    await new Promise((resolve) => {
      server.close(resolve);
    });
  });

  it("GET /api/profiles returns supported scene profiles", async () => {
    const res = await fetch(`${baseUrl}/api/profiles`);
    assert.equal(res.status, 200);
    const profiles = await res.json();
    assert.ok(Array.isArray(profiles));
    const keys = profiles.map(p => p.key);
    assert.ok(keys.includes("varek_defense_line"));
    assert.ok(keys.includes("fortis_pilot"));
  });

  it("GET /api/beats returns Episode 001 script beats", async () => {
    const res = await fetch(`${baseUrl}/api/beats`);
    assert.equal(res.status, 200);
    const beats = await res.json();
    assert.ok(Array.isArray(beats));
    assert.equal(beats.length, 10);
    assert.equal(beats[0].title, "The Throat & Shield Wall");
  });

  it("POST /api/synthesize propagates varek_defense_line profile and audits validly", async () => {
    const res = await fetch(`${baseUrl}/api/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scene: "Miners holding defensive line at the lift collar",
        sceneProfile: "varek_defense_line"
      })
    });
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.profile, "varek_defense_line");
    assert.ok(data.positivePrompt.includes("sloped bronze"));
    assert.ok(data.positivePrompt.includes("hydraulic"));
    assert.ok(data.positivePrompt.includes("heavy ink"));
    assert.equal(data.audit.valid, true);
    assert.deepEqual(data.audit.violations, []);
  });

  it("POST /api/synthesize propagates fortis_pilot profile and audits validly without forced bronze", async () => {
    const res = await fetch(`${baseUrl}/api/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scene: "Nessa cradling warm bread inside worn cloak, Ansen turning from loose shelter boards",
        sceneProfile: "fortis_pilot"
      })
    });
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.profile, "fortis_pilot");
    assert.ok(data.positivePrompt.includes("European graphic-novel ink"));
    assert.ok(!data.positivePrompt.includes("sloped bronze"));
    assert.equal(data.audit.valid, true);
    assert.deepEqual(data.audit.violations, []);
  });

  it("POST /api/synthesize rejects unknown scene profiles with HTTP 400", async () => {
    const res = await fetch(`${baseUrl}/api/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scene: "A random futuristic cyberpunk city with flying cars",
        sceneProfile: "cyberpunk_matrix_unsupported"
      })
    });
    assert.equal(res.status, 400);
    const data = await res.json();
    assert.ok(data.error.includes("Unknown sceneProfile: \"cyberpunk_matrix_unsupported\""));
  });

  it("POST /api/synthesize preserves legacy fallback to varek_defense_line when profile is omitted", async () => {
    const res = await fetch(`${baseUrl}/api/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scene: "Miners holding defensive line at lift collar"
      })
    });
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.profile, "varek_defense_line");
    assert.ok(data.positivePrompt.includes("sloped bronze"));
  });

  it("POST /api/production/validate rejects manifest entries missing sceneProfile with HTTP 422", async () => {
    const res = await fetch(`${baseUrl}/api/production/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: "FORTIS-P01-02",
        styleReference: "FORTIS_STYLE_V1.0",
        story_beat: "Ansen watches passage through board gap"
      })
    });
    assert.equal(res.status, 422);
    const data = await res.json();
    assert.equal(data.valid, false);
    assert.ok(data.errors.some(e => e.includes("Missing required sceneProfile")));
  });

  it("POST /api/production/validate passes compliant FORTIS manifest with HTTP 200 and visual disclaimer", async () => {
    const res = await fetch(`${baseUrl}/api/production/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: "FORTIS-P01-02",
        sceneProfile: "fortis_pilot",
        styleReference: "FORTIS_STYLE_V1.0",
        story_beat: "Ansen watches passage through board gap, Nessa sits behind under warm pipe"
      })
    });
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.valid, true);
    assert.equal(data.errors.length, 0);
    assert.ok(data.styleAudit.disclaimer.includes("human visual review"));
  });

  it("POST /api/generate rejects unknown sceneProfile with HTTP 400", async () => {
    const res = await fetch(`${baseUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: "A scene in space",
        sceneProfile: "nonexistent_sci_fi_profile"
      })
    });
    assert.equal(res.status, 400);
    const data = await res.json();
    assert.ok(data.error.includes("Unknown sceneProfile: \"nonexistent_sci_fi_profile\""));
  });
});
