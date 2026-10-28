import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import { synthesizePrompt, auditPrompt, SCENE_PROFILES } from "./lib/loreGuard.mjs";
import { generateImage } from "./lib/imageGenerator.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 3333;
const STORYBOARD_DIR = path.resolve(__dirname, "../../episodes/001_eleven_bells/storyboard");
const DRAFTS_DIR = path.resolve(__dirname, "drafts");
if (!fs.existsSync(DRAFTS_DIR)) fs.mkdirSync(DRAFTS_DIR, { recursive: true });

const CANON_PLATES = [
  {
    id: 1,
    title: "THE THROAT & SHIELD WALL",
    sector: "THE THROAT / LIFT-SECTOR-01",
    filename: "panel_01_the_throat.jpg",
    url: "/storyboard/panel_01_the_throat.jpg",
    description: "Interlocking ballistic mantlets, floor hydraulic rams, industrial pressure suits"
  },
  {
    id: 2,
    title: "THE WELDED (PROFILE)",
    sector: "GATHAUR-BANO / SECTOR-6A112",
    filename: "plate_02_the_welded_profile_canon.jpg",
    url: "/storyboard/plate_02_the_welded_profile_canon.jpg",
    description: "Bolted iron skull cage, brass filter respirator, exhausted human eye"
  },
  {
    id: 3,
    title: "THE BREAKER CADENCE",
    sector: "HAUL-DRIFT-04 / SECTOR-6A112",
    filename: "plate_03_the_breaker_cadence_canon.jpg",
    url: "/storyboard/plate_03_the_breaker_cadence_canon.jpg",
    description: "Steam-driven arm cams, hydraulic breaker torso frame, timber drift"
  }
];

const SCRIPT_BEATS = [
  {
    id: 1,
    title: "The Throat & Shield Wall",
    sector: "THE THROAT / LIFT-SECTOR-01",
    script: "Twelve shield warriors held the throat of the lift, three hundred civilians jammed knee to knee in the cage, a dockhand with one crushed hand still wrapped around a dented enamel tin, backs pressed to the grating, boots in sump water, breath sour with coal dust and grease.",
    suggestedPrompt: "Interlocking sloped bronze and hammered copper ballistic blast-mantlets anchored into the wet stone floor by thick hydraulic shock pistons. Behind the barricade, rugged Thulan miners in bolted copper boiler cuirasses, rubberized blast aprons, and full-face brass respirator hoods with dark welding glass visors gripping two-handed pneumatic breaker tools and hydraulic lever valves. Background elevator cage jammed with miners behind iron grating. Boiling steam hissing from overhead pipes, dense coal dust, grease lanterns, zero swords, zero spears, zero chainmail, zero handheld shields",
    filename: "panel_01_the_throat.jpg"
  },
  {
    id: 2,
    title: "The Welded (Advance)",
    sector: "HAUL-DRIFT-04 / SECTOR-6A112",
    script: "The men coming down the gallery weren't soldiers. They were the Welded—condemned miners bolted into hydraulic frames, jawbones pinned with rivets, eyelids stitched open on iron wire, ribs capped in plate, arms driven by steam cams that never rested.",
    suggestedPrompt: "Condemned miners known as The Welded advancing down dark timber-shored coal mine drift, bolted into heavy rusted iron and bronze hydraulic breaker frames, ribbed breastplate over chest, mechanical steam piston arms, dual-valve respirator venting exhaust steam, zero swords, zero spears",
    filename: "panel_02_the_welded_advance.jpg"
  },
  {
    id: 3,
    title: "The Welded (Profile)",
    sector: "GATHAUR-BANO / SECTOR-6A112",
    script: "Jawbones pinned with rivets, eyelids stitched open on iron wire, ribs capped in plate, arms driven by steam cams that never rested.",
    suggestedPrompt: "Extreme profile close-up of a condemned Thulan miner encased in a bolted iron skull cage, heavy brass filter canister respirator venting exhaust steam, exhausted human eye visible behind the steel plate, massive bolted shoulder pauldron, zero text, zero speech bubbles",
    filename: "panel_03_the_welded_profile.jpg"
  },
  {
    id: 4,
    title: "The Iron Bell",
    sector: "SIGNAL-GANTRY / LEVEL-09",
    script: "Every time the lift came back for more, an iron bell struck. Each bell meant another line had failed above.",
    suggestedPrompt: "Massive heavy wrought iron mechanical lift bell suspended in a heavy riveted steel gantry frame deep within a dark subterranean mine shaft, thick grease, heavy chains, iron clapper, dark crosshatched stone walls, warm lantern light, zero characters, zero text, zero speech bubbles, zero comic lettering",
    filename: "panel_04_the_iron_bell.jpg"
  },
  {
    id: 5,
    title: "Third Bell (Pressure Rupture)",
    sector: "PRESSURE-MAIN / SHAFT-03",
    script: "At the third bell, a pressure main burst in the ceiling, spitting boiling mist through the beams, slicking the walls white.",
    suggestedPrompt: "Industrial steam pressure main rupturing violently from timber ceiling beams in subterranean tunnel, blinding white boiling steam blast, armored Thulan miners in brass respirator hoods crouching behind floor-anchored copper ballistic blast mantlets, zero swords",
    filename: "panel_05_pressure_rupture.jpg"
  },
  {
    id: 6,
    title: "Fifth Bell (Cable Snap)",
    sector: "WINCH-DRUM / SHAFT-THROAT",
    script: "At the fifth... the haul cable tore free. It lashed across the shaft throat, took six warriors at once, armor split, shields knocked loose, bodies folded into the winch frame.",
    suggestedPrompt: "Thick woven steel hoist cable snapping under immense tension, whipping violently across industrial elevator shaft throat, severed bronze armor plates, sheared hydraulic pistons, sparks and kinetic chaos frozen in stark pitch-black brush ink, zero swords, zero spears",
    filename: "panel_06_cable_snap.jpg"
  },
  {
    id: 7,
    title: "Seventh Bell (Locked Harnesses)",
    sector: "DEFENSE-LINE / COLLAR-07",
    script: "By the seventh bell, dead men were still upright in their harnesses—industrial shield hooks locked under the bodies' weight. And the Welded kept hammering at the corpses, steel fists ringing off dented helms.",
    suggestedPrompt: "Fallen Thulan miners held rigidly upright by industrial bronze mantlet harnesses anchored under dead weight, unstoppable mechanical Welded miners striking relentlessly with iron piston fists, dented helms, sparks flying, zero swords, zero spears",
    filename: "panel_07_locked_harnesses.jpg"
  },
  {
    id: 8,
    title: "The Final Run (Jammed Hoist)",
    sector: "HOIST-CAGE / DRIVE-TEETH",
    script: "On the final run, the hoist jammed. The last warrior hauled up his pneumatic hammer... stepped out of the cage... drove the steel head into the drive teeth so the safety doors could seal shut.",
    suggestedPrompt: "Sole surviving Thulan miner stepping out of elevator cage threshold, raising a massive heavy pneumatic fault hammer with both hands, driving the steel head directly into massive revolving hoist spur drive teeth to force safety doors closed, zero swords",
    filename: "panel_08_jammed_hoist.jpg"
  },
  {
    id: 9,
    title: "Eleventh Bell (The Hollow Thrum)",
    sector: "SHAFT-ABYSS / ELEVENTH-BELL",
    script: "The eleventh bell rang from the shaft below, a hollow thrum that echoed the last breath of those still trapped.",
    suggestedPrompt: "Looking down into the vast vertical darkness of empty industrial shaft abyss, distant sealed steel safety hatch far below, faint amber glow from grease lanterns, dripping rock walls, solitary heavy sound waves echoing in dark crosshatch ink, zero characters",
    filename: "panel_09_eleventh_bell.jpg"
  },
  {
    id: 10,
    title: "The Residue & Myth (Council Plaque)",
    sector: "COMMEMORATIVE-SEAL / SECTOR-6A",
    script: "Years later, the hammer remains embedded in the rusted hoist. The Council labels it a heroic monument; in truth, it is simply an unfinished repair over an industrial slaughter.",
    suggestedPrompt: "Years later, polished ornamental bronze Council plaque with crisp engraved lettering mounted directly over bent rusted iron spur gears and the still-embedded shattered pneumatic fault hammer head, green verdigris patina, cold dim overhead work lamp",
    filename: "panel_10_council_plaque.jpg"
  }
];

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // API Endpoints
  if (url.pathname === "/api/beats") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(SCRIPT_BEATS));
    return;
  }

  if (url.pathname === "/api/storyboard") {
    try {
      const files = fs.readdirSync(STORYBOARD_DIR)
        .filter(f => f.endsWith(".jpg") || f.endsWith(".png"))
        .map(f => ({
          filename: f,
          url: `/storyboard/${encodeURIComponent(f)}`
        }));
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(files));
    } catch {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end("[]");
    }
    return;
  }

  if (url.pathname.startsWith("/storyboard/")) {
    const filename = decodeURIComponent(url.pathname.replace("/storyboard/", ""));
    const filePath = path.join(STORYBOARD_DIR, filename);
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { "Content-Type": "image/jpeg" });
      res.end(fs.readFileSync(filePath));
      return;
    }
  }

  if (url.pathname === "/api/profiles" && req.method === "GET") {
    const profiles = Object.entries(SCENE_PROFILES).map(([key, p]) => ({
      key,
      name: p.name,
      description: p.description || p.name
    }));
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(profiles));
    return;
  }

  if (url.pathname === "/api/synthesize" && req.method === "POST") {
    let body = "";
    req.on("data", chunk => body += chunk);
    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        const sceneProfile = data.sceneProfile || data.options?.sceneProfile;
        const opts = sceneProfile ? { sceneProfile } : (data.options || {});
        const result = synthesizePrompt(data.scene || "", opts);
        const audit = auditPrompt(result.positivePrompt, opts);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ...result, audit }));
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  if (url.pathname === "/api/canon") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(CANON_PLATES));
    return;
  }

  if (url.pathname === "/api/drafts" && req.method === "GET") {
    try {
      const files = fs.readdirSync(DRAFTS_DIR)
        .filter(f => f.endsWith(".jpg") || f.endsWith(".png"))
        .map(f => {
          const stat = fs.statSync(path.join(DRAFTS_DIR, f));
          return {
            filename: f,
            url: `/drafts/${encodeURIComponent(f)}`,
            createdAt: stat.mtimeMs
          };
        })
        .sort((a, b) => b.createdAt - a.createdAt);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(files));
    } catch {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end("[]");
    }
    return;
  }

  if (url.pathname.startsWith("/drafts/")) {
    const filename = decodeURIComponent(url.pathname.replace("/drafts/", ""));
    const filePath = path.join(DRAFTS_DIR, filename);
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { "Content-Type": "image/jpeg" });
      res.end(fs.readFileSync(filePath));
      return;
    }
  }

  if (url.pathname === "/api/drafts/delete" && req.method === "POST") {
    let body = "";
    req.on("data", c => body += c);
    req.on("end", () => {
      try {
        const { filename } = JSON.parse(body);
        const target = path.join(DRAFTS_DIR, path.basename(filename));
        if (fs.existsSync(target)) fs.unlinkSync(target);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ success: true }));
      } catch (err) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Direct AI Generation Endpoint
  if (url.pathname === "/api/generate" && req.method === "POST") {
    let body = "";
    req.on("data", chunk => body += chunk);
    req.on("end", async () => {
      try {
        const data = JSON.parse(body);
        const sceneProfile = data.sceneProfile || data.options?.sceneProfile;
        const opts = sceneProfile ? { sceneProfile } : (data.options || {});
        if (data.prompt) {
          const synth = synthesizePrompt(data.prompt, opts);
          data.prompt = synth.positivePrompt;
          data.negativePrompt = synth.negativePrompt;
        }
        const result = await generateImage(data);
        if (result && result.imageBase64) {
          const draftName = `draft_${Date.now()}_beat_${data.beatId || 1}.jpg`;
          const draftPath = path.join(DRAFTS_DIR, draftName);
          const rawB64 = result.imageBase64.replace(/^data:image\/\w+;base64,/, "");
          fs.writeFileSync(draftPath, Buffer.from(rawB64, "base64"));
          result.draftUrl = `/drafts/${encodeURIComponent(draftName)}`;
          result.draftName = draftName;
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
      } catch (err) {
        console.error("Generate error:", err);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  if (url.pathname === "/api/export" && req.method === "POST") {
    let body = "";
    req.on("data", chunk => body += chunk);
    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        const base64Data = data.imageBase64.replace(/^data:image\/\w+;base64,/, "");
        const buffer = Buffer.from(base64Data, "base64");
        
        const tempPath = path.join(__dirname, "temp_incoming.png");
        fs.writeFileSync(tempPath, buffer);

        const outPath = path.join(STORYBOARD_DIR, data.filename || `panel_${Date.now()}.jpg`);
        
        const py = spawn("python3", [
          path.join(__dirname, "lib/composite_panel.py"),
          tempPath,
          outPath,
          data.title || "THE THULANS",
          data.sector || "SECTOR-UNKNOWN / 001",
          data.quote || ""
        ]);

        py.stderr.on("data", d => console.error(`Compositor err: ${d}`));
        py.on("close", code => {
          if (code === 0) {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ success: true, savedPath: outPath, filename: path.basename(outPath) }));
          } else {
            res.writeHead(500, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: `Compositor exited with code ${code}` }));
          }
        });
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Serve Frontend UI
  if (url.pathname === "/" || url.pathname === "/index.html") {
    const htmlPath = path.join(__dirname, "public/index.html");
    if (fs.existsSync(htmlPath)) {
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(fs.readFileSync(htmlPath));
    } else {
      res.writeHead(404);
      res.end("Not Found");
    }
    return;
  }

  res.writeHead(404);
  res.end("Not Found");
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  server.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`  THULAN GRAPHIC NOVEL STUDIO ACTIVE`);
    console.log(`  URL: http://localhost:${PORT}`);
    console.log(`  Storyboard Target: ${STORYBOARD_DIR}`);
    console.log(`==================================================\n`);
  });
}

export { server };
