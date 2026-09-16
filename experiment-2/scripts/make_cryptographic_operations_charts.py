#!/usr/bin/env python3
"""Plot the expanded cryptographic-operation results by task depth."""

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
    (
        "toy_crc4",
        "Toy CRC-4",
        ("crc-scaled-tranche1", "crc-scaled-tranche2"),
        "crc-scaled-success-by-depth",
        3,
        (
            "Samples per depth (unrestricted/constrained): d3 1/6; d4 1/7; "
            "d5–6 2/13; d7–11 3/13; d12 2/7."
        ),
    ),
    (
        "mini_hash",
        "Mini-hash",
        ("hash-scaled-tranche1", "hash-easy-tranche1"),
        "hash-scaled-success-by-depth",
        1,
        (
            "Samples per depth (unrestricted/constrained): d1–2 1/6; d3 2/12; "
            "d4–6 1/7; d7–12 2/7."
        ),
    ),
]
COMBINED_FAMILIES = [
    (
        "lcg_prng",
        "LCG PRNG",
        ("lcg-scaled", "lcg-scaled-tranche1"),
        1,
        False,
    ),
    *[
        (family, label, scaled_dirs, min_depth, True)
        for family, label, scaled_dirs, _, min_depth, _ in FAMILIES
    ],
]


def has_complete_scaled_data(scaled_dirs: tuple[str, ...]) -> bool:
    return all(
        (ROOT / "eval" / scaled_dir / filename).exists()
        for scaled_dir in scaled_dirs
        for filename, *_ in CONDITIONS
    )


def records(
    filename: str,
    scaled_dirs: tuple[str, ...],
    include_legacy: bool,
) -> list[dict]:
    paths = [ROOT / "eval" / scaled_dir / filename for scaled_dir in scaled_dirs]
    if include_legacy:
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


def plot_family(
    axis,
    family: str,
    scaled_dirs: tuple[str, ...],
    include_legacy: bool,
) -> None:
    for filename, label, color, marker in CONDITIONS:
        grouped: dict[int, list[bool]] = defaultdict(list)
        for record in records(filename, scaled_dirs, include_legacy):
            if record["family"] == family:
                grouped[record["depth"]].append(
                    record["correct"] and not record.get("cheating", False)
                )
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


def style_axis(axis, min_depth: int) -> None:
    axis.set_xlim(min_depth - 0.3, 12.3)
    axis.set_xticks(range(min_depth, 13))
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
    for family, label, scaled_dirs, stem, min_depth, note in available:
        figure, axis = plt.subplots(figsize=(10.5, 6), facecolor="#FAFAF8")
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family, scaled_dirs, include_legacy=True)
        style_axis(axis, min_depth)
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

    if not all(has_complete_scaled_data(family[2]) for family in COMBINED_FAMILIES):
        return

    figure, axes = plt.subplots(
        1,
        3,
        figsize=(18, 5.8),
        sharey=True,
        facecolor="#FAFAF8",
    )
    for axis, (family, label, scaled_dirs, min_depth, include_legacy) in zip(
        axes, COMBINED_FAMILIES
    ):
        axis.set_facecolor("#FAFAF8")
        plot_family(axis, family, scaled_dirs, include_legacy)
        style_axis(axis, min_depth)
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
    figure.text(
        0.5,
        0.01,
        "Sample sizes vary by family and depth; see individual charts.",
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.92), pad=2)
    figure.savefig(
        ROOT / "cryptographic-operations-scaled-combined.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(
        ROOT / "cryptographic-operations-scaled-combined.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
