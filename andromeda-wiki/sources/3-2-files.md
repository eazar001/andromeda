# Source: 3-2-Files.html

Peter Kelly's AGI Specifications, vendored at `AGI_Specifications/Specifications/3-2-Files.html`. Specifies the VOL (volume) file container format.

## Scope

VOL container format only: the uniform 5-byte resource header (signature, VOL number, length) that precedes every resource in a VOL file. Resource-internal formats (LOGIC bytecode, PICTURE/VIEW imagery, SOUND data) are specified in later chapters.

## Informs

- [[entities/vol-file]] — VOL file structure and resource header layout

## Notes

- Corroborated by working code in [resource/header.py:ResourceHeader.parse] and [resource/volume.py:VolumeReader.read_resource], which decode real game resources successfully.
- No conflicts observed against code in `resource/`.
