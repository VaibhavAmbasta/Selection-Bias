"""1936 Literary Digest poll: 2.4 million ballots, wrong by ~20 points.

Published inputs (Squire 1988; Lohr & Brick 2017):
  - ~10 million ballots mailed, 2,376,523 returned (~24% response)
  - Digest tally: Landon 1,293,669 vs Roosevelt 972,897
  - Actual popular vote: Roosevelt 60.8%, Landon 36.5%

Two analyses:
  1. Exact arithmetic on the published numbers: how many *random* respondents
     would have produced the same expected error? (Meng 2018's framing.)
  2. An illustrative two-stage model (biased frame, then vote-dependent
     nonresponse) calibrated to hit the published figures, used to show that
     the error does not shrink as n grows. The model's parameters are chosen,
     not measured; only the anchors above are historical.
"""
import numpy as np

from style import BLUE, INK, INK_2, ORANGE, apply, label_hbars, plt, save, titled

DIGEST_LANDON = 1_293_669
DIGEST_FDR = 972_897
ACTUAL_FDR, ACTUAL_LANDON = 0.608, 0.365

# Illustrative model parameters (calibrated, not historical measurements).
FRAME_SHARE = 0.35          # share of voters reachable via phone/car/subscriber lists
FRAME_FDR = 0.50            # FDR two-party support inside the frame
RESP_FDR, RESP_LANDON = 0.215, 0.285  # response rates by vote among those mailed


def run(fig_dir, rng):
    digest_fdr = DIGEST_FDR / (DIGEST_FDR + DIGEST_LANDON)
    actual_fdr = ACTUAL_FDR / (ACTUAL_FDR + ACTUAL_LANDON)
    error = actual_fdr - digest_fdr
    n_returned = DIGEST_FDR + DIGEST_LANDON
    # A simple random sample of size n has standard error sqrt(p(1-p)/n).
    # Solve sqrt(p(1-p)/n) = |error| for n: the random sample whose *typical*
    # miss equals the Digest's actual miss.
    n_equiv = actual_fdr * (1 - actual_fdr) / error**2

    out_fdr = (actual_fdr - FRAME_SHARE * FRAME_FDR) / (1 - FRAME_SHARE)
    resp_fdr_share = FRAME_FDR * RESP_FDR / (FRAME_FDR * RESP_FDR + (1 - FRAME_FDR) * RESP_LANDON)
    resp_rate = FRAME_FDR * RESP_FDR + (1 - FRAME_FDR) * RESP_LANDON

    gallup_fdr = 0.56  # Gallup's final 1936 forecast as commonly reported (~56%)
    pq = actual_fdr * (1 - actual_fdr)
    miss_1000 = np.sqrt(pq / 1000) * 100
    miss_6 = np.sqrt(pq / 6) * 100

    # Sanity check by simulation: a 2.27M-ballot poll drawn from the calibrated
    # respondent pool still misses by ~19.5 points; sampling noise is negligible.
    dig = rng.binomial(n_returned, resp_fdr_share, 400) / n_returned
    digest_err_sim = np.mean(np.abs(dig - actual_fdr)) * 100

    apply()
    # Chart A: what each poll said vs what happened.
    fig, ax = plt.subplots(figsize=(8, 3.6))
    rows = [("Literary Digest\n2.3 million ballots", digest_fdr * 100, ORANGE),
            ("Gallup\n~50,000 interviews", gallup_fdr * 100, BLUE),
            ("Actual result", actual_fdr * 100, INK_2)]
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.56)
    label_hbars(ax, y, [r[1] for r in rows], [f"{digest_fdr * 100:.1f}%", "~56%", f"{actual_fdr * 100:.1f}%"], 0.8)
    ax.axvline(50, color=INK, lw=1.2, ls="--")
    ax.set_ylim(-0.5, 2.95)
    ax.text(50.6, 2.5, "50%: needed to win", fontsize=9, color=INK_2, va="bottom")
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 75)
    ax.set_xlabel("Roosevelt's share of the vote (Roosevelt vs Landon)")
    ax.grid(axis="y", visible=False)
    titled(ax, "The biggest poll in history picked the wrong winner",
           "1936 US election: what each poll said Roosevelt would get, and what he got")
    save(fig, f"{fig_dir}/01a_literary_digest_polls.png",
         note="Digest and actual: Roosevelt's share of Roosevelt + Landon votes. Gallup: final forecast as commonly reported (~56%).")

    # Chart B: how far off you'd typically be.
    fig, ax = plt.subplots(figsize=(8, 3.6))
    rows = [("Ask 1,000 random voters", miss_1000, BLUE),
            ("Ask 6 random voters", miss_6, BLUE),
            ("Literary Digest\n(2.3 million ballots)", error * 100, ORANGE)]
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.56)
    label_hbars(ax, y, [r[1] for r in rows], [f"{r[1]:.1f} points" for r in rows], 0.4)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 26)
    ax.set_xlabel("How far off the poll typically lands (percentage points)")
    ax.grid(axis="y", visible=False)
    titled(ax, "2.3 million biased ballots were as accurate as 6 random people",
           "A small fair sample beats a huge skewed one")
    save(fig, f"{fig_dir}/01b_literary_digest_six_voters.png",
         note="Random-sample rows: standard sampling error, sqrt(p(1-p)/n), with p = Roosevelt's actual 62.5%. Digest row: its actual miss.")

    return {
        "digest_fdr_two_party_pct": round(digest_fdr * 100, 1),
        "actual_fdr_two_party_pct": round(actual_fdr * 100, 1),
        "error_points": round(error * 100, 1),
        "ballots_returned": n_returned,
        "equivalent_random_sample_size": round(n_equiv, 1),
        "model": {
            "frame_only_fdr_pct": round(FRAME_FDR * 100, 1),
            "frame_plus_nonresponse_fdr_pct": round(resp_fdr_share * 100, 1),
            "outside_frame_fdr_pct": round(out_fdr * 100, 1),
            "implied_response_rate_pct": round(resp_rate * 100, 1),
            "share_of_error_from_nonresponse_pct": round(
                (FRAME_FDR - resp_fdr_share) / (actual_fdr - resp_fdr_share) * 100, 0),
        },
        "digest_err_simulated_at_full_size_points": round(digest_err_sim, 1),
        "typical_miss_random_1000_points": round(miss_1000, 2),
        "typical_miss_random_6_points": round(miss_6, 1),
        "gallup_forecast_pct_as_reported": 56,
    }
