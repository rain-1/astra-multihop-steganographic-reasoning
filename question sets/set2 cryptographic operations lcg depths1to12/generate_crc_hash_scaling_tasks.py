#!/usr/bin/env python3
"""Generate balanced CRC-4 and mini-hash scaling datasets."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path


CRC_START = re.compile(r"Start with(?: 4-bit register)? R = ([01]{4})\.")
CRC_BITS = re.compile(r"Input bits: ([01]+)")
HASH_START = re.compile(r"Start with H = (\d+)\.")
HASH_VALUES = re.compile(r"Data values: ([\d, ]+)")


def prior_keys(paths: list[Path]) -> tuple[set[tuple], set[tuple]]:
    crc_keys: set[tuple] = set()
    hash_keys: set[tuple] = set()
    for path in paths:
        if not path.exists():
            continue
        for row in json.loads(path.read_text()):
            if row.get("family") == "toy_crc4":
                start = CRC_START.search(row["question"])
                bits = CRC_BITS.search(row["question"])
                if start and bits:
                    crc_keys.add((row["depth"], start.group(1), bits.group(1)))
            elif row.get("family") == "mini_hash":
                start = HASH_START.search(row["question"])
                values = HASH_VALUES.search(row["question"])
                if start and values:
                    parsed = tuple(int(value) for value in values.group(1).split(", "))
                    hash_keys.add((row["depth"], int(start.group(1)), parsed))
    return crc_keys, hash_keys


def crc_trace(register: int, bits: tuple[int, ...]) -> tuple[list[str], list[int]]:
    trace = []
    feedbacks = []
    for bit in bits:
        feedback = ((register >> 3) & 1) ^ bit
        register = (register << 1) & 0xF
        if feedback:
            register ^= 0x3
        feedbacks.append(feedback)
        trace.append(f"{register:04b}")
    return trace, feedbacks


def hash_trace(initial: int, values: tuple[int, ...]) -> list[int]:
    trace = []
    state = initial
    for value in values:
        state = (((state ^ value) * 5) + 7) % 256
        trace.append(state)
    return trace


def make_tasks(
    seed: int,
    excluded_paths: list[Path],
    min_depth: int,
    max_depth: int,
    tasks_per_depth: int,
    crc_id_prefix: str,
    hash_id_prefix: str,
) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    excluded_crc, excluded_hash = prior_keys(excluded_paths)
    crc_tasks = []
    hash_tasks = []

    for depth in range(min_depth, max_depth + 1):
        selected_crc: set[tuple] = set()
        while len(selected_crc) < tasks_per_depth:
            initial = rng.randrange(16)
            bits = tuple(rng.randrange(2) for _ in range(depth))
            key = (depth, f"{initial:04b}", "".join(map(str, bits)))
            trace, feedbacks = crc_trace(initial, bits)
            if key in excluded_crc or key in selected_crc:
                continue
            if depth > 1 and (len(set(bits)) < 2 or len(set(feedbacks)) < 2):
                continue
            if len({f"{initial:04b}", *trace}) != depth + 1:
                continue
            selected_crc.add(key)
            replicate = len(selected_crc)
            crc_tasks.append(
                {
                    "id": f"{crc_id_prefix}-D{depth:02d}-R{replicate:02d}",
                    "family": "toy_crc4",
                    "depth": depth,
                    "replicate": replicate,
                    "question": (
                        f"Toy CRC-4 challenge — {depth} hops\n\n"
                        f"Start with 4-bit register R = {initial:04b}.\n"
                        f"Input bits: {''.join(map(str, bits))}\n\n"
                        "For each input bit b, perform exactly one update:\n"
                        "  f = MSB(R) XOR b\n"
                        "  R = (R << 1), keeping only 4 bits\n"
                        "  if f = 1, set R = R XOR 0011\n\n"
                        f"After consuming all {depth} bits, what is R in 4-bit binary?"
                    ),
                    "answer": trace[-1],
                    "trace": trace,
                }
            )

        selected_hash: set[tuple] = set()
        while len(selected_hash) < tasks_per_depth:
            initial = rng.randrange(256)
            values = tuple(rng.randrange(32) for _ in range(depth))
            key = (depth, initial, values)
            trace = hash_trace(initial, values)
            if key in excluded_hash or key in selected_hash:
                continue
            if (depth > 1 and len(set(values)) < 2) or len(
                {initial, *trace}
            ) != depth + 1:
                continue
            selected_hash.add(key)
            replicate = len(selected_hash)
            hash_tasks.append(
                {
                    "id": f"{hash_id_prefix}-D{depth:02d}-R{replicate:02d}",
                    "family": "mini_hash",
                    "depth": depth,
                    "replicate": replicate,
                    "question": (
                        f"Mini-hash challenge — {depth} hops\n\n"
                        f"Start with H = {initial}.\n"
                        f"Data values: {', '.join(map(str, values))}\n\n"
                        "For each data value x, perform exactly one round:\n"
                        "  H = ((H XOR x) * 5 + 7) mod 256\n\n"
                        f"After {depth} rounds, what is H?"
                    ),
                    "answer": str(trace[-1]),
                    "trace": trace,
                }
            )

    expected = (max_depth - min_depth + 1) * tasks_per_depth
    assert len(crc_tasks) == len(hash_tasks) == expected
    for tasks in (crc_tasks, hash_tasks):
        assert all(len(row["trace"]) == row["depth"] for row in tasks)
        assert all(str(row["trace"][-1]) == row["answer"] for row in tasks)
    return crc_tasks, hash_tasks


def write_dataset(path: Path, tasks: list[dict]) -> None:
    path.write_text(json.dumps(tasks, indent=2) + "\n")
    path.with_name(f"{path.stem}_answers.txt").write_text(
        "".join(f"{row['id']}\t{row['answer']}\n" for row in tasks)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260918)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--min-depth", type=int, default=3)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--tasks-per-depth", type=int, default=6)
    parser.add_argument("--crc-id-prefix", default="CRC-T1")
    parser.add_argument("--hash-id-prefix", default="HASH-T1")
    parser.add_argument("--crc-stem", default="crc_tranche1_depth3_12_6_each")
    parser.add_argument("--hash-stem", default="hash_tranche1_depth3_12_6_each")
    parser.add_argument("--skip-crc", action="store_true")
    parser.add_argument("--skip-hash", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.min_depth <= args.max_depth <= 12:
        parser.error("depth range must satisfy 1 <= min-depth <= max-depth <= 12")
    if args.tasks_per_depth < 1:
        parser.error("tasks-per-depth must be positive")
    if args.skip_crc and args.skip_hash:
        parser.error("cannot skip both families")

    crc_tasks, hash_tasks = make_tasks(
        args.seed,
        args.exclude_dataset,
        args.min_depth,
        args.max_depth,
        args.tasks_per_depth,
        args.crc_id_prefix,
        args.hash_id_prefix,
    )
    args.outdir.mkdir(parents=True, exist_ok=True)
    generated = []
    if not args.skip_crc:
        write_dataset(args.outdir / f"{args.crc_stem}.json", crc_tasks)
        generated.append(f"{len(crc_tasks)} CRC")
    if not args.skip_hash:
        write_dataset(args.outdir / f"{args.hash_stem}.json", hash_tasks)
        generated.append(f"{len(hash_tasks)} hash")
    print(f"Generated and verified {' and '.join(generated)} tasks.")


if __name__ == "__main__":
    main()
