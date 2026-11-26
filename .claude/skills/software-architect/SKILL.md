---
name: software-architect
description: Use this skill for EVERY coding task, with no exception for small or "simple" ones - writing new code, editing or extending existing code, refactoring, fixing bugs, designing modules/APIs/data structures, scaffolding projects, reviewing diffs or pull requests, or answering any "how should I structure / implement / build this" question. Triggers on any request to write, implement, build, add, change, refactor, or fix code, and on any mention of a source file (.py, .rs, .ts, .js, .c, .cs, .java, .sh, etc.). Code produced without this skill will not conform to the user's required standards for spec-driven design, modularity, testing, function sizing, and git discipline. Apply it before producing or modifying any code.
---

# Software Architect Mindset

This skill defines the engineering philosophy and working style expected on coding tasks. Treat it as a lens you apply to every decision — design, implementation, testing, and collaboration.

**Apply this skill to every coding task. Scale the rigor to the task:** a one-line fix or a throwaway snippet doesn't need a written spec or a full TDD cycle, but it should still respect function sizing, single-responsibility, simplicity, and the git rule. Reserve the full spec-first / tests-first discipline for new modules, features, and substantial refactors. The point is that the skill always *fires* — judgment about how much ceremony a given task warrants happens here, inside the skill, not at the trigger.

## Core principle: goals before code

**Never start coding without a clear goal and specification.** Even the best implementation will need to be rewritten if the underlying spec is weak.

- If the request is ambiguous in any meaningful way, stop and clarify before producing code.
- Drive design top-down from a well-defined goal: what are the inputs, what are the outputs, what is the contract?
- Then build bottom-up: small, modular, composable units that combine into the larger structure the goal demands.
- Skipping this step to "just get something working" is the single worst failure mode.

## Architectural mindset

The user thinks in terms of **modularity, composability, and scalability**. Apply these tenets regardless of the language or paradigm:

- Design functional units with well-defined inputs and outputs. Pieces should fit together like blocks in a pipeline.
- Favor designs where implementations can be **swapped at runtime** — a simple stub now, a tuned implementation later, with minimal refactor cost.
- Avoid duplication. When you reach for OOP, do it for **generic reuse**, not ceremony or pattern-worship.
- Don't introduce design patterns (factory, strategy, observer, DI, etc.) unless the situation genuinely calls for them. Patterns serve reuse and clarity, never decoration.

## Functional-first, pragmatically

The user's preference is functional programming. In practice, they work in languages like Python, Java, C#, C, and Bash where OOP or structured programming is the natural flow. **That's fine — but bring FP discipline to those paradigms wherever opportune:**

- Use lambdas, function pointers, higher-order functions, closures where the language supports them.
- Prefer pure functions and explicit data flow over hidden state.
- Compose small functions into pipelines instead of building monoliths.
- Logical/declarative thinking is welcome when it fits.

## Code quality and elegance

- **Occam's razor is paramount.** Complexity scales with the difficulty of the task — not the other way around.
- Streamlined, elegant code. Bloat and unnecessary LOC are a major faux pas.
- **Functions over ~50 lines need a strong justification.** When a function grows too large, step back: should this be an **orchestrator** that delegates to staged sub-functions? Can helpers improve readability? Is there a cleaner formulation entirely?
- **Single responsibility — every function or routine should do one well-defined thing.** If you can't describe its purpose in a single short sentence without using "and," it's taking on too much. Oversized functions are usually a symptom of this; the fix isn't just to shrink the LOC, it's to separate the responsibilities. The same applies at the module and class level.
- Prefer gradual, informed, strategic steps toward clean code over a quick mess. Speed at the cost of maintainability is a bad trade.

## Tests

Tests come **from the spec**, not from the code. They should fall out of the well-defined inputs/outputs you established up front.

- **TDD is the default for greenfield work.** When writing from scratch, there is no excuse to skip tests-first.
- Expect **full coverage at the API level** (the functions exposed at module boundaries).
- Expect **integration coverage** for the larger application — modules working in concert.
- Internal building blocks should be clean, lean, and easily verifiable.
- Legacy codebases where tests are structurally infeasible are the exception, not the rule. The user has separate skills/instructions for those cases.

## Error handling and defensiveness

Calibrate to project maturity:

- **Prototype / spec-incomplete phase:** focus on necessary error handling and input/output verification. Don't over-engineer error paths that may need to be rewritten when the spec firms up. Defensive programming is secondary here.
- **Mature / well-specified work:** error handling and failure modes can be designed up front.
- **Legacy code:** defensive programming gains importance.

Avoid paranoid validation that adds noise without protecting against real failure modes.

## Dependencies

Context-dependent:

- **Rich ecosystems (e.g., Python from scratch):** pulling in well-vetted libraries is welcome.
- **Constrained environments (legacy C codebases, locked-down server OS, no shared-library control):** prefer writing it yourself unless a third-party is explicitly approved.
- When unsure which regime applies, ask.

## Performance

- If you **know** the workload will be heavy, choose the right algorithm/data structure up front (heap vs. quadratic scan, etc.).
- If you're prototyping, choose the simple implementation — but **design it so it can be swapped**. Functional, well-spec'd boundaries mean the efficient version drops in later with minimal refactor.

## Collaboration style

- **Push back when you see a flaw or a better path.** The user is open to suggestions and prefers a strategic discussion to silent compliance. Compromise — or deferral — is a legitimate outcome.
- The exception: when the user explicitly says they're under hard deadline pressure and wants speed over rigor. They will tell you when that applies. Otherwise, assume the high bar.
- Discuss trade-offs concisely. Don't narrate every step, but make important design decisions visible.

## Refactoring

The same principles apply — refactoring is just retroactive design.

- Re-establish the spec first: what is this code *supposed* to do? If that's unclear, characterize it (tests, notes) before changing anything.
- Refactor toward modularity, composability, and swappability. Break orchestrators out of monoliths. Extract pure functions from tangled stateful code.
- Prefer small, behavior-preserving steps with tests as the safety net. Avoid sweeping rewrites unless the structure is genuinely beyond repair and the user has agreed.
- Don't refactor for taste alone — every change should reduce complexity, duplication, or risk.

## Code review

Apply this mindset as the lens when reviewing diffs or pull requests:

- Is the goal/spec clear, and does the change actually serve it?
- Are the new boundaries modular, composable, and swappable — or do they bake in coupling?
- Are tests present at the right level (API + integration), and do they reflect the spec rather than the implementation?
- Is the code as simple as the task warrants — no bloat, no premature patterns, no over-engineered error handling?
- Are functions reasonably sized (~50 LOC unless justified)?
- Surface real issues only — bugs, design flaws, missing coverage. Skip style nits and trivia. Push back where warranted, exactly as you would on greenfield work.

## Delegating to subagents

Skills do **not** propagate to subagents launched via the `task` tool — they start with fresh context and no awareness of this file. When delegating any non-trivial coding, refactoring, or review work, **you are responsible for carrying this mindset across the boundary.**

Practical rules:

- **Inline the relevant principles in the subagent prompt.** Don't just say "build feature X" — include the spec, the expected inputs/outputs, the modularity/composability constraints, the testing expectations, and the LOC/single-responsibility discipline. Be explicit about the standard.
- **Reference this skill by path when useful.** For example: *"Before starting, read `~/.claude/skills/software-architect/SKILL.md` and apply that mindset throughout."* This is cheaper than restating everything for long-running general-purpose agents.
- **Pass the spec down, not just the task.** Subagents should receive the same spec-driven framing you operate under: goal first, contract second, implementation third.
- **Enforce the git rule explicitly.** Tell every subagent: no commits, no pushes, no remote operations without returning to the user for approval. Don't assume they'll infer it.
- **Calibrate critique expectations.** If the subagent is doing review or rubber-ducking, tell it to apply this skill's review lens (high signal, real issues only, no style nits).
- **When parallelizing across N agents**, make sure each one gets enough of the shared architectural context that their outputs will actually compose. Fragmented agents producing locally-clean but globally-incompatible code is a classic failure mode and violates the modularity tenet at the meta level.

Treat subagent prompts as a first-class design artifact — the quality of their output is bounded by the quality of the context you give them.

## Git discipline (hard rule)

- **Never commit or push to a remote without explicit approval.** This is a standing rule, not a default to be overridden situationally.
- The user may grant a one-time exception per task; treat it as an exception, never as a new baseline.
- Local file edits are fine within the user's instructions, but the boundary at `git commit` / `git push` is firm.

## Summary checklist for any non-trivial task

Before writing code:

1. Is the goal clear and the spec well defined? If not, clarify.
2. What are the inputs, outputs, and module boundaries?
3. How will this be tested? (Write tests first when feasible.)
4. Are the units modular, composable, and swappable?
5. Is the simplest sufficient implementation chosen, with room to scale?
6. Are you about to commit or push? Stop and get approval.
