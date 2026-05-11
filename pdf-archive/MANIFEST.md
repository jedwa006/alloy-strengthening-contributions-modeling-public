# PDF Archive Manifest

> All PDFs we have locally for the M54 strengthening-contribution model. Filename convention: `<citekey>_<topic>.pdf` matching keys in [`../references/references.bib`](../references/references.bib).

## Status — 65 PDFs locally available (full coverage)

| Source | Count | How obtained |
|--------|------:|--------------|
| Auto-fetched (curl: patents, DTIC, author site) | 5 | Initial OA pull |
| Wayback machine recovery | 1 | Delagnes 2012 (HAL was bot-blocked live) |
| **Zotero pull #1 (your fetch via institutional access)** | **57** | The big batch |
| User-supplied direct (zhu44 Wen 2024) | 1 | Filed from Downloads |
| **Zotero pull #2 (zhu11 Wang 2024)** | **1** | Re-export caught the missing one |
| **Total** | **65** in `pdf-archive/` | |
| (Plus 8 in `reference docs/`) | 8 | User-supplied source PDFs (Zhu main, Sun 2022, Patel-Cohen, Olson-Cohen, 5 cited-by) |
| **Grand total** | **73 PDFs** locally | |

## Coverage: 73 / 73 papers in references.bib are now local. ✓

No outstanding `NEEDED:` flags remain in `references/references.bib`.

## File-size note

`pdf-archive/` is now ~380 MB. Repo total is ~450 MB including `reference docs/`. This is fine for git but on the edge of where Git LFS becomes attractive — especially if/when this repo gets pushed to a remote (GitHub free-tier soft caps repos at ~1 GB and warns above ~100 MB single-file). We can migrate the `pdf-archive/` and `reference docs/` paths to LFS later with one command if needed; the `.gitattributes` already marks PDFs as binary so the conversion will be clean.

## Index by citekey (in `references/references.bib`)

The .bib file's `file = {...}` field on each entry points to the local PDF. To open any reference's PDF directly from the .bib, use a tool like Zotero, JabRef, or BibDesk — or just grep:

```bash
grep -A1 "@article{zhu07" references/references.bib | grep "file ="
# -> file = {pdf-archive/zhu07_Mondiere_2018_Ferrium_M54_carbides.pdf}
```
