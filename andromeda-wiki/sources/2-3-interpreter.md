# Source: 2-3-Interpreter.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/2-3-Interpreter.html`. Catalog of the seven semantic data types used as parameters throughout the AGI command model.

## Scope

Enumeration and semantics of Variable (8-bit unsigned), Flag (1-bit boolean), String (40-char buffer including zero terminator), Word (token from parsed input), Inventory Item (OBJECT-table index), Object (runtime VIEW-instance index), and Message (LOGIC-resident text with a `%g<n>` cross-LOGIC format code for LOGIC 0 messages). Includes the version-by-version table for string allocation and clarifies that the OBJECT file (inventory) and the interpreter's runtime "objects" (VIEW instances) are distinct despite the shared name.

## Informs

- [[concepts/agi-data-types]] — full type catalog; central reference for command-parameter semantics.
- Cross-linked from [[interpreter/overview]] and [[interpreter/variables-and-flags]] as the broader type model.

## Notes

- No conflicts with existing pages.
- The OBJECT-file vs. runtime-object distinction is an important conceptual clarification flagged in the spec itself; preserved verbatim on the new page.
- String allocation by interpreter version is captured in a table; the spec itself flags the 24-string case as possibly unsupported (agidev, unverified).
