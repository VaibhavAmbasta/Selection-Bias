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

from style import BLUE, GRAY, ORANGE, apply, label_hbars, plt, save, titled

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

    per1000 = 1000 / N_STUDIES
    n_pub = published.sum() * per1000
    n_pub_null = (published & ~real).sum() * per1000
    n_rep = rep_success.sum() * per1000
    res.update({"per_1000_run": 1000, "per_1000_published": round(n_pub),
                "per_1000_published_null": round(n_pub_null), "per_1000_replicate": round(n_rep)})

    apply()
    # Chart A: the real Reproducibility Project numbers.
    fig, ax = plt.subplots(figsize=(8, 3.4))
    rows = [("Original studies with a\n'significant' result", 97, BLUE),
            ("Same studies, repeated\nby other teams", 36, ORANGE)]
    y = np.arange(2)[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.5)
    label_hbars(ax, y, [r[1] for r in rows], [f"{r[1]}%" for r in rows], 1.0)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100], ["0", "25%", "50%", "75%", "100%"])
    ax.grid(axis="y", visible=False)
    titled(ax, "Most famous psychology results didn't survive a re-run",
           "100 studies from top journals (2008), repeated by 270 researchers")
    save(fig, f"{fig_dir}/06a_replication_real.png",
         note="Source: Open Science Collaboration (2015), Science 349(6251). Replicated effects were also about half as large on average.")

    # Chart B: the filter, per 1,000 studies.
    fig, ax = plt.subplots(figsize=(8, 3.9))
    rows = [("Studies run", 1000, GRAY),
            ("Got p < 0.05 and published", n_pub, BLUE),
            ("...of which the effect isn't real", n_pub_null, ORANGE),
            ("...that work again when repeated", n_rep, BLUE)]
    y = np.arange(4)[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.56)
    label_hbars(ax, y, [r[1] for r in rows], [f"{r[1]:,.0f}" for r in rows], 12)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 1150)
    ax.set_xlabel("Number of studies (simulated, per 1,000 run)")
    ax.grid(axis="y", visible=False)
    titled(ax, "Only the lucky results get printed",
           f"Published effects looked {res['mean_published_d'] / res['mean_true_d_of_published']:.1f}x bigger than they really were")
    save(fig, f"{fig_dir}/06b_publication_filter.png",
         note="Simulation; the mix of real and zero effects and the sample sizes are assumptions. See analysis/publication_filter.py.")
    return res
