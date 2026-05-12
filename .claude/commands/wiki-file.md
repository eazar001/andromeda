File the finding from our conversation into the andromeda-wiki.

A fact, correction, or insight was established in this session — from code inspection, spec cross-check, or decoder work. File it so future sessions find it rather than re-deriving it.

## Steps

1. **Identify the finding.** State it in one sentence. If `$ARGUMENTS` was provided, use it as the summary; otherwise derive it from the conversation context.

2. **Locate the right page.** Read `andromeda-wiki/index.md`. Find the entity, concept, or interpreter page the finding belongs under. If no page fits, propose a new one (path + one-paragraph body). Confirm it doesn't contradict anything already on the target page — if it does, flag the conflict before writing.

3. **Propose the edit.** Show the exact change: which file, which section, what text to add or revise. Don't write yet — confirm with the user first.

4. **Apply.** Write the edit. If a new page was created, add its one-line entry to `andromeda-wiki/index.md` under the correct category.

5. **Log it.**
```
## [YYYY-MM-DD] file | <topic>

<One paragraph: what the finding is, where it was filed, and any conflict it resolved or surfaced.>
```
