# Source: 4-2-Logic.html

**Chapter:** 4.2 LOGIC Syntax
**Path:** `AGI_Specifications/Specifications/4-2-Logic.html`
**Author:** Peter Kelly (`ptrkelly@ozemail.com.au`)
**Last updated:** 27 January 1998
**Provenance:** "Retrived from the Internet Archive" (sic, in HTML)

## Scope

Source-language syntax for AGI LOGIC scripts — the high-level language that AGI Studio's compiler reads and decoders display, distinct from the bytecode encoding documented in [[entities/logic]]. The chapter covers:

- **Action commands** — function-call syntax `cmd(arg, arg, ...);` (semicolon-terminated).
- **`if` / `else` structures and test commands** — `if (condition) { ... } else { ... }`; relational operators (`==`, `>`, `<`, `!=`, `<=`, `>=`); `&&` (AND), `||` (OR), `!` (NOT); the `said` test command takes 1+ vocabulary-word arguments (16-bit numbers from WORDS.TOK or quoted strings). Quote marks around messages and `said` words are mandatory.
- **Argument types** — nine source-syntax argument types with one-letter prefixes: Number (no prefix), Var (`v`), Flag (`f`), Message (`m`), Object (`o`), Inventory Item (`i`), String (`s`), Word (`w`), Controller (`c`). Numbers 0–255 follow the prefix. The `said` command uses its own 16-bit-vocabulary-code parameters distinct from the rest.
- **Labels and `goto`** — `Label1:` then `goto(Label1);`.
- **Comments** — `//`, `[`, and `/* */` (the spec calls out `[` as a third comment marker).
- **Preprocessor-style directives** — `#define name value` for compile-time aliases; `#include "file"` for inclusion; `#message N "text"` to declare message-table entries by index. (4-2 only sketches these; full semantics are compiler-specific.)
- **`return`** — terminates the LOGIC; required at the end of every script.

## Informs

- [[concepts/agi-data-types]] — Controller (`c` prefix) added as the 8th data-type section. 2-3 enumerated 7 runtime types (Variable, Flag, String, Word, Inventory Item, Object, Message); 4-2's enumeration adds Controller as a real new runtime type and Number as a source-syntax category for immediate literals (not a runtime type and therefore not given its own section).

No new entity, interpreter-subsystem, or other concept pages — 4-2 is a source-syntax reference, not a byte-level format spec. Source-syntax conventions (prefix-typing discipline, quote rules, comment markers, preprocessor directives) are authoring concerns and stay in this source page rather than fanning out into wiki pages.

Deferred to later Group 3 chapters:

- The full opcode catalogue (command names, semantics, argument signatures per version) — 4-2 explicitly says "A complete list of the commands and their argument types is available as part of AGI Specs" without identifying which chapter contains it. The forward-reference to [[interpreter/commands]] from [[interpreter/overview]] remains dangling.
- Controller opcode semantics — `set.controller`, `set.menu`, `submit.menu`, etc. — runtime behavior is not in 4-2.

## Notes

**Scope boundary.** The wiki is byte-level format only (per the plan's "Out of scope" section). Source-language syntax is an authoring concern that sits above the bytecode layer documented in [[entities/logic]]. 4-2 generates no entity / concept / interpreter pages beyond the Controller-type delta because everything else in it is compiler-specific authoring convention, not on-disk format.

**Quote-mark contracts.** 4-2 explicitly requires quote marks around messages, inventory-item names, and `said` words because identifiers can contain brackets and commas that would otherwise confuse parsing — e.g., `if (has("Buckazoid(s)"))`. Escape rules: `\"` for embedded quote, `\\` for backslash, `\n` for newline. These are compiler rules; the bytecode contains only resolved indices.

**Said-word lookup.** Source authors can write `said("look", "tree")` and the compiler resolves quoted words against WORDS.TOK to their group numbers; the bytecode stores only the 16-bit group numbers. This is the source-syntax counterpart of the bytecode-level `said` encoding documented in [[entities/logic]] §"The `said` test command".

**Said synonym-group syntax.** A `||`-separated group within a single `said` argument denotes alternative spellings of the same concept (e.g., `said(OPEN, DOOR||DOORS||DOORWAY||DOORWAYS)`). All alternatives share one WORDS.TOK vocabulary word code, so the bytecode reduces to a single 2-byte code per argument position — the `||` is pure source sugar. This convention is not described in 4-2 itself; it is documented here based on real-game GAME-form samples observed in [[sources/4-5-logic]] (KQ4 Room 7 disassembly).

**Number-vs-Controller delta rationale.** Of 4-2's nine argument types, only Controller is genuinely new as a runtime data type. Number (no prefix) is the absence of a type marker — every type-prefixed argument can also appear as a literal byte, so Number is an addressing mode (immediate vs. indirect), not a peer runtime type. The 7 → 8 expansion in [[concepts/agi-data-types]] reflects that.

**Authorship.** Peter Kelly, the first directly-verified Peter-Kelly-authored chapter in our corpus (2-1 / 2-2 / 2-3 were assumed-Peter-Kelly without HTML verification in their ingests; 2-5 lists him as a contributor; 4-2 explicitly credits him by name + email). Internet-Archive provenance matches the broader corpus pattern.
