
# scripts/run_single.py
# ============================================================
"""Run a single simulation point and print results to stdout."""

import argparse
import json
from chipletsim import ChipletSimulator

def parse_args():
    p = argparse.ArgumentParser(description="Run a single ChipletSim point")
    p.add_argument("--chiplets", type=int, default=4, choices=[2, 4, 8, 16])
    p.add_argument("--cores-per-chiplet", type=int, default=16)
    p.add_argument("--workload", type=str, default="ResNet-50",
                   choices=["ResNet-50", "VGG-16", "DarkNet-19"])
    p.add_argument("--partitioning-quality", type=float, default=0.75,
                   help="Partitioning quality in [0.0, 1.0]")
    return p.parse_args()

def main():
    args = parse_args()
    sim = ChipletSimulator()
    result = sim.run(
        num_chiplets=args.chiplets,
        workload=args.workload,
        partitioning_quality=args.partitioning_quality,
        cores_per_chiplet=args.cores_per_chiplet,
    )
    print(json.dumps(result.to_dict(), indent=2))

if __name__ == "__main__":
    main()
