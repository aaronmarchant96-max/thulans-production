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
});
