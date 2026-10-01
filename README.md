# Sampling Report -- Simulation Code

This folder contains the Python code used to generate all four Monte-Carlo
simulation figures in the MATH F113 report "Sampling and Sampling
Techniques: Concept, Theory and Practice".

## Contents

- `make_figs.py` -- the full simulation script (all four figures)
- `requirements.txt` -- the two packages needed to run it
- `figs/` -- output folder; populated when you run the script
  (pre-generated copies are included here too, so you don't have to
  rerun anything just to get the images)

## What each figure shows

| Script function | Output file | Used in report as | What it demonstrates |
|---|---|---|---|
| `make_fig1()` | `fig1_srs_vs_stratified.png` | Fig. 1 | SRS vs. stratified sampling: 3,000 simulated samples, showing the stratified design's smaller standard error |
| `make_fig_design_effect()` | `fig4_design_effect.png` | Fig. 2 (design effect) | SE of the mean under SRS, stratified, systematic, and cluster sampling on the same clustered population, with the design effect (deff) labelled on each bar |
| `make_fig_systematic_periodicity()` | `fig2_systematic_periodicity.png` | Fig. 2 (i.i.d. section) | A systematic sample whose interval coincides with a hidden weekly cycle, showing the resulting bias |
| `make_fig_outlier_cleaning()` | `fig3_outlier_cleaning.png` | Fig. 3 (cleaning section) | Before/after box-plots from applying the 1.5xIQR outlier rule |

(Note: the function names above don't match the report's figure numbers
one-to-one -- the script's internal file names were kept consistent with
what's referenced inside `main.tex` for the LaTeX report, so you can
drop this `figs/` folder straight into the Overleaf project without
renaming anything.)

## How to run it

```bash
pip install -r requirements.txt
python3 make_figs.py
```

This regenerates all four PNGs inside `figs/`. A fixed random seed
(`np.random.default_rng(42)`) is used throughout, so rerunning the
script reproduces the exact same numbers and figures every time --
useful if anyone asks you to demonstrate reproducibility.

## Reproducing the numbers quoted in the report

Running the script prints the key statistics to the console as it goes
(standard errors, design effects, means, IQR bounds), e.g.:

```
[Fig 1] SRS SD of means: 1.6495...  Stratified SD of means: 0.6186...
[Design effect] deff: {'SRS': 1.0, 'Stratified': 0.95, 'Systematic': 0.19, 'Cluster': 43.79}
[Periodicity] True mean: 57.42  Systematic (bad phase) mean: 49.42
[Cleaning] Raw mean/sd: 52.23 15.36   Cleaned mean/sd: 51.03 7.90
```

These are exactly the figures quoted in the report's captions and text.
