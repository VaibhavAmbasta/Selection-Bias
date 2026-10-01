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

from matplotlib.patches import Ellipse, Polygon
from matplotlib.path import Path

from style import INK, INK_2, ORANGE, apply, plt, save

SECTIONS = ["Engines", "Cockpit", "Fuel system", "Fuselage", "Wings"]
AREA = np.array([0.10, 0.05, 0.10, 0.40, 0.35])       # share of plane's exposed area
LETHALITY = np.array([0.60, 0.50, 0.30, 0.04, 0.03])  # P(downed | one hit there), assumed
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

    _draw_planes(fig_dir, dens_surv / dens_all, rng)

    return {
        "loss_rate_pct": round(downed.mean() * 100, 1),
        "returned_density_vs_true_pct": {s: round(r * 100) for s, r in zip(SECTIONS, dens_surv / dens_all)},
        "true_lethality": dict(zip(SECTIONS, LETHALITY.tolist())),
        "wald_estimated_lethality": {s: round(float(q), 3) for s, q in zip(SECTIONS, q_hat)},
    }


# Top-down bomber outline (nose up). Coordinates are arbitrary drawing units.
FUSELAGE = [(-0.65, -4.2), (0.65, -4.2), (0.65, 3.6), (-0.65, 3.6)]
COCKPIT = [(-0.65, 3.6), (0.65, 3.6), (0.45, 4.9), (0.0, 5.4), (-0.45, 4.9)]
WINGS = [(-0.65, 1.6), (-7.2, 0.4), (-7.2, -0.4), (-0.65, -0.2),
         (0.65, -0.2), (7.2, -0.4), (7.2, 0.4), (0.65, 1.6)]
TAIL = [(-0.65, -3.0), (-2.8, -3.8), (-2.8, -4.3), (2.8, -4.3), (2.8, -3.8), (0.65, -3.0)]
FUEL = [(-0.65, -1.4), (0.65, -1.4), (0.65, 1.6), (-0.65, 1.6)]
ENGINES = [(-4.3, 0.75), (-2.3, 1.05), (2.3, 1.05), (4.3, 0.75)]
ENG_W, ENG_H = 0.8, 2.0


def _section_of(pts):
    """Map each point to a section index (-1 = outside the plane)."""
    sec = np.full(len(pts), -1)
    in_eng = np.zeros(len(pts), bool)
    for cx, cy in ENGINES:
        in_eng |= ((pts[:, 0] - cx) / (ENG_W / 2)) ** 2 + ((pts[:, 1] - cy) / (ENG_H / 2)) ** 2 <= 1
    in_cock = Path(COCKPIT).contains_points(pts)
    in_fuel = Path(FUEL).contains_points(pts)
    in_body = Path(FUSELAGE).contains_points(pts) | Path(TAIL).contains_points(pts)
    in_wing = Path(WINGS).contains_points(pts)
    for idx, mask in [(4, in_wing), (3, in_body), (2, in_fuel), (1, in_cock), (0, in_eng)]:
        sec[mask] = idx  # later assignments win: engines > cockpit > fuel > body > wings
    return sec


def _draw_plane(ax):
    for poly in (WINGS, TAIL, FUSELAGE, COCKPIT):
        ax.add_patch(Polygon(poly, closed=True, fc="#e9ecef", ec="#9aa1a9", lw=1.2, zorder=1))
    for cx, cy in ENGINES:
        ax.add_patch(Ellipse((cx, cy), ENG_W, ENG_H, fc="#d5dae0", ec="#9aa1a9", lw=1.2, zorder=2))
    ax.set_xlim(-7.6, 7.6)
    ax.set_ylim(-4.8, 5.8)
    ax.set_aspect("equal")
    ax.axis("off")


def _draw_planes(fig_dir, rel_density, rng, n_candidates=9000):
    pts = np.column_stack([rng.uniform(-7.3, 7.3, n_candidates), rng.uniform(-4.4, 5.5, n_candidates)])
    sec = _section_of(pts)
    inside = sec >= 0
    pts, sec = pts[inside], sec[inside]
    base_keep = 0.12  # thin the dots so the picture stays readable
    keep_all = rng.random(len(pts)) < base_keep
    keep_ret = rng.random(len(pts)) < base_keep * rel_density[sec] / rel_density.max() * 1.0

    apply()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, keep, head in [(axes[0], keep_all, "Where bullets actually hit\n(all planes, including those shot down)"),
                           (axes[1], keep_ret, "Holes on the planes that came home\n(the only ones anyone could inspect)")]:
        _draw_plane(ax)
        ax.scatter(pts[keep, 0], pts[keep, 1], s=7, color=ORANGE, zorder=3, lw=0)
        ax.set_title(head, fontsize=11, loc="center", fontweight="normal", color=INK)
    axes[1].annotate("far fewer holes\non the engines", xy=(4.3, 1.9), xytext=(4.6, 4.2), fontsize=9.5,
                     color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.9))
    axes[1].annotate("and the cockpit", xy=(0.3, 4.8), xytext=(-3.6, 4.5), fontsize=9.5, color=INK,
                     ha="center", arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.9))
    fig.suptitle("The missing holes show where planes couldn't afford to be hit",
                 x=0.02, ha="left", fontsize=13, fontweight="bold", color=INK, y=1.02)
    save(fig, f"{fig_dir}/02_wald_bombers.png",
         note="Simulation of 200,000 sorties. Dot density on the right is proportional to the simulated hole density on returning planes. Section deadliness is assumed.")
