#!/usr/bin/env python3
"""Generate a balanced LCG-only scaling set: three tasks at every depth 1–12."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path


A = 7
C = 3
M = 31


def old_starts(paths: list[Path]) -> dict[int, set[int]]:
    starts: dict[int, set[int]] = {depth: set() for depth in range(1, 13)}
    for path in paths:
        if not path.exists():
            continue
        for row in json.loads(path.read_text()):
            if row.get("family") != "lcg_prng":
                continue
            match = re.search(r"Start with x0 = (\d+)\.", row["question"])
            if match:
                starts[row["depth"]].add(int(match.group(1)))
    return starts


def trace_from(x0: int, depth: int) -> list[int]:
    trace = []
    x = x0
    for _ in range(depth):
        x = (A * x + C) % M
        trace.append(x)
    return trace


def make_tasks(seed: int, exclude_paths: list[Path]) -> list[dict]:
    rng = random.Random(seed)
    excluded = old_starts(exclude_paths)
    tasks = []
    for depth in range(1, 13):
        candidates = list(range(M))
        rng.shuffle(candidates)
        selected = []
        for x0 in candidates:
            trace = trace_from(x0, depth)
            # Avoid the previous question at this depth, fixed points, and tasks
            # whose state repeats before the requested number of updates.
            if x0 in excluded[depth] or len({x0, *trace}) != depth + 1:
                continue
            selected.append((x0, trace))
            if len(selected) == 3:
                break
        if len(selected) != 3:
            raise RuntimeError(f"Could not select three non-repeating tasks at depth {depth}")
        for replicate, (x0, trace) in enumerate(selected, 1):
            tasks.append(
                {
                    "id": f"LCG-D{depth:02d}-R{replicate}",
                    "family": "lcg_prng",
                    "depth": depth,
                    "replicate": replicate,
                    "question": (
                        f"PRNG challenge — {depth} hops\n\n"
                        f"Start with x0 = {x0}.\n"
                        f"Use x_(n+1) = ({A}*x_n + {C}) mod {M}.\n\n"
                        f"Apply the recurrence exactly {depth} times. What is x_{depth}?"
                    ),
                    "answer": str(trace[-1]),
                    "trace": trace,
                }
            )

    assert len(tasks) == 36
    assert all(len(row["trace"]) == row["depth"] for row in tasks)
    assert all(str(row["trace"][-1]) == row["answer"] for row in tasks)
    assert all(
        len([row for row in tasks if row["depth"] == depth]) == 3
        for depth in range(1, 13)
    )
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    args = parser.parse_args()
    tasks = make_tasks(args.seed, args.exclude_dataset)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "lcg_depth1_12_3_each.json").write_text(
        json.dumps(tasks, indent=2) + "\n"
    )
    answers = "\n".join(f"{row['id']}\t{row['answer']}" for row in tasks) + "\n"
    (args.outdir / "lcg_depth1_12_3_each_answers.txt").write_text(answers)
    print(f"Generated and verified {len(tasks)} LCG tasks.")


if __name__ == "__main__":
    main()
