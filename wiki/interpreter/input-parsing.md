# Input Parsing and the `said` Test

Player input processing is a four-step pipeline: preprocessing the input line, looking up words against the game's vocabulary, filtering the resulting codes, and testing the code sequence against `said` command patterns [2-6-Interpreter.html].

## Input preprocessing

After the player types a message and presses Enter, the interpreter applies these transformations in order [2-6-Interpreter.html]:

1. Remove all punctuation marks.
2. Convert all characters to lowercase.
3. Replace any run of more than one space with a single space.
4. Starting with the first word of the input, look up the vocabulary, trying to find the longest character sequence matching the input. The vocabulary itself is stored on disk as [[entities/words-tok]] — a prefix-compressed table mapping every recognised input token to a word number.

The spec's phrasing "trying to find the longest character sequence matching the entered" is ambiguous: it could describe full-word longest-match (preferring a multi-word vocabulary entry over a shorter one), prefix matching against the remaining input, or another strategy (agidev, unverified — exact lookup algorithm not specified). ScummVM's AGI implementation uses a trie-based vocabulary; the Python prototype has no word-lookup code yet to cross-check.

If a word in the input cannot be matched, the interpreter assigns `var(9)` the position of that word (1-indexed, in the original input) and aborts preprocessing — `flag(2)` is left unset for this cycle [2-6-Interpreter.html].

## Filtering and signaling

If all input words match the vocabulary, the interpreter [2-6-Interpreter.html]:

1. Discards all codes equal to 0 from the resulting sequence — vocabulary entries with code 0 are filler/ignored words.
2. Sets `flag(2)` to 1 (input line entered and successfully parsed).
3. Sets `flag(4)` to 0 (no `said` test has consumed this input yet).

The remaining codes form a sequence `V(1), V(2), ..., V(m)` against which LOGIC scripts can test patterns via the `said` command.

## The `said` test command

`said` matches a fixed word-code pattern `W(1), W(2), ..., W(n)` against the parsed input sequence `V(1)..V(m)` [2-6-Interpreter.html].

**Precondition.** If `flag(2) = 0` (no input parsed this cycle) or `flag(4) = 1` (a previous `said` already matched in this cycle), return FALSE without examining the pattern.

**Element match.** Otherwise, compare each `W(i)` to `V(i)`:

- `W(i) = 1` matches any `V(i)` (single-word wildcard).
- `W(i) = 9999` matches the entire remaining input `V(i), V(i+1), ..., V(m)` and terminates the comparison (rest-of-input wildcard).
- Otherwise, `W(i)` must equal `V(i)` exactly.

**Result.** If every pattern element matches, set `flag(4) = 1` and return TRUE. Otherwise return FALSE.

### At-most-once-per-cycle semantics

The `flag(4)` precondition gives `said` a "first match wins" property within a single interpreter cycle. Once any `said` test in a cycle succeeds, every subsequent `said` in the same cycle short-circuits to FALSE on the `flag(4) = 1` check [2-6-Interpreter.html]. `flag(4)` is cleared again either at the start of the next cycle (per the event-loop's flag-cleanup step, see [[interpreter/event-loop]]) or whenever the next input line is parsed successfully (the filtering step above). The spec does *not* clear `flag(4)` on a *failed* `said` match — only successes claim the input.

## See also

- [[interpreter/variables-and-flags]] — `var(9)` (unparsed-word index), `flag(2)` (input parsed), `flag(4)` (`said` consumed) — full reserved-slot context.
- [[concepts/agi-data-types]] — the Word type and its relationship to parsed input.
- [[interpreter/event-loop]] — step 4 (input poll) feeds keyboard input into the preprocessing pipeline described here.
- `4-3-Logic.html` (Group 3, not yet ingested) — the original AGDS chapter from which this content was excerpted; opcode-level `said` details (bytecode parameter encoding, version-specific argument-count changes) belong there.
