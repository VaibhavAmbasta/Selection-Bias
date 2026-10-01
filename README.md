# Selection Bias in Famous Studies

Reproducible code behind a Substack post on six well-known cases where the sample chose itself.

| # | Case | Type | What's real vs simulated |
|---|---|---|---|
| 1 | Literary Digest poll, 1936 | Frame + nonresponse bias | Vote counts real; mail-poll mechanism calibrated |
| 2 | Wald's WWII bombers | Survivorship bias | Fully simulated; Wald correction applied |
| 3 | Hormone replacement therapy | Self-selection (healthy-user) | True effect set to WHI's 1.24; uptake model assumed |
| 4 | Hot hand (GVT 1985) | Streak-selection bias | Exact enumeration + Monte Carlo, no assumptions beyond a fair coin |
| 5 | Low-birth-weight paradox | Collider / selection on outcome | Exact calculation from an assumed causal model |
| 6 | Replication crisis (OSC 2015) | Publication filter | Simulated; calibrated to land near OSC's 36% / ~50% |

## Run

```bash
pip install -r requirements.txt
python analysis/run_all.py
```

This writes `figures/*.png` and `results/results.json`. Seeded, so the output is deterministic.

## Layout

- `analysis/`: one module per case plus `run_all.py`. Each module's docstring lists the published anchors and the assumed parameters.
- `figures/`: charts used in the post.
- `results/results.json`: every number quoted in the post.
- `post/substack_draft.md`: the draft post.
