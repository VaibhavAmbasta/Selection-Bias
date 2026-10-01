"""The hot hand: the famous debunking had a selection bias of its own.

Gilovich, Vallone & Tversky (1985) compared P(hit | previous k hits) with
P(hit | previous k misses) within each shooter's finite sequence, and found no
difference -> "the hot hand is a fallacy". Miller & Sanjurjo (Econometrica
2018) proved this estimator is biased downward: selecting the shots that
follow a streak, inside a finite sequence, systematically under-samples
continuations. A truly random shooter therefore shows a *negative* gap, so a
measured gap of zero is evidence *for* a hot hand.

This module computes the bias exactly (n=4, k=1, by enumeration) and by
Monte Carlo for GVT-sized sequences (n=100, k=3).
"""
import itertools

import numpy as np

from style import GRAY, ORANGE, apply, label_hbars, plt, save, titled


def exact_small(n=4):
    vals = []
    for seq in itertools.product([0, 1], repeat=n):
        after = [seq[i + 1] for i in range(n - 1) if seq[i] == 1]
        if after:
            vals.append(np.mean(after))
    return float(np.mean(vals))


def streak_stats(seqs, k):
    """Per-sequence P(hit | k hits before) and P(hit | k misses before)."""
    n = seqs.shape[1]
    win = np.lib.stride_tricks.sliding_window_view(seqs, k, axis=1)[:, : n - k]
    nxt = seqs[:, k:]
    after_h = win.all(axis=2)
    after_m = (~win.astype(bool)).all(axis=2)
    nh, nm = after_h.sum(1), after_m.sum(1)
    ph = np.where(nh > 0, (nxt * after_h).sum(1) / np.maximum(nh, 1), np.nan)
    pm = np.where(nm > 0, (nxt * after_m).sum(1) / np.maximum(nm, 1), np.nan)
    return ph, pm


def run(fig_dir, rng, reps=200_000):
    small = exact_small(4)
    seqs = (rng.random((reps, 100)) < 0.5).astype(np.int8)
    ph, pm = streak_stats(seqs, 3)
    both = ~np.isnan(ph) & ~np.isnan(pm)
    e_ph = np.nanmean(ph)
    e_gap = np.mean(ph[both] - pm[both])

    apply()
    fig, ax = plt.subplots(figsize=(8, 3.8))
    rows = [("If streaks don't exist,\nyou'd expect", 50.0, GRAY),
            ("What the method reports:\n4 coin flips, after a head", small * 100, ORANGE),
            ("What the method reports:\n100 shots, after 3 makes in a row", e_ph * 100, ORANGE)]
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.56)
    label_hbars(ax, y, [r[1] for r in rows], [f"{r[1]:.1f}%" for r in rows], 0.6)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 60)
    ax.set_xlabel("Chance the next shot (or flip) goes in, for a purely random 50/50 shooter")
    ax.grid(axis="y", visible=False)
    titled(ax, "The hot-hand test is rigged against finding a hot hand",
           "Applied to pure coin flips, the 1985 method says streaks make you colder")
    save(fig, f"{fig_dir}/04_hot_hand.png",
         note="4 flips: exact, by listing all 16 sequences. 100 shots: average over 200,000 simulated random shooters.")

    table = []
    for seq in itertools.product("HT", repeat=4):
        after = [seq[i + 1] for i in range(3) if seq[i] == "H"]
        share = (f"{after.count('H')}/{len(after)}" if after else "n/a (no flip follows a head)")
        table.append({"sequence": "".join(seq), "heads_after_heads": share})

    return {
        "exact_n4_k1_expected_p_hit_after_hit": round(small, 4),
        "n100_k3_expected_p_hit_after_3_hits": round(float(e_ph), 4),
        "n100_k3_expected_gap_hits_minus_misses_points": round(float(e_gap) * 100, 1),
        "four_flip_table": table,
    }
