/**
 * Lore Guard & Anti-Fantasy Enforcement Engine (Hardened v2.1)
 * Authority: RULINGS.md, GDR-SLOP.md, CANON_BOUNDARY_SPEC.md, docs/FORTIS_PRODUCTION_RECONCILIATION_DRAFT.md
 * Owner: Aaron Marchant
 */

export const UNIVERSAL_FORBIDDEN_TOKENS = [
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

export const VAREK_DEFENSE_LINE_FORBIDDEN_TOKENS = [
  ...UNIVERSAL_FORBIDDEN_TOKENS,
  "wooden shield",
  "wood plank",
  "crude wood",
  "round buckler"
];

export const FORTIS_FORBIDDEN_TOKENS = [
  ...UNIVERSAL_FORBIDDEN_TOKENS,
  "wooden shield",
  "round buckler",
  "glossy cgi",
  "anime face",
  "anime faces",
  "neon glow",
  "ambient orange skyline",
  "decorative bloom"
];

// Retain FORBIDDEN_TOKENS for backward compatibility with existing Episode 001 imports
export const FORBIDDEN_TOKENS = VAREK_DEFENSE_LINE_FORBIDDEN_TOKENS;

export const VAREK_REQUIRED_CANONICAL_ANCHORS = [
  "sloped bronze",
  "hydraulic",
  "heavy ink"
];

// Retain REQUIRED_CANONICAL_ANCHORS for backward compatibility with existing Episode 001 imports
export const REQUIRED_CANONICAL_ANCHORS = VAREK_REQUIRED_CANONICAL_ANCHORS;

export const CANONICAL_POSITIVE_PRESET = 
  "Dark Horse comic book illustration, heavy angular black brush ink, deep chiaroscuro solid pitch-black shadows, high contrast grimdark industrial dieselpunk, deep subterranean coal mine shaft, sloped bronze and hammered copper ballistic mantlets, floor-anchored hydraulic shock-absorber pistons, heavy iron rivets, industrial pressure suits with heavy leather blast aprons, full-face brass respirator helmets with dark rectangular welding glass visors, heavy pneumatic breaker tools, coal dust and venting steam plumes, warm amber lantern glow, zero swords, zero spears, zero chainmail, zero handheld shields, zero text, zero speech bubbles, zero signatures";

export const CANONICAL_NEGATIVE_PRESET = 
  "Hellboy, red demon, horns, tail, trenchcoat, swords, blades, daggers, spears, pikes, lances, polearms, chainmail, mail armor, medieval fantasy, Dark Souls, Roman soldiers, legionaries, knights, crude wooden shields, round bucklers, speech bubbles, comic word balloons, sound effect text, onomatopoeia, lettering, captions inside image, artist signatures, watermark, outdoors, mountains, sunny daylight, photorealistic, 3d cgi render, clean smooth plastic";

export const FORTIS_POSITIVE_PRESET =
  "Heavy European graphic-novel ink, firm silhouettes, subdued halftone and soot grain, near-monochrome charcoal and slate black tones, single motivated warm amber accent, print lithograph texture, deep structural shadows, zero swords, zero fantasy armor, zero magic glow, zero text, zero speech bubbles, zero signatures";

export const FORTIS_NEGATIVE_PRESET =
  "glossy CGI, 3D render, photorealistic, anime faces, manga, neon glow, ambient orange skyline, decorative bloom, fantasy armor, swords, blades, spears, capes, medieval fantasy, Dark Souls, speech bubbles, comic word balloons, sound effect text, lettering, captions inside image, artist signatures, watermark";

export const SCENE_PROFILES = {
  varek_defense_line: {
    name: "varek_defense_line",
    forbiddenTokens: VAREK_DEFENSE_LINE_FORBIDDEN_TOKENS,
    requiredAnchors: VAREK_REQUIRED_CANONICAL_ANCHORS,
    positivePreset: CANONICAL_POSITIVE_PRESET,
    negativePreset: CANONICAL_NEGATIVE_PRESET
  },
  fortis_pilot: {
    name: "fortis_pilot",
    forbiddenTokens: FORTIS_FORBIDDEN_TOKENS,
    requiredAnchors: [], // Validated through style reference configuration, not brittle keyword gating
    positivePreset: FORTIS_POSITIVE_PRESET,
    negativePreset: FORTIS_NEGATIVE_PRESET
  }
};

// Aliases
SCENE_PROFILES["episode_001"] = SCENE_PROFILES.varek_defense_line;
SCENE_PROFILES["salvation_pilot"] = SCENE_PROFILES.fortis_pilot;

/**
 * Audits a prompt for forbidden tokens and canonical anchors according to scene profile.
 * Defaults to "varek_defense_line" for 100% backward compatibility.
 * @param {string} promptText 
 * @param {object|string} options - profile name string or options object { sceneProfile, profile, requireStyleRef, styleReference }
 * @returns {{ valid: boolean, violations: string[], missingAnchors: string[], profile: string }}
 */
export function auditPrompt(promptText, options = {}) {
  const profileKey = typeof options === "string" ? options : (options.sceneProfile || options.profile || "varek_defense_line");
  const profile = SCENE_PROFILES[profileKey] || SCENE_PROFILES.varek_defense_line;

  const lower = promptText.toLowerCase();
  const violations = profile.forbiddenTokens.filter(token => {
    const regex = new RegExp(`\\b${token}\\b`, "i");
    return regex.test(lower);
  });
  const missingAnchors = profile.requiredAnchors.filter(anchor => !lower.includes(anchor));
  
  if (options.requireStyleRef && !options.styleReference) {
    missingAnchors.push("styleReference");
  }

  return {
    valid: violations.length === 0 && missingAnchors.length === 0,
    violations,
    missingAnchors,
    profile: profile.name
  };
}

/**
 * Synthesizes an input scene beat into a strictly guarded Thulan prompt.
 * Strips any forbidden tokens and enforces canonical mastercrafter anchors per scene profile.
 * @param {string} sceneDescription 
 * @param {object|string} options - profile name string or options object { sceneProfile, profile }
 * @returns {{ positivePrompt: string, negativePrompt: string, profile: string }}
 */
export function synthesizePrompt(sceneDescription, options = {}) {
  const profileKey = typeof options === "string" ? options : (options.sceneProfile || options.profile || "varek_defense_line");
  const profile = SCENE_PROFILES[profileKey] || SCENE_PROFILES.varek_defense_line;

  let cleaned = sceneDescription;
  for (const forbidden of profile.forbiddenTokens) {
    const regex = new RegExp(`\\b${forbidden}\\b`, "gi");
    cleaned = cleaned.replace(regex, "");
  }

  const positivePrompt = `${cleaned.trim()}, ${profile.positivePreset}`.replace(/\s+/g, " ");
  
  return {
    positivePrompt,
    negativePrompt: profile.negativePreset,
    profile: profile.name
  };
}
