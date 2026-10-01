"""Wald and the returning bombers: survivorship bias, and how to undo it.

Abraham Wald's 1943 Statistical Research Group memoranda (reprinted by
Mangel & Samaniego, JASA 1984) estimated aircraft vulnerability using only
damage on planes that came back. The popular "armour where the holes aren't"
story is a simplification, but the math is real. This simulation:

  - Hits land uniformly by area across five sections.
  - Each hit downs the plane with a section-specific probability (assumed).
  - We observe only survivors, then apply Wald's correction to recover the
    per-hit lethality using the known overall loss rate.
"""
import numpy as np

from style import BLUE, INK_2, ORANGE, apply, plt, save

SECTIONS = ["Engines", "Cockpit", "Fuel system", "Fuselage", "Wings"]
AREA = np.array([0.10, 0.05, 0.10, 0.40, 0.35])       # share of plane's exposed area
LETHALITY = np.array([0.40, 0.35, 0.25, 0.04, 0.03])  # P(downed | one hit there), assumed
MEAN_HITS = 2.0
N_PLANES = 200_000


def run(fig_dir, rng):
    hits = rng.poisson(MEAN_HITS, N_PLANES)
    total_hits = hits.sum()
    section = rng.choice(len(SECTIONS), size=total_hits, p=AREA)
    plane = np.repeat(np.arange(N_PLANES), hits)
    lethal = rng.random(total_hits) < LETHALITY[section]
    downed = np.zeros(N_PLANES, bool)
    np.logical_or.at(downed, plane, lethal)
    survived = ~downed

    all_counts = np.bincount(section, minlength=5)
    surv_counts = np.bincount(section[survived[plane]], minlength=5)
    # Hit density (hits per unit area), normalised so the all-aircraft mean = 1.
    dens_all = all_counts / AREA / (all_counts.sum())
    dens_surv = surv_counts / AREA / (surv_counts.sum())

    # Wald-style correction using only single-hit survivors plus the known
    # loss rate among single-hit sorties L: obs_i ∝ area_i (1 - q_i) and
    # Σ area_i q_i = L  ⇒  q_i = 1 - (1 - L) · obs_i / area_i.
    one = hits == 1
    L = downed[one].mean()
    one_surv_sections = section[np.isin(plane, np.where(one & survived)[0])]
    obs = np.bincount(one_surv_sections, minlength=5) / len(one_surv_sections)
    q_hat = 1 - (1 - L) * obs / AREA

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = np.arange(5)
    w = 0.38
    ax.bar(x - w / 2 - 0.01, dens_all, w, color=BLUE, label="All aircraft (unobserved)")
    ax.bar(x + w / 2 + 0.01, dens_surv, w, color=ORANGE, label="Aircraft that returned")
    ax.set_xticks(x, SECTIONS)
    ax.set_ylabel("Bullet holes per unit area (relative)")
    ax.set_title("The holes you see are where planes could afford to be hit")
    ax.set_ylim(0, 1.3)
    ax.legend(loc="upper left", ncol=2)
    for i in range(5):
        ax.text(i + w / 2 + 0.01, dens_surv[i] + 0.02, f"{dens_surv[i]/dens_all[i]:.0%}",
                ha="center", va="bottom", fontsize=8.5, color=INK_2)
    save(fig, f"{fig_dir}/02_wald_bombers.png",
         note="Simulation; lethality per section assumed. Labels: returning-plane hole density as % of true density.")

    return {
        "loss_rate_pct": round(downed.mean() * 100, 1),
        "returned_density_vs_true_pct": {s: round(r * 100) for s, r in zip(SECTIONS, dens_surv / dens_all)},
        "true_lethality": dict(zip(SECTIONS, LETHALITY.tolist())),
        "wald_estimated_lethality": {s: round(float(q), 3) for s, q in zip(SECTIONS, q_hat)},
    }
