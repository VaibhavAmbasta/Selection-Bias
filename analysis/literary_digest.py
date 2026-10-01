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

from style import BLUE, GRAY, INK_2, ORANGE, apply, plt, save

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

    # Simulate polls of increasing size under each design.
    sizes = np.unique(np.logspace(2, 6.4, 25).astype(int))
    reps = 400
    srs_err, digest_err = [], []
    for n in sizes:
        srs = rng.binomial(n, actual_fdr, reps) / n
        dig = rng.binomial(n, resp_fdr_share, reps) / n
        srs_err.append(np.mean(np.abs(srs - actual_fdr)) * 100)
        digest_err.append(np.mean(np.abs(dig - actual_fdr)) * 100)

    apply()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.plot(sizes, srs_err, color=BLUE, lw=2, label="Random sample of voters")
    ax.plot(sizes, digest_err, color=ORANGE, lw=2, label="Digest-style mail poll")
    ax.axvline(n_returned, color=GRAY, lw=1, ls="--")
    ax.text(n_returned * 0.92, 21.2, "2.27M two-party\nballots", ha="right", va="top",
            fontsize=9, color=INK_2)
    ax.axvline(50_000, color=GRAY, lw=1, ls=":")
    ax.text(50_000 * 1.08, 21.2, "Gallup\n~50k", ha="left", va="top", fontsize=9, color=INK_2)
    ax.set_xscale("log")
    ax.set_ylim(0, 22)
    ax.set_xlabel("Poll size (number of responses, log scale)")
    ax.set_ylabel("Average miss on Roosevelt's share (points)")
    ax.set_title("More ballots never fixed the Literary Digest's error")
    ax.legend(loc="center left")
    save(fig, f"{fig_dir}/01_literary_digest.png",
         note="Mail-poll curve: illustrative model calibrated to the Digest's published 43% Roosevelt share. Random-sample curve: exact sampling math.")

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
        "digest_err_at_2_4M_points": round(digest_err[-1], 1),
        "srs_err_at_1500_points": round(
            np.sqrt(actual_fdr * (1 - actual_fdr) / 1500) * np.sqrt(2 / np.pi) * 100, 2),
    }
