#!/usr/bin/env python3
"""Plot the expanded CRC-4 and mini-hash results by task depth."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = [
    ("unrestricted.json", "Unrestricted", "#79AEC8", "D"),
    ("unrelated.json", "Unrelated", "#D88FA8", "o"),
    ("punctuation.json", "Punctuation", "#D99A45", "s"),
    (
        "unrelated-punctuation.json",
        "Unrelated + Punctuation",
        "#66A997",
        "^",
    ),
]
FAMILIES = [
    ("toy_crc4", "Toy CRC-4", "crc-scaled-tranche1", "crc-scaled-success-by-depth"),
    ("mini_hash", "Mini-hash", "hash-scaled-tranche1", "hash-scaled-success-by-depth"),
]


def has_complete_scaled_data(scaled_dir: str) -> bool:
    directory = ROOT / "eval" / scaled_dir
    return all((directory / filename).exists() for filename, *_ in CONDITIONS)


def records(filename: str, scaled_dir: str) -> list[dict]:
    paths = [ROOT / "eval" / scaled_dir / filename]
    if filename == "unrestricted.json":
        paths.append(ROOT / "eval" / filename)
    else:
        paths.extend(
            [
                ROOT / "eval" / "depths-4-6" / filename,
                ROOT / "eval" / filename,
            ]
        )
    rows = []
    for path in paths:
        if path.exists():
            rows.extend(json.loads(path.read_text()))
    return rows


def plot_family(axis, family: str, scaled_dir: str) -> None:
    for filename, label, color, marker in CONDITIONS:
        grouped: dict[int, list[bool]] = defaultdict(list)
        for record in records(filename, scaled_dir):
            if record["family"] == family:
                grouped[record["depth"]].append(record["correct"])
        depths = sorted(grouped)
        rates = [100 * sum(grouped[depth]) / len(grouped[depth]) for depth in depths]
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


def style_axis(axis) -> None:
    axis.set_xlim(2.7, 12.3)
    axis.set_xticks(range(3, 13))
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
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "svg.hashsalt": "goodhart-cryptographic-operations",
        }
    )
    available = [family for family in FAMILIES if has_complete_scaled_data(family[2])]
    if not available:
        raise FileNotFoundError("no complete expanded CRC/hash evaluation is available")
    note = (
        "Depth 3: n=1 unrestricted and n=6 per constrained condition. "
        "Depths 4–6: n=1 and n=7; depths 7–12: n=2 and n=7, respectively."
    )
    for family, label, scaled_dir, stem in available:
        figure, axis = plt.subplots(figsize=(10.5, 6), facecolor="#FAFAF8")
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family, scaled_dir)
        style_axis(axis)
        axis.set_ylabel("Success Rate")
        axis.set_title(label, loc="left", fontsize=17, fontweight="bold", pad=18)
        axis.legend(
            frameon=False,
            loc="lower right",
            bbox_to_anchor=(1, 1.01),
            ncol=2,
        )
        figure.text(0.5, 0.01, note, ha="center", color="#68727A", fontsize=9.5)
        figure.tight_layout(rect=(0, 0.04, 1, 1), pad=2)
        figure.savefig(
            ROOT / f"{stem}.svg",
            bbox_inches="tight",
            metadata={"Date": None},
        )
        figure.savefig(ROOT / f"{stem}.png", dpi=220, bbox_inches="tight")
        plt.close(figure)

    if len(available) != len(FAMILIES):
        return

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(14, 5.8),
        sharey=True,
        facecolor="#FAFAF8",
    )
    for axis, (family, label, scaled_dir, _) in zip(axes, available):
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family, scaled_dir)
        style_axis(axis)
        axis.set_title(label, fontsize=15, fontweight="bold", pad=14)
    axes[0].set_ylabel("Success Rate")
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=4,
        frameon=False,
    )
    figure.text(0.5, 0.01, note, ha="center", color="#68727A", fontsize=9.5)
    figure.tight_layout(rect=(0, 0.05, 1, 0.92), pad=2)
    figure.savefig(
        ROOT / "crc-hash-scaled-combined.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(ROOT / "crc-hash-scaled-combined.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    main()
