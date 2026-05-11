# PDF Archive Manifest

> What's been fetched and what still needs your browser/institution. Filename prefix `refNN_` matches Zhu 2025 ref numbers; `sun_refNN_` matches Sun 2022 ref numbers.

## Successfully auto-fetched (5 PDFs, ~20 MB)

| File | Source | Notes |
|------|--------|-------|
| [ref13_Jiang_2017_Nature_ultrastrong.pdf](ref13_Jiang_2017_Nature_ultrastrong.pdf) | dierk-raabe.com (author-hosted) | Landmark NiAl ultrastrong steel paper, Nature 544 (2017). Pages 460-464. |
| [ref25_Hemphill_1999_US5866066_age_hardenable.pdf](ref25_Hemphill_1999_US5866066_age_hardenable.pdf) | Google Patents | Crucible Materials AerMet-family patent. Inventors: Hemphill & Wert. |
| [ref26_Jou_2015_US9051635B2_FerriumM54_patent.pdf](ref26_Jou_2015_US9051635B2_FerriumM54_patent.pdf) | Google Patents | **The foundational Ferrium M54 patent.** Sole inventor: H.-J. Jou (QuesTek). Zhu's bibliography misattributes to "X. Cao". |
| [sun_ref01_Lee_2009_Aircraft_steels_DTIC_ADA494348.pdf](sun_ref01_Lee_2009_Aircraft_steels_DTIC_ADA494348.pdf) | DTIC | US Govt-public review of aircraft steels. |
| [sun_ref25_Kuehmann_2007_US7160399_nanocarbide_patent.pdf](sun_ref25_Kuehmann_2007_US7160399_nanocarbide_patent.pdf) | Google Patents | Kuehmann & Olson QuesTek nanocarbide IP — parent technology for Ferrium family. |

## Bot-protected, need your browser (10 PDFs)

These OA papers are technically open access but the hosts (HAL, Elsevier, SSRN, KIT) all gate with Cloudflare/Anubis/WAF challenges that block `curl`. You can grab them with a browser visit:

| Ref | Source URL | Save as |
|-----|------------|---------|
| Zhu [7] **Mondière 2018 M54 carbides** | https://imt-mines-albi.hal.science/hal-01761384 | `ref07_Mondiere_2018_Ferrium_M54_carbides.pdf` |
| Zhu [8] Delagnes 2012 cementite-free | https://hal.science/hal-01687325 | `ref08_Delagnes_2012_cementite-free.pdf` |
| Zhu [28] Jacques 2009 RA round-robin | https://hal.science/hal-00413810 | `ref28_Jacques_2009_RA_roundrobin.pdf` |
| Zhu [30] Feitosa 2024 maraging 350 | https://publikationen.bibliothek.kit.edu/1000169667 | `ref30_Feitosa_2024_maraging350.pdf` |
| Zhu [1] Li 2023 UHSS review | https://doi.org/10.1016/j.jmrt.2022.12.177 | `ref01_Li_2023_UHSS_review.pdf` |
| Zhu [14] **Xiong 2021 PMS review** | https://doi.org/10.1016/j.pmatsci.2020.100764 | `ref14_Xiong_2021_clustering_review.pdf` |
| Zhu [18] Zhao 2022 phase-field | https://doi.org/10.1016/j.jmrt.2022.09.032 | `ref18_Zhao_2022_phase_field.pdf` |
| Zhu [19] Zhang 2024 NiAl HSLA | https://doi.org/10.1016/j.matdes.2024.112927 | `ref19_Zhang_2024_NiAl_HSLA.pdf` |
| Zhu [22] Borbély 2022 Williamson-Hall | https://doi.org/10.1016/j.scriptamat.2022.114768 | `ref22_Borbely_2022_WH_disloc.pdf` |
| Zhu [41] **B. Wang 2024 M54 carbides** | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4725560 | `ref41_Wang_2024_M54_multicarbide.pdf` |

**Suggested workflow for these:** open each URL in your browser, hit "Download PDF" or equivalent, save with the suggested filename, drop into `pdf-archive/`, and we'll commit them on a follow-up pass.

## Still TODO / parked

- **Zhu [3] Xu/Qian 2025 rail bright bands** — SSRN preprint id 4956737. Cloudflare-blocked. Low priority anyway.
- **Sun [11] Cho 2015** (Metall. Mater. Trans. A 46, 1535) — *ausformed Co-Ni precipitation kinetics* — paywalled at Springer. **High priority** for the model; likely user-institutional.
- **Sun [21] Galindo-Nava 2015** (Acta Mater. 98, 81) — *lath martensite model* — paywalled at Elsevier. High priority.
- **Sun [20] Krauss 1999** (MSEA, "Martensite in steel") — paywalled. Foundational equation reference.
- **Sun [7] Lee Tech Memo 2015** (Patuxent River) — Navy tech memo, source of K_IC = 126 MPa·m^½ for M54. May be on DTIC under a different ADA number.

## Tally

- 5 of ~15 target OA refs fetched cleanly via `curl`.
- 10 OA refs reachable via browser; bot-protected against curl.
- 4+ high-priority paywalled refs flagged for institutional access.

The win rate for direct curl fetches is roughly: **patents (3/3), DTIC (1/1), author personal sites (1/1), aggregator OA repos (0/4)**, **publisher hybrid OA (0/5)**, **preprint servers (0/2)**. Aggregator-and-publisher hosts have all rolled out Cloudflare/Anubis challenges in the last year+.
