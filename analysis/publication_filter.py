"""The significance filter: why famous findings shrink on replication.

Published anchor: Open Science Collaboration (Science, 2015) re-ran 100
psychology studies. 97% of originals were significant; 36% of replications
were; replication effect sizes averaged about half the originals.

Simulated mechanism: many labs run small studies of modest true effects.
Journals select the ones that cross p < 0.05. We then replicate each published
study with a larger sample and compare. Effect-size distribution and sample
sizes are assumptions chosen to be plausible for 2008-era social psychology,
not estimates of the OSC sample.
"""
import numpy as np
from scipy import stats

from style import BLUE, GRAY, INK_2, ORANGE, apply, plt, save

N_STUDIES = 200_000
P_NULL = 0.6            # share of tested hypotheses with no true effect (assumed)
TRUE_D_MEAN = 0.20      # mean true effect (Cohen's d) when real, exponential (assumed)
N_ORIG = 25             # per group, original
N_REP = 40              # per group, replication (replications were typically larger)


def simulate_d(true_d, n, rng):
    se = np.sqrt(2 / n)
    d_hat = true_d + se * rng.standard_normal(true_d.shape)
    p = 2 * stats.norm.sf(np.abs(d_hat) / se)
    return d_hat, p


def run(fig_dir, rng):
    real = rng.random(N_STUDIES) >= P_NULL
    true_d = np.where(real, rng.exponential(TRUE_D_MEAN, N_STUDIES), 0.0)
    d_orig, p_orig = simulate_d(true_d, N_ORIG, rng)
    published = (p_orig < 0.05) & (d_orig > 0)

    d_rep, p_rep = simulate_d(true_d[published], N_REP, rng)
    rep_success = (p_rep < 0.05) & (d_rep > 0)

    res = {
        "share_of_studies_published_pct": round(published.mean() * 100, 1),
        "published_that_are_null_pct": round((~real[published]).mean() * 100, 1),
        "mean_published_d": round(float(d_orig[published].mean()), 3),
        "mean_true_d_of_published": round(float(true_d[published].mean()), 3),
        "mean_replication_d": round(float(d_rep.mean()), 3),
        "replication_success_pct": round(rep_success.mean() * 100, 1),
        "shrinkage_ratio": round(float(d_rep.mean() / d_orig[published].mean()), 2),
    }

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    idx = rng.choice(published.sum(), 1500, replace=False)
    ax.scatter(d_orig[published][idx], d_rep[idx], s=9, color=BLUE, alpha=0.35, lw=0,
               label="Published study (1 dot each)")
    lim = (-0.6, 1.5)
    ax.plot(lim, lim, color=GRAY, lw=1, ls="--")
    ax.text(1.15, 1.25, "replication = original", fontsize=8.5, color=INK_2, rotation=33)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.scatter([res["mean_published_d"]], [res["mean_replication_d"]], s=90, color=ORANGE,
               edgecolor="white", lw=2, zorder=5, label="Average")
    ax.annotate(f"published avg d = {res['mean_published_d']:.2f}\nreplication avg d = {res['mean_replication_d']:.2f}",
                (res["mean_published_d"], res["mean_replication_d"]), xytext=(0.85, -0.45),
                fontsize=9, color=INK_2, arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8))
    ax.set_xlim(*lim)
    ax.set_ylim(-0.6, 1.5)
    ax.set_xlabel("Effect size in the original, published study (Cohen's d)")
    ax.set_ylabel("Effect size when replicated")
    ax.set_title("Publishing only 'significant' results inflates every effect")
    ax.legend(loc="upper left")
    save(fig, f"{fig_dir}/06_publication_filter.png",
         note="Simulation; true-effect distribution and sample sizes assumed. Real-world anchor: OSC 2015 (97% → 36% significant; effects ~halved).")
    return res
