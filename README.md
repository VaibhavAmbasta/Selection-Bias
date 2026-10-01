# Selection Bias in Famous Studies

The code and charts behind a Substack post: **"The Data Was Lying About Who It Left Out."**

The post looks at six well-known studies, from WWII bombers to basketball's "hot hand." In each one the data was filtered before anyone analysed it, and that filter led smart people to the wrong answer. This repo re-runs each case in Python, so every number and chart in the post can be checked.

## What is selection bias?

Selection bias happens when the people or things in your data aren't a fair picture of the group you care about, because of *how they got into your data*. Collecting more of the same data doesn't fix it.

## The six cases

| # | Study | What filtered the data | What the code shows | Real or simulated |
|---|---|---|---|---|
| 1 | WWII bombers (Wald, 1943) | Only planes that came home could be inspected | Returning planes show less than half the engine damage that really happened; Wald's method recovers the truth | Simulated |
| 2 | Literary Digest poll (1936) | Who got a ballot, and who sent it back | 2.3 million skewed ballots were as accurate as asking about 6 random voters | Real vote counts + exact maths |
| 3 | Hormone replacement therapy (1980s–2002) | Healthier women chose to take HRT | A drug set to *raise* heart risk by 24% looks like it *cuts* it by 45% | Real published results + simulation |
| 4 | Birth-weight paradox (1971–2006) | Looking only at small babies | Smoking harms every baby in the model, yet appears protective among small babies | Exact calculation from an assumed model |
| 5 | Psychology replication project (2015) | Journals publish the "significant" results | Of 1,000 studies run, 74 get published and 29 replicate; effects look twice as big as they are | Real results + simulation |
| 6 | The hot hand (1985 → 2018) | Picking out only the shots that follow a streak | A purely random shooter looks 8 points colder after streaks | Exact maths + simulation |

## Run it

```bash
pip install -r requirements.txt
python analysis/run_all.py
```

This regenerates `figures/*.png` and `results/results.json`. Random seeds are fixed, so the output is identical every run.

## Repo layout

```
analysis/              one Python file per case, plus run_all.py
  style.py             shared chart styling
  wald_bombers.py      survivorship bias
  literary_digest.py   nonresponse and sampling-frame bias
  hrt.py               healthy-user self-selection
  birth_weight.py      collider bias (selecting on an outcome)
  publication_filter.py  publication bias
  hot_hand.py          streak-selection bias
figures/               charts used in the post
results/results.json   every number quoted in the post
post/substack_draft.md the post, with sources
```

Each analysis file starts with a short note listing which inputs are published facts and which are assumptions chosen for the simulation.

## Sources

Full references are at the end of `post/substack_draft.md`. Key ones: Mangel & Samaniego (1984); Squire (1988); Lohr & Brick (2017); WHI Writing Group (2002); Manson et al. (2003); Hernández-Díaz, Schisterman & Hernán (2006); Open Science Collaboration (2015); Gilovich, Vallone & Tversky (1985); Miller & Sanjurjo (2018).
