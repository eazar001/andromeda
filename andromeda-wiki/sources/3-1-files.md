# Source: 3-1-Files.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/3-1-Files.html`. Specifies the file-system layer for VOL/DIR addressing in AGI v2 and v3.

## Scope

File-system layer only: directory file formats, the 3-byte offset-encoding scheme, VOL numbering, and the resource-nonexistence sentinel. Resource-internal formats (LOGIC bytecode, PICTURE/VIEW imagery, SOUND data) are specified in later chapters.

## Informs

- [[entities/dir-file]] — complete directory file structure for AGI v2 and v3
- [[concepts/offset-encoding]] — the 3-byte VOL+offset encoding used in every directory entry

## Notes

- Corroborated by working code in [resource/directory.py], which decodes real game directory files successfully.
- No conflicts observed against code in `resource/`.
