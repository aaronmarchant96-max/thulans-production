/**
 * Tactical Badge & Caption Plate Validator
 * Enforces canonical Dark Horse tactical badges and narrative plates.
 * Example: "THE WELDED / EASTSHAFT-6A112"
 */

export const BADGE_REGEX = /^[A-Z0-9\s\-]+ \/ [A-Z0-9\-]+$/;

/**
 * Validates a tactical badge against canonical formatting rules.
 * @param {string} badgeText 
 * @returns {{ valid: boolean, error?: string }}
 */
export function validateBadgeSyntax(badgeText) {
  if (!badgeText || typeof badgeText !== "string") {
    return { valid: false, error: "Badge text must be a non-empty string" };
  }
  
  const trimmed = badgeText.trim();
  if (!BADGE_REGEX.test(trimmed)) {
    return { 
      valid: false, 
      error: `Badge "${trimmed}" does not match canonical syntax "TITLE / SECTOR-CODE"` 
    };
  }
  
  return { valid: true };
}

/**
 * Generates an SVG overlay definition for the tactical badge.
 * @param {string} badgeText 
 * @param {number} canvasWidth 
 * @param {number} canvasHeight 
 * @returns {string} SVG markup
 */
export function renderBadgeSvg(badgeText, canvasWidth = 1920, canvasHeight = 1080) {
  const check = validateBadgeSyntax(badgeText);
  if (!check.valid) {
    throw new Error(check.error);
  }

  const [title, sector] = badgeText.split(" / ");
  
  // Tactical Dark Horse badge dimensions
  const x = 60;
  const y = 60;
  const padX = 24;
  const padY = 14;

  return `
  <g id="thulan-tactical-badge" font-family="'Impact', 'Arial Black', sans-serif">
    <!-- Outer heavy ink frame -->
    <rect x="${x}" y="${y}" width="420" height="74" fill="#0b0b0d" stroke="#d49b42" stroke-width="4" />
    <rect x="${x + 6}" y="${y + 6}" width="408" height="62" fill="none" stroke="#1a1a1f" stroke-width="2" />
    <!-- Sector callsign -->
    <text x="${x + padX}" y="${y + 32}" fill="#d49b42" font-size="14" letter-spacing="3" font-weight="900">${sector}</text>
    <!-- Primary title -->
    <text x="${x + padX}" y="${y + 58}" fill="#f2ede4" font-size="24" letter-spacing="2" font-weight="900">${title}</text>
  </g>
  `.trim();
}
