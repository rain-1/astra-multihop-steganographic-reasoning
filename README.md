# Controllable-CoT leads to covert reasoning capabilities

Research materials accompanying [Edward Cant's published article](https://www.lesswrong.com/posts/CPJ2kYRKo77ucZEEG/controllable-cot-leads-to-covert-reasoning-capabilities) (September 22, 2026).

Start with the **[experiment-by-experiment reproducibility index](REPRODUCIBILITY.md)** for datasets, generators, public evaluation outputs, chart scripts, and known gaps.

## Available materials

- [Experiment 1: lookup chains](experiment-1/README.md)
- [Experiment 2: cryptographic operations](experiment-2/README.md)
- [Experiment 3: film-chain reasoning — independent replication](experiment-3/README.md)
- [Experiment 4: AMO mathematics — asset status and reproduction gaps](experiment-4/README.md)
- [Open-weights evaluations — asset status and reproduction gaps](open-weights/README.md)
- [File inventory](reproducibility-manifest.json): audited public evaluation paths, record counts, and SHA-256 hashes.

The article also links [scrubbed GPT-6 Astra rollouts on Hugging Face](https://huggingface.co/datasets/eac123/astra-multihop-steganographic-reasoning). Their contents could not be inspected in the October 13, 2026 audit; experiment coverage is unverified. Scrubbed outputs are not complete original rollouts.

## Reproduction scope and trace release

The existing scripts regenerate charts from public evaluation records; they do not rerun model inference or establish an exact reconstruction of every published figure. Experiments 1–3 and their original assets are preserved. The new experiment-4 and open-weights directories document gaps, not new results.

Private reasoning traces remain excluded. Reproduction metadata, final answers, aggregate metrics, and approved scrubbed exports should be released separately from private reasoning. No private traces are required to fill the documentation gaps listed in the index.
