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

from style import BLUE, GRAY, INK, ORANGE, apply, label_hbars, plt, save, titled

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
    fig, ax = plt.subplots(figsize=(8, 3.9))
    rows = [("1990s observational studies\n(e.g. Nurses' Health Study)", -45, ORANGE, "about 45% lower"),
            ("Randomised trial\n(Women's Health Initiative, 2002-03)", 24, BLUE, "24% higher"),
            ("Our simulation: drug set to\n24% higher, women choose", (naive - 1) * 100, GRAY,
             f"{abs(naive - 1) * 100:.0f}% lower")]
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.56)
    label_hbars(ax, y, [r[1] for r in rows], [r[3] for r in rows], 1.5)
    ax.axvline(0, color=INK, lw=1.2)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(-100, 50)
    ax.set_xticks([-60, -40, -20, 0, 20, 40], ["-60%", "-40%", "-20%", "0", "+20%", "+40%"])
    ax.set_xlabel("Change in heart-disease risk for women on HRT   (left = looks protective, right = harmful)")
    ax.grid(axis="y", visible=False)
    titled(ax, "Studies said HRT protected the heart. A trial found the opposite",
           "And a simulation shows self-selection alone can produce the false result")
    save(fig, f"{fig_dir}/03_hrt.png",
         note="Observational: 40-50% reduction reported across 1980s-90s cohort studies. WHI: hazard ratio 1.24 (Manson et al. 2003). Simulation: see analysis/hrt.py.")

    return {
        "true_rr": TRUE_RR,
        "observational_naive_rr": round(naive, 2),
        "observational_adjusted_rr": round(adjusted, 2),
        "rct_rr": round(rct, 2),
        "hrt_uptake_pct": round(chose.mean() * 100, 1),
    }
