#!/usr/bin/env python3
"""Plot average state-update performance by thinking instruction."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
ALL_CONDITIONS = [
    ("unrestricted.json", "Unrestricted", "#9CC7DC"),
    ("unrelated.json", "Unrelated", "#E7A9BD"),
    ("punctuation.json", "Punctuation", "#F1BE72"),
    (
        "unrelated-punctuation.json",
        "Unrelated + Punctuation",
        "#8BC5B3",
    ),
]
FAMILIES = [
    ("lcg_prng", "LCG PRNG", ("lcg-scaled", "lcg-scaled-tranche1"), False),
    (
        "toy_crc4",
        "CRC-4",
        ("crc-scaled-tranche1", "crc-scaled-tranche2"),
        True,
    ),
    (
        "mini_hash",
        "Mini-hash",
        ("hash-scaled-tranche1", "hash-easy-tranche1"),
        True,
    ),
]


def records(filename: str, directories: tuple[str, ...], include_legacy: bool):
    paths = [ROOT / "eval" / directory / filename for directory in directories]
    if include_legacy:
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


def family_records(
    family: str,
    filename: str,
    directories: tuple[str, ...],
    include_legacy: bool,
):
    return [
        record
        for record in records(filename, directories, include_legacy)
        if record["family"] == family
    ]


def style_axis(axis, maximum: int = 65) -> None:
    axis.set_ylim(0, maximum)
    axis.set_yticks(range(0, maximum, 10))
    axis.yaxis.set_major_formatter(PercentFormatter(100))
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#CBD0D3")
    axis.grid(axis="y", color="#DDE1E3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", length=0)
    axis.tick_params(axis="x", pad=9)


def main() -> None:
    labels = []
    sample_sizes = {condition: [] for condition, *_ in ALL_CONDITIONS}
    rates = {condition: [] for condition, *_ in ALL_CONDITIONS}
    cheat_rates = {condition: [] for condition, *_ in ALL_CONDITIONS}

    for family, label, directories, include_legacy in FAMILIES:
        labels.append(label)
        for filename, *_ in ALL_CONDITIONS:
            selected_records = family_records(
                family, filename, directories, include_legacy
            )
            rates[filename].append(
                100
                * sum(
                    record["correct"] and not record.get("cheating", False)
                    for record in selected_records
                )
                / len(selected_records)
            )
            cheat_rates[filename].append(
                100
                * sum(
                    record["correct"] and record.get("cheating", False)
                    for record in selected_records
                )
                / len(selected_records)
            )
            sample_sizes[filename].append(len(selected_records))

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "svg.hashsalt": "goodhart-average-thinking-instruction",
        }
    )
    figure, axis = plt.subplots(figsize=(11.5, 5.8), facecolor="#FAFAF8")
    axis.set_facecolor("#FAFAF8")

    positions = range(len(FAMILIES))
    width = 0.2
    offsets = (-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width)
    for (filename, condition, color), offset in zip(ALL_CONDITIONS, offsets):
        bar_positions = [position + offset for position in positions]
        axis.bar(
            bar_positions,
            rates[filename],
            width=width,
            label=condition,
            color=color,
            edgecolor="#46515A",
            linewidth=1.2,
        )
        axis.bar(
            bar_positions,
            cheat_rates[filename],
            bottom=rates[filename],
            width=width,
            color=color,
            alpha=0.42,
            hatch="////",
            edgecolor="#46515A",
            linewidth=1.2,
        )

    axis.set_xticks(list(positions), labels)
    style_axis(axis, maximum=105)
    axis.set_ylabel("Average Correct")
    axis.set_title(
        "Cryptography",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )
    handles, legend_labels = axis.get_legend_handles_labels()
    legend_order = [0, 2, 1, 3]
    axis.legend(
        [handles[index] for index in legend_order],
        [legend_labels[index] for index in legend_order],
        frameon=False,
        loc="lower right",
        bbox_to_anchor=(1, 1.01),
        ncol=2,
    )
    constrained_note = ", ".join(
        f"{label} n={size}"
        for label, size in zip(labels, sample_sizes["unrelated.json"])
    )
    unrestricted_note = ", ".join(
        f"{label} n={size}"
        for label, size in zip(labels, sample_sizes["unrestricted.json"])
    )
    figure.text(
        0.5,
        0.027,
        (
            f"Question-weighted averages. Constrained per condition: {constrained_note}. "
            f"Unrestricted: {unrestricted_note}."
        ),
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.text(
        0.5,
        0.006,
        "Hatched extensions are correct answers containing visible task computation; they are excluded from compliant success.",
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.075, 1, 1), pad=2)
    figure.savefig(
        ROOT / "arithmetic-state-updates-average.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(
        ROOT / "arithmetic-state-updates-average.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(9.6, 5.4), facecolor="#FAFAF8")
    axis.set_facecolor("#FAFAF8")
    vertical_positions = list(reversed(range(len(FAMILIES))))
    point_offsets = (0.18, 0.06, -0.06, -0.18)
    markers = ("D", "o", "s", "^")
    for (filename, condition, color), offset, marker in zip(
        ALL_CONDITIONS, point_offsets, markers
    ):
        point_positions = [position + offset for position in vertical_positions]
        for honest, cheated, point_position in zip(
            rates[filename], cheat_rates[filename], point_positions
        ):
            if cheated:
                axis.plot(
                    [honest, honest + cheated],
                    [point_position, point_position],
                    color=color,
                    alpha=0.5,
                    linewidth=7,
                    solid_capstyle="butt",
                    zorder=1,
                )
        axis.scatter(
            rates[filename],
            point_positions,
            s=105,
            label=condition,
            color=color,
            marker=marker,
            edgecolor="#46515A",
            linewidth=1.2,
            zorder=2,
        )
    axis.set_yticks(vertical_positions, labels)
    axis.set_xlim(0, 105)
    axis.set_xticks(range(0, 101, 10))
    axis.xaxis.set_major_formatter(PercentFormatter(100))
    axis.set_xlabel("Average Correct")
    axis.set_title(
        "Cryptography",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#CBD0D3")
    axis.grid(axis="x", color="#DDE1E3", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", length=0)
    axis.tick_params(axis="y", pad=10)
    handles, legend_labels = axis.get_legend_handles_labels()
    axis.legend(
        [handles[index] for index in legend_order],
        [legend_labels[index] for index in legend_order],
        frameon=False,
        loc="lower right",
        bbox_to_anchor=(1, 1.01),
        ncol=2,
    )
    figure.text(
        0.5,
        0.027,
        (
            f"Question-weighted averages. Constrained per condition: {constrained_note}. "
            f"Unrestricted: {unrestricted_note}."
        ),
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.text(
        0.5,
        0.006,
        "Faded extensions are correct answers containing visible task computation; they are excluded from compliant success.",
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.075, 1, 1), pad=2)
    figure.savefig(
        ROOT / "arithmetic-state-updates-paired-dot.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(
        ROOT / "arithmetic-state-updates-paired-dot.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)

    buckets = [
        ("Easy", 1, 4),
        ("Medium", 5, 8),
        ("Hard", 9, 12),
    ]
    bucket_width = 0.18
    bucket_offsets = (
        -1.5 * bucket_width,
        -0.5 * bucket_width,
        0.5 * bucket_width,
        1.5 * bucket_width,
    )
    figure, axes = plt.subplots(
        1,
        3,
        figsize=(15.5, 5.8),
        sharey=True,
        facecolor="#FAFAF8",
    )
    for axis, (family, label, directories, include_legacy) in zip(axes, FAMILIES):
        axis.set_facecolor("#FAFAF8")
        positions = range(len(buckets))
        for (filename, condition, color), offset in zip(
            ALL_CONDITIONS, bucket_offsets
        ):
            selected_records = family_records(
                family, filename, directories, include_legacy
            )
            bucket_rates = []
            bucket_cheat_rates = []
            for _, lower, upper in buckets:
                bucket_records = [
                    record
                    for record in selected_records
                    if lower <= record["depth"] <= upper
                ]
                bucket_rates.append(
                    100
                    * sum(
                        record["correct"] and not record.get("cheating", False)
                        for record in bucket_records
                    )
                    / len(bucket_records)
                )
                bucket_cheat_rates.append(
                    100
                    * sum(
                        record["correct"] and record.get("cheating", False)
                        for record in bucket_records
                    )
                    / len(bucket_records)
                )
            bar_positions = [position + offset for position in positions]
            axis.bar(
                bar_positions,
                bucket_rates,
                width=bucket_width,
                label=condition,
                color=color,
                edgecolor="#46515A",
                linewidth=1.2,
            )
            axis.bar(
                bar_positions,
                bucket_cheat_rates,
                bottom=bucket_rates,
                width=bucket_width,
                color=color,
                alpha=0.42,
                hatch="////",
                edgecolor="#46515A",
                linewidth=1.2,
            )
        axis.set_xticks(list(positions), [bucket[0] for bucket in buckets])
        style_axis(axis, maximum=105)
        axis.set_title(label, fontsize=15, fontweight="bold", pad=14)

    axes[0].set_ylabel("Average Correct")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    figure.legend(
        [handles[index] for index in legend_order],
        [legend_labels[index] for index in legend_order],
        frameon=False,
        loc="upper right",
        bbox_to_anchor=(0.99, 1.02),
        ncol=2,
    )
    figure.text(
        0.5,
        0.01,
        (
            "Question-weighted averages. Easy: 1–4 hops; Medium: 5–8 hops; "
            "Hard: 9–12 hops. Hatched extensions are correct but cheating."
        ),
        ha="center",
        color="#68727A",
        fontsize=9.5,
    )
    figure.suptitle(
        "Cryptography",
        x=0.02,
        y=1.02,
        ha="left",
        fontsize=17,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.91), pad=2)
    figure.savefig(
        ROOT / "arithmetic-state-updates-by-depth-bucket.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(
        ROOT / "arithmetic-state-updates-by-depth-bucket.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)

    macro_rates = {condition: [] for condition, *_ in ALL_CONDITIONS}
    macro_cheat_rates = {condition: [] for condition, *_ in ALL_CONDITIONS}
    for _, lower, upper in buckets:
        for filename, *_ in ALL_CONDITIONS:
            family_rates = []
            family_cheat_rates = []
            for family, _, directories, include_legacy in FAMILIES:
                bucket_records = [
                    record
                    for record in family_records(
                        family, filename, directories, include_legacy
                    )
                    if lower <= record["depth"] <= upper
                ]
                family_rates.append(
                    100
                    * sum(
                        record["correct"] and not record.get("cheating", False)
                        for record in bucket_records
                    )
                    / len(bucket_records)
                )
                family_cheat_rates.append(
                    100
                    * sum(
                        record["correct"] and record.get("cheating", False)
                        for record in bucket_records
                    )
                    / len(bucket_records)
                )
            macro_rates[filename].append(sum(family_rates) / len(family_rates))
            macro_cheat_rates[filename].append(
                sum(family_cheat_rates) / len(family_cheat_rates)
            )

    figure, axis = plt.subplots(figsize=(9.6, 5.8), facecolor="#FAFAF8")
    axis.set_facecolor("#FAFAF8")
    positions = range(len(buckets))
    for (filename, condition, color), offset in zip(
        ALL_CONDITIONS, bucket_offsets
    ):
        bar_positions = [position + offset for position in positions]
        axis.bar(
            bar_positions,
            macro_rates[filename],
            width=bucket_width,
            label=condition,
            color=color,
            edgecolor="#46515A",
            linewidth=1.2,
        )
        axis.bar(
            bar_positions,
            macro_cheat_rates[filename],
            bottom=macro_rates[filename],
            width=bucket_width,
            color=color,
            alpha=0.42,
            hatch="////",
            edgecolor="#46515A",
            linewidth=1.2,
        )
    axis.set_xticks(list(positions), [bucket[0] for bucket in buckets])
    style_axis(axis, maximum=105)
    axis.set_ylabel("Average Correct")
    axis.set_title(
        "Cryptography",
        loc="left",
        fontsize=17,
        fontweight="bold",
        pad=18,
    )
    handles, legend_labels = axis.get_legend_handles_labels()
    axis.legend(
        [handles[index] for index in legend_order],
        [legend_labels[index] for index in legend_order],
        frameon=False,
        loc="lower right",
        bbox_to_anchor=(1, 1.01),
        ncol=2,
    )
    figure.tight_layout(pad=2)
    figure.savefig(
        ROOT / "arithmetic-state-updates-depth-summary.svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    figure.savefig(
        ROOT / "arithmetic-state-updates-depth-summary.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
