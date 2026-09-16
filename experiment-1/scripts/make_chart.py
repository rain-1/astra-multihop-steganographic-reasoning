#!/usr/bin/env python3
"""Render the Experiment 1 comparison chart from the five public JSON files."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = [
    ("unrestricted.json", "Unrestricted"),
    ("dots.json", "Dots"),
    ("unrelated.json", "Unrelated"),
    ("punctuation.json", "Punctuation"),
    ("scenes-punctuation.json", "Unrelated + Punctuation"),
]


def main() -> None:
    labels = []
    values = []
    for filename, label in CONDITIONS:
        records = json.loads((ROOT / "eval" / filename).read_text())
        labels.append(label)
        values.append(sum(record["correct"] for record in records))

    colors = ["#B8D8E8", "#D9D5EC", "#F2D1DC", "#F6D6AD", "#BFDCC7"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    figure, axis = plt.subplots(figsize=(11, 5.8), facecolor="#FAFAF8")
    axis.set_facecolor("#FAFAF8")
    axis.bar(
        labels,
        values,
        width=0.78,
        color=colors,
        edgecolor="#46515A",
        linewidth=1.25,
    )
    axis.set_ylim(0, 12.8)
    axis.set_yticks(range(0, 13, 2))
    axis.set_ylabel("Correct Answers")
    axis.set_title(
        "Set-1: Lookup Chains", loc="left", fontsize=17, fontweight="bold", pad=18
    )
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#CBD0D3")
    axis.grid(axis="y", color="#DDE1E3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="y", length=0, colors="#5D6770")
    axis.tick_params(axis="x", length=0, pad=9)
    figure.tight_layout(pad=2)
    figure.savefig(ROOT / "lookup-chain-comparison.svg", bbox_inches="tight")
    figure.savefig(ROOT / "lookup-chain-comparison.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
