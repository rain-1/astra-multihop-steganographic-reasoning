#!/usr/bin/env python3
"""Generate balanced, non-overlapping LCG-only scaling datasets."""

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


def make_tasks(
    seed: int,
    exclude_paths: list[Path],
    min_depth: int,
    max_depth: int,
    tasks_per_depth: int,
    id_prefix: str,
    replicate_width: int,
) -> list[dict]:
    rng = random.Random(seed)
    excluded = old_starts(exclude_paths)
    tasks = []
    for depth in range(min_depth, max_depth + 1):
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
            if len(selected) == tasks_per_depth:
                break
        if len(selected) != tasks_per_depth:
            raise RuntimeError(
                f"Could not select {tasks_per_depth} non-repeating tasks at depth {depth}"
            )
        for replicate, (x0, trace) in enumerate(selected, 1):
            replicate_id = (
                f"{replicate:0{replicate_width}d}"
                if replicate_width
                else str(replicate)
            )
            tasks.append(
                {
                    "id": f"{id_prefix}-D{depth:02d}-R{replicate_id}",
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

    assert len(tasks) == (max_depth - min_depth + 1) * tasks_per_depth
    assert all(len(row["trace"]) == row["depth"] for row in tasks)
    assert all(str(row["trace"][-1]) == row["answer"] for row in tasks)
    assert all(
        len([row for row in tasks if row["depth"] == depth]) == tasks_per_depth
        for depth in range(min_depth, max_depth + 1)
    )
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--min-depth", type=int, default=1)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--tasks-per-depth", type=int, default=3)
    parser.add_argument("--id-prefix", default="LCG")
    parser.add_argument("--replicate-width", type=int, default=0)
    parser.add_argument("--output-stem", default="lcg_depth1_12_3_each")
    args = parser.parse_args()
    if not 1 <= args.min_depth <= args.max_depth <= 12:
        parser.error("depth range must satisfy 1 <= min-depth <= max-depth <= 12")
    if args.tasks_per_depth < 1:
        parser.error("tasks-per-depth must be positive")
    if args.replicate_width < 0:
        parser.error("replicate-width cannot be negative")
    tasks = make_tasks(
        args.seed,
        args.exclude_dataset,
        args.min_depth,
        args.max_depth,
        args.tasks_per_depth,
        args.id_prefix,
        args.replicate_width,
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / f"{args.output_stem}.json").write_text(
        json.dumps(tasks, indent=2) + "\n"
    )
    answers = "\n".join(f"{row['id']}\t{row['answer']}" for row in tasks) + "\n"
    (args.outdir / f"{args.output_stem}_answers.txt").write_text(answers)
    print(f"Generated and verified {len(tasks)} LCG tasks.")


if __name__ == "__main__":
    main()
