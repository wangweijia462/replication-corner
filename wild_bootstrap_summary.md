# Wild Cluster Bootstrap Summary

Stata was run from `C:/stata_tis_run` on 9 June 2026 using 9,999 wild bootstrap replications with province-level clustering (`PROVINCECODE`) and Webb weights.

Because `boottest` did not run directly after `reghdfe` with two absorbed fixed effects in this local Stata setup, the bootstrap tests use the algebraically equivalent specification `areg ..., absorb(code)` with year fixed effects included as `i.year`.

| Test | N | Province clusters | Coefficient | Cluster SE | Conventional p | Wild bootstrap p |
|---|---:|---:|---:|---:|---:|---:|
| Certification x institutional quality | 27,998 | 30 | 0.042999 | 0.037857 | 0.265 | 0.280 |
| Certification, high-institution subgroup | 14,303 | 16 | 0.065745 | 0.051391 | 0.220 | 0.121 |
| Certification, low-institution subgroup | 13,695 | 26 | 0.068757 | 0.050743 | 0.188 | 0.258 |

Interpretation: the bootstrap inference does not support a strong statistical claim for the baseline interaction or for the split-sample certification coefficients. The results are directionally positive but imprecise under province-level clustered small-sample inference. A previous Rademacher-weight run gave a very similar p-value for the main interaction, 0.274.
