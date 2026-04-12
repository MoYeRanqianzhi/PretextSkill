# Demo Spec: 小猫动态实时变化排版 (Kitten Dynamic Real-Time Layout)

## 1. Overview

A single self-contained HTML file that demonstrates `@chenglou/pretext`'s two-phase text measurement engine (prepare → layout) through an interactive kitten-card gallery. The core educational goal is to make the prepare/layout split **visible and intuitive**: prepare runs once per text/font change; layout runs on every width/size change—pure arithmetic, no DOM reflow.

**Target file:** `demos/kitten-layout.html`

---

## 2. UI Layout (ASCII Mockup)

```
┌─────────────────────────────────────────────────────────────────────┐
│  🐱 小猫动态实时变化排版 — Pretext Demo                              │
│  Kitten Dynamic Real-Time Layout                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─── Controls Panel ──────────────────────────────────────────┐    │
│  │ Container Width: ═══════════●═══════  [420px]               │    │
│  │ Font Size:       ═══●══════════════   [16px]                │    │
│  │ Language:  [🇺🇸 EN] [🇨🇳 中文] [🇯🇵 日本語] [🌐 Mixed]       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─── Performance Dashboard ───────────────────────────────────┐    │
│  │                                                             │    │
│  │  prepare() calls: 4        layout() calls: 127             │    │
│  │  ┌──────────┐              ┌──────────┐                    │    │
│  │  │ 2.34 ms  │ (last)       │ 0.02 ms  │ (last)            │    │
│  │  └──────────┘              └──────────┘                    │    │
│  │                                                             │    │
│  │  ◉ prepare fires on text/font change only                  │    │
│  │  ◉ layout fires on every width change (pure arithmetic!)   │    │
│  │                                                             │    │
│  │  [Flash indicator: 🟠 PREPARE] [Flash indicator: 🟢 LAYOUT] │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─── Kitten Cards (responsive container) ─────────────────────┐    │
│  │                                                             │    │
│  │  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │   🐱 Mochi       │  │   🐱 Sakura      │                  │    │
│  │  │                  │  │                  │                  │    │
│  │  │  Line 1 (blue)   │  │  Line 1 (blue)   │                  │    │
│  │  │  Line 2 (green)  │  │  Line 2 (green)  │                  │    │
│  │  │  Line 3 (purple) │  │  Line 3 (purple) │                  │    │
│  │  │  Line 4 (orange) │  │  Line 4 (orange) │                  │    │
│  │  │                  │  │                  │                  │    │
│  │  │  H: 80px  L: 4  │  │  H: 100px  L: 5 │                  │    │
│  │  └─────────────────┘  └─────────────────┘                  │    │
│  │                                                             │    │
│  │  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │   🐱 Tangerine   │  │   🐱 Luna        │                  │    │
│  │  │                  │  │                  │                  │    │
│  │  │  (lines...)      │  │  (lines...)      │                  │    │
│  │  │                  │  │                  │                  │    │
│  │  └─────────────────┘  └─────────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Breakdown

### 3.1 Header

- Title: "🐱 小猫动态实时变化排版"
- Subtitle: "Kitten Dynamic Real-Time Layout — Pretext Demo"
- Brief one-liner explaining the prepare/layout split concept

### 3.2 Controls Panel

| Control | Type | Range | Default | Triggers |
|---------|------|-------|---------|----------|
| Container Width | `<input type="range">` | 120 – 800 px | 420 px | `layout()` only |
| Font Size | `<input type="range">` | 10 – 36 px | 16 px | `prepare()` + `layout()` |
| Language | 4 radio buttons | EN / 中文 / 日本語 / Mixed | Mixed | `prepare()` + `layout()` |

### 3.3 Performance Dashboard

- **Prepare counter**: increments whenever `prepareWithSegments()` is called (text or font change)
- **Layout counter**: increments whenever `layoutWithLines()` is called (any change including width)
- **Last prepare time**: `performance.now()` delta in ms, displayed to 2 decimal places
- **Last layout time**: `performance.now()` delta in ms, displayed to 2 decimal places
- **Flash indicators**: two circular indicators that flash on fire:
  - 🟠 orange flash on prepare (lingers 600ms with CSS animation)
  - 🟢 green flash on layout (lingers 300ms with CSS animation)
- **Explanatory text**: always-visible labels explaining when each phase fires

### 3.4 Kitten Card Grid

A CSS grid of 4 kitten cards. Each card contains:

1. **Header**: emoji + kitten name (e.g., "🐱 Mochi")
2. **Rendered lines area**: each line rendered as an individual `<span>` element, positioned absolutely, styled with a line-specific color from a rotating palette. This is the core visual proof that `layoutWithLines()` provides per-line text/width data.
3. **Metrics footer**: computed height and line count from `layoutWithLines()` return value

**Why absolute positioning per line?** This proves that Pretext gives you the actual line text and dimensions—you don't need DOM flow to lay out text. Each line is an independently placed element.

---

## 4. Data Flow

```
User Action
    │
    ├── Width slider change ──────────────────────┐
    │                                              │
    ├── Font size slider change ──┐                │
    │                             │                │
    └── Language toggle ──────────┤                │
                                  │                │
                          text OR font changed?    │
                                  │                │
                              ┌───┴───┐            │
                              │  YES  │            │
                              └───┬───┘            │
                                  │                │
                    ┌─────────────▼──────────┐     │
                    │  prepareWithSegments() │     │
                    │  (per card × 4)        │     │
                    │  ⏱ ~2-5ms              │     │
                    └─────────────┬──────────┘     │
                                  │                │
                          Store prepared[] ◄───────┘
                                  │
                    ┌─────────────▼──────────┐
                    │  layoutWithLines()     │
                    │  (per card × 4)        │
                    │  ⏱ ~0.01-0.05ms       │
                    └─────────────┬──────────┘
                                  │
                          { height, lineCount, lines[] }
                                  │
                    ┌─────────────▼──────────┐
                    │  Render lines to DOM   │
                    │  - Per-line <span>     │
                    │  - Color by index      │
                    │  - Position: absolute  │
                    └────────────────────────┘
```

### State Model

```js
const state = {
  // Inputs
  maxWidth: 420,          // from width slider
  fontSize: 16,           // from font size slider
  language: 'mixed',      // from language toggle

  // Derived (invalidation keys)
  font: '16px "Helvetica Neue"',  // derived from fontSize

  // Cached prepare results (invalidated on text OR font change)
  prepared: [],           // PreparedTextWithSegments[] — one per card

  // Counters
  prepareCount: 0,
  layoutCount: 0,
  lastPrepareMs: 0,
  lastLayoutMs: 0,
}
```

### Invalidation Rules (Critical for Demo's Educational Point)

| What changed | Re-prepare? | Re-layout? |
|:---|:---:|:---:|
| Width slider | ❌ | ✅ |
| Font size slider | ✅ | ✅ |
| Language toggle | ✅ | ✅ |

---

## 5. Pretext APIs Used

### Primary APIs

| API | When Used | Why |
|-----|-----------|-----|
| `prepareWithSegments(text, font)` | On text or font change | Returns `PreparedTextWithSegments` which includes `.segments[]` for per-line rendering. We need `WithSegments` (not plain `prepare`) because we render lines individually. |
| `layoutWithLines(prepared, maxWidth, lineHeight)` | On every render (including width-only changes) | Returns `{ height, lineCount, lines }`. Each `LayoutLine` has `.text` (the line's visible characters) and `.width` (measured width). This is the educational centerpiece—pure arithmetic, no DOM. |

### Why Not Other APIs?

| API | Not Used Because |
|-----|-----------------|
| `prepare()` + `layout()` | Only returns `{ height, lineCount }`. We need actual line text for per-line rendering. |
| `layoutNextLine()` | Designed for variable-width-per-line scenarios (e.g., text flowing around images). Our cards have fixed width, so `layoutWithLines()` is simpler and sufficient. |
| `walkLineRanges()` | Returns geometry without materializing line text strings. We need the text for DOM rendering. |

### CDN Import

```html
<script type="module">
  import {
    prepareWithSegments,
    layoutWithLines
  } from 'https://esm.sh/@chenglou/pretext@0.0.3'
</script>
```

**Fallback CDN** (if esm.sh is unavailable): `https://cdn.jsdelivr.net/npm/@chenglou/pretext@0.0.3/dist/layout.js`

> **Note:** The library requires `Intl.Segmenter` support (all modern browsers). No polyfill needed for Chrome 87+, Firefox 125+, Safari 17.4+.

---

## 6. Text Content Samples

Four kitten cards, each with a description in the selected language.

### English (`en`)

```js
const EN = [
  { name: 'Mochi', emoji: '🐱', text: 'Mochi is a fluffy white kitten who loves to curl up in warm laundry baskets. She purrs like a tiny engine and her favorite toy is a crinkly ball of foil.' },
  { name: 'Sakura', emoji: '🌸', text: 'Sakura has striking calico markings and an adventurous spirit. She climbs bookshelves with ease and watches birds through the window for hours on end.' },
  { name: 'Tangerine', emoji: '🍊', text: 'Tangerine is an orange tabby with boundless energy. He zooms through the house at 3 AM and has knocked over exactly fourteen houseplants this month.' },
  { name: 'Luna', emoji: '🌙', text: 'Luna is a sleek black kitten with golden eyes. She is incredibly gentle and loves to nap on keyboards, accidentally sending mysterious emails to your coworkers.' },
]
```

### Chinese (`zh`)

```js
const ZH = [
  { name: '麻糬', emoji: '🐱', text: '麻糬是一只毛茸茸的白色小猫，最喜欢蜷缩在温暖的洗衣篮里。她的呼噜声像一台小发动机，最爱的玩具是一个皱巴巴的锡箔球。' },
  { name: '樱花', emoji: '🌸', text: '樱花有着引人注目的三色花纹和冒险精神。她轻松爬上书架，能连续好几个小时透过窗户观察小鸟。她的好奇心永远不会被满足。' },
  { name: '橘子', emoji: '🍊', text: '橘子是一只精力充沛的橙色虎斑猫。他凌晨三点在房间里疯跑，这个月已经打翻了整整十四盆绿植。但没有人能对他生气。' },
  { name: '月亮', emoji: '🌙', text: '月亮是一只有着金色眼睛的黑色小猫。她性格温柔，最爱在键盘上打盹，不小心给你的同事发送各种神秘的电子邮件。' },
]
```

### Japanese (`ja`)

```js
const JA = [
  { name: 'もち', emoji: '🐱', text: 'もちはふわふわの白い子猫で、温かい洗濯カゴの中で丸くなるのが大好きです。小さなエンジンのようにゴロゴロ喉を鳴らし、お気に入りのおもちゃはくしゃくしゃのアルミボールです。' },
  { name: 'さくら', emoji: '🌸', text: 'さくらは目を引く三毛猫で、冒険心にあふれています。本棚を軽々と登り、窓越しに何時間も鳥を観察しています。彼女の好奇心は尽きることがありません。' },
  { name: 'みかん', emoji: '🍊', text: 'みかんはエネルギーいっぱいのオレンジ色のトラ猫です。午前3時に家中を走り回り、今月だけで観葉植物を14鉢も倒しました。でも誰も彼に怒れません。' },
  { name: 'ルナ', emoji: '🌙', text: 'ルナは金色の目をした黒い子猫です。とても優しい性格で、キーボードの上で昼寝をするのが好きで、同僚に謎のメールを送ってしまいます。' },
]
```

### Mixed (`mixed`)

```js
const MIXED = [
  { name: 'Mochi 麻糬', emoji: '🐱', text: 'Mochi是一只fluffy白色kitten 🐱 最喜欢curl up在warm laundry baskets里。她purrs like a tiny engine，最爱的toy是一个crinkly ball of foil。' },
  { name: 'Sakura さくら', emoji: '🌸', text: 'Sakura有着striking的calico markings和冒険心 🌸 She climbs本棚を軽々と登り、窓越しに何時間もbirds watching。好奇心は尽きることがありません！' },
  { name: 'Tangerine 橘子', emoji: '🍊', text: '橘子is an orange tabby with boundless energy 🍊 凌晨3AM在house里zooming，今月だけで14 houseplants knocked over。But nobody can stay mad at him!' },
  { name: 'Luna ルナ', emoji: '🌙', text: 'Luna是一只sleek black kitten 🌙 golden eyes闪闪发光。キーボードの上でnap、accidentally sending mysterious emails给your coworkers。温柔で優しい。' },
]
```

---

## 7. CSS Theme Description

### Design Language

- **Warm, playful "cat café" aesthetic** — cream/warm-white backgrounds, rounded corners, soft shadows
- Inspired by the existing Pretext demo style (bubbles demo) but with a distinct kitten character

### Color Palette

| Role | Value | Usage |
|------|-------|-------|
| Page background | `#faf6f0` | Warm cream base |
| Card background | `#fffdf8` | Slightly lighter cream |
| Card border | `#e8ddd0` | Warm taupe border |
| Text (primary) | `#2d2520` | Dark brown-black |
| Text (muted) | `#7a6e63` | Warm gray |
| Accent | `#e87040` | Orange — cat themed! |
| Accent soft | `#fff0e8` | Light orange wash |
| Prepare flash | `#f59e0b` | Amber/orange |
| Layout flash | `#10b981` | Emerald green |

### Line Color Palette (rotating per line index)

```js
const LINE_COLORS = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#8b5cf6', // violet
  '#f59e0b', // amber
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f43f5e', // rose
]
```

Each line `<span>` gets `color: LINE_COLORS[lineIndex % LINE_COLORS.length]`, making line boundaries visually obvious.

### Card Styling

```css
.kitten-card {
  border: 1px solid #e8ddd0;
  border-radius: 20px;
  background: #fffdf8;
  box-shadow: 0 8px 24px rgba(45, 37, 32, 0.06);
  padding: 20px;
  overflow: hidden;
}
```

### Line Rendering Area

Each card has a `.lines-container` with `position: relative` and a computed `height` from `layoutWithLines().height`. Lines are absolutely positioned spans:

```css
.line-span {
  position: absolute;
  left: 0;
  white-space: nowrap;
  font: var(--card-font);
  line-height: var(--card-line-height);
}
```

### Responsive Behavior

- Grid: `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- On narrow screens (< 640px): single column, controls stack vertically
- Card width adapts to grid cell, but the text layout inside respects the `maxWidth` slider (clamped to card width)

### Animations

- Prepare flash: `.flash-prepare` — background fades from `#f59e0b` to transparent over 600ms
- Layout flash: `.flash-layout` — background fades from `#10b981` to transparent over 300ms
- Counter value changes: brief scale pulse via CSS `transform: scale(1.15)` → `scale(1)` over 200ms
- Slider thumb: custom styled with the accent orange color

---

## 8. Implementation Notes

### Module Loading

```html
<script type="module">
  import { prepareWithSegments, layoutWithLines } from 'https://esm.sh/@chenglou/pretext@0.0.3'

  // All app code follows inline...
</script>
```

`esm.sh` will resolve the ESM export from the published npm package. The `dist/layout.js` entry is proper ESM (`"type": "module"` in package.json).

### Font Loading

Wait for fonts before first render to ensure measurements are accurate:

```js
await document.fonts.ready
// then do initial prepare + layout + render
```

Use a named font (not `system-ui`) per the Pretext caveats. Recommended: `"Helvetica Neue", Helvetica, Arial, sans-serif`.

### Render Loop Pattern

Follow the existing demo convention (bubbles, dynamic-layout): no `setInterval`; instead, schedule a single `requestAnimationFrame` on input events.

```js
let rafId = null

function scheduleRender() {
  if (rafId !== null) return
  rafId = requestAnimationFrame(() => {
    rafId = null
    render()
  })
}

slider.addEventListener('input', scheduleRender)
```

### Key Render Function Pseudocode

```js
function render() {
  const font = `${state.fontSize}px "Helvetica Neue", Helvetica, Arial, sans-serif`
  const lineHeight = Math.round(state.fontSize * 1.5)
  const textChanged = font !== state.lastFont || state.language !== state.lastLanguage

  if (textChanged) {
    const t0 = performance.now()
    state.prepared = cards.map(card =>
      prepareWithSegments(card.text, font)
    )
    state.lastPrepareMs = performance.now() - t0
    state.prepareCount++
    state.lastFont = font
    state.lastLanguage = state.language
    flashPrepareIndicator()
  }

  const t0 = performance.now()
  const results = state.prepared.map(p =>
    layoutWithLines(p, state.maxWidth, lineHeight)
  )
  state.lastLayoutMs = performance.now() - t0
  state.layoutCount++
  flashLayoutIndicator()

  // Render each card's lines to DOM
  results.forEach((result, cardIndex) => {
    renderCardLines(cardIndex, result.lines, result.height, lineHeight)
  })

  updateDashboard()
}
```

### DOM Pooling

Reuse `<span>` elements across renders (pool pattern from existing demos) rather than clearing innerHTML. This keeps the demo itself performant and doesn't introduce its own DOM overhead.

---

## 9. File Structure

Everything in a single `demos/kitten-layout.html`:

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🐱 Kitten Layout — Pretext Demo</title>
  <style>
    /* ~200 lines of inline CSS (theme, layout, animations) */
  </style>
</head>
<body>
  <!-- ~80 lines of HTML structure -->
  <script type="module">
    /* ~250 lines of inline JS (import, state, render loop, DOM pooling) */
  </script>
</body>
</html>
```

Estimated total: **~530 lines**, all self-contained, no build step.

---

## 10. Acceptance Criteria

1. ✅ Opening the HTML file in a modern browser shows 4 kitten cards with colorful per-line text
2. ✅ Dragging the width slider re-wraps all card text in real time without visible lag
3. ✅ The prepare counter does **NOT** increment when only the width slider moves
4. ✅ The prepare counter **DOES** increment when font size or language changes
5. ✅ The layout counter increments on every slider movement
6. ✅ Performance times show prepare ≫ layout (typically ~100× difference)
7. ✅ All 4 language modes render correctly (including CJK line-breaking and mixed-script)
8. ✅ Each line in a card has a distinct color from the rotating palette
9. ✅ The page works without any build step or server — just open the `.html` file (with a CDN-available network connection for the module import)
10. ✅ The design has a cohesive warm "cat café" aesthetic

---

## 11. Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| CDN unavailable | Document fallback CDN URL in comments. Could also include a note about local bundling. |
| `Intl.Segmenter` not available | All target browsers (Chrome 87+, FF 125+, Safari 17.4+) support it. Add a visible error message for unsupported browsers. |
| Canvas font measurement differs from DOM | Use a named font (not `system-ui`). This is a documented Pretext caveat. |
| Very narrow widths cause grapheme-level word breaking | This is expected `overflow-wrap: break-word` behavior and actually demonstrates Pretext's correctness. |
| Performance timers too fast to read | Show values with 2-decimal precision. Aggregate layout time across all 4 cards for a more readable number. |
