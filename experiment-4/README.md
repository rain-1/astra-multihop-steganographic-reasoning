# Experiment 4: AMO mathematics — reproducibility status

[Published study](https://www.lesswrong.com/posts/CPJ2kYRKo77ucZEEG/controllable-cot-leads-to-covert-reasoning-capabilities) · [Full asset index](../REPRODUCIBILITY.md)

The article reports evaluating GPT-6 Astra on challenging mathematics questions from [meituan-longchat/AMO-Bench](https://huggingface.co/datasets/meituan-longchat/AMO-Bench) under controlled reasoning instructions, including word-suppression compliance and token-frequency analysis. This directory documents asset status; it contains no new evaluations or reproduced results.

## Available references

- External benchmark link above; its exact revision and study-selected questions have not been verified here.
- Article descriptions, prompt appendix, and rendered figures.
- Article-linked [scrubbed Astra dataset](https://huggingface.co/datasets/eac123/astra-multihop-steganographic-reasoning). Contents and AMO coverage were inaccessible in the October 13, 2026 audit.

## Missing from the audited GitHub main

| Asset | Information needed to reproduce the published result |
| --- | --- |
| Selected dataset / answer key | Benchmark revision, split, exact question IDs, ordering, sampling seed, preprocessing, reference answers, and any permitted public question export |
| Inference configuration | Exact model/provider/version/date, system and user templates, full condition list and forbidden-word list, effort, sampling, token limits, repetitions, retry policy, and runnable driver |
| Public evaluation records | Task/run IDs, condition, final answer, correctness, compliance annotations, usage metadata, and explicit output-limit/missing-answer status, without private reasoning |
| Scoring and compliance code | Math answer extraction/equivalence rules, grader/version, treatment of failures, definition of strict word suppression, matching/tokenization/case rules, and annotation provenance |
| Figure inputs / scripts | Approved per-run metrics or aggregate counts, denominators, exclusions, figure-to-run mapping, scripts for accuracy/compliance and regular-versus-suppressed token counts |

Historical trace-dependent analyses may remain unavailable for independent rechecking without an approved scrubbed export or derived annotations. Do not fill gaps with synthetic results or release private reasoning. If existing approved assets become accessible, add them with provenance and update this status rather than rerunning and presenting a new experiment as the original.
