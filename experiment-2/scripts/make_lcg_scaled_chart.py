#!/usr/bin/env python3
"""Plot the scaled LCG batch results by task depth."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIRS = [
    ROOT / "eval" / "lcg-scaled",
    ROOT / "eval" / "lcg-scaled-tranche1",
]
CONDITIONS = [
    ("unrestricted.json", "Unrestricted", "#79AEC8", "D"),
    ("unrelated.json", "Unrelated", "#D88FA8", "o"),
    ("punctuation.json", "Punctuation", "#D99A45", "s"),
    ("unrelated-punctuation.json", "Unrelated + Punctuation", "#66A997", "^"),
]


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    figure, axis = plt.subplots(figsize=(10.5, 6), facecolor="#FAFAF8")
    axis.set_facecolor("#FAFAF8")
    for filename, label, color, marker in CONDITIONS:
        grouped: dict[int, list[bool]] = defaultdict(list)
        for eval_dir in EVAL_DIRS:
            path = eval_dir / filename
            if not path.exists():
                continue
            for record in json.loads(path.read_text()):
                grouped[record["depth"]].append(
                    record["correct"] and not record.get("cheating", False)
                )
        depths = sorted(grouped)
        rates = [100 * sum(grouped[d]) / len(grouped[d]) for d in depths]
        axis.plot(
            depths,
            rates,
            label=label,
            color=color,
            marker=marker,
            markersize=7,
            markeredgecolor="#46515A",
            markeredgewidth=0.8,
            linewidth=2.2,
        )

    axis.set_xlim(0.7, 12.3)
    axis.set_xticks(range(1, 13))
    axis.set_ylim(-5, 105)
    axis.set_yticks(range(0, 101, 20))
    axis.yaxis.set_major_formatter(PercentFormatter(100))
    axis.set_xlabel("Task Depth")
    axis.set_ylabel("Success Rate")
    axis.set_title(
        "LCG PRNG Success by Task Depth",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#CBD0D3")
    axis.grid(axis="y", color="#DDE1E3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", length=0)
    axis.legend(
        frameon=False,
        loc="lower right",
        bbox_to_anchor=(1, 1.01),
        ncol=2,
    )
    figure.text(
        0.5,
        0.01,
        (
            "Depths 1–2: n=1 unrestricted and n=3 per constrained condition. "
            "Depths 3–12: n=2 and n=9, respectively."
        ),
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.04, 1, 1), pad=2)
    figure.savefig(ROOT / "lcg-scaled-success-by-depth.svg", bbox_inches="tight")
    figure.savefig(ROOT / "lcg-scaled-success-by-depth.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
