"""The low-birth-weight paradox: conditioning on a collider.

US vital statistics show that among low-birth-weight (LBW) infants, babies of
smokers have *lower* mortality than babies of non-smokers. Hernández-Díaz,
Schisterman & Hernán (Am J Epidemiol 2006) showed this follows from selecting
on birth weight, which is caused both by smoking and by other, far deadlier
causes (e.g. birth defects). Among LBW babies, a non-smoker's baby is more
likely to be small *because of* the deadlier cause.

Computed exactly by enumerating the four (smoking, defect) cells, so there is
no sampling noise. Smoking is given a strictly harmful effect everywhere.
"""
import itertools

from style import BLUE, INK_2, ORANGE, apply, plt, save, titled

P_SMOKE = 0.25
P_DEFECT = 0.02
# P(LBW | smoke, defect): smoking roughly doubles LBW risk; defects make it common.
P_LBW = {(0, 0): 0.05, (1, 0): 0.11, (0, 1): 0.50, (1, 1): 0.60}
# P(death | lbw, smoke, defect): smoking adds risk in every stratum.
BASE, LBW_ADD, DEFECT_ADD, SMOKE_ADD = 0.002, 0.020, 0.150, 0.003


def mortality(lbw, s, d):
    return BASE + LBW_ADD * lbw + DEFECT_ADD * d + SMOKE_ADD * s


def run(fig_dir, rng=None):
    cells = []
    for s, d, lbw in itertools.product((0, 1), (0, 1), (0, 1)):
        p = (P_SMOKE if s else 1 - P_SMOKE) * (P_DEFECT if d else 1 - P_DEFECT)
        p *= P_LBW[(s, d)] if lbw else 1 - P_LBW[(s, d)]
        cells.append((s, d, lbw, p, mortality(lbw, s, d)))

    def rate(s, lbw=None):
        sel = [c for c in cells if c[0] == s and (lbw is None or c[2] == lbw)]
        w = sum(c[3] for c in sel)
        return sum(c[3] * c[4] for c in sel) / w, sum(c[3] for c in sel if c[1]) / w

    res = {}
    for name, lbw in (("all", None), ("lbw", 1), ("normal", 0)):
        (m1, d1), (m0, d0) = rate(1, lbw), rate(0, lbw)
        res[name] = {"smoker_per_1000": round(m1 * 1000, 1), "nonsmoker_per_1000": round(m0 * 1000, 1),
                     "rr": round(m1 / m0, 2), "defect_share_smoker_pct": round(d1 * 100, 1),
                     "defect_share_nonsmoker_pct": round(d0 * 100, 1)}

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.4))
    groups = [("All babies", "all"), ("Normal-weight babies", "normal"), ("Small babies only\n(under 2.5 kg)", "lbw")]
    w = 0.36
    for i, (label, key) in enumerate(groups):
        ax.bar(i - w / 2 - 0.01, res[key]["nonsmoker_per_1000"], w, color=BLUE,
               label="Non-smoking mother" if i == 0 else None)
        ax.bar(i + w / 2 + 0.01, res[key]["smoker_per_1000"], w, color=ORANGE,
               label="Smoking mother" if i == 0 else None)
        top = max(res[key]["nonsmoker_per_1000"], res[key]["smoker_per_1000"])
        ax.text(i, top + 1.2, (f"{(res[key]['rr'] - 1) * 100:+.0f}% for smokers"), ha="center", fontsize=9.5, color=INK_2)
    ax.set_xticks(range(3), [g[0] for g in groups])
    ax.set_ylabel("Babies who die in their first year, per 1,000")
    titled(ax, "Smoking harms babies, yet seems to 'protect' small ones",
           "Look only at small babies, and smoking mothers' babies appear to do better")
    ax.set_ylim(0, 58)
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    save(fig, f"{fig_dir}/05_birth_weight.png",
         note="Exact calculation from an assumed model in which smoking raises the risk of death for every baby. The real-world pattern is in US vital statistics.")
    return res
