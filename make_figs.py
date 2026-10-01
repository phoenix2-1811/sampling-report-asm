"""
make_figs.py

Generates the four figures used in the MATH F113 sampling-techniques report:

  Fig 1 -- fig1_srs_vs_stratified.png
           Monte-Carlo sampling distribution of the mean: SRS vs. proportional
           stratified sampling, on a synthetic population with 4 income strata.

  Fig 2 -- fig4_design_effect.png
           Design-effect comparison: SE of the sample mean under SRS,
           stratified, systematic, and cluster sampling, on a synthetic
           clustered population.

  Fig 3 -- fig2_systematic_periodicity.png
           Systematic sampling coinciding with a hidden weekly periodicity
           in simulated daily footfall data -- shows the resulting bias.

  Fig 4 -- fig3_outlier_cleaning.png
           Outlier detection via the 1.5x IQR rule: before/after box-plots
           on a simulated dataset with injected outliers.

Run with:
    pip install numpy matplotlib --break-system-packages   # if needed
    python3 make_figs.py

All figures are written to ./figs/
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

rng = np.random.default_rng(42)          # fixed seed -> reproducible numbers
plt.rcParams.update({"font.size": 10, "figure.dpi": 150})

OUT_DIR = "figs"
os.makedirs(OUT_DIR, exist_ok=True)


# =====================================================================
# FIGURE 1: Sampling distribution of the mean -- SRS vs Stratified
# =====================================================================
def make_fig1():
    # Synthetic population of N = 2000 households' monthly expenditure
    # (Rs '00), built from 4 unequal strata (e.g. income tiers) with
    # different means/SDs.
    N = 2000
    strata_sizes = [800, 600, 400, 200]                 # Nh
    strata_means = [15, 25, 40, 70]
    strata_sds = [4, 5, 8, 12]

    population = []
    strata_id = []
    for h, (Nh, mh, sh) in enumerate(zip(strata_sizes, strata_means, strata_sds)):
        vals = rng.normal(mh, sh, Nh)
        population.append(vals)
        strata_id.append(np.full(Nh, h))
    population = np.concatenate(population)
    strata_id = np.concatenate(strata_id)
    true_mean = population.mean()

    n = 100          # overall sample size
    reps = 3000      # Monte-Carlo replications

    # --- Simple Random Sampling (without replacement) ---
    srs_means = np.empty(reps)
    for r in range(reps):
        idx = rng.choice(N, size=n, replace=False)
        srs_means[r] = population[idx].mean()

    # --- Stratified sampling: proportional allocation ---
    prop_n = [int(round(n * Nh / N)) for Nh in strata_sizes]
    strat_means = np.empty(reps)
    for r in range(reps):
        picks = []
        for h, (Nh, nh) in enumerate(zip(strata_sizes, prop_n)):
            idx_h = np.where(strata_id == h)[0]
            chosen = rng.choice(idx_h, size=nh, replace=False)
            picks.append(population[chosen])
        strat_means[r] = np.concatenate(picks).mean()

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    bins = np.linspace(min(srs_means.min(), strat_means.min()),
                        max(srs_means.max(), strat_means.max()), 40)
    ax.hist(srs_means, bins=bins, alpha=0.55, label=f"SRS  (SE={srs_means.std():.2f})",
            color="#4C72B0", edgecolor="white")
    ax.hist(strat_means, bins=bins, alpha=0.55, label=f"Stratified  (SE={strat_means.std():.2f})",
            color="#DD8452", edgecolor="white")
    ax.axvline(true_mean, color="black", linestyle="--", linewidth=1,
               label=f"Population mean = {true_mean:.1f}")
    ax.set_xlabel("Sample mean, $\\bar{x}$  (n = 100)")
    ax.set_ylabel("Frequency (of 3000 samples)")
    ax.set_title("Sampling distribution of $\\bar{x}$: SRS vs. Proportional Stratified Sampling")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/fig1_srs_vs_stratified.png")
    plt.close(fig)

    print("[Fig 1] SRS SD of means:", srs_means.std(),
          " Stratified SD of means:", strat_means.std())


# =====================================================================
# FIGURE 2 (report Fig. 2 / design effect): design-effect comparison
# across four probability designs on a clustered population
# =====================================================================
def make_fig_design_effect():
    # Population: 60 natural clusters (e.g. housing blocks) of 50 units
    # each, with a shared cluster-level effect -> positive intra-cluster
    # correlation.
    n_clusters = 60
    cluster_size = 50
    N4 = n_clusters * cluster_size

    cluster_means = rng.normal(100, 15, n_clusters)
    cluster_of = np.repeat(np.arange(n_clusters), cluster_size)
    pop4 = cluster_means[cluster_of] + rng.normal(0, 5, N4)

    # An unrelated stratifying variable (e.g. income tier), independent
    # of cluster membership.
    strata4 = rng.integers(0, 4, N4)
    strata4_sizes = [np.sum(strata4 == s) for s in range(4)]

    n_target = 150
    reps4 = 2000
    true_mean4 = pop4.mean()

    # --- SRS ---
    srs4 = np.empty(reps4)
    for r in range(reps4):
        idx = rng.choice(N4, size=n_target, replace=False)
        srs4[r] = pop4[idx].mean()

    # --- Stratified (proportional, on the unrelated stratifying variable) ---
    strat4 = np.empty(reps4)
    prop_n4 = [int(round(n_target * s / N4)) for s in strata4_sizes]
    for r in range(reps4):
        picks = []
        for s, ns in enumerate(prop_n4):
            idx_s = np.where(strata4 == s)[0]
            picks.append(pop4[rng.choice(idx_s, size=ns, replace=False)])
        strat4[r] = np.concatenate(picks).mean()

    # --- Systematic (random start each rep, list order = cluster order) ---
    k4 = N4 // n_target
    sys4 = np.empty(reps4)
    for r in range(reps4):
        start = rng.integers(0, k4)
        idx = np.arange(start, N4, k4)[:n_target]
        sys4[r] = pop4[idx].mean()

    # --- Cluster sampling (whole clusters selected, ~n_target units) ---
    clusters_needed = n_target // cluster_size  # 3 clusters of 50 = 150
    clu4 = np.empty(reps4)
    for r in range(reps4):
        chosen = rng.choice(n_clusters, size=clusters_needed, replace=False)
        mask = np.isin(cluster_of, chosen)
        clu4[r] = pop4[mask].mean()

    methods = ["SRS", "Stratified", "Systematic", "Cluster"]
    ses = [srs4.std(), strat4.std(), sys4.std(), clu4.std()]
    deff = [s**2 / ses[0]**2 for s in ses]

    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    bars = ax.bar(methods, ses, color=colors, alpha=0.85, edgecolor="black", linewidth=0.6)
    for b, d in zip(bars, deff):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03,
                f"deff={d:.2f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Standard error of $\\bar{x}$ (n $\\approx$ 150)")
    ax.set_title("Design Effect: SE of the Sample Mean under Four Probability Designs")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/fig4_design_effect.png")
    plt.close(fig)

    print("[Design effect] N:", N4, "true mean:", true_mean4)
    print("[Design effect] SEs:", dict(zip(methods, ses)))
    print("[Design effect] deff:", dict(zip(methods, deff)))


# =====================================================================
# FIGURE 3 (report Fig. 2 in the i.i.d. section): systematic sampling
# hitting a hidden periodicity
# =====================================================================
def make_fig_systematic_periodicity():
    # Population arranged in a list order that has a hidden weekly cycle,
    # e.g. daily footfall at a store, period = 7 (higher on weekends).
    days = np.arange(1, 281)              # 40 weeks of data
    base = 50 + 25 * (np.sin(2 * np.pi * (days % 7) / 7 - np.pi / 2) > 0.5)
    noise = rng.normal(0, 3, len(days))
    footfall = base + noise

    k = 7  # sampling interval equal to the period -> disaster case
    start = 5  # always lands on a "high" day (e.g. Saturday)
    sys_idx = np.arange(start, len(days), k)

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.plot(days, footfall, color="lightgray", linewidth=1, label="Daily footfall (population)")
    ax.scatter(days[sys_idx], footfall[sys_idx], color="crimson", zorder=5, s=25,
               label=f"Systematic sample (k={k}, every day landing on Sat.)")
    ax.axhline(footfall.mean(), color="black", linestyle="--", linewidth=1,
               label=f"True population mean = {footfall.mean():.1f}")
    ax.axhline(footfall[sys_idx].mean(), color="crimson", linestyle=":", linewidth=1.3,
               label=f"Systematic sample mean = {footfall[sys_idx].mean():.1f}")
    ax.set_xlabel("Day index (280 days, weekly cycle = 7)")
    ax.set_ylabel("Footfall")
    ax.set_title("Systematic Sampling Coinciding with a Hidden Periodicity")
    ax.legend(fontsize=7.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/fig2_systematic_periodicity.png")
    plt.close(fig)

    print("[Periodicity] True mean:", footfall.mean(),
          " Systematic (bad phase) mean:", footfall[sys_idx].mean())


# =====================================================================
# FIGURE 4 (report Fig. 3 in the cleaning section): outlier detection
# via the 1.5x IQR rule, before/after
# =====================================================================
def make_fig_outlier_cleaning():
    clean_vals = rng.normal(50, 8, 194)
    outliers = np.array([5, 8, 130, 135, 140, 150])  # data-entry errors
    raw = np.concatenate([clean_vals, outliers])
    rng.shuffle(raw)

    q1, q3 = np.percentile(raw, [25, 75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (raw >= lower) & (raw <= upper)
    cleaned = raw[mask]

    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.4), sharey=True)
    axes[0].boxplot(raw, vert=True, patch_artist=True,
                     boxprops=dict(facecolor="#4C72B0", alpha=0.5))
    axes[0].set_title(f"Raw data (n={len(raw)})")
    axes[0].set_ylabel("Value")
    axes[1].boxplot(cleaned, vert=True, patch_artist=True,
                     boxprops=dict(facecolor="#55A868", alpha=0.5))
    axes[1].set_title(f"After IQR cleaning (n={len(cleaned)})")
    fig.suptitle("Outlier Detection via the 1.5\u00d7IQR Rule", y=1.02)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/fig3_outlier_cleaning.png", bbox_inches="tight")
    plt.close(fig)

    print("[Cleaning] Raw mean/sd:", raw.mean(), raw.std())
    print("[Cleaning] Cleaned mean/sd:", cleaned.mean(), cleaned.std())
    print("[Cleaning] Bounds:", lower, upper)


if __name__ == "__main__":
    # NOTE: this order matches the original sequence the figures were
    # generated in (all draw from one shared seeded RNG), so re-running
    # this script reproduces exactly the numbers quoted in the report.
    # Reordering these calls will still work, but will shift every
    # number downstream of the reordered call.
    make_fig1()
    make_fig_systematic_periodicity()
    make_fig_outlier_cleaning()
    make_fig_design_effect()
    print(f"\nAll figures written to ./{OUT_DIR}/")
