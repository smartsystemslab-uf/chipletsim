
# scripts/run_comparison.py
# ============================================================
"""Compare all workloads across all chiplet counts. Saves combined CSV."""

import pandas as pd
from chipletsim import ChipletSimulator, WORKLOAD_REGISTRY

def main():
    sim = ChipletSimulator()
    all_results = []

    for wl in WORKLOAD_REGISTRY:
        for n in [2, 4, 8, 16]:
            rows = sim.sweep(n, wl, quality_steps=11)
            all_results.extend(rows)

    df = pd.DataFrame([r.to_dict() for r in all_results])
    out = "results/full_comparison.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows → {out}")

if __name__ == "__main__":
    main()
