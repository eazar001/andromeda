# WORDS.TOK

WORDS.TOK is the game's vocabulary store — a standalone per-game file containing every input token the parser recognises, mapped to a word number that LOGIC scripts test via the `$0E said` command. Words are compressed using a prefix-share encoding and lightly obfuscated with a `0x7F`-XOR scheme on each character byte [8-2-WORDS_TOK.html].

## File location

WORDS.TOK lives in the game directory next to the VOL/DIR files. It is **not** stored inside a VOL container and **not** indexed by the directory files [8-2-WORDS_TOK.html]. See [[entities/vol-file]] and [[entities/dir-file]] for the indexed-resource contrast.

## Byte-order convention

**WORDS.TOK is the one place in AGI that does not use the system's standard Lo-Hi (little-endian) byte order.** Both the 26-entry alphabet index *and* the per-word "word number" are stored Hi-Lo (big-endian) [8-2-WORDS_TOK.html §THE FIRST SECTION; §THE WORDS SECTION]:

> *"the normal Lo-Hi byte order convention used everywhere else in the AGI system is not used here. For example, 0x00 and 0x24 means 0x0024, not 0x2400. This method is used later on for word numbers as well."* — 8-2-WORDS_TOK.html

## Layout

### Alphabet index (52 bytes at offset 0)

Twenty-six 2-byte entries, one per letter `A..Z`. Each entry is the **big-endian** file offset (from byte 0) at which the first word starting with that letter appears, or `0x0000` if no word starts with that letter [8-2-WORDS_TOK.html §THE FIRST SECTION].

| Offset | Entry |
|---|---|
| 0–1 | Hi/Lo offset to first word starting with `A` |
| 2–3 | Hi/Lo offset to first word starting with `B` |
| … | … |
| 50–51 | Hi/Lo offset to first word starting with `Z` |

### Words section (offset 52 onward)

Words are stored in alphabetic order as a stream of variable-length entries [8-2-WORDS_TOK.html §THE WORDS SECTION]:

```
Prefix (1 B) | Suffix bytes (N B) | WordNum Hi (1 B) | WordNum Lo (1 B)
```

| Field | Meaning |
|---|---|
| **Prefix** | Number of leading characters to inherit verbatim from the previously decoded word. `0` means no shared prefix — always the case at the start of a new letter. The file ends with one more `0` byte, which is not the start of an entry. |
| **Suffix bytes** | Variable-length sequence of obfuscated character bytes. Each byte `b` decodes to ASCII `b XOR 0x7F`. The high bit (`0x80`) of the *final* suffix byte is set to mark end-of-word; strip the high bit before XOR'ing [8-2-WORDS_TOK.html §THE WORDS SECTION]. |
| **WordNum Hi, Lo** | 2-byte **big-endian** word number: `word_num = (hi << 8) \| lo`. This is the value LOGIC `$0E said` patterns compare against. |

#### Decoding pseudocode

```
previous_word = ""
loop:
    prefix_len   = read u8      # stop when the file has no more entries
    current_word = previous_word[:prefix_len]
    loop:
        b = read u8
        end = (b & 0x80) != 0
        ch  = (b & 0x7F) ^ 0x7F      # always: ASCII = 0x7F XOR (b & 0x7F)
        current_word += chr(ch)
        if end: break
    hi          = read u8
    lo          = read u8
    word_number = (hi << 8) | lo     # big-endian — Hi-Lo per spec
    emit(current_word, word_number)
    previous_word = current_word
```

## Special word numbers

[8-2-WORDS_TOK.html §A NOTE ABOUT WORD NUMBERS]

| Code | Meaning |
|---|---|
| 0 | Ignored / filler word (e.g. "the", "at"). Discarded during input filtering; never appears in the sequence presented to `said`. |
| 1 | Anyword wildcard. In `said` patterns, matches any single input word. |
| 9999 | Rest-of-line. In `said` patterns, matches the remainder of the input sequence and terminates the pattern. SQ1's vocabulary has no word with this code; it exists only in patterns [SQ1 data check, log 2026-11-01]. |

See [[interpreter/input-parsing]] for how the parser consumes these special codes during filtering and `said` matching.

## How AGI 2.917 searches it

The file is loaded whole and searched in place, never decoded into a table. The lookup confirms this page's layout and byte order, and it relies on three properties of the file [AGI 2.917 1000:1A6B, 1000:1BE4]:

- **Sorted order:** the search stops at the first entry whose prefix is shorter than the characters matched so far, so entries must be sorted.
- **Stream shape:** that same rule ends the search at each letter's boundary, and the final `0` byte ends it at the end of the file. There is no other end marker.
- **Index:** an index entry of 0 means the word is unknown.

On SQ1, all 26 index entries point at a word with the right first letter, all 738 words are in sorted order, the stream ends one byte before the file's last byte, and a port of this search finds every word with its own code. The highest code is 345 [SQ1 data check, log 2026-11-01]. A vocabulary word coded `0xFFFF` would look like an unknown word, since that value signals one; SQ1 has none.

## Reference implementation

`AGI_Specifications/Code/words.pas` (Peter Kelly, indexed by [[sources/8-3-samplecode]]) is a working WORDS.TOK reader and corroborates the format. Notable lines:

- `words.pas:75-77` reads a single byte at file offset 1 as `DataStart`. This is a code shortcut that assumes the Hi byte of `A`'s alphabet-index offset is always `0x00`. Real-world WORDS.TOK files satisfy this (the words section starts well within the first 256 bytes), but a strict decoder should read both bytes Hi-Lo.
- `words.pas:86-102` — prefix-copy + XOR-decode loop. Note the Pascal expression `chr(63 + 32 - curbyte)` is arithmetically equivalent to `chr(0x7F XOR curbyte)` for `curbyte ≤ 0x7F`.
- `words.pas:104-106` — `wordblocknum := msbyte*256 + lsbyte` confirms the **big-endian** word-number byte order from the spec.

andromeda has no WORDS.TOK decoder yet. Besides `words.pas`, a throwaway decoder following this page read 738 words from SQ1's file, and all 242 word codes used by SQ1's `said` tests resolve [SQ1 data check, log 2026-11-01].

## See also

- [[interpreter/input-parsing]] — the consumer: parser-side vocabulary lookup and `said` semantics.
- [[concepts/agi-data-types]] §Word — the semantic type backed by this storage.
- [[sources/8-2-words-tok]] — chapter source.
- [[sources/8-3-samplecode]] — reference implementation (`words.pas`).
