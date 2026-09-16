#!/usr/bin/env python3
"""Plot success rate by task depth for each cryptographic operation."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = [
    ("Unrelated", "unrelated.json", "#D88FA8", "o"),
    ("Punctuation", "punctuation.json", "#D99A45", "s"),
    (
        "Unrelated + Punctuation",
        "unrelated-punctuation.json",
        "#66A997",
        "^",
    ),
]
FAMILIES = [
    ("toy_crc4", "CRC-4"),
    ("mini_hash", "Mini-hash"),
    ("lcg_prng", "LCG PRNG"),
]


def records(filename: str) -> list[dict]:
    shallow = json.loads((ROOT / "eval" / "depths-4-6" / filename).read_text())
    deep = json.loads((ROOT / "eval" / filename).read_text())
    return shallow + deep


def plot_family(axis, family: str) -> None:
    for condition, filename, color, marker in CONDITIONS:
        grouped: dict[int, list[bool]] = defaultdict(list)
        for record in records(filename):
            if record["family"] == family:
                grouped[record["depth"]].append(record["correct"])
        depths = sorted(grouped)
        rates = [100 * sum(grouped[d]) / len(grouped[d]) for d in depths]
        axis.plot(
            depths,
            rates,
            label=condition,
            color=color,
            marker=marker,
            markersize=7,
            markeredgecolor="#46515A",
            markeredgewidth=0.8,
            linewidth=2.2,
        )


def style_axis(axis) -> None:
    axis.set_xlim(3.7, 12.3)
    axis.set_xticks(range(4, 13))
    axis.set_ylim(-5, 105)
    axis.set_yticks(range(0, 101, 20))
    axis.yaxis.set_major_formatter(PercentFormatter(100))
    axis.set_xlabel("Task Depth")
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#CBD0D3")
    axis.grid(axis="y", color="#DDE1E3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", length=0)


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    for family, family_label in FAMILIES:
        figure, axis = plt.subplots(figsize=(9, 5.8), facecolor="#FAFAF8")
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family)
        style_axis(axis)
        axis.set_ylabel("Success Rate")
        axis.set_title(
            f"{family_label} Success by Task Depth",
            loc="left",
            fontsize=17,
            fontweight="bold",
            pad=18,
        )
        axis.legend(frameon=False, loc="upper right")
        figure.text(
            0.5,
            0.01,
            "Each point represents one task (n=1).",
            ha="center",
            color="#68727A",
            fontsize=9.5,
        )
        figure.tight_layout(rect=(0, 0.04, 1, 1), pad=2)
        stem = f"success-by-depth-{family.replace('_', '-')}"
        figure.savefig(ROOT / f"{stem}.svg", bbox_inches="tight")
        figure.savefig(ROOT / f"{stem}.png", dpi=220, bbox_inches="tight")
        plt.close(figure)

    figure, axes = plt.subplots(
        1,
        3,
        figsize=(18, 5.5),
        sharey=True,
        facecolor="#FAFAF8",
    )
    for axis, (family, family_label) in zip(axes, FAMILIES):
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family)
        style_axis(axis)
        axis.set_title(family_label, fontsize=15, fontweight="bold", pad=14)
    axes[0].set_ylabel("Success Rate")
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=False,
    )
    figure.text(
        0.5,
        0.01,
        "Each point represents one task (n=1).",
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.92), pad=2)
    figure.savefig(ROOT / "success-by-depth-combined.svg", bbox_inches="tight")
    figure.savefig(ROOT / "success-by-depth-combined.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
