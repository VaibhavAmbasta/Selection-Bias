"""Hormone replacement therapy: observational "protection" vs. the RCT.

Published anchors:
  - Observational studies (e.g. Nurses' Health Study) reported roughly a
    40-50% lower coronary heart disease (CHD) risk in HRT users.
  - The Women's Health Initiative RCT (estrogen + progestin) found
    HR 1.29 at the 2002 stop, 1.24 in the 2003 adjusted final analysis.

Mechanism simulated: women self-select into HRT. Those who chose it were, on
average, healthier, wealthier and more adherent ("healthy-user" selection).
We give HRT a true *harmful* effect (risk ratio 1.24, the WHI figure) and
show that self-selection alone flips it to apparent protection. Epidemiologists
classify this as confounding by self-selection into treatment.
"""
import numpy as np

from style import BLUE, GRAY, INK_2, ORANGE, apply, plt, save

N = 2_000_000
TRUE_RR = 1.24
UPTAKE_SLOPE = 1.1      # how strongly latent health drives choosing HRT (assumed)
RISK_SLOPE = 0.9        # how strongly latent health lowers CHD risk (assumed)
BASE_RISK = 0.02        # ~5-year CHD risk at average health (assumed)
PROXY_NOISE = 1.0       # measured covariates capture latent health imperfectly


def rr(outcome, treated, mask=None):
    if mask is not None:
        outcome, treated = outcome[mask], treated[mask]
    return outcome[treated].mean() / outcome[~treated].mean()


def run(fig_dir, rng):
    health = rng.standard_normal(N)
    p_take = 1 / (1 + np.exp(-(-0.7 + UPTAKE_SLOPE * health)))
    chose = rng.random(N) < p_take
    base = BASE_RISK * np.exp(-RISK_SLOPE * health)

    def outcome(treated):
        return rng.random(N) < np.clip(base * np.where(treated, TRUE_RR, 1.0), 0, 1)

    obs_y = outcome(chose)
    naive = rr(obs_y, chose)

    # "Adjusted" analysis: stratify on a noisy proxy (education, BMI, smoking...)
    proxy = health + PROXY_NOISE * rng.standard_normal(N)
    bins = np.quantile(proxy, np.linspace(0, 1, 11))
    strata = np.clip(np.digitize(proxy, bins[1:-1]), 0, 9)
    num = den = 0.0
    for s in range(10):
        m = strata == s
        w = m.sum()
        num += w * obs_y[m & chose].mean()
        den += w * obs_y[m & ~chose].mean()
    adjusted = num / den

    randomized = rng.random(N) < 0.5
    rct_y = outcome(randomized)
    rct = rr(rct_y, randomized)

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    labels = ["Observational\n(raw)", "Observational\n(adjusted for\nmeasured factors)",
              "Randomised trial", "True effect"]
    vals = [naive, adjusted, rct, TRUE_RR]
    colors = [ORANGE, ORANGE, BLUE, GRAY]
    y = np.arange(4)[::-1]
    ax.barh(y, [v - 1 for v in vals], left=1, color=colors, height=0.55)
    ax.axvline(1, color=INK_2, lw=1)
    for yi, v in zip(y, vals):
        ax.text(v + (0.015 if v >= 1 else -0.015), yi, f"{v:.2f}", va="center",
                ha="left" if v >= 1 else "right", fontsize=10, color=INK_2)
    ax.set_yticks(y, labels)
    ax.set_xlim(0.4, 1.45)
    ax.set_xlabel("Risk ratio for heart disease, HRT users vs non-users  (<1 looks protective)")
    ax.set_title("Same drug, same harm: self-selection made HRT look protective")
    ax.grid(axis="y", visible=False)
    save(fig, f"{fig_dir}/03_hrt.png",
         note="Simulation with true risk ratio fixed at 1.24 (WHI 2003). Real-world anchors: observational ~0.5-0.6; WHI RCT 1.24-1.29.")

    return {
        "true_rr": TRUE_RR,
        "observational_naive_rr": round(naive, 2),
        "observational_adjusted_rr": round(adjusted, 2),
        "rct_rr": round(rct, 2),
        "hrt_uptake_pct": round(chose.mean() * 100, 1),
    }
