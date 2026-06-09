# Revision Notes

## Files in This Submission

| File | Description |
|------|-------------|
| `paper_technology_in_society_anonymous_revised.tex` | Main manuscript (blind review) |
| `title_page_with_author_details.tex` | Separate title page with author details |
| `cover_letter_technology_in_society_revised.tex` | Cover letter |
| `declarations_and_author_biography.tex` | Declarations and author biography |
| `fig_event_study.png` / `fig_event_study.pdf` | Re-exported event-study figure |
| `fig_placebo_permutation.png` / `fig_placebo_permutation.pdf` | Redesigned placebo permutation figure |
| `wild_bootstrap_summary.md` | Summary of province-level wild-cluster bootstrap results |
| `make_event_study.do` / `make_placebo_permutation.do` / `run_wild_bootstrap.do` | Stata scripts used for the new figures and bootstrap checks |
| `revision_notes.md` | This file |

## Summary of Changes From Previous Version

### Theory

- **Section 2.1**: Added Stiglitz and Weiss (1981) citation for credit rationing; added a bridge sentence connecting posterior belief updating, financing relaxation, and innovation quality.
- **Section 2.2**: Added published evidence on China's patenting surge and patent-subsidy policy (Hu et al. 2017; Lin et al. 2021) to motivate the distinction between quantity-rewarding and capability-screening instruments.
- **Section 2.3**: Added institutional voids background paragraph citing North (1990), Khanna and Palepu (1997), and Mair and Marti (2009); added Lucas (1990), Acemoglu et al. (2001), Li (2008), and Hall and Lerner (2010).

### Results

- **Section 4.1**: Added province-level wild-cluster bootstrap inference for the preferred interaction specification. Using 9,999 replications with Webb weights, the bootstrap p-value for `Certification x institutional quality` is 0.280. A Rademacher-weight run gives a similar value, 0.274.
- **Section 4.2 / Figure 1**: Re-exported `fig_event_study.png` and `fig_event_study.pdf` from Stata. The horizontal axis now reads "Years relative to certification"; the text and figure note are aligned with the regenerated coefficients.
- **Figure 2**: Redesigned `fig_placebo_permutation.png` and `fig_placebo_permutation.pdf` as a histogram plus kernel density overlay, with a vertical dashed line at the observed interaction estimate beta3 = 0.046. The finite-simulation permutation p-value is 0.004975.
- **Sections 4.5/4.6**: Callaway and Sant'Anna results now appear before the methodological explanation of why TWFE and heterogeneity-robust estimates differ.

### References and Submission Files

- Updated Li et al. (2026) from forthcoming to the formally published Chinese journal article: *The Journal of World Economy*, 49(4), 36--67.
- Replaced the unverifiable Liu et al. (2017) working-paper citation with published references: Hu et al. (2017) and Lin et al. (2021).
- Removed unused Heckman and Smith (1999) after the event-study discussion no longer uses the pre-programme dip mechanism.
- Updated the cover letter, declarations, author biography, and data-availability language for the Technology in Society submission package.

## Remaining Optional Items

None.
