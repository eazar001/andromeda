# Command Argument-Count Evolution

The AGI command set grew across interpreter versions, and four commands changed how many arguments they accept between specific releases. A LOGIC bytecode decoder must branch on the target interpreter version when decoding these four commands; all other commands have stable argument counts across versions [2-8-Interpreter.html §COMMAND ARGUMENT NUMBER DESCREPENCIES]. The opcode catalogue at [[interpreter/commands]] carries inline version notes on the same four commands sourced independently from [4-3-Logic.html §Action commands].

## Commands with version-conditional argument counts

| Command | Argument count | Versions |
|---|---|---|
| `quit` | 0 | 2.089 only |
| `quit` | 1 | All versions ≥ 2.272 |
| `print.at` | 3 | 2.089 through "2.400" (spec text; see conflict below) |
| `print.at` | 4 | Later versions |
| `print.at.v` | 3 | Same boundary as `print.at` |
| `print.at.v` | 4 | Later versions |
| Unknown #176 | 1 | 3.002.086 only |
| Unknown #176 | 0 | All later v3 versions ≥ 3.002.098 |

> [!conflict]
> **The `print.at` / `print.at.v` boundary version is ambiguous in the spec.** Both [2-8-Interpreter.html] and [4-3-Logic.html §Action commands] carry the same string "2.400" — 2-8 in prose ("for versions 2.089 - 2.400 and four for the other versions"), 4-3 in inline note cells on opcodes `$97 print.at` and `$98 print.at.v`. `2.400` is not a real AGI interpreter version — it appears in neither [[sources/2-7-interpreter]]'s game-cross-reference enumeration nor 2-8's own version table. Two same-era chapters carrying the identical erroneous string strengthens the typo reading rather than the real-version reading. Plausible corrections:
>
> - `2.440` (a real version; the last "early v2" before the 2.915 command-count jump) — most likely typo source.
> - `2.272` (the next real version after 2.089) — if the boundary is right at the first command-count growth.
> - `2.411` (the version where 8 new commands were added, going from 161 to 169) — if the change rode in with the bigger expansion.
>
> Conclusive resolution requires ScummVM source or AGI Studio cross-check. Provisional reading: 2.440 is the typo target (agidev, unverified).

## Total command count by interpreter version

Each row of 2-8's version table fingerprints the opcode-index range that interpreter accepts [2-8-Interpreter.html, version table]:

| Interpreter version(s) | Commands |
|---|---|
| 2.089 | 155 |
| 2.272 | 161 |
| 2.411, 2.435, 2.439, 2.440 | 169 |
| 2.915, 2.917 | 173 |
| 2.936 | 175 |
| 3.002.086 | 177 |
| 3.002.098, 3.002.102, 3.002.107, 3.002.149 | 181 |

A decoder encountering a command index greater than the target interpreter version's documented count is reading invalid bytecode (or attempting to interpret newer game data on an older interpreter — see [[sources/2-5-interpreter]] for the `set.game.id` mechanism that the original interpreter uses to prevent this).

## Unknown commands

The spec states: "the last eleven we do not know the names of" [2-8-Interpreter.html]. For the final v3 release (3.002.149, 181 commands), this means roughly the last eleven opcode indices have no documented names or semantics in the AGI Specifications corpus. Unknown command #176 (with its version-conditional argument count, above) is one of these eleven. Group 3 (Logic) will need to cross-check ScummVM and AGI Studio to recover the unknown commands' identities.

## See also

- [[sources/2-8-interpreter]] — source chapter; also documents OBJECT-encryption timeline, LZW adoption boundary, PICTURE-opcode v2/v3 color-encoding difference, and the v2-LOGIC-text-encryption inference.
- [[sources/2-7-interpreter]] — empirical enumeration of interpreter versions shipped in commercial AGI games.
- [[interpreter/commands]] — full opcode catalogue (test commands `$01..$12`, action commands `$00..$B5`) with per-argument types, sourced from [4-3-Logic.html].
- [[sources/4-3-logic]] — source chapter for the opcode catalogue; corroborates the four version-conditional mutations documented here and replicates the same "2.400" typo.
