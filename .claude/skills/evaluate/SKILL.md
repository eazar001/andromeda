---
name: evaluate
description: Evaluate project source code in this Andromeda repo (Python AGI emulator under `resource/`, `gfx/`, `util/`, `main.py`). Use when the user says "evaluate", "review code", "check my decoder", or asks for a critique of a specific file, module, function, or pasted snippet. Reports findings only — no fixes, no draft edits. Not for PR reviews (use `/review`) or wiki maintenance (use `wiki-*` commands).
---

# Evaluate project source

This skill owns the trigger, the boundary policy, and the orchestration policy. The evaluation criteria themselves (project style preferences, evaluation axes, severity rubric, output shape) live in `.claude/agents/reviewer.md` so the same content is reused when the work is delegated to a `reviewer` sub-agent.

## Boundary checks (do these first)

1. **Resolve target.** Accept file paths (`resource/view.py`), module names, function/class names with a module qualifier, or pasted snippets. If the request is vague (e.g., "review my recent changes" with no path), ask one clarifying question and stop until answered.
2. **Wiki guard.** If the target lives under `andromeda-wiki/`, refuse and redirect to `/wiki-lint` (full lint pass) or `/wiki-file` (single finding). Do not read the file.
3. **PR guard.** If the request is clearly a PR review (mentions a PR number, branch name, or "the PR"), defer to `/review` and stop.

## Doing the review

Read `.claude/agents/reviewer.md` to load the reviewer criteria, then apply them to the target yourself. Emit the findings block as specified in that file. Default to reviewing in-process — fan-out is the exception, not the rule.

## When to fan out

Spawn `reviewer` sub-agents only when the target is large enough that in-process review would strain the main context — multi-module sweep, whole-repo audit, or several files at once. In that case:

- Spawn one sub-agent per logical slice (e.g., `resource/`, `gfx/`, `util/`) in parallel, via a single message with multiple Agent tool calls (`subagent_type: "reviewer"`).
- Sub-agents already carry the reviewer criteria via their system prompt — no briefing block needed. Pass the slice path/scope and any target-specific context in the prompt.
- After sub-agents return, open the cited `file:line` for each `Critical` and `Major` finding to confirm it's real before emitting; drop or downgrade anything you can't substantiate; de-duplicate across slices; then emit the combined findings block in the same severity order.
