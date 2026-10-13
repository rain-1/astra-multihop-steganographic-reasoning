# Open-weights evaluations — reproducibility status

[Published study](https://www.lesswrong.com/posts/CPJ2kYRKo77ucZEEG/controllable-cot-leads-to-covert-reasoning-capabilities) · [Full asset index](../REPRODUCIBILITY.md)

The article describes a low-sample CoT-control pilot, Kimi K3 cryptographic and AMO evaluations, and further low-effort/output-block elicitation. It mentions Qwen3-235B and Deepseek 4.1 Flash, among other pilot models. These publication labels do not establish exact provider model IDs or checkpoint revisions. The complete pilot roster and run configurations still need identification.

This directory contains documentation only. No open-weights experiments were run in this audit, and none are claimed reproduced.

## Available references

The article contains descriptions, figures, selected examples, and some prompts. Existing [cryptographic task assets](../question%20sets/set2%20cryptographic%20operations%20lcg%20depths1to12/) and external [AMO-Bench](https://huggingface.co/datasets/meituan-longchat/AMO-Bench) are candidate task sources, but their exact use in each open-weights run is not mapped. The linked Hugging Face release is described as scrubbed **Astra** rollouts; its contents could not be inspected and open-weights coverage is unverified.

## Missing from the audited GitHub main

| Evaluation group | Required public assets / metadata |
| --- | --- |
| Low-sample control pilot | Full model roster and exact model/provider/checkpoint IDs; selected tasks; all condition templates; sample counts; correctness/compliance records and figure scripts |
| Kimi cryptographic evaluations | Exact task IDs and repeats, high-effort settings, language/punctuation prompts, final-answer records, failure states, compliance definitions, and chart aggregation |
| Kimi AMO high-effort runs | Exact 53-run manifest, selected questions and conditions, token limits, final-answer extraction, scoring and output-limit handling; article-reported counts need supporting records |
| Low-effort/output-block follow-ups | Exact prompt versions including mixed-case elicitation, tasks, effort/settings, separation of reasoning-block and output-block compliance, and run-level results; identify the article's 15 AMO examples |
| All groups | Runnable inference/evaluation driver, dependency versions, provider chat formatting and reasoning-channel handling, dates, retries, usage metadata, scorer versions, exclusions, and figure-to-run mapping |

Correctness, instruction compliance, output-limit termination, and missing final answers must remain separate fields. A model failing to answer before its output limit should not be silently treated as an ordinary completed incorrect answer in every metric. Record each published metric's denominator and failure policy.

Add existing approved final-answer records, metadata, annotations, aggregates and chart code when located. Do not release private reasoning traces, fabricate historical outputs, or substitute new pilot runs for the reported study. Exact trace-dependent rechecking requires an approved export or derived annotations whose limitations are stated.
