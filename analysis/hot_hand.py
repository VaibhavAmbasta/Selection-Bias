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

from style import BLUE, INK_2, ORANGE, apply, plt, save


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

    lengths = [10, 20, 40, 60, 100, 200, 400]
    curve = {}
    for k in (1, 2, 3):
        row = []
        for n in lengths:
            s = (rng.random((40_000, n)) < 0.5).astype(np.int8)
            h, _ = streak_stats(s, k)
            row.append((np.nanmean(h) - 0.5) * 100)
        curve[k] = row

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colors = {1: BLUE, 2: ORANGE, 3: INK_2}
    for k in (1, 2, 3):
        ax.plot(lengths, curve[k], color=colors[k], lw=2, marker="o", ms=5,
                label=f"after {k} hit{'s' if k > 1 else ''} in a row")
    ax.axhline(0, color=INK_2, lw=1)
    ax.axvline(100, color=INK_2, lw=1, ls=":")
    ax.text(104, -11, "GVT-sized\nsequence", fontsize=9, color=INK_2, va="top")
    ax.set_xscale("log")
    ax.set_xticks(lengths, [str(n) for n in lengths])
    ax.set_xlabel("Shots per sequence (log scale)")
    ax.set_ylabel("Measured hit rate minus true 50% (points)")
    ax.set_title("A perfectly random 50% shooter 'looks cold' after streaks")
    ax.legend(loc="lower right")
    save(fig, f"{fig_dir}/04_hot_hand.png",
         note="Monte Carlo, 40,000 sequences per point. Coin-flip shooter: every shot independent, P(hit)=0.5.")

    return {
        "exact_n4_k1_expected_p_hit_after_hit": round(small, 4),
        "n100_k3_expected_p_hit_after_3_hits": round(float(e_ph), 4),
        "n100_k3_expected_gap_hits_minus_misses_points": round(float(e_gap) * 100, 1),
        "curve_points": {f"k={k}": dict(zip(map(str, lengths), [round(v, 2) for v in curve[k]])) for k in curve},
    }
