---
name: evaluate
description: Evaluate project source code in this Andromeda repo (Python AGI emulator under `resource/`, `gfx/`, `util/`, `main.py`). Use when the user says "evaluate", "review code", "check my decoder", or asks for a critique of a specific file, module, function, or pasted snippet. Reports findings only — no fixes, no draft edits. Not for PR reviews (use `/review`) or wiki maintenance (use `wiki-*` commands).
---

# Evaluate project source

Evaluate a specified target — a file, module, function, or pasted snippet — against this project's correctness, reuse, and style concerns. Report findings only.

- Reports findings only — no fixes, no draft edits, no code suggestions.
- `andromeda-wiki/` is out of scope; defer wiki concerns to `/wiki-lint` or `/wiki-file`.
- PR-wide reviews belong to `/review`; this skill is for ad-hoc local code.
- If the target is empty or ambiguous, ask the user which module, file, function, or snippet to evaluate before reading anything.

## Project style preferences

These are the user's durable coding preferences for this project. Internalize them before reviewing.

- The project leans **opportunistically functional, not dogmatically.** Prefer separating pure functions from side effects, first-class functions, closures, function composition, and partial application where they yield clearer or more reusable units.
- Lambdas, `map`, `reduce`, `filter`, and list/dict comprehensions are welcome where they read naturally.
- Build **small modular units** that compose into larger-scope functions. Reuse-over-reimplementation is the default.
- **Structured/procedural and OOP code are equally acceptable** where they fit — this is a game-engine emulator with low-latency rendering, so performance and clarity outrank style ideology. PySDL2 lifecycle code in particular tends to be procedural or class-based; that is fine.
- When in doubt about a tradeoff, name it; do not flag procedural code as a style issue unless it is also a clarity or correctness issue.

## Steps

1. **Resolve target.** Accept: file paths (`resource/view.py`), module names, function/class names with a module qualifier, or pasted snippets. If the request is vague (e.g., "review my recent changes" with no path), ask one clarifying question and stop until answered.

2. **Boundary checks.**
   - If the target lives under `andromeda-wiki/`, refuse and redirect to `/wiki-lint` (for lint passes) or `/wiki-file` (for individual findings). Do not read the file.
   - If the request is clearly a PR review (mentions a PR number, branch name, or "the PR"), defer to `/review` and stop.

3. **Load context.** Read `CLAUDE.md` and the target files. Do not read `andromeda-wiki/`. For symbols referenced by but not in the target, read only enough surrounding context to evaluate — no broad codebase tours. Note: `CLAUDE.md` says the EGA palette lives in `gfx/view_render.py`, but it has moved to `gfx/palette.py`; trust the actual module layout.

4. **Evaluate against project concerns.** Walk the target with these axes in mind. They are evaluation prompts, not output sections.

   - **Byte-level correctness** — nibble ordering, endianness, offset arithmetic against AGI v2 conventions in `CLAUDE.md` and the existing decoders.
   - **Encoding edge cases** — RLE row termination (`0x00`), XOR key rotation (`Avis Durgan`), mirror/loop flag extraction, off-by-one risks at section boundaries.
   - **Resource pipeline correctness** — file-handle lifecycle, seek/read pairing, sentinel handling for missing resources (`0xFF` / `0xFFFFF`).
   - **PySDL2 lifecycle** — `SDL_FreeSurface` paired with `SDL_CreateRGBSurfaceFrom`, texture ownership relative to renderer, palette correctness, alpha-as-index transparency.
   - **Reuse** — flag duplicates of existing utilities:
     - `util/byte.py:nibble` (hi/lo nibble extraction)
     - `util/crypto.py:xor_cycle` (repeating-key XOR)
     - `resource/volume.py:VolumeReader` and `resource/header.py:ResourceHeader` (volume read + resource header parsing)
     - `resource/directory.py:read_dir` (DIR triplet parsing)
     - `gfx/palette.py:palette` (16-color EGA table)
   - **Python idiom & project style** — over-abstraction, premature generality, error handling for impossible cases, defensive code that contradicts the project's "trust internal code" stance in `CLAUDE.md`.
   - **FP-fit (opportunistic, not dogmatic).** Cross-reference *Project style preferences* above. Flag spots where a small refactor toward FP would yield a clearly more reusable or composable unit — e.g., a side-effecting function that could be split into a pure transform + a thin I/O wrapper; an imperative accumulator that maps cleanly to `map`/`reduce`/comprehension; repeated function shapes that suggest partial application or composition. Do **not** flag procedural or OOP code purely for being procedural or OOP — only flag when functional decomposition would measurably improve clarity, reuse, or testability without harming performance.

5. **Emit findings.** One section per severity tier, in this order: `Critical`, `Major`, `Minor`, `Nit`. Omit empty tiers. Each finding is a single bullet:
   - `path/to/file.py:LINE` — one-sentence statement of the issue and its consequence.
   - For a range, use `file.py:START-END`.
   - No code blocks, no patch suggestions, no "consider doing X" prose.

## Severity rubric

- **Critical** — produces wrong output, crashes, corrupts state, or silently mis-decodes a resource.
- **Major** — latent correctness risk: unhandled edge case, plausible off-by-one, spec mismatch, resource leak.
- **Minor** — style/clarity/idiom that does not affect correctness but adds friction or surprises a reader.
- **Nit** — cosmetic: naming, ordering, whitespace, dead imports.

## Closing

If no findings at any tier, say so in a single sentence. Otherwise stop after the last tier — no summary commentary.
