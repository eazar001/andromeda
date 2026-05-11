# Source: 2-5-Interpreter.html

Lance Ewing's chapter on AGI interpreter binary distribution and copy protection, with additions/modifications by Peter Kelly and Anders M Olsson, vendored at `AGI_Specifications/Specifications/2-5-Interpreter.html`. Bibliographic for this wiki's scope — no entity or concept pages derive from it.

## Scope

Distribution-layer mechanics for the AGI interpreter executable, not the game-data resources the wiki catalogs:

- **Game IDs.** Each shipped interpreter binary embeds a game-ID string used at runtime to verify that loaded game data matches the interpreter version. The `set.game.id` LOGIC command in game data triggers the check; a mismatch causes the interpreter to quit immediately.
- **Game-ID byte format.** Null-terminated 2–5-character string followed by filler bytes that complete the literal `"eIDX"` (or a tail of it: `"IDX"`, `"DX"`, `"X"`). Example bytes: `"PQ\0eIDX"` (Police Quest), `"MG\0eIDX"` (Mother Goose), `"MH2\0IDX"` (Manhunter 2), `"XMAS\0DX"` (XMAS Demo), `"LLLLL\0X"` (Leisure Suit Larry). The filler is not semantically meaningful — it's a search anchor for finding the ID in a binary.
- **Loaders.** The AGI interpreter executable ships encrypted on the original distribution disk; a loader program (`SIERRA.COM`, `LOAD` in v1, or a game-named `*.COM`) decrypts it into memory and runs it. Unencrypted interpreters have an `MZ` EXE-header signature; encrypted ones don't. A game with no loader is not encrypted; a game with a loader may or may not be encrypted.
- **128-byte rolling-XOR encryption.** Applied to the interpreter binary, not to game data. The loader holds a 128-byte key. For each 128-byte block of the binary: (1) XOR with the key; (2) rotate the whole key right by one bit with carry feedback — bit 0 of the last byte → carry, then carry → bit 7 of the first byte (OR-combined, not assignment); (3) advance to the next block [2-5-Interpreter.html §HOW DOES THE ENCRYPTION WORK?]. The key was originally read from track 6 of the floppy disk — a copy-protected sector with a format the standard PC floppy controller could not reproduce. Copy-protection-removed releases and the CD re-releases embed the key inline in the loader. A loader containing 128 `'k'` bytes for the key means either the binary is unencrypted or the game is still copy-protected (key fetched at runtime). The decryption-key region in the loader is followed immediately by the stack (typically 256 bytes of `'s'` bytes); the key region is preceded by the literal string `"keyOfs"` followed by 2 bytes giving the track-6 offset.
- **Bypassing the game-ID check.** Two methods. (1) Patch the interpreter's embedded ID to match the game data; binds the interpreter to one game. (2) Remove the `set.game.id` call from the game's initialization LOGIC (typically logic 90–100 referenced from LOGIC 0); savegame filenames lose the game-ID prefix as a side effect (e.g., `SG.1` instead of `KQ2SG.1`).

## Informs

No wiki entity or concept pages. Forward breadcrumbs for later ingests:

- **Group 3 (Logic)** opcode tables should cross-reference this page when documenting `set.game.id` semantics.
- The chapter notes that "about four AGI commands have changed the number of arguments passed to them as the interpreter developed" without enumerating them [2-5-Interpreter.html §POSSIBILITIES]. Group 3 will need to surface these per-version argument-count differences when building the opcode tables.

## Notes

- Authored by Lance Ewing primarily, with additions/modifications by Peter Kelly and Anders M Olsson per the chapter header; last updated 3 March 1998. (Compare 2-4, solo Lance Ewing.) Per-chapter authorship continues to vary across the corpus — check the HTML header rather than assuming Peter Kelly.
- **Out-of-scope for this wiki's mission.** The encryption described here protects the AGI interpreter binary on the original distribution disk, not the game-data resources (VOL/DIR/VIEW/LOGIC/PIC/SND/OBJECT/WORDS.TOK) the wiki documents. Andromeda reimplements the AGI interpreter rather than running Sierra's original binary, so loader decryption is not on the implementation path. This source page is preserved as a reference in case future work needs to identify or extract data from a sealed original distribution.
- The XOR-rotate encryption algorithm is fully specified in the Scope section above; if a concrete use case emerges, it can be promoted to a `concepts/` page then. Creating one now would orphan with no inbound links from any entity or interpreter page.
- The `"Avis Durgan"` encryption key documented under [[interpreter/memory-layout]] is unrelated to the loader-binary encryption described here. They are different keys for different purposes: `"Avis Durgan"` is XOR'd against OBJECT-file contents at game load time inside the interpreter; the 128-byte loader key is XOR'd against the interpreter binary itself before the interpreter ever runs.
- No conflicts observed against existing pages.
