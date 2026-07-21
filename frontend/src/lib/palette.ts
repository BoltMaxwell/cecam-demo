// Validated categorical palette (dataviz skill, 2026-07-20): 8 slots, light and
// dark steps of the same hues. Adjacent-pair CVD dE 9.1 light / 8.4 dark,
// normal-vision dE 19.6 / 19.3 — all checks pass; light slots 3-5 are sub-3:1
// contrast, mitigated by legend + tooltips + the ledger table (relief rule).
const LIGHT = ["#2a78d6", "#008300", "#e87ba4", "#eda100", "#1baf7a", "#eb6834", "#4a3aa7", "#e34948"]
const DARK  = ["#3987e5", "#008300", "#d55181", "#c98500", "#199e70", "#d95926", "#9085e9", "#e66767"]

// Reserved status colors (never used as series colors) + neutral.
export const STATUS = { good: "#0ca30c", critical: "#d03b3b", neutral: "#898781" }

// Purdue gold — chrome only (header rule), never data ink.
export const GOLD = "#cfb991"

const OBSERVED = ["NO3", "NO2", "N2", "NH3", "N2O"]

// Color follows the species NAME, not its position: observed species keep
// slots 0-4 forever; hidden species take slots 5-7 by order of appearance in
// the model. Never cycled: a 4th hidden species falls back to neutral gray.
function slot(name: string, species: string[]): number {
  const obs = OBSERVED.indexOf(name)
  if (obs >= 0) return obs
  return 5 + species.filter((s) => !OBSERVED.includes(s)).indexOf(name)
}

export function speciesTheme(name: string, species: string[]) {
  const i = slot(name, species)
  return {
    light: LIGHT[i] ?? STATUS.neutral,
    dark: DARK[i] ?? STATUS.neutral,
  }
}
