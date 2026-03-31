# Script And Browser Caveats

Use this file when the task is about script-sensitive segmentation, punctuation-glue classes, bidi, emoji, browser behavior, or research canaries.

## Punctuation And Structured Token Rules

Tests establish explicit expectations for:

- closing punctuation attaching to the preceding word
- opening punctuation and quote clusters attaching to the following word when context requires
- contextual ASCII quote glue
- Arabic punctuation and punctuation-plus-mark clusters
- Devanagari danda punctuation
- Myanmar punctuation and possessive-marker glue
- URL-like runs and query-string structure
- numeric time ranges
- hyphenated numeric identifiers
- repeated punctuation runs

## Script And Directional Behavior

- CJK text can split into grapheme-level break units
- Hangul punctuation attachment has explicit behavior
- astral CJK ideographs are treated as CJK break units
- mixed-direction text is a stable smoke-test path
- locale-sensitive segmentation uses `Intl.Segmenter`
- Thai and other locale-sensitive scripts can depend on `setLocale()` before preparation

## Browser Caveats

- `system-ui` is unsafe for accuracy-sensitive macOS layout
- Chrome and Firefox on macOS can over-measure emoji in canvas at small sizes; Pretext uses a cached correction

## Research Canaries

These are not ordinary "just patch it" bug zones. Treat them as places where the current model has known tension or exactness ceilings.

| Area | Current Read | Design Caution |
| --- | --- | --- |
| Myanmar | unresolved quote and follower-style classes | do not stack instinctive glue rules without broad evidence |
| Japanese | punctuation and proportional-font exactness ceiling | do not keep piling on narrow punctuation heuristics |
| Chinese | narrow-width and font-sensitive exactness ceiling | treat as a real canary, not an obvious missed punctuation rule |
| Arabic | remaining fine-width shaping or context classes | be skeptical of heavy shaping-aware width caches |

## Practical Rule

When a task touches one of these areas, ask:

1. Is this a reproducible regression or a known canary?
2. Does upstream already document this as a frontier or exactness ceiling?
3. Am I about to overfit one script or browser at the expense of the broader model?
