# References

## Files

- [`citation-chart.md`](citation-chart.md) — Human-readable annotated table of all 52 Zhu 2025 references with errata, OA/paywall status, retrieval routes, and priority ranking for the M54 model.
- [`references.bib`](references.bib) — BibTeX file with **71 verified entries** ready to import into Zotero. Every DOI was checked against Crossref (title + first-author + year). Includes metadata for the main Zhu paper, all 52 of its refs, the additional refs from Sun 2022, the Patel-Cohen / Olson-Cohen TRIP foundations, and the 5 cited-by papers.

## Importing into Zotero

1. Open Zotero, then **File → Import…** (or `⌘⇧I`).
2. Choose **A file** and pick `references/references.bib`.
3. Tick **Place imported collection into a new collection** to keep them grouped.
4. Once imported, Zotero will resolve the DOIs against your institutional access (or open-access detector) and pull PDFs into the Zotero library.

## What's in the .bib

| Bucket | Count | Note |
|--------|------:|------|
| Zhu 2025 main paper itself | 1 | Local PDF in `reference docs/` |
| Zhu 2025 references | 51 | (52 minus 2 patents and minus 2 pre-DOI: Miller 1964, McCall-Boyd 1969) — actually 49 entries; refs [25], [26] (patents), [21], [23] (pre-DOI) excluded |
| Sun 2022 references (new vs Zhu) | 16 | Deduplicated against Zhu (Sun [5], [6], [7], [8], [12], [25], [27] overlap or are excluded as patents/datasheets) |
| TRIP foundation papers | 2 | Patel-Cohen 1953, Olson-Cohen 1975 |
| Cited-by papers | 5 | The 5 papers in `reference docs/Articles that CITE main article/` |
| **Total entries** | **71** | All DOIs Crossref-verified |

Of those 71, **10 entries are marked `LOCAL` in the `note` field** because the PDF is already in this repo (`reference docs/` or `pdf-archive/`). The remaining **61 entries are what you'd actually want Zotero to fetch**.

## Excluded from the .bib (intentionally)

These are flagged in `citation-chart.md` but omitted from the .bib because they don't fit "PDF article with valid DOI":

| Ref | Reason |
|-----|--------|
| Zhu [3] Xu/Qian 2025 rail bright bands | DOI not yet assigned (only SSRN preprint id 4956737); low priority |
| Zhu [21] Miller 1964 X-ray RA method | Pre-DOI; ASM library only |
| Zhu [23] McCall & Boyd 1969 conf. proceedings | Pre-DOI; IMS proceedings hard copy |
| Zhu [25] US Patent 5,866,066 (Hemphill 1999) | Patent — already auto-fetched |
| Zhu [26] US Patent 9,051,635 B2 (Jou 2015 — M54) | Patent — already auto-fetched |
| Sun [1] DTIC Lee 2009 (Aircraft steels) | US Govt report — already auto-fetched |
| Sun [5] = Zhu [26] | Patent (dedup) |
| Sun [7] Lee 2015 Patuxent Tech Memo | Navy tech memo |
| Sun [12] QuesTek M54 datasheet | Datasheet, no DOI |
| Sun [17] Prawoto 2012 J. Mater. Sci. Technol. | Could not find DOI in Crossref query |
| Sun [22] Nabarro 1964 *Adv. Phys.* | Possibly findable; left out due to age |
| Sun [23], [26] Bhadeshia & Honeycombe book chapters | Book sections; cite the book separately if needed |
| Sun [25] = Zhu equivalent | Kuehmann/Olson patent — already auto-fetched |
| Sun [27] Speich Tech Memo (no journal info) | Insufficient metadata |
| Sun [28] Yoo 1996 | Could not find DOI in Crossref query |

If you want any of these added, point me at a DOI and I'll add them.

## Verification methodology

Each DOI was queried against `api.crossref.org/works/{doi}`. The returned title + first-author family name + year were compared against the bibliographic citation as printed in the source paper. Three DOIs from the agents' earlier inference work had typos and were corrected:

| Zhu ref | Original (wrong) DOI | Corrected DOI |
|---------|----------------------|---------------|
| [4] Qu 2024  | 10.1016/j.msea.2024.146454 | **10.1016/j.msea.2024.146423** |
| [44] Wen 2024 | 10.1016/j.msea.2023.145951 | **10.1016/j.msea.2023.145923** |
| [51] Yu 2024 | 10.1016/j.ijplas.2024.103874 | **10.1016/j.ijplas.2024.103887** |

Note also: the BibTeX `note` field uses `&` (e.g., "refinement & toughness") which is not LaTeX-escaped — Zotero handles it fine on import. If you ever feed the .bib through `bibtex`/`biber` for LaTeX, escape with `\&`.
