# Package Workflows

Use this file when the task is about the built artifact, package-consumer behavior, or release-oriented validation rather than browser rendering semantics.

## Package Contract

The published package is a built ESM artifact:

- `main` points to `./dist/layout.js`
- `types` points to `./dist/layout.d.ts`
- the published `exports` map exposes:
  - `.`
  - `./demos/*`
  - `./assets/*`
  - `./package.json`

Treat this as the package-consumer contract. Do not reason from raw source alone when the task is about publishing or consuming the package.

## Shipped Files Versus Exported Contract

The tarball also ships:

- `dist/`
- `src/`
- `pages/demos/`
- `pages/assets/`
- `CHANGELOG.md`
- `LICENSE`

This does not mean consumers should import repo-internal modules from `src/`. The `exports` map still defines the supported import surface.

## Package Confidence Loop

Commands:

- `bun run check`
- `bun run build:package`
- `bun run package-smoke-test`

Use this loop when:

- the package entrypoint changes
- exported types change
- package build output changes
- consumer-facing API shape changes
- `package.json`, `tsconfig.build.json`, or `scripts/package-smoke-test.ts` changes

## Packaging Mechanics

- `prepack` rebuilds `dist/` before packaging
- `bun run package-smoke-test` validates the packed tarball against temporary JS and TS consumers
- internal `.ts` source imports should keep `.js` specifiers so `tsc -p tsconfig.build.json` emits correct runtime JS and declarations

## Release-Oriented Guardrails

- validate package-consumer behavior separately from upstream source internals
- use [public-api.md](public-api.md) for the package-facing contract
- use [internal-exports.md](internal-exports.md) only when the release is about upstream repo internals rather than package consumers
- when package shape changes, also run `python skills/pretext/scripts/check_layout_api_sync.py`

## Upstream Anchors

- `pretext/package.json`
- `pretext/CHANGELOG.md`
- `pretext/scripts/package-smoke-test.ts`
- `pretext/tsconfig.build.json`

## When To Escalate

Escalate beyond the package confidence loop when:

- browser parity may have shifted
- benchmark methodology changed
- text-engine internals changed in a way that could move correctness or performance
- demo-site assets or exported demo pages changed and the packaged examples may need checking
