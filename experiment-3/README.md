# Set-3: Film-Chain Reasoning

This is the independent 24-question replication. Every question has 15 intended
route edges, and each condition was run once per question.

The four JSON files in `eval/` are public containing the model
identifier, prompt, model answer, target answer, and offline-rescored correctness
value. The exploratory prompt-development runs from the earlier 12-question
collection are not included.

Run `python scripts/make_chart.py` to regenerate the PNG and SVG charts.
