# AGI 2.917 analysis scripts

Headless Ghidra scripts for auditing `andromeda-wiki/` against the SQ1 interpreter. Findings go in the wiki; see `WIKI_AUDIT_PLAN.md`. REA refuses this DOS MZ target on Windows, so these use Ghidra directly.

The scripts and seed lists hold no game data. The Ghidra project does, because it contains the decoded interpreter, so it stays outside the repo in `C:\Users\ebrah\tools\andromeda-re\ghidra_project`. Never commit it, or `AGI.decoded` and other game files.

## Running a script

From the repo root in PowerShell:

    $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-21.0.13.9-hotspot"
    $env:Path = "$env:JAVA_HOME\bin;$env:Path"
    $r = "C:\Users\ebrah\tools\andromeda-re"
    & "C:\Users\ebrah\tools\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat" "$r\ghidra_project" AGI -process AGI.decoded -noanalysis -scriptPath "$PWD\tools\ghidra\scripts" -postScript AgiRange.java "$r\out.txt" 1000:0D70-1000:0DB0 -log "$r\x.log" -scriptlog "$r\xs.log"

Then read `out.txt`. Allow up to 5 minutes per run. Add `-readOnly` for scripts that don't change the project. Addresses are `1000:xxxx` for code; data is `DS:xxxx`, from `AGIDATA.OVL` loaded at segment `19F5`.

## Scripts

| Script | Arguments | Use | `-readOnly` |
|---|---|---|---|
| `AgiDump.java` | report, address... | Listing and decompilation of the function containing each address. Reports "no function" if none was recovered | Yes |
| `AgiRange.java` | report, start-end... | Listing of explicit ranges, for code outside a recovered function | No, it disassembles |
| `AgiGrep.java` | report, token... | Instructions whose text contains a token, such as `0xc9b`, to find who uses an address | Yes |
| `AgiCalls.java` | report | Every indirect call or jump | Yes |
| `AgiSeed.java` | seed file, `AGIDATA.OVL` | Loads the overlay, then disassembles and names table-reached handlers | No |
| `AgiSurvey.java` | none | Blocks, coverage, functions, errors, strings | Yes |
| `AgiEntry.java` | none | Linear instructions from the entry point, and functions by address | Yes |

`seeds/` holds the address and name lists for `AgiSeed.java`, in the form `1000:0823 test_equaln`. They were applied in order, and the project already includes them. They're kept so the project can be rebuilt.

## Handler addresses

The action table is at `AGIDATA.OVL` offset `0x61D` and the test table at `0x8F5`. Each has 4-byte entries: handler (little-endian word), argument count, type byte. Handlers are already named `action_*`, `test_*` and `core_*` in the project.

## Things to watch

- Ghidra locks a project while it's open, so give each concurrent run its own project; whether `-readOnly` runs can share one is untested. For parallel agents, copy `ghidra_project` per agent and prefix its output files.
- Ghidra prints moves into segment registers with the operands swapped. Trust the raw bytes for those.
- Some handlers use assembly-only register conventions, so prefer the listing to the decompilation.
- `AgiGrep` can miss direct memory moves, so a negative result is unproven. Confirm "only writer" claims with a raw byte scan of `AGI.decoded`, where the file offset is `1000:xxxx` + `0x200`.
- `AgiRange` stops with an "uninitialized block" error at the image's end, `1000:9800`, and loses any later ranges. Addresses after `1000:972A` print as `1964:xxxx`. One run also stopped early at a range starting at `1000:9740`, for a reason not found.
- The display and object overlays aren't in the project. Disassemble them separately as 16-bit code at their load base, `1000:9740` for `*_GRAF.OVL` and `1000:9CF0` for `*_OBJS.OVL`. Capstone works for this.
- Running `AgiRange` over the whole image forces disassembly across data regions, so don't use a project copy that has had this as a clean base.
