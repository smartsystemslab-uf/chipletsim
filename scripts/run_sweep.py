# scripts/run_sweep.py
# ============================================================
"""Sweep partitioning quality from 0 to 1 and save results as CSV."""

import argparse
import pandas as pd
from chipletsim import ChipletSimulator

def parse_args():
    p = argparse.ArgumentParser(description="Parameter sweep across partitioning quality")
    p.add_argument("--chiplets", type=int, default=4, choices=[2, 4, 8, 16])
    p.add_argument("--workload", type=str, default="ResNet-50",
                   choices=["ResNet-50", "VGG-16", "DarkNet-19"])
    p.add_argument("--steps", type=int, default=21, help="Number of quality steps (default 21 → 0.00, 0.05, …, 1.00)")
    p.add_argument("--output", type=str, default="results/sweep.csv")
    return p.parse_args()

def main():
    args = parse_args()
    sim = ChipletSimulator()
    results = sim.sweep(args.chiplets, args.workload, quality_steps=args.steps)
    df = pd.DataFrame([r.to_dict() for r in results])
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} rows → {args.output}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
