# Revision Notes

## Files in this submission

| File | Description |
|------|-------------|
| `paper_technology_in_society_anonymous_revised.tex` | Main manuscript (blind review) |
| `cover_letter_technology_in_society_revised.tex` | Cover letter |
| `declarations_and_author_biography.tex` | Declarations and author biography |
| `revision_notes.md` | This file |

## Summary of changes from previous version (`_1.tex`)

### Theory (Section 2)
- **Section 2.1**: Added Stiglitz & Weiss (1981) citation for credit rationing; added bridge sentence in the two-type signaling paragraph connecting posterior belief updating → financing relaxation → innovation quality, making the substitution prediction explicit
- **Section 2.2**: Added Liu et al. (2017) citation on China's patent subsidy environment to motivate the distinction between quantity-rewarding and capability-screening instruments
- **Section 2.3**: Added institutional voids background paragraph citing North (1990), Khanna & Palepu (1997), Mair & Marti (2009); added Lucas (1990) on capital flow and institutional frailty; added Acemoglu et al. (2001) on institutional persistence; added Li (2008) and Hall & Lerner (2010) on financial development and innovation

### Introduction
- Added one paragraph contextualizing SRDI within the broader industrial-policy literature, citing Rodrik (2004), Aghion et al. (2015), and Lerner (2009)

### Results (Section 4)
- **Section 4.1**: Changed "wild-cluster bootstrap inference is not yet reported" to "wild-cluster bootstrap p-values are not reported here" to avoid implying the paper is incomplete
- **Sections 4.5/4.6 reordered**: C&S results (Table 7) now appear as Section 4.5 *before* the methodological explanation (Section 4.6 "Why TWFE and heterogeneity-robust estimates differ"), so readers see the results before the explanation
- **Figure 1 caption**: Added explicit note that the horizontal axis shows years relative to SRDI certification (not stock listing)

### Appendix
- Added description of the instrument construction (province non-self city adoption rate) in the appendix text
- Added Andrews et al. (2019) citation for weak-instrument methodology

### References
- Removed `acemoglu2012` (no natural home in the condensed paper)
- All remaining 24 references now have at least one in-text citation

### Cover letter
- Updated from "four" to "five" substantive revisions
- Fifth revision explicitly describes theory strengthening and citation infrastructure added
- Data availability language updated to "upon request during review and upon acceptance"

### Declarations
- Data availability language aligned with cover letter
- Author biography updated to foreground "technology governance" as primary research area

## Outstanding items (require author action)

1. **Figure 1 (`fig_event_study.png`)**: The x-axis label in the actual figure file must be changed from "Years relative to listing" to "Years relative to certification". This must be done in the figure-generating code (Stata/R) and the PNG re-exported before final submission.

2. **Wild Cluster Bootstrap**: Province-level clustering uses ~33 clusters, below the recommended threshold. Adding wild-cluster bootstrap p-values (e.g., via `boottest` in Stata) to Table 2 would strengthen inference claims.

3. **Li et al. (2026)**: Verify whether this paper has been formally published in *The World Economy*. If so, update the bibliography entry with volume, issue, and page numbers.

4. **Figure 2 (`fig_placebo_permutation.png`)**: Consider redesigning as a histogram + kernel density overlay showing the distribution of 200 permuted coefficients, with a vertical line at the true estimate (0.046). The current scatter format is hard to read.
