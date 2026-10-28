/**
 * Lore Guard & Anti-Fantasy Enforcement Engine (Hardened v2)
 * Authority: RULINGS.md, GDR-SLOP.md, CANON_BOUNDARY_SPEC.md
 * Owner: Aaron Marchant
 */

export const FORBIDDEN_TOKENS = [
  "wooden shield",
  "wood plank",
  "crude wood",
  "round buckler",
  "knight in shining armor",
  "dark souls",
  "fantasy sword",
  "sword",
  "swords",
  "spear",
  "spears",
  "pike",
  "pikes",
  "lance",
  "chainmail",
  "chain mail",
  "mail armor",
  "leather tunic",
  "roman legion",
  "testudo",
  "hellboy",
  "right hand of doom",
  "horns",
  "magic glow",
  "magical aura",
  "ornate filigree",
  "flowing cape",
  "cloth cape",
  "spiked pauldrons"
];

export const REQUIRED_CANONICAL_ANCHORS = [
  "sloped bronze",
  "hydraulic",
  "heavy ink"
];

export const CANONICAL_POSITIVE_PRESET = 
  "Dark Horse comic book illustration, heavy angular black brush ink, deep chiaroscuro solid pitch-black shadows, high contrast grimdark industrial dieselpunk, deep subterranean coal mine shaft, sloped bronze and hammered copper ballistic mantlets, floor-anchored hydraulic shock-absorber pistons, heavy iron rivets, industrial pressure suits with heavy leather blast aprons, full-face brass respirator helmets with dark rectangular welding glass visors, heavy pneumatic breaker tools, coal dust and venting steam plumes, warm amber lantern glow, zero swords, zero spears, zero chainmail, zero handheld shields, zero text, zero speech bubbles, zero signatures";

export const CANONICAL_NEGATIVE_PRESET = 
  "Hellboy, red demon, horns, tail, trenchcoat, swords, blades, daggers, spears, pikes, lances, polearms, chainmail, mail armor, medieval fantasy, Dark Souls, Roman soldiers, legionaries, knights, crude wooden shields, round bucklers, speech bubbles, comic word balloons, sound effect text, onomatopoeia, lettering, captions inside image, artist signatures, watermark, outdoors, mountains, sunny daylight, photorealistic, 3d cgi render, clean smooth plastic";

// A staging preset for human scenes, not approval of any character design or layout.
export const CIVILIAN_SHELTER_POSITIVE_PRESET =
  "Graphic novel illustration, heavy ink, angular brushwork, readable human faces and hands, crosshatching, rough paper texture, deep chiaroscuro, muted soot-grey and brown with restrained amber light, inhabited subterranean industrial passage, damp stone, worn patched civilian clothing, practical iron pipework, ordinary unarmoured human bodies, intimate framing, zero text, zero speech bubbles, zero signatures";

const SCENE_PROFILES = {
  mastercraft: {
    positive: CANONICAL_POSITIVE_PRESET,
    negative: CANONICAL_NEGATIVE_PRESET,
    anchors: REQUIRED_CANONICAL_ANCHORS
  },
  civilian_shelter: {
    positive: CIVILIAN_SHELTER_POSITIVE_PRESET,
    negative: `${CANONICAL_NEGATIVE_PRESET}, powered armour, giant armoured figure, respirator helmets, pressure suits, ballistic mantlets`,
    anchors: ["heavy ink", "subterranean"]
  }
};

function sceneProfile(options) {
  const name = options.sceneProfile ?? "mastercraft";
  if (!Object.hasOwn(SCENE_PROFILES, name)) {
    throw new Error(`Unknown scene profile: ${name}`);
  }
  return SCENE_PROFILES[name];
}

/**
 * Audits a prompt for forbidden tokens and canonical anchors.
 * @param {string} promptText 
 * @returns {{ valid: boolean, violations: string[], missingAnchors: string[] }}
 */
export function auditPrompt(promptText, options = {}) {
  const profile = sceneProfile(options);
  const lower = promptText.toLowerCase();
  const violations = FORBIDDEN_TOKENS.filter(token => {
    const regex = new RegExp(`\\b${token}\\b`, "i");
    return regex.test(lower);
  });
  const missingAnchors = profile.anchors.filter(anchor => !lower.includes(anchor));
  
  return {
    valid: violations.length === 0 && missingAnchors.length === 0,
    violations,
    missingAnchors
  };
}

/**
 * Synthesizes an input scene beat into a strictly guarded Thulan prompt.
 * Strips any forbidden tokens and enforces canonical mastercrafter anchors.
 * @param {string} sceneDescription 
 * @param {object} options 
 * @returns {{ positivePrompt: string, negativePrompt: string }}
 */
export function synthesizePrompt(sceneDescription, options = {}) {
  const profile = sceneProfile(options);
  let cleaned = sceneDescription;
  for (const forbidden of FORBIDDEN_TOKENS) {
    const regex = new RegExp(`\\b${forbidden}\\b`, "gi");
    cleaned = cleaned.replace(regex, "");
  }

  const positivePrompt = `${cleaned.trim()}, ${profile.positive}`.replace(/\s+/g, " ");
  
  return {
    positivePrompt,
    negativePrompt: profile.negative
  };
}
