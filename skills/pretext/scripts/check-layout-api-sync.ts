#!/usr/bin/env bun
/**
 * Check whether skill docs cover the exports from pretext/src/layout.ts.
 *
 * Usage:
 *   bun run skills/pretext/scripts/check-layout-api-sync.ts
 *
 * Exit code 0 if in sync, 1 if mismatches found.
 */

import { join, resolve } from "node:path";

// ── Regex patterns (identical to the Python version) ────────────────────────

const FUNCTION_RE = /^export function (\w+)\(/gm;
const TYPE_RE = /^export type (\w+)\b/gm;
const HEADING_RE = /^### `([A-Za-z_]\w*)(?:\(|`)/gm;
const BULLET_CODE_RE = /^- `([A-Za-z_]\w*)`$/gm;

// ── Helpers ─────────────────────────────────────────────────────────────────

/** Collect all capture-group-1 matches for a global regex. */
function allMatches(re: RegExp, text: string): string[] {
  const results: string[] = [];
  // Reset lastIndex in case the regex was used before
  re.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    results.push(m[1]);
  }
  return results;
}

function extractLayoutExports(layoutTs: string): Set<string> {
  const exports = new Set<string>(allMatches(FUNCTION_RE, layoutTs));
  for (const name of allMatches(TYPE_RE, layoutTs)) {
    exports.add(name);
  }
  return exports;
}

function extractDocumentedNames(markdown: string): Set<string> {
  const names = new Set<string>(allMatches(HEADING_RE, markdown));
  for (const name of allMatches(BULLET_CODE_RE, markdown)) {
    names.add(name);
  }
  return names;
}

// ── Main ────────────────────────────────────────────────────────────────────

async function main(): Promise<number> {
  // import.meta.dir → …/skills/pretext/scripts  →  3 parents up = repo root
  const repoRoot = resolve(import.meta.dir, "..", "..", "..");

  const layoutPath = join(repoRoot, "pretext", "src", "layout.ts");
  const publicApiPath = join(
    repoRoot,
    "skills",
    "pretext",
    "reference",
    "public-api.md",
  );
  const internalExportsPath = join(
    repoRoot,
    "skills",
    "pretext",
    "reference",
    "internal-exports.md",
  );

  // Read all files concurrently using Bun-native file reading
  const [layoutText, publicApiText, internalExportsText] = await Promise.all([
    Bun.file(layoutPath).text(),
    Bun.file(publicApiPath).text(),
    Bun.file(internalExportsPath).text(),
  ]);

  const layoutExports = extractLayoutExports(layoutText);

  const documentedNames = extractDocumentedNames(publicApiText);
  for (const name of extractDocumentedNames(internalExportsText)) {
    documentedNames.add(name);
  }

  // Set difference: missing = layoutExports − documentedNames
  const missing = [...layoutExports]
    .filter((n) => !documentedNames.has(n))
    .sort();
  // Set difference: extra = documentedNames − layoutExports
  const extra = [...documentedNames]
    .filter((n) => !layoutExports.has(n))
    .sort();

  if (missing.length === 0 && extra.length === 0) {
    console.log("Layout export docs are in sync.");
    return 0;
  }

  if (missing.length > 0) {
    console.log("Missing documented exports:");
    for (const name of missing) {
      console.log(`- ${name}`);
    }
  }

  if (extra.length > 0) {
    console.log("Documented names that are not layout.ts exports:");
    for (const name of extra) {
      console.log(`- ${name}`);
    }
  }

  return 1;
}

process.exit(await main());
