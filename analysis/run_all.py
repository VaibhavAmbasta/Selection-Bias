"""Run every analysis, write figures/ and results/results.json."""
import json
import pathlib

import numpy as np

import birth_weight
import hot_hand
import hrt
import literary_digest
import publication_filter
import wald_bombers

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
OUT = ROOT / "results"


def main(seed=1936):
    FIG.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    results = {}
    for name, mod in [("literary_digest", literary_digest), ("wald_bombers", wald_bombers),
                      ("hrt", hrt), ("hot_hand", hot_hand), ("birth_weight", birth_weight),
                      ("publication_filter", publication_filter)]:
        results[name] = mod.run(str(FIG), np.random.default_rng(seed))
        print(f"== {name}\n{json.dumps(results[name], indent=2)}")
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
