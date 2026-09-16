# Set-2: Cryptographic Operations

This directory contains the public evaluation datasets, dataset generators,
chart generators, and rendered charts for the cryptographic-operations
experiments.

## Evaluation data

- `eval/` contains the original depth-7–12 results.
- `eval/depths-4-6/` contains the easier depth-4–6 results.
- `eval/lcg-scaled/` contains the first balanced LCG scaling set.
- `eval/lcg-scaled-tranche1/` contains the subsequent LCG expansion.

Each evaluation JSON record contains the model identifier, prompt, model
answer, target answer, and correctness value.

The corresponding generated question datasets and answer keys are in
`../question sets/set2 cryptographic operations lcg depths1to12/`.

## Charts

Run the scripts from the repository root:

```bash
python3 experiment-2/scripts/make_chart.py
python3 experiment-2/scripts/make_depth_charts.py
python3 experiment-2/scripts/make_lcg_scaled_chart.py
```

`make_crc_hash_scaled_charts.py` generates the expanded CRC-4 and Mini-hash
charts after their public evaluation JSON files are present.
