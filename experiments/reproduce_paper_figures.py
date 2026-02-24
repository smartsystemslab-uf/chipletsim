
# experiments/reproduce_paper_figures.py
# ============================================================
"""Reproduce all figures from the paper. Run: python experiments/reproduce_paper_figures.py"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from chipletsim import ChipletSimulator, WORKLOAD_REGISTRY

sns.set_theme(style="whitegrid", palette="colorblind", font_scale=1.2)
COLORS = sns.color_palette("colorblind")

def get_sweep_df(sim, workloads, chiplet_counts, steps=21):
    rows = []
    for wl in workloads:
        for n in chiplet_counts:
            for r in sim.sweep(n, wl, quality_steps=steps):
                rows.append(r.to_dict())
    return pd.DataFrame(rows)

def fig3_latency(df, out_dir):
    """Fig 3: Inter-chiplet latency vs partitioning quality (4 chiplets, all workloads)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sub = df[df.num_chiplets == 4]
    for i, wl in enumerate(WORKLOAD_REGISTRY):
        d = sub[sub.workload == wl]
        ax.plot(d.partitioning_quality * 100, d.inter_chiplet_latency_ns,
                label=wl, color=COLORS[i], linewidth=2)
    ax.set_xlabel("Partitioning Quality (%)")
    ax.set_ylabel("Inter-Chiplet Latency (ns)")
    ax.set_title("Fig. 3: Latency vs Partitioning Quality (4 chiplets)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig3_latency.pdf"), dpi=300)
    fig.savefig(os.path.join(out_dir, "fig3_latency.png"), dpi=300)
    print("Saved fig3_latency")

def fig4_throughput(df, out_dir):
    """Fig 4: Throughput scaling vs chiplet count at 75% partitioning quality."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sub = df[np.isclose(df.partitioning_quality, 0.75, atol=0.03)]
    for i, wl in enumerate(WORKLOAD_REGISTRY):
        d = sub[sub.workload == wl].sort_values("num_chiplets")
        ax.plot(d.num_chiplets, d.throughput_img_per_sec,
                label=wl, color=COLORS[i], marker="o", linewidth=2)
    ax.set_xlabel("Number of Chiplets")
    ax.set_ylabel("Throughput (images/sec)")
    ax.set_title("Fig. 4: Throughput Scaling (75% partitioning quality)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig4_throughput.pdf"), dpi=300)
    fig.savefig(os.path.join(out_dir, "fig4_throughput.png"), dpi=300)
    print("Saved fig4_throughput")

def fig5_congestion(df, out_dir):
    """Fig 5: Network congestion vs partitioning quality (VGG-16, 8 chiplets)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sub = df[(df.workload == "VGG-16") & (df.num_chiplets == 8)]
    ax.plot(sub.partitioning_quality * 100, sub.network_congestion_pct,
            color=COLORS[1], linewidth=2, label="VGG-16, 8 chiplets")
    ax.axhline(70, linestyle="--", color="red", linewidth=1.5, label="Unsustainable threshold (70%)")
    ax.fill_between(sub.partitioning_quality * 100, 70, sub.network_congestion_pct,
                    where=sub.network_congestion_pct > 70, alpha=0.2, color="red")
    ax.set_xlabel("Partitioning Quality (%)")
    ax.set_ylabel("Network Congestion (%)")
    ax.set_title("Fig. 5: Congestion Threshold (VGG-16, 8 Chiplets)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig5_congestion.pdf"), dpi=300)
    fig.savefig(os.path.join(out_dir, "fig5_congestion.png"), dpi=300)
    print("Saved fig5_congestion")

def fig6_energy(df, out_dir):
    """Fig 6: Energy efficiency heatmap (workload × chiplet count at 100% quality)."""
    sub = df[np.isclose(df.partitioning_quality, 1.0, atol=0.05)]
    pivot = sub.pivot_table(values="energy_efficiency_tops_per_w",
                             index="workload", columns="num_chiplets")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax,
                cbar_kws={"label": "TOPS/W"})
    ax.set_title("Fig. 6: Energy Efficiency (TOPS/W) at Optimal Partitioning")
    ax.set_xlabel("Number of Chiplets")
    ax.set_ylabel("Workload")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig6_energy.pdf"), dpi=300)
    fig.savefig(os.path.join(out_dir, "fig6_energy.png"), dpi=300)
    print("Saved fig6_energy")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=str, default="figures/")
    p.add_argument("--fig", type=int, default=None, help="Reproduce specific figure (3-6). Omit for all.")
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    sim = ChipletSimulator()
    df = get_sweep_df(sim, list(WORKLOAD_REGISTRY.keys()), [2, 4, 8, 16])

    fig_map = {3: fig3_latency, 4: fig4_throughput, 5: fig5_congestion, 6: fig6_energy}
    targets = [args.fig] if args.fig else [3, 4, 5, 6]
    for fig_num in targets:
        fig_map[fig_num](df, args.output_dir)

    print(f"\nAll figures saved to: {args.output_dir}")

if __name__ == "__main__":
    main()
