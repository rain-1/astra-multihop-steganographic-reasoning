# Reproducibility index

Audit date: October 13, 2026. GitHub baseline: [`599d8fde3381c1630d91517cce6921808d875a28`](https://github.com/rain-1/astra-multihop-steganographic-reasoning/tree/599d8fde3381c1630d91517cce6921808d875a28).

Publication: [Controllable-CoT leads to covert reasoning capabilities](https://www.lesswrong.com/posts/CPJ2kYRKo77ucZEEG/controllable-cot-leads-to-covert-reasoning-capabilities).

This is an asset audit, not an experimental replication. No model calls were made. File presence, JSON record counts, model identifiers, chart input paths, and existing README descriptions were inspected. Counts below are stored records, not deduplicated runs. [The manifest](reproducibility-manifest.json) records each evaluation file and its hash.

## Coverage

| Published study | Task data / answers | Generators | Public evaluation outputs | Chart scripts / figures | Coverage limitation |
| --- | --- | --- | --- | --- | --- |
| 1: deeper lookup chains | [Deep questions](question%20sets/set1%20lookup-chains%20hops7to12/deep_multistep.json), [answers](question%20sets/set1%20lookup-chains%20hops7to12/deep_multistep_with_answers.txt) | [Deep generator](question%20sets/set1%20lookup-chains%20hops7to12/generate_deep_multistep_tasks.py), [other generator](question%20sets/set1%20lookup-chains%20hops7to12/generate_multistep_tasks.py) | [eval](experiment-1/eval): 5 files, 60 records, 12 per condition | [make_chart.py](experiment-1/scripts/make_chart.py); [figures](experiment-1) | Public final-answer records; private CoT omitted; original inference runner/configuration not present |
| 2: cryptographic operations | [CRC / Mini-hash / LCG questions and answer files](question%20sets/set2%20cryptographic%20operations%20lcg%20depths1to12/) | [CRC/hash/PRNG](question%20sets/set2%20cryptographic%20operations%20lcg%20depths1to12/generate_crc_hash_prng_tasks.py), [scaling](question%20sets/set2%20cryptographic%20operations%20lcg%20depths1to12/generate_crc_hash_scaling_tasks.py), [LCG](question%20sets/set2%20cryptographic%20operations%20lcg%20depths1to12/generate_lcg_tasks.py) | [eval](experiment-2/eval): 31 files, 979 records; tranches described below | [scripts](experiment-2/scripts), [figures](experiment-2) | Article reports 2,509 rollouts across five conditions; GitHub files have four conditions and no identified no-CoT baseline. Exact article-run reconciliation missing |
| 3: film questions | [15-edge questions](question%20sets/set5%20film-chain-reasoning/questions_15edge.json), [answer key](question%20sets/set5%20film-chain-reasoning/answer_key_15edge.json); [earlier questions](question%20sets/set5%20film-chain-reasoning/questions.json), [earlier key](question%20sets/set5%20film-chain-reasoning/answer_key.json) | No film dataset generator identified | [eval](experiment-3/eval): 4 files, 96 records, 24 per condition | [make_chart.py](experiment-3/scripts/make_chart.py); [figures](experiment-3) | Existing README identifies independent 24-question replication and excludes earlier 12-question prompt-development runs. Do not equate it with the exact article figure |
| 4: AMO mathematics | Article names external [AMO-Bench](https://huggingface.co/datasets/meituan-longchat/AMO-Bench); exact evaluated subset not identified | Study-specific selection/preprocessing not found | No identified GitHub outputs | No identified scripts or source figure data | [Specific gaps](experiment-4/README.md); external benchmark is not this study's evaluation output |
| Open-weights evaluations | Article describes control pilot, cryptographic and AMO runs; existing task sets may be relevant, but run-to-task mapping is absent | No identified open-weights runner/configuration | No identified open-weights outputs; all current eval JSON model identifiers are Astra | No identified scripts or source figure data | [Specific gaps](open-weights/README.md) |

## Experiment 2 tranches and chart inputs

The four GitHub conditions are `unrestricted`, `unrelated`, `punctuation`, and `unrelated-punctuation`. The original root evaluation has 72 records. [depths-4-6](experiment-2/eval/depths-4-6) has 27, [lcg-scaled](experiment-2/eval/lcg-scaled) 120, [lcg-scaled-tranche1](experiment-2/eval/lcg-scaled-tranche1) 190, [crc-scaled-tranche1](experiment-2/eval/crc-scaled-tranche1) 190, [crc-scaled-tranche2](experiment-2/eval/crc-scaled-tranche2) 133, [hash-scaled-tranche1](experiment-2/eval/hash-scaled-tranche1) 190, and [hash-easy-tranche1](experiment-2/eval/hash-easy-tranche1) 57.

| Script | Public input selection |
| --- | --- |
| [make_chart.py](experiment-2/scripts/make_chart.py) | Original root `eval/*.json` |
| [make_depth_charts.py](experiment-2/scripts/make_depth_charts.py) | Root evaluation plus `depths-4-6` |
| [make_lcg_scaled_chart.py](experiment-2/scripts/make_lcg_scaled_chart.py) | LCG scaling sets; see script for selection |
| [make_cryptographic_operations_charts.py](experiment-2/scripts/make_cryptographic_operations_charts.py) | LCG scaling sets; CRC/hash scaling tranches plus legacy data selected by family |
| [make_average_instruction_chart.py](experiment-2/scripts/make_average_instruction_chart.py) | Per-family scaling tranches, with legacy records for CRC/hash; alternative summaries |

These selections need not match the article's aggregation. In constrained records, `cheating: true` marks correct visible answers that exposed intermediate computation; charts distinguish these from compliant successes. Missing no-CoT data must not be reconstructed by relabelling `unrelated`.

## Regenerating the existing charts

From the repository root, install the chart dependency in your chosen Python environment:

```bash
python3 -m pip install -r experiment-1/scripts/requirements.txt
python3 experiment-1/scripts/make_chart.py
python3 experiment-2/scripts/make_chart.py
python3 experiment-2/scripts/make_depth_charts.py
python3 experiment-2/scripts/make_lcg_scaled_chart.py
python3 experiment-2/scripts/make_cryptographic_operations_charts.py
python3 experiment-2/scripts/make_average_instruction_chart.py
python3 experiment-3/scripts/make_chart.py
```

All three requirements files currently specify `matplotlib>=3.8`; this is not a pinned historical environment. Scripts write figures into their experiment directories. Regenerating these charts does not rerun model inference. Dataset generators exist for experiments 1–2, but historical seed/CLI provenance must be confirmed before claiming exact regeneration; use committed question files for current chart/data audits.

## Hugging Face and release boundaries

The article links [eac123/astra-multihop-steganographic-reasoning](https://huggingface.co/datasets/eac123/astra-multihop-steganographic-reasoning) as **scrubbed GPT-6 Astra rollouts**. During this audit, browser/search retrieval was inaccessible and the dataset API returned HTTP 401 (authentication required), so direct retrieval did not yield inspectable contents. No dataset revision, file listing, schema, row count, or experiment coverage was verified. This is an access limitation, not evidence that the dataset is empty or that AMO materials are absent there. It also does not establish coverage of open-weights runs.

A future audit should record the dataset revision and per-file schema/counts; map task/run IDs to experiment, condition, and figure; describe exactly which fields were scrubbed; and link only approved public assets. Scrubbed exports cannot be described as complete original rollouts. Do not upload private reasoning traces or infer omitted trace content. Trace-dependent compliance and token analyses need approved per-run annotations or aggregates, definitions, and provenance rather than private trace release.

## Shared information needed for exact reproduction

For each published figure/table, supply a manifest connecting run IDs, task IDs and dataset revisions, conditions, exclusions, and scoring versions. Record exact model/provider identifiers and dates, prompt templates (including message roles), effort and generation settings, token limits, retries and failure handling, and code/environment versions. Retain raw final-answer correctness separately from compliance, visible-answer leakage, missing final answers, and output-limit failures. The article provides several prompt templates, but that does not replace a complete run configuration.

The present gaps are missing **from the audited GitHub main**, unless otherwise stated. They are not claims that the author has no such assets elsewhere. Existing experiments 1–3 remain authoritative public assets and have not been recreated.
