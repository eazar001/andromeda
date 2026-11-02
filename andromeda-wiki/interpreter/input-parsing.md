# Input Parsing and the `said` Test

A typed line becomes a list of word codes, which LOGIC scripts test with `said`. This page gives the procedure read from AGI 2.917, then lists where the spec [2-6-Interpreter.html; 4-4-Logic.html §TEST COMMANDS] differs. Other versions are unchecked.

A line reaches the parser when the player presses Enter on a non-empty input line, or when a script runs `parse(string)` [AGI 2.917 1000:3652, 1000:1958]. `parse` first clears `flag(2)` and `flag(4)`, and ignores strings numbered 12 and up, leaving those flags clear.

## Preprocessing

The line is copied to a working buffer as follows [AGI 2.917 1000:199D, DS:0C5F, DS:0C6D]:

1. **Separators:** the characters ``space , . ? ! ( ) ; : [ ] { }`` end a word. Any run of them becomes one space, and leading and trailing ones are dropped.
2. **Deleted characters:** ``' ` - "`` are removed without ending the word, so "don't" becomes "dont".

Everything else is kept. Case is left alone here and folded during lookup.

## Vocabulary lookup

Words are looked up from the start of the buffer, one at a time [AGI 2.917 1000:1A6B]:

1. **Bad first character:** a word that doesn't start with a letter is unknown.
2. **Longest match:** entries under the word's first letter in [[entities/words-tok]] are compared in order. An entry counts as a match only if the input ends or has a space right after it. Longer matches replace shorter ones, and the search stops when the input runs out or the entries no longer share the matched prefix.
3. **Multi-word entries:** entries can contain spaces, so a match can span several input words. SQ1 has entries such as "access tube" and "cartridge retrieval unit" [SQ1 data check, log 2026-11-01].
4. **"a" and "i":** a single-letter word "a" or "i" starts out as filler (code 0) even without a vocabulary entry. A matching entry overrides this. SQ1 lists both with code 0.

## Building the word list

The parser clears the list, then repeats lookups until the buffer ends or 10 words are stored [AGI 2.917 1000:18AC]:

- **Unknown word:** the word count becomes the words stored so far plus 1, `var(9)` gets the same number, and parsing stops with `flag(2)` set. The slot for the unknown word holds code 0, and the word's text is kept for display.
- **Code 0:** the word is dropped.
- **Any other code:** the code and a pointer to the word's text are stored.

After a normal finish, `flag(2)` is set if at least one word was stored. A line of only filler or punctuation leaves `flag(2)` clear, and the old word count stays in memory, which is harmless because `said` checks the flag first. Words past the tenth are ignored without error.

Scripts can display the stored text through message `%w` codes; that formatting is unread.

## The `said` test

`said(n, W1..Wn)` is evaluated as follows [AGI 2.917 1000:095C]:

**Precondition.** The test fails if `flag(4)` is set, `flag(2)` is clear, or the word count is 0. The bytes of the pattern are still skipped.

**Matching.** Pattern codes are read in order against the word list:

- **`9999`:** matches the rest of the input, including nothing, and the test succeeds.
- **No input left:** any other code fails the test.
- **`1`:** matches any one word, including the slot of an unknown word.
- **Any other code:** must equal the word's code.

**Result.** The test succeeds only if the pattern and the input run out together, or a `9999` was reached. Success sets `flag(4)`. Failure leaves it alone.

An empty pattern is an edge case. It succeeds only when the word count is 0, regardless of the flags, and it then sets `flag(4)`. A valid game shouldn't rely on this.

### How games use this

Since `flag(2)` is set even for an unknown word, a script can catch input nothing matched by testing `flag(2)` set and `flag(4)` clear after its `said` tests, then print `var(9)`'s word. A `said` with a real code never matches the unknown word's slot, but `1` and `9999` can: with "look xyzzy", both `said(look, 1)` and `said(look, 9999)` succeed.

Because conditions short-circuit, a `said` skipped by an earlier false test doesn't run and can't set `flag(4)`. See [[entities/logic]] §"Condition evaluation".

## Where the spec differs

> [!conflict] Spec input pipeline vs. AGI 2.917
> [2-6-Interpreter.html] and the matching text in [4-4-Logic.html §TEST COMMANDS] differ from the binary as follows.
>
> - **Contradicted:** the spec says an unknown word leaves `flag(2)` unset. 2.917 sets it.
> - **Contradicted:** the spec gives `var(9)` as the word's position in the original input. 2.917 counts only kept words, so filler words before the unknown word don't count.
> - **Contradicted:** the spec has every successful parse clear `flag(4)`. The parser doesn't touch it. The `parse` command and the start of each cycle clear it, and Enter is handled after that cycle's clear.
> - **Refined:** "remove all punctuation" hides two behaviors. Some characters separate words and others are deleted, and characters outside both sets stay in the word and make it unknown if they don't match.
> - **Refined:** the spec's "longest character sequence" is confirmed, and it does span spaces.
> - **New:** the limit of 10 words, and the built-in filler handling of "a" and "i".

## See also

- [[entities/words-tok]] — the on-disk vocabulary
- [[entities/logic]] — bytecode encoding of `said` and condition evaluation
- [[interpreter/event-loop]] — how keys reach the input line, and the `flag(2)`, `flag(4)` and `var(9)` clears
- [[interpreter/variables-and-flags]] — `var(9)`, `flag(2)`, `flag(4)`
- [[interpreter/commands]] — `$0E said` and `$75 parse` entries
- [[sources/2-6-interpreter]] — the spec chapter this page checks
