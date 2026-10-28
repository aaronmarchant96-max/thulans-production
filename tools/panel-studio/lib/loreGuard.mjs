/**
 * Lore Guard & Anti-Fantasy Enforcement Engine (Hardened v2.2)
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

// Positive presets describe purely affirmative visual elements to prevent self-conflicts with forbidden tokens during audits
export const CANONICAL_POSITIVE_PRESET = 
  "Dark Horse comic book illustration, heavy ink, angular black brushwork, deep chiaroscuro solid pitch-black shadows, high contrast grimdark industrial dieselpunk, deep subterranean coal mine shaft, sloped bronze and hammered copper ballistic mantlets, floor-anchored hydraulic shock-absorber pistons, heavy iron rivets, industrial pressure suits with heavy leather blast aprons, full-face brass respirator helmets with dark rectangular welding glass visors, heavy pneumatic breaker tools, coal dust and venting steam plumes, warm amber lantern glow";

export const CANONICAL_NEGATIVE_PRESET = 
  "swords, blades, daggers, spears, pikes, lances, polearms, chainmail, mail armor, medieval fantasy, Dark Souls, Roman soldiers, legionaries, knights, crude wooden shields, round bucklers, speech bubbles, comic word balloons, sound effect text, onomatopoeia, lettering, captions inside image, artist signatures, watermark, outdoors, mountains, sunny daylight, photorealistic, 3d cgi render, clean smooth plastic, Hellboy, red demon, horns, tail, trenchcoat";

export const FORTIS_POSITIVE_PRESET =
  "Heavy European graphic-novel ink, firm silhouettes, subdued halftone and soot grain, near-monochrome charcoal and slate black tones, single motivated warm amber accent, print lithograph texture, deep structural shadows";

export const FORTIS_NEGATIVE_PRESET =
  "swords, blades, spears, daggers, fantasy armor, flowing capes, cloth capes, magic glow, magical aura, medieval fantasy, Dark Souls, knights, wooden shields, round bucklers, glossy CGI, 3D render, photorealistic, anime faces, manga, neon glow, ambient orange skyline, decorative bloom, speech bubbles, comic word balloons, sound effect text, lettering, captions inside image, artist signatures, watermark";

export const SCENE_PROFILES = {
  varek_defense_line: {
    name: "varek_defense_line",
    description: "Episode 001 defense line / Varek ballistic combat",
    forbiddenTokens: VAREK_DEFENSE_LINE_FORBIDDEN_TOKENS,
    requiredAnchors: VAREK_REQUIRED_CANONICAL_ANCHORS,
    positivePreset: CANONICAL_POSITIVE_PRESET,
    negativePreset: CANONICAL_NEGATIVE_PRESET
  },
  fortis_pilot: {
    name: "fortis_pilot",
    description: "FORTIS / Salvation 16-page pilot (Ansen & Nessa)",
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
 * Resolves a sceneProfile name or throws an explicit error if unknown.
 * @param {string|undefined} profileKey 
 * @returns {object} The resolved scene profile object
 */
export function getSceneProfile(profileKey) {
  if (!profileKey) {
    return SCENE_PROFILES.varek_defense_line;
  }
  const resolved = SCENE_PROFILES[profileKey];
  if (!resolved) {
    const valid = Object.keys(SCENE_PROFILES).join(", ");
    throw new Error(`Unknown sceneProfile: "${profileKey}". Valid profiles are: ${valid}`);
  }
  return resolved;
}

/**
 * Audits a prompt for forbidden tokens, canonical anchors, and optional production metadata.
 * Defaults to "varek_defense_line" for 100% backward compatibility.
 * Rejects unknown profiles explicitly.
 * @param {string} promptText 
 * @param {object|string} options - profile name string or options object { sceneProfile, profile, requireStyleRef, styleReference, production }
 * @returns {{ valid: boolean, violations: string[], missingAnchors: string[], missingMetadata: string[], profile: string, styleAudit: object }}
 */
export function auditPrompt(promptText, options = {}) {
  const profileKey = typeof options === "string" ? options : (options.sceneProfile || options.profile);
  const profile = getSceneProfile(profileKey);

  const lower = promptText.toLowerCase();
  const violations = profile.forbiddenTokens.filter(token => {
    const regex = new RegExp(`\\b${token}\\b`, "i");
    return regex.test(lower);
  });
  const missingAnchors = profile.requiredAnchors.filter(anchor => !lower.includes(anchor));
  const missingMetadata = [];

  const styleRef = typeof options === "object" ? (options.styleReference || options.reference_versions?.visual_style) : null;
  const requireStyle = typeof options === "object" && (options.requireStyleRef || options.production);

  if (requireStyle) {
    if (!styleRef || typeof styleRef !== "string" || styleRef.trim() === "" || styleRef === "pending_approval" || styleRef === "unassigned") {
      missingMetadata.push("styleReference");
    }
  }

  const valid = violations.length === 0 && missingAnchors.length === 0 && missingMetadata.length === 0;

  return {
    valid,
    violations,
    missingAnchors,
    missingMetadata,
    profile: profile.name,
    styleAudit: {
      metadataVerified: requireStyle ? (missingMetadata.length === 0) : Boolean(styleRef),
      styleReference: styleRef || null,
      disclaimer: "Text audit verifies prompt token compliance and style reference metadata presence only. It does not prove rendered image style, which requires human visual review."
    }
  };
}

/**
 * Synthesizes an input scene beat into a strictly guarded Thulan prompt.
 * Strips any forbidden tokens and enforces canonical mastercrafter anchors per scene profile.
 * Rejects unknown profiles explicitly.
 * @param {string} sceneDescription 
 * @param {object|string} options - profile name string or options object { sceneProfile, profile }
 * @returns {{ positivePrompt: string, negativePrompt: string, profile: string }}
 */
export function synthesizePrompt(sceneDescription, options = {}) {
  const profileKey = typeof options === "string" ? options : (options.sceneProfile || options.profile);
  const profile = getSceneProfile(profileKey);

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

/**
 * Validates a panel production contract entry at the production boundary.
 * Requires approved, versioned style-reference metadata without claiming text audit proves rendered style.
 * @param {object} manifestEntry - Panel manifest entry matching FORTIS visual specification
 * @returns {{ valid: boolean, errors: string[], audit: object, styleAudit: object }}
 */
export function validateProductionBoundary(manifestEntry) {
  if (!manifestEntry || typeof manifestEntry !== "object") {
    throw new Error("Production manifest entry must be a valid object");
  }

  const errors = [];
  const styleRef = manifestEntry.styleReference || manifestEntry.reference_versions?.visual_style;

  if (!styleRef || typeof styleRef !== "string" || styleRef.trim() === "" || styleRef === "pending_approval" || styleRef === "unassigned") {
    errors.push("Missing approved, versioned style reference metadata (e.g. 'FORTIS_STYLE_V1')");
  }

  const promptText = manifestEntry.prompt || manifestEntry.positivePrompt || manifestEntry.story_beat || "";
  const profileKey = manifestEntry.sceneProfile || manifestEntry.profile || "varek_defense_line";

  const audit = auditPrompt(promptText, {
    sceneProfile: profileKey,
    requireStyleRef: true,
    styleReference: styleRef
  });

  if (!audit.valid) {
    if (audit.violations.length > 0) errors.push(`Forbidden tokens: ${audit.violations.join(", ")}`);
    if (audit.missingAnchors.length > 0) errors.push(`Missing anchors: ${audit.missingAnchors.join(", ")}`);
    if (audit.missingMetadata.length > 0) errors.push(`Missing metadata: ${audit.missingMetadata.join(", ")}`);
  }

  return {
    valid: errors.length === 0,
    errors,
    audit,
    styleAudit: {
      metadataVerified: Boolean(styleRef && styleRef !== "pending_approval" && styleRef !== "unassigned"),
      styleReference: styleRef || null,
      disclaimer: "Text audit verifies prompt token compliance and style reference metadata presence only. It does not prove rendered image style, which requires human visual review."
    }
  };
}
