# Source: 9-2AGDS.html

**Chapter:** §9.2 AGDS
**Path:** `AGI_Specifications/Specifications/9-2AGDS.html`
**Authors:** Alex Simkin (AGDS primary), Serge Lapin (AGDS co-author); Vassili Bykov (English translator); Konstantin Mironovich (introducer)
**Last updated:** 27 January 1998
**Provenance:** Retrieved from the Internet Archive

## What AGDS is

The **Adventure Game Development System (AGDS)** is a parallel Russian-language AGI toolkit developed circa 1990–91 by Alex Simkin and Serge Lapin. Originally motivated by Leisure Suit Larry 1 translation work, it grew into a full reverse-engineered LOGIC editor and documentation set. Its manual — the *AGDS docs* — became the single most substantial source of Sierra-internal interpreter knowledge in the corpus, sitting alongside Lance Ewing's English-original reverse engineering.

Vassili Bykov translated the AGDS manual into English and contributed the translations to Peter Kelly's specification corpus.

## Why this chapter matters to the wiki

This is the **provenance anchor for three previously-ingested wiki sources** that all derive from the Bykov-translated AGDS manual:

- [[sources/2-6-interpreter]] — input preprocessing and `said` semantics (AGDS §4.3)
- [[sources/4-4-logic]] — full LOGIC command-set prose (AGDS §I.2.6)
- [[sources/5-2-picture]] — PICTURE format from the AGDS perspective

These three chapters were already correctly attributed in their respective source pages; what 9-2 adds is the *history* of where AGDS came from and who built it.

## Scope of new content

Historical narrative only. No byte-level format claims, no entity descriptions, no opcode additions.

## Informs

Back-references added to:

- [[sources/2-6-interpreter]] — Notes section references 9-2 for AGDS toolkit history.
- [[sources/4-4-logic]] — Notes section "Same AGDS source as 2-6" extended with 9-2 cross-link.
- [[sources/5-2-picture]] — Notes section "Fourth Bykov/AGDS chapter in the corpus" extended with 9-2 cross-link.

No new entity, concept, or interpreter pages.

## Notes

- AGDS was a self-contained DOS toolkit: LOGIC editor (`SE`), VIEW editor (`VIM`), PICTURE editor (`PM`), debugger (`DUU`), and a packing tool (`VM`). The reference impls cited elsewhere in the wiki (`oldplay.c`, `viewview.pas`, `object.pas`, `words.pas`) are independent contributions, not parts of AGDS.
- AGDS's interpreter ID is `TQ` (cited on [[interpreter/command-semantics]] under `set.game.id`); the Russian-language manual described AGI's command set primarily through worked examples of that custom-ID interpreter.
- 9-2 references "section 9.1" (`9-1-Info.html`) as the source for AGDS download links. See [[sources/9-1-info]].
- The chapter quotes correspondence with Alex Simkin and an introduction by Konstantin Mironovich, providing the only first-hand account of AGDS's origins. None of this surfaces format claims, but it is the canonical citation for "where the AGDS docs came from" if a future reader asks.
- **Fourth time** the wiki has touched AGDS material (after 2-6, 4-4, 5-2); this is the only chapter that documents the *toolkit* rather than reproducing AGDS-manual content.
